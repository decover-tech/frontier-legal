import copy
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from tools.preservation_rlvr.environment import DEFAULT_TASK, PreservationEnvironment, normalize
from tools.preservation_rlvr.controls import oracle_answer, discover_and_read
from tools.preservation_rlvr.run import main
from tools.rlvr.providers import ProviderError


class PreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = PreservationEnvironment()
        cls.answer = oracle_answer(cls.env)

    def setUp(self):
        self.env.reset()

    def ready(self):
        # Tests other than the trajectory control read the references directly.
        ids = {r['document_id'] for v in self.answer['assessments'].values() for r in v['evidence']+v['challenges']}
        for key in ids:
            offset = 0
            while offset is not None:
                result = self.env.step({'tool':'read','document_id':key,'offset':offset})
                self.assertFalse(result['done'])
                offset = result['observation']['next_offset']
        return copy.deepcopy(self.answer)

    def submit(self, answer):
        return self.env.step({'tool':'submit','answer':answer})

    def test_complete_search_read_submit_episode(self):
        trace = discover_and_read(self.env, self.answer)
        result = self.submit(self.answer)
        self.assertEqual(result['reward'], 1)
        self.assertTrue(result['success'])
        self.assertLess(result['steps'], self.env.task['limits']['max_steps'])
        self.assertTrue(any(r['action']['tool']=='search' for r in trace))
        with self.assertRaises(RuntimeError):
            self.submit(self.answer)

    def test_memorized_answer_without_reading_earns_zero(self):
        self.assertEqual(self.submit(self.answer)['reward'], 0)

    def test_same_fact_changes_as_of_cutoff(self):
        answer = self.ready()
        answer['assessments']['C02'] = copy.deepcopy(answer['assessments']['C03'])
        result = self.submit(answer)
        self.assertEqual(result['assessments']['C02']['reward'], 0)
        self.assertEqual(result['assessments']['C03']['reward'], 1)

    def test_future_source_allowed_only_as_rejected_challenge(self):
        self.ready()
        item = next(x for x in self.env._gold['items'] if x['id']=='C02')
        group = item['challenges'][0]
        ref = self.answer['assessments']['C02']['challenges'][0]
        cutoff = datetime.fromisoformat(item['cutoff'])
        self.assertEqual(self.env._references([ref], [group], cutoff, True), (1,1))
        support = {'document_id':ref['document_id'],'quote':ref['quote']}
        self.assertEqual(self.env._references([support], [group], cutoff), (0,0))

    def test_generic_export_subject_is_not_named_completion(self):
        answer = self.ready()
        self.env.step({'tool':'read','document_id':'EMAIL-1124'})
        answer['assessments']['C03']['evidence'] = [{'document_id':'EMAIL-1124','quote':'Subject: Mailbox export — Nina Alvarez'}]
        self.assertEqual(self.submit(answer)['assessments']['C03']['reward'],0)

    def test_no_confirmation_does_not_prove_deletion(self):
        answer = self.ready()
        answer['assessments']['C06']['status'] = 'documented_complete'
        self.assertEqual(self.submit(answer)['assessments']['C06']['reward'],0)

    def test_unsupported_scope_and_wrong_rules_reduce_reward(self):
        answer = self.ready()
        answer['assessments']['C01']['scope'] = 'all_cascade_systems'
        answer['assessments']['C01']['rules'] = ['R4']
        score = self.submit(answer)['assessments']['C01']['reward']
        self.assertGreater(score,0)
        self.assertLess(score,1)

    def test_exact_event_date_cannot_replace_supported_bound(self):
        answer = self.ready()
        answer['assessments']['C03']['effective_date'] = '2023-06-30'
        self.assertLess(self.submit(answer)['assessments']['C03']['reward'],1)

    def test_missing_conflicts_and_incomplete_audit_lose_credit(self):
        answer = self.ready()
        answer['assessments']['C02']['challenges'] = []
        del answer['assessments']['C05']
        result = self.submit(answer)
        self.assertLess(result['assessments']['C02']['reward'],1)
        self.assertEqual(result['assessments']['C05']['reward'],0)
        self.assertFalse(result['success'])

    def test_fabricated_or_unread_quote_rejected(self):
        answer = self.ready()
        answer['assessments']['C01']['evidence'][0]['quote'] = 'All systems were preserved and all exports were complete.'
        self.assertEqual(self.submit(answer)['assessments']['C01']['reward'],0)

    def test_citation_stuffing_is_not_free(self):
        answer = self.ready()
        self.env.step({'tool':'read','document_id':'EMAIL-003'})
        text = self.env.documents['EMAIL-003']['text']
        answer['assessments']['C01']['evidence'].append({'document_id':'EMAIL-003','quote':text[:150]})
        self.assertLess(self.submit(answer)['assessments']['C01']['reward'],1)

    def test_single_markdown_fence_is_transport_decoration(self):
        answer = self.ready()
        action = '```json\n'+json.dumps({'tool':'submit','answer':answer})+'\n```'
        self.assertEqual(self.env.step(action)['reward'],1)

    def test_duplicate_json_keys_and_invalid_tools_do_not_leak_gold(self):
        for action in ['{"tool":"read","tool":"submit"}', {'tool':'read','document_id':'../../benchmark/hidden_gold/preservation/CTH-PRESERVATION-001.json'}, {'tool':'shell','command':'cat oracle'}]:
            result = self.env.step(action)
            self.assertFalse(result['done'])
            self.assertEqual(result['observation']['error'],'INVALID_ACTION')
            self.assertNotIn('expected',json.dumps(result))

    def test_empty_unknown_and_duplicate_assessments(self):
        self.assertEqual(self.submit({'assessments':{}})['reward'],0)
        self.env.reset()
        self.assertEqual(self.submit({'assessments':{'C99':{}}})['failure_codes'],['INVALID_SUBMISSION'])

    def test_limits_and_reset(self):
        self.env.steps = self.env.task['limits']['max_steps']-1
        self.assertEqual(self.env.step({'tool':'search','query':'mailbox'})['failure_codes'],['STEP_LIMIT'])
        self.env.reset()
        self.env.observation_chars = self.env.task['limits']['max_observation_chars']
        self.assertEqual(self.env.step({'tool':'read','document_id':'EMAIL-024'})['failure_codes'],['OBSERVATION_LIMIT'])
        self.env.reset()
        self.assertEqual(self.env.steps,0)
        self.assertEqual(self.env.read_ranges,{})

    def test_adjacent_read_pages_support_cross_boundary_quotes(self):
        key = 'EMAIL-1096';text = self.env.documents[key]['text']
        quote = self.answer['assessments']['C03']['evidence'][0]['quote']
        start = text.index(quote);middle = start+len(quote)//2
        self.env.read_ranges[key] = [(start,middle),(middle,start+len(quote))]
        self.assertTrue(self.env._seen(key,normalize(quote)))
        self.env.read_ranges[key] = [(start,middle-1),(middle+1,start+len(quote))]
        self.assertFalse(self.env._seen(key,normalize(quote)))

    def test_public_observation_has_no_authoring_material(self):
        text = json.dumps(self.env.reset())
        for forbidden in ['source_path','oracle_path','oracle_sha256','"expected"','hidden_gold','source_anchors','X-Decover-']:
            self.assertNotIn(forbidden,text)
        result = self.env.step({'tool':'search','query':'"Nina Alvarez"'})
        self.assertTrue(result['observation']['hits'])
        self.assertNotIn('source_path',json.dumps(result))

    def test_pinned_assets_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'task.json';task=json.loads(DEFAULT_TASK.read_text())
            task['policy_sha256']='bad';path.write_text(json.dumps(task))
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                PreservationEnvironment(path)
            task=json.loads(DEFAULT_TASK.read_text());task['sources'][0]['source_path']='benchmark/hidden_gold/preservation/CTH-PRESERVATION-001.json';path.write_text(json.dumps(task))
            with self.assertRaisesRegex(ValueError,'outside permitted'):
                PreservationEnvironment(path)

    def test_search_pagination_and_invalid_inputs(self):
        first=self.env.step({'tool':'search','query':'mailbox'})['observation']
        second=self.env.step({'tool':'search','query':'mailbox','offset':first['next_offset']})['observation']
        self.assertFalse({h['document_id'] for h in first['hits']} & {h['document_id'] for h in second['hits']})
        for action in [{'tool':'read','document_id':['bad']},{'tool':'search','query':'"unfinished'},{'tool':'read','document_id':'EMAIL-024','offset':-1}]:
            self.assertEqual(self.env.step(action)['observation']['error'],'INVALID_ACTION')


class RunnerTests(unittest.TestCase):
    def test_provider_error_is_unscored_and_counts_attempt(self):
        with tempfile.TemporaryDirectory() as directory, patch('tools.preservation_rlvr.run.generate',side_effect=ProviderError('HTTP_429')):
            code=main(['--model','openrouter:test','--output-dir',directory])
            result=json.loads(next(Path(directory).glob('*/result.json')).read_text())
            self.assertEqual(code,2)
            self.assertEqual(result['calls'],1)
            self.assertIsNone(result['result']['reward'])
            self.assertIsNone(result['reported_cost_usd'])

    def test_provider_action_to_terminal_environment(self):
        reply={'completion':json.dumps({'tool':'submit','answer':{'assessments':{}}}), 'tokens':{'input':100,'output':20},'usage':{},'stop_reason':'stop','cost_usd':0.01}
        with tempfile.TemporaryDirectory() as directory, patch('tools.preservation_rlvr.run.generate',return_value=reply):
            self.assertEqual(main(['--model','openrouter:test','--output-dir',directory]),0)
            result=json.loads(next(Path(directory).glob('*/result.json')).read_text())
            self.assertEqual(result['result']['reward'],0)
            self.assertEqual(result['reported_output_tokens'],20)
            self.assertEqual(result['reported_cost_usd'],0.01)


if __name__=='__main__':
    unittest.main()
