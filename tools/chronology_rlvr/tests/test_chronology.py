import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from tools.chronology_rlvr.controls import discover_and_read, oracle_answer
from tools.chronology_rlvr.environment import DEFAULT_TASK, VERSION, ChronologyEnvironment
from tools.chronology_rlvr.run import main
from tools.rlvr.providers import ProviderError


class ChronologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = ChronologyEnvironment()
        cls.answer = oracle_answer(cls.env)

    def setUp(self):
        self.env.reset()

    def ready(self):
        # Use actual tool observations; do not grant a test-only citation bypass.
        ids = {ref['document_id'] for section in ('events', 'resolutions')
               for row in self.answer[section].values()
               for ref in row['evidence'] + row.get('challenges', [])}
        for key in sorted(ids):
            offset = 0
            while offset is not None:
                result = self.env.step({'tool': 'read', 'document_id': key, 'offset': offset})
                self.assertFalse(result['done'])
                offset = result['observation']['next_offset']
        return copy.deepcopy(self.answer)

    def submit(self, answer):
        return self.env.step({'tool': 'submit', 'answer': answer})

    def test_complete_search_read_submit_episode(self):
        trace = discover_and_read(self.env, self.answer)
        result = self.submit(self.answer)
        self.assertEqual(result['reward'], 1)
        self.assertTrue(result['success'])
        self.assertTrue(any(row['action']['tool'] == 'search' for row in trace))
        self.assertLess(result['steps'], self.env.task['limits']['max_steps'])
        with self.assertRaises(RuntimeError):
            self.submit(self.answer)

    def test_unread_answer_and_order_cannot_earn_reward(self):
        result = self.submit(self.answer)
        self.assertEqual(result['reward'], 0)
        self.assertEqual(result['components']['ordering'], 0)

    def test_search_snippets_are_not_read_evidence(self):
        self.env.step({'tool': 'search', 'query': '"renewal"'})
        self.assertEqual(self.submit(self.answer)['reward'], 0)

    def test_event_date_is_not_following_day_report(self):
        answer = self.ready()
        row = answer['events']['held_files_excluded']
        row['event_start'] = row['event_end'] = row['reported_on']
        result = self.submit(answer)['events']['held_files_excluded']
        self.assertAlmostEqual(result['timing'], 1 / 3)
        self.assertLess(result['reward'], 1)

    def test_pilot_event_is_not_later_summary_date(self):
        answer = self.ready()
        row = answer['events']['pilot_first_pass']
        row['event_start'] = row['event_end'] = '2023-09-07'
        row['reported_on'] = '2023-09-07'
        result = self.submit(answer)['events']['pilot_first_pass']
        self.assertEqual(result['report_time'], 0)
        self.assertLess(result['reward'], 1)

    def test_this_week_does_not_support_an_invented_exact_day(self):
        answer = self.ready()
        row = answer['events']['claimed_renewal']
        row['event_start'] = row['event_end'] = '2022-12-20'
        row['precision'] = 'day'
        self.assertAlmostEqual(self.submit(answer)['events']['claimed_renewal']['timing'], 1 / 3)

    def test_claim_cannot_be_promoted_to_completed_action(self):
        answer = self.ready()
        answer['events']['claimed_renewal']['nature'] = 'completed_action'
        self.assertEqual(self.submit(answer)['events']['claimed_renewal']['reward'], 0)

    def test_restatement_is_not_a_second_renewal(self):
        answer = self.ready()
        answer['events']['renewal_restatement']['event_start'] = '2022-12-20'
        answer['events']['renewal_restatement']['event_end'] = '2022-12-20'
        self.assertLess(self.submit(answer)['events']['renewal_restatement']['reward'], 1)

    def test_scheduling_date_is_not_target_execution_date(self):
        answer = self.ready()
        answer['events']['pilot_scheduling']['event_start'] = '2023-09-05'
        answer['events']['pilot_scheduling']['event_end'] = '2023-09-05'
        self.assertLess(self.submit(answer)['events']['pilot_scheduling']['reward'], 1)

    def test_wrong_actor_loses_credit(self):
        answer = self.ready()
        answer['events']['claimed_renewal']['actor'] = 'pshah@alderpointpartners.com'
        self.assertEqual(self.submit(answer)['events']['claimed_renewal']['actor'], 0)

    def test_same_day_instruction_precedes_status_response(self):
        answer = self.ready()
        order = answer['order']
        a, b = order.index('h1_conditional_route'), order.index('h1_still_held')
        order[a], order[b] = order[b], order[a]
        result = self.submit(answer)
        self.assertAlmostEqual(result['components']['ordering'], 90 / 91)
        self.assertFalse(result['success'])

    def test_reversed_order_earns_zero_ordering(self):
        answer = self.ready()
        answer['order'].reverse()
        self.assertEqual(self.submit(answer)['components']['ordering'], 0)

    def test_order_does_not_earn_credit_for_missing_event(self):
        answer = self.ready()
        del answer['events']['renewal_pending']
        self.assertAlmostEqual(self.submit(answer)['components']['ordering'], 78 / 91)

    def test_unverified_claim_is_not_proven_false(self):
        answer = self.ready()
        answer['resolutions']['registration_issuance']['conclusion'] = 'contradicted'
        self.assertEqual(self.submit(answer)['resolutions']['registration_issuance']['reward'], 0)

    def test_permission_and_tieout_do_not_prove_transmission(self):
        answer = self.ready()
        row = answer['resolutions']['h1_transmittal']
        row['conclusion'] = 'established'
        row['event_date'] = '2022-11-17'
        self.assertEqual(self.submit(answer)['resolutions']['h1_transmittal']['reward'], 0)

    def test_review_completion_does_not_close_substantive_exceptions(self):
        answer = self.ready()
        answer['resolutions']['pilot_exceptions']['conclusion'] = 'established'
        self.assertEqual(self.submit(answer)['resolutions']['pilot_exceptions']['reward'], 0)

    def test_later_pilot_does_not_date_historical_quarterly_controls(self):
        answer = self.ready()
        answer['resolutions']['historical_quarterly_tests']['event_date'] = '2023-09-06'
        result = self.submit(answer)['resolutions']['historical_quarterly_tests']
        self.assertEqual(result['event_date'], 0)
        self.assertLess(result['reward'], 1)

    def test_after_cutoff_evidence_only_works_as_rejected_challenge(self):
        self.ready()
        item = next(x for x in self.env._gold['resolutions'] if x['id'] == 'pilot_asof_august')
        group = item['challenges'][0]
        ref = self.answer['resolutions'][item['id']]['challenges'][0]
        cutoff = datetime.fromisoformat(item['cutoff'])
        self.assertEqual(self.env._references([ref], [group], cutoff, True), (1, 1))
        support = {'document_id': ref['document_id'], 'quote': ref['quote']}
        self.assertEqual(self.env._references([support], [group], cutoff), (0, 0))

    def test_wrong_conflict_reason_and_extra_rules_lose_credit(self):
        answer = self.ready()
        row = answer['resolutions']['registration_issuance']
        row['challenges'][0]['reason'] = 'forecast_not_execution'
        row['rules'] = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        result = self.submit(answer)['resolutions']['registration_issuance']
        self.assertEqual(result['conflict_resolution'], 0)
        self.assertLess(result['rule_selection'], 1)

    def test_partial_support_cannot_earn_full_event_credit(self):
        answer = self.ready()
        answer['events']['pilot_first_pass']['evidence'] = answer['events']['pilot_first_pass']['evidence'][:1]
        self.assertEqual(self.submit(answer)['events']['pilot_first_pass']['support_coverage'], 0.5)

    def test_fabricated_quote_earns_zero(self):
        answer = self.ready()
        answer['events']['renewal_pending']['evidence'][0]['quote'] = 'The broker renewal was still awaiting approval on September 15.'
        self.assertEqual(self.submit(answer)['events']['renewal_pending']['reward'], 0)

    def test_citation_stuffing_lowers_precision(self):
        answer = self.ready()
        result = self.env.step({'tool': 'read', 'document_id': 'EMAIL-003'})
        answer['events']['renewal_pending']['evidence'].append({'document_id': 'EMAIL-003', 'quote': result['observation']['text'][:150]})
        self.assertEqual(self.submit(answer)['events']['renewal_pending']['evidence_precision'], 0.5)

    def test_malformed_dates_and_nested_values_fail_safely(self):
        for field, value in [('event_start', '2023-02-30'), ('event_end', None), ('precision', []), ('actor', {}), ('evidence', [{'document_id': [], 'quote': 'x' * 25}])]:
            with self.subTest(field=field):
                answer = copy.deepcopy(self.answer)
                answer['events']['renewal_pending'][field] = value
                result = self.env.verify(answer)
                self.assertEqual(result['events']['renewal_pending']['failure'], 'MISSING_OR_MALFORMED_EVENT')

    def test_unknown_ids_and_duplicate_order_are_invalid(self):
        for change in ('event', 'resolution', 'duplicate', 'nested_order'):
            with self.subTest(change=change):
                answer = copy.deepcopy(self.answer)
                if change == 'event':
                    answer['events']['invented'] = {}
                elif change == 'resolution':
                    answer['resolutions']['invented'] = {}
                elif change == 'duplicate':
                    answer['order'].append(answer['order'][0])
                else:
                    answer['order'].append([])
                self.assertEqual(self.env.verify(answer)['failure_codes'], ['INVALID_SUBMISSION'])

    def test_single_markdown_fence_is_accepted(self):
        answer = self.ready()
        action = '```json\n' + json.dumps({'tool': 'submit', 'answer': answer}) + '\n```'
        self.assertEqual(self.env.step(action)['reward'], 1)

    def test_public_interface_excludes_oracle_and_filesystem(self):
        observation = json.dumps(self.env.reset())
        for forbidden in ('source_path', 'oracle_path', 'oracle_sha256', '"expected"', 'hidden_gold', 'X-Decover-'):
            self.assertNotIn(forbidden, observation)
        for action in ({'tool': 'shell', 'command': 'cat oracle'}, {'tool': 'read', 'document_id': '../../benchmark/hidden_gold/chronology/CTH-CHRONOLOGY-001.json'}, '{"tool":"read","tool":"submit"}'):
            result = self.env.step(action)
            self.assertFalse(result['done'])
            self.assertEqual(result['observation']['error'], 'INVALID_ACTION')

    def test_limits_keep_chronology_verifier_version(self):
        self.env.steps = self.env.task['limits']['max_steps'] - 1
        result = self.env.step({'tool': 'search', 'query': 'pilot'})
        self.assertEqual(result['failure_codes'], ['STEP_LIMIT'])
        self.assertEqual(result['verifier_version'], VERSION)
        self.env.reset()
        self.env.observation_chars = self.env.task['limits']['max_observation_chars']
        result = self.env.step({'tool': 'read', 'document_id': 'EMAIL-003'})
        self.assertEqual(result['failure_codes'], ['OBSERVATION_LIMIT'])
        self.assertEqual(result['verifier_version'], VERSION)
        self.env.reset()
        self.assertEqual(self.env.read_ranges, {})

    def test_pinned_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'task.json'
            for field in ('policy_sha256', 'schema_sha256', 'oracle_sha256'):
                task = json.loads(DEFAULT_TASK.read_text())
                task[field] = 'bad'
                path.write_text(json.dumps(task))
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    ChronologyEnvironment(path)
            task = json.loads(DEFAULT_TASK.read_text())
            task['sources'][0]['source_path'] = task['oracle_path']
            path.write_text(json.dumps(task))
            with self.assertRaisesRegex(ValueError, 'outside permitted'):
                ChronologyEnvironment(path)


class RunnerTests(unittest.TestCase):
    def test_provider_error_is_unscored_and_counts_attempt(self):
        with tempfile.TemporaryDirectory() as directory, patch('tools.chronology_rlvr.run.generate', side_effect=ProviderError('HTTP_429')):
            self.assertEqual(main(['--model', 'openrouter:test', '--output-dir', directory]), 2)
            result = json.loads(next(Path(directory).glob('*/result.json')).read_text())
            self.assertEqual(result['calls'], 1)
            self.assertIsNone(result['result']['reward'])
            self.assertIsNone(result['reported_cost_usd'])

    def test_provider_action_reaches_terminal_verifier(self):
        reply = {'completion': json.dumps({'tool': 'submit', 'answer': {'events': {}, 'order': [], 'resolutions': {}}}), 'tokens': {'input': 100, 'output': 20}, 'usage': {}, 'stop_reason': 'stop', 'cost_usd': 0.01}
        with tempfile.TemporaryDirectory() as directory, patch('tools.chronology_rlvr.run.generate', return_value=reply):
            self.assertEqual(main(['--model', 'openrouter:test', '--output-dir', directory]), 0)
            result = json.loads(next(Path(directory).glob('*/result.json')).read_text())
            self.assertEqual(result['result']['reward'], 0)
            self.assertEqual(result['reported_output_tokens'], 20)
            self.assertEqual(result['reported_cost_usd'], 0.01)


if __name__ == '__main__':
    unittest.main()
