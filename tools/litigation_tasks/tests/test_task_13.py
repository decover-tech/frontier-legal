"""Family independence, consultant scope, and uncertainty adversaries."""
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]

class PrivilegeTaskTests(unittest.TestCase):
    def test_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        result = exercise_controls('CTH-LIT-13', root=ROOT)
        self.assertTrue(result['positive']['passed'])
        for name, outcome in result['negative'].items():
            with self.subTest(name=name):
                self.assertLess(outcome['reward'], result['positive']['reward'])

    def test_independent_attachment_and_uncertainty_cases(self):
        gold = json.loads((ROOT/'benchmark/hidden_gold/litigation_skills/CTH-LIT-13.json').read_text())
        names = {n['name'] for n in gold['negative_controls']}
        self.assertTrue({'family_inherits_privilege', 'invent_provision_attachment_inspection',
                         'borrow_direction_from_other_workbook', 'proposed_sharing_becomes_waiver'} <= names)
        # A legal-advice self-marking alone is not the separately inspected memo proof.
        alternatives = gold['findings']['F01']['support_groups'][1]['alternatives']
        self.assertTrue(all('We recommend pausing' in c['quote'] for c in alternatives))

if __name__ == '__main__':
    unittest.main()
