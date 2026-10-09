"""Source-grounded controls for demand-draft."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class Task07Tests(unittest.TestCase):
    def test_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        result=exercise_controls('CTH-LIT-07',root=ROOT)
        self.assertTrue(result['positive']['passed'])
        for name,outcome in result['negative'].items():
            with self.subTest(name=name):self.assertLess(outcome['reward'],result['positive']['reward'])
if __name__=='__main__':unittest.main()
