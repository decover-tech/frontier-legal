"""Source-grounded controls for deposition-prep."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class Task12Tests(unittest.TestCase):
    def test_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        result=exercise_controls('CTH-LIT-12',root=ROOT)
        self.assertTrue(result['positive']['passed'])
        for name,outcome in result['negative'].items():
            with self.subTest(name=name):self.assertLess(outcome['reward'],result['positive']['reward'])
    def test_topic_permutation_is_not_a_label_penalty(self):
        from tools.litigation_tasks.controls import run_control
        result=run_control('CTH-LIT-12',root=ROOT,mutation={
            'kind':'artifact_field','path':'witness/tom-reyes-outline.json',
            'pointer':'/question_order','value':['F01','F03','F02','F05','F04']})
        self.assertTrue(result['passed'])

if __name__=='__main__':unittest.main()
