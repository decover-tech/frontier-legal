import json
import tempfile
import unittest
from pathlib import Path
from tools.rlvr.audit import AuditEnvironment, equal, verify_audit
from tools.rlvr.environment import ROOT
from tools.rlvr.providers import normalize, read_openrouter_key, request_spec, ProviderError
from tools.rlvr.run import summarize


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = AuditEnvironment(ROOT / 'benchmark/rlvr/tasks/CTH-AUDIT-001.json')

    def test_golden_and_episode(self):
        self.env.reset()
        self.assertEqual(self.env.step(self.env.golden_solution())['reward'], 1)
        with self.assertRaises(RuntimeError):
            self.env.step(self.env.golden_solution())

    def test_public_observation_excludes_gold(self):
        text = json.dumps(self.env.reset())
        for hidden in ['source_anchors', 'evidence_groups', 'oracle_sha256', 'hidden_gold', 'source_path', 'value_accuracy']:
            self.assertNotIn(hidden, text)
        self.assertEqual(len(self.env.documents), 75)

    def test_wrong_value_cannot_earn_citation_credit(self):
        item = self.env.items[1]
        answer = {'answers': {item['id']: {'value': 999, 'evidence': [g[0] for g in item['evidence_groups']]}}}
        self.assertEqual(verify_audit(json.dumps(answer), [item])['reward'], 0)

    def test_partial_citations_and_irrelevant_citations(self):
        item = self.env.items[1]
        refs = [item['evidence_groups'][0][0]]
        answer = {'answers': {item['id']: {'value': item['value'], 'evidence': refs}}}
        self.assertAlmostEqual(verify_audit(json.dumps(answer), [item])['reward'], .85)
        refs.append('EMAIL-999')
        self.assertAlmostEqual(verify_audit(json.dumps(answer), [item])['reward'], .775)
        refs.extend(['EMAIL-998', 'EMAIL-997', 'EMAIL-996'])
        self.assertEqual(verify_audit(json.dumps(answer), [item])['reward'], 0)

    def test_context_citations_are_relevant_but_do_not_replace_anchors(self):
        item = next(i for i in self.env.items if i['id'] == 'Q04')
        answer = {'answers': {'Q04': {'value': item['value'], 'evidence': ['EMAIL-171', 'EMAIL-068']}}}
        self.assertEqual(verify_audit(json.dumps(answer), [item])['reward'], 1)
        answer['answers']['Q04']['evidence'] = ['EMAIL-068']
        self.assertEqual(verify_audit(json.dumps(answer), [item])['reward'], .7)

    def test_invalid_output(self):
        for text in ['null', '{"answers":{},"answers":{}}', '{"answers":{"Q99":{}}}', '{"answers":NaN}', '```json\n{}\n```']:
            self.assertEqual(verify_audit(text, self.env.items)['failure_codes'], ['INVALID_OUTPUT'])
        self.assertEqual(verify_audit('{"answers":{}}', self.env.items)['reward'], 0)

    def test_strict_types_and_normalized_strings(self):
        self.assertFalse(equal(False, 0))
        self.assertFalse(equal(29.0, 29))
        self.assertTrue(equal(' Board ', 'board'))

    def test_tampered_oracle_and_source(self):
        for field in ['oracle_sha256', 'source_sha256']:
            task = json.loads(json.dumps(self.env.task))
            (task if field == 'oracle_sha256' else task['sources'][0])[field] = 'bad'
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'task.json'
                path.write_text(json.dumps(task))
                with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                    AuditEnvironment(path)


class OpenRouterTests(unittest.TestCase):
    def test_request_response_and_cost(self):
        url, body = request_spec('openrouter', 'a/b', [{'role': 'user', 'content': 'test'}], 42)
        self.assertEqual(url, 'https://openrouter.ai/api/v1/chat/completions')
        self.assertFalse(body['provider']['allow_fallbacks'])
        result = normalize('openrouter', {'choices': [{'message': {'content': '{}'}, 'finish_reason': 'stop'}], 'provider': 'Example', 'usage': {'prompt_tokens': 10, 'completion_tokens': 4, 'cost': .02}}, 'a/b')
        self.assertEqual(result['cost_usd'], .02)
        self.assertEqual(result['routing_provider'], 'Example')
        row = {**result, 'provider': 'openrouter', 'requested_model': 'a/b', 'status': 'scored', 'evaluation': {'reward': .5, 'success': False}, 'latency_seconds': 1}
        self.assertEqual(summarize([row, row])[0]['cost_usd'], .04)

    def test_explicit_key_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'keys.txt'
            path.write_text('OpenRouter: sk-or-v1-testcredential')
            self.assertEqual(read_openrouter_key(path), 'sk-or-v1-testcredential')
            path.write_text('sk-or-v1-one sk-or-v1-two')
            with self.assertRaisesRegex(ProviderError, '^KEY_FILE_MUST_CONTAIN_ONE_OPENROUTER_KEY$'):
                read_openrouter_key(path)
