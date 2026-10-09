"""Executable controls for CTH-LIT-04; distinct sources and artifact/state adversaries."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class Task04Tests(unittest.TestCase):
    def test_end_to_end_and_adversaries(self):
        from tools.litigation_tasks.controls import exercise_controls
        result=exercise_controls('CTH-LIT-04',root=ROOT)
        self.assertTrue(result['positive']['passed'])
        self.assertEqual(result['positive']['reward'],1.0)
        for name,outcome in result['negative'].items():
            with self.subTest(name=name):
                self.assertLess(outcome['reward'],result['positive']['reward'])
if __name__=='__main__':unittest.main()
