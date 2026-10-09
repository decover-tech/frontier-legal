import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from tools.rlvr.environment import ROOT, sha256
from tools.rlvr.inventory import InventoryEnvironment, VERSION, derive, score_value


class InventoryTests(unittest.TestCase):
    def test_derived_inventory_on_hand_counted_fixture(self):
        rows = [
            {'id': 'EMAIL-001', 'date': datetime.fromisoformat('2023-06-17T23:30:00-07:00'), 'sender': 'a@cascadetimber.com', 'domain': 'cascadetimber.com', 'recipients': {'cascadetimber.com', 'bellhavenadvisory.com'}},
            {'id': 'EMAIL-002', 'date': datetime.fromisoformat('2023-06-18T08:00:00-07:00'), 'sender': 'b@llassociates.com', 'domain': 'llassociates.com', 'recipients': {'cascadetimber.com', 'bellhavenadvisory.com'}},
            {'id': 'EMAIL-003', 'date': datetime.fromisoformat('2023-07-01T08:00:00-07:00'), 'sender': 'a@cascadetimber.com', 'domain': 'cascadetimber.com', 'recipients': {'cascadetimber.com'}},
        ]
        expected = derive(rows)
        self.assertEqual(expected['Q01'], {'2023-06': 2, '2023-07': 1})
        self.assertEqual(expected['Q03'], ['EMAIL-001'])
        self.assertEqual(expected['Q04'], ['EMAIL-002'])
        self.assertEqual(expected['Q05'], ['EMAIL-001', 'EMAIL-002'])
        self.assertEqual(expected['Q06'], ['a@cascadetimber.com', 'b@llassociates.com'])
        self.assertEqual(expected['Q07'], ['EMAIL-001', 'EMAIL-002', 'EMAIL-003'])
        self.assertEqual(expected['Q08'], ['EMAIL-001'])
        self.assertEqual(expected['Q09'], {'cascadetimber.com -> bellhavenadvisory.com': 1, 'llassociates.com -> cascadetimber.com': 1, 'llassociates.com -> bellhavenadvisory.com': 1})
        self.assertEqual(expected['Q10'], [])
        self.assertEqual(expected['Q11'], ['EMAIL-002'])
        self.assertEqual(expected['Q12'], ['EMAIL-003', 'EMAIL-002', 'EMAIL-001'])

    def test_rewards_penalize_overgeneration(self):
        self.assertEqual(score_value({'a': 1, 'b': 2}, {'a': 1}, 'mapping'), .5)
        self.assertEqual(score_value({'a': True}, {'a': 1}, 'mapping'), 0)
        self.assertEqual(score_value(['a', 'a'], ['a'], 'set'), 0)
        self.assertAlmostEqual(score_value(['a', 'b'], ['a'], 'set'), 2/3)
        self.assertEqual(score_value([], [], 'set'), 1)
        self.assertEqual(score_value(['b', 'a'], ['a', 'b'], 'ordered'), 0)
        self.assertEqual(score_value(['a', 'b', 'c'], ['a', 'b'], 'ordered'), 2/3)

    def test_actual_packet_and_single_step(self):
        env = InventoryEnvironment(ROOT / 'benchmark/rlvr/tasks/CTH-INVENTORY-001.json')
        self.assertEqual(sum(env.expected['Q01'].values()), 75)
        self.assertEqual(sum(env.expected['Q02'].values()), 75)
        public = env.reset()['messages'][0]['content']
        self.assertNotIn('source_sha256', public)
        self.assertNotIn('hidden_gold', public)
        self.assertEqual(env.step(env.golden_solution())['reward'], 1)
        with self.assertRaises(RuntimeError): env.step(env.golden_solution())
        for text in ['{"answers":{}}', '{"answers":{"Q99":[]}}', '{"answers":{},"answers":{}}', 'null']:
            env.reset()
            self.assertEqual(env.step(text)['reward'], 0)

    def test_larger_packet_is_pinned_and_overlaps_development_packet(self):
        small = InventoryEnvironment(ROOT / 'benchmark/rlvr/tasks/CTH-INVENTORY-001.json')
        large = InventoryEnvironment(ROOT / 'benchmark/rlvr/tasks/CTH-INVENTORY-002.json')
        self.assertEqual(len(large.documents), 300)
        self.assertTrue(small.documents.keys() <= large.documents.keys())
        self.assertEqual(sum(large.expected['Q01'].values()), 300)
        large.reset()
        self.assertEqual(large.step(large.golden_solution())['reward'], 1)

    def test_loader_excludes_quoted_headers_and_bcc(self):
        raw = b"Date: Sat, 17 Jun 2023 23:30:00 -0700\nFrom: A <A@cascadetimber.com>\nTo: B <b@cascadetimber.com>\nCc: C <c@cascadetimber.com>\nBcc: Other <x@outside.test>\nSubject: Test\n\nFrom: X <x@outside.test>\nTo: Y <y@bellhavenadvisory.com>\nDate: 18 Jun 2023\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'data/emails/Custodians/A/EMAIL-001_test.eml'
            source.parent.mkdir(parents=True)
            source.write_bytes(raw)
            task = {'task_id': 'test', 'verifier': VERSION, 'sources': [{'document_id': 'EMAIL-001', 'source_path': str(source.relative_to(root)), 'source_sha256': sha256(raw)}]}
            path = root / 'task.json'
            path.write_text(json.dumps(task))
            env = InventoryEnvironment(path, root=root)
            self.assertEqual(env.expected['Q02'], {'cascadetimber.com': 1})
            self.assertEqual(env.expected['Q03'], [])
            self.assertEqual(env.expected['Q05'], [])
            self.assertEqual(env.expected['Q09'], {})
            self.assertEqual(env.expected['Q10'], ['EMAIL-001'])
