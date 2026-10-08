import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock

from tools.rlvr.environment import DateEnvironment, DEFAULT_TASK, expected_date, verify
from tools.rlvr.providers import ProviderError, generate, normalize, request_spec
from tools.rlvr.run import main, summarize


class VerificationTests(unittest.TestCase):
    def test_correct(self):
        self.assertEqual(verify(' {"sent_date":"2022-03-02"}\n', "2022-03-02")["reward"], 1)

    def test_reject_bad_answers(self):
        values = ['{"sent_date":"2022-03-03"}', '```json\n{"sent_date":"2022-03-02"}\n```',
                  '{"sent_date":"2022-3-2"}', '{"sent_date":"2022-02-30"}',
                  '{"sent_date":20220302}', '{"sent_date":null}', '[]', 'null',
                  '{"sent_date":"2022-03-02","extra":true}',
                  '{"sent_date":"wrong","sent_date":"2022-03-02"}',
                  '{"sent_date":"2022-03-02"} trailing', 'NaN']
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(verify(value, "2022-03-02")["reward"], 0)

    def test_local_date_not_utc(self):
        raw = b'Date: Wed, 02 Mar 2022 23:47:00 -0800\r\n\r\nDate: Jan 1 1999'
        self.assertEqual(expected_date(raw), "2022-03-02")

    def test_eastern_offset_midnight(self):
        self.assertEqual(expected_date(b'Date: Wed, 02 Mar 2022 00:10:00 +1400\n\n'), "2022-03-02")

    def test_bad_source_headers(self):
        for raw in [b'Subject: missing date\n\n', b'Date: nonsense\n\n',
                    b'Date: Wed, 02 Mar 2022 11:47:00 -0000\n\n',
                    b'Date: Wed, 02 Mar 2022 11:47:00 -0800\nDate: Wed, 02 Mar 2022 11:47:00 -0800\n\n']:
            with self.subTest(raw=raw):
                with self.assertRaises((ValueError, TypeError)):
                    expected_date(raw)

    def test_actual_evidence_and_episode(self):
        env = DateEnvironment()
        with self.assertRaises(RuntimeError):
            env.step('{}')
        observation = env.reset()
        self.assertEqual(set(observation), {"task_id", "messages"})
        self.assertNotIn("X-Decover-", observation["messages"][0]["content"])
        self.assertTrue(env.step('{"sent_date":"2022-03-02"}')["success"])
        with self.assertRaises(RuntimeError):
            env.step('{}')
        env.reset()
        self.assertEqual(env.step('{}')["reward"], 0)

    def test_hash_and_path_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            task = json.loads(DEFAULT_TASK.read_text())
            file = Path(directory) / 'task.json'
            task['source_sha256'] = 'bad'
            file.write_text(json.dumps(task))
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                DateEnvironment(file)
            task['source_path'] = 'benchmark/hidden_gold/flagship_gold.jsonl'
            file.write_text(json.dumps(task))
            with self.assertRaisesRegex(ValueError, 'permitted email corpus'):
                DateEnvironment(file)


class AdapterTests(unittest.TestCase):
    def test_requests_use_same_prompt(self):
        messages = [{"role": "user", "content": "evidence prompt"}]
        for provider in ['openai', 'anthropic', 'gemini']:
            with self.subTest(provider=provider):
                url, body = request_spec(provider, 'model', messages, 123)
                self.assertTrue(url.startswith('https://'))
                self.assertIn('evidence prompt', json.dumps(body))
                self.assertIn('123', json.dumps(body))
                self.assertNotIn('expected', json.dumps(body))

    def test_openai_response(self):
        response = {'model': 'resolved', 'status': 'completed', 'output': [
            {'type': 'reasoning', 'summary': []},
            {'type': 'message', 'content': [{'type': 'output_text', 'text': '{"sent_date":"2022-03-02"}'}]}],
            'usage': {'input_tokens': 20, 'output_tokens': 10}}
        result = normalize('openai', response, 'requested')
        self.assertEqual(result['resolved_model'], 'resolved')
        self.assertEqual(result['tokens'], {'input': 20, 'output': 10})
        self.assertEqual(verify(result['completion'], '2022-03-02')['reward'], 1)

    def test_anthropic_response(self):
        response = {'content': [{'type': 'thinking', 'thinking': 'ignore'}, {'type': 'text', 'text': '{}'}],
                    'stop_reason': 'end_turn', 'usage': {'input_tokens': 10, 'cache_read_input_tokens': 3, 'output_tokens': 4}}
        result = normalize('anthropic', response, 'model')
        self.assertEqual(result['completion'], '{}')
        self.assertEqual(result['tokens']['input'], 13)

    def test_gemini_response(self):
        response = {'modelVersion': 'pinned', 'candidates': [{'content': {'parts': [
            {'text': 'private reasoning', 'thought': True}, {'text': '{}'}]}, 'finishReason': 'STOP'}],
            'usageMetadata': {'promptTokenCount': 10, 'candidatesTokenCount': 4, 'thoughtsTokenCount': 8}}
        result = normalize('gemini', response, 'model')
        self.assertEqual(result['completion'], '{}')
        self.assertEqual(result['tokens']['output'], 12)
        self.assertEqual(result['resolved_model'], 'pinned')

    def test_refusal_empty_output_is_scored_failure(self):
        result = normalize('openai', {'output': [{'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'no'}]}]}, 'model')
        self.assertEqual(verify(result['completion'], '2022-03-02')['reward'], 0)

    def test_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ProviderError, 'MISSING_CREDENTIAL'):
                generate('anthropic', 'model', [])

    def test_safe_http_error(self):
        opener = MagicMock()
        opener.open.side_effect = urllib.error.HTTPError('https://example', 401, 'secret provider detail', {}, None)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-secret'}), patch('urllib.request.build_opener', return_value=opener):
            with self.assertRaisesRegex(ProviderError, '^HTTP_401$'):
                generate('openai', 'model', [])

    def test_transport_to_verifier_all_providers(self):
        fixtures = {
            'openai': {'error': None, 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': '{"sent_date":"2022-03-02"}'}]}]},
            'anthropic': {'content': [{'type': 'text', 'text': '{"sent_date":"2022-03-02"}'}]},
            'gemini': {'candidates': [{'content': {'parts': [{'text': '{"sent_date":"2022-03-02"}'}]}}]},
        }
        for provider, response in fixtures.items():
            with self.subTest(provider=provider):
                opener = MagicMock()
                opener.open.return_value.__enter__.return_value.read.return_value = json.dumps(response)
                keys = {'OPENAI_API_KEY': 'test', 'ANTHROPIC_API_KEY': 'test', 'GEMINI_API_KEY': 'test'}
                with patch.dict(os.environ, keys), patch('urllib.request.build_opener', return_value=opener):
                    result = generate(provider, 'model', [{'role': 'user', 'content': 'prompt'}])
                self.assertEqual(verify(result['completion'], '2022-03-02')['reward'], 1)


class RunnerTests(unittest.TestCase):
    def test_offline_controls(self):
        with tempfile.TemporaryDirectory() as directory, patch('tools.rlvr.run.generate') as mock:
            self.assertEqual(main(['--self-test', '--output-dir', directory]), 0)
            mock.assert_not_called()
            report = json.loads(next(Path(directory).glob('*/self_test.json')).read_text())
            self.assertEqual(report['checks']['correct']['reward'], 1)

    def test_records_and_errors(self):
        answer = {'completion': '{"sent_date":"2022-03-02"}', 'tokens': {'input': 10, 'output': 10},
                  'usage': {}, 'resolved_model': 'test-model', 'stop_reason': 'completed'}
        with tempfile.TemporaryDirectory() as directory, patch('tools.rlvr.run.generate', side_effect=[answer, ProviderError('HTTP_429')]):
            code = main(['--model', 'openai:test-model', '--repetitions', '2', '--output-dir', directory])
            self.assertEqual(code, 2)
            report = json.loads(next(Path(directory).glob('*/summary.json')).read_text())['results'][0]
            self.assertEqual((report['scored'], report['errors'], report['mean_reward']), (1, 1, 1))
            self.assertIsNone(report['cost_usd'])
            records = next(Path(directory).glob('*/records.jsonl')).read_text()
            self.assertNotIn('Authorization', records)

    def test_all_errors_no_false_zero(self):
        result = summarize([{'provider': 'openai', 'requested_model': 'm', 'status': 'error'}])[0]
        self.assertIsNone(result['mean_reward'])
        self.assertIsNone(result['success_rate'])


if __name__ == '__main__':
    unittest.main()
