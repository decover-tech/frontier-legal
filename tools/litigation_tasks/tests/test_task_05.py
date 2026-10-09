"""Actual demand trigger, version and conditional-clock adversaries."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
class DemandReceivedTests(unittest.TestCase):
    def test_controls(self):
        from tools.litigation_tasks.controls import exercise_controls
        r=exercise_controls('CTH-LIT-05',root=ROOT)
        self.assertTrue(r['positive']['passed'])
        for name,v in r['negative'].items():
            with self.subTest(name=name):self.assertLess(v['reward'],r['positive']['reward'])
if __name__=='__main__':unittest.main()
