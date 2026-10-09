"""Source-grounded controls for claim-chart."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class Task11Tests(unittest.TestCase):
    def test_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        result=exercise_controls('CTH-LIT-11',root=ROOT)
        self.assertTrue(result['positive']['passed'])
        for name,outcome in result['negative'].items():
            with self.subTest(name=name):self.assertLess(outcome['reward'],result['positive']['reward'])
if __name__=='__main__':unittest.main()
