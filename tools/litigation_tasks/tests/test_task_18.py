import unittest
from tools.litigation_tasks.controls import exercise_controls
class Task18Tests(unittest.TestCase):
    def test_source_grounded_state_controls(self):
        results=exercise_controls("CTH-LIT-18")
        self.assertTrue(results["positive"]["passed"])
        for name,result in results["negative"].items():
            with self.subTest(name=name):
                self.assertFalse(result.get("passed",False))
                self.assertLess(result["reward"],results["positive"]["reward"])
