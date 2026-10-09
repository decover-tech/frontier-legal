"""Summons triage controls include actual instrument conflict and report/event time."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class SummonsTriageTests(unittest.TestCase):
    def test_task_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        result = exercise_controls('CTH-LIT-08', root=ROOT)
        self.assertTrue(result['positive']['passed'])
        for name, outcome in result['negative'].items():
            with self.subTest(name=name):
                self.assertLess(outcome['reward'], result['positive']['reward'])

    def test_version_conflict_and_temporal_adversaries_exist(self):
        import json
        gold = json.loads((ROOT / 'benchmark/hidden_gold/litigation_skills/CTH-LIT-08.json').read_text())
        names = {item['name'] for item in gold['negative_controls']}
        self.assertTrue({'unproved_historical_amendment', 'scope_version_conflict_omitted',
                         'report_time_conflated_with_interim_event',
                         'receipt_after_deadline_proves_default'} <= names)
        # Each matrix row has its own actual supplied-instrument proof.
        self.assertEqual(len(gold['findings']['F04']['support_groups']), 7)


if __name__ == '__main__':
    unittest.main()
