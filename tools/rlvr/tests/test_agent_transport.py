import json
import os
import unittest
from unittest.mock import MagicMock, patch

from tools.rlvr.providers import budget_diagnostics, generate, request_spec


class AgentTransportTests(unittest.TestCase):
    def test_default_request_retains_legacy_behavior(self):
        body = request_spec('openrouter', 'test', [], 24000)[1]
        self.assertNotIn('reasoning', body)
        self.assertEqual(body['provider'], {'allow_fallbacks': False})

    def test_reasoning_control_reaches_actual_http_request(self):
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value.read.return_value = json.dumps({
            'choices': [{'message': {'content': '{}'}, 'finish_reason': 'stop'}]})
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-secret'}), patch('urllib.request.build_opener', return_value=opener):
            generate('openrouter', 'test', [], 16384, reasoning_effort='low')
        request = opener.open.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(body['reasoning'], {'effort': 'low'})
        self.assertEqual(body['provider'], {'allow_fallbacks': False, 'require_parameters': True})
        self.assertEqual(body['max_tokens'], 16384)
        self.assertNotIn('test-secret', request.data.decode())

    def test_direct_provider_does_not_silently_ignore_control(self):
        with self.assertRaises(ValueError):
            request_spec('anthropic', 'test', [], 100, reasoning_effort='low')

    def test_overrun_is_distinct_from_truncation(self):
        result = budget_diagnostics({'completion': '{}', 'stop_reason': 'stop',
                                    'tokens': {'output': 200},
                                    'usage': {'completion_tokens_details': {'reasoning_tokens': 150}}}, 100)
        self.assertTrue(result['reported_output_exceeds_requested_limit'])
        self.assertFalse(result['output_budget_exhausted'])
        self.assertEqual(result['estimated_visible_tokens'], 50)
        self.assertTrue(budget_diagnostics({'stop_reason': 'length'}, 100)['output_budget_exhausted'])

    def test_missing_usage_is_not_reported_as_zero(self):
        result = budget_diagnostics({}, 100)
        self.assertIsNone(result['reported_output_tokens'])
        self.assertIsNone(result['estimated_visible_tokens'])
        self.assertIsNone(result['reported_output_exceeds_requested_limit'])


if __name__ == '__main__':
    unittest.main()
