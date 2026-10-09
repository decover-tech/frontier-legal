"""Cross-task verifier, state isolation, provenance and replay regressions."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from tools.litigation_tasks.environment import LitigationEnvironment,ROOT,strict_json,field_accuracy
from tools.litigation_tasks.controls import control_answer,read_citations

class RuntimeTests(unittest.TestCase):
    def env(self): return LitigationEnvironment('CTH-LIT-08',ROOT)

    def test_public_observation_does_not_expose_oracle_or_provenance_paths(self):
        env=self.env(); data=json.dumps(env.reset())
        for forbidden in ['accepted_answers','control_artifacts','support_groups','hidden_gold','oracle_sha256','source_files','source_path']:
            self.assertNotIn(forbidden,data)
        self.assertNotIn('alternatives',env.reset())

    def test_unknown_tools_and_paths_do_not_read_host(self):
        env=self.env()
        for action in [{'tool':'read','document_id':'../../benchmark/hidden_gold/litigation_skills/CTH-LIT-08.json'},
                       {'tool':'read_artifact','path':'../../.claude/keys.txt'},
                       {'tool':'write_artifact','path':'/tmp/external','content':{}},{'tool':'shell','command':'pwd'}]:
            self.assertIn('error',env.step(action)['observation'])

    def test_read_before_cite_and_forgery(self):
        env=self.env(); citation=control_answer(env)['findings']['F01']['support'][0]
        self.assertFalse(env.valid_citation(citation))
        env.step({'tool':'read','document_id':citation['document_id'],'locator':citation['locator']})
        self.assertTrue(env.valid_citation(citation))
        forged={**citation,'quote':'This passage is fabricated and never existed in the source.'}
        self.assertFalse(env.valid_citation(forged))
        self.assertFalse(env.valid_citation({**citation,'locator':'line:999999'}))

    def test_search_is_literal_and_does_not_count_as_read(self):
        env=self.env(); citation=control_answer(env)['findings']['F01']['support'][0]
        result=env.step({'tool':'search','query':'"production"'})['observation']
        self.assertLessEqual(len(result['hits']),8)
        self.assertFalse(env.valid_citation(citation))
        self.assertEqual(env.step({'tool':'search','query':'.*'})['observation']['total'],0)

    def test_parent_date_controls_attachments(self):
        env=self.env()
        late=[d for d in env.all_documents.values() if d.get('parent_email_id') and d['parent_email_id'] not in env.documents]
        self.assertGreater(len(late),0)
        self.assertNotIn(late[0]['document_id'],env.documents)
        self.assertIn('error',env.step({'tool':'read','document_id':late[0]['document_id']})['observation'])

    def test_duplicate_and_nonfinite_json_rejected(self):
        for value in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
            with self.assertRaises(ValueError): strict_json(value)
        self.assertEqual(strict_json('```json\n{"x":1}\n```'),{'x':1})
        with self.assertRaises(ValueError): strict_json({'x':float('nan')})

    def test_schema_failure_and_terminal_only_reward(self):
        env=self.env(); self.assertEqual(env.step({'tool':'list_artifacts'})['reward'],0)
        result=env.step({'tool':'submit','answer':{'findings':{}}})
        self.assertTrue(result['done']);self.assertEqual(result['reward'],0)
        with self.assertRaises(RuntimeError):env.step({'tool':'list_artifacts'})

    def test_step_and_observation_caps(self):
        env=self.env();env.task['limits']['max_steps']=1
        env.step({'tool':'list_artifacts'})
        result=env.step({'tool':'list_artifacts'})
        self.assertEqual(result['observation']['error'],'step_budget_exceeded')
        env=self.env();env.task['limits']['max_observation_chars']=1
        result=env.step({'tool':'read','document_id':'EMAIL-001'})
        self.assertEqual(result['observation']['error'],'observation_budget_exceeded')

    def test_reset_restores_fixture_and_seen_ranges(self):
        env=self.env(); path=next(iter(env.schemas))
        initial=deepcopy(env.artifacts)
        env.step({'tool':'write_artifact','path':path,'content':env.oracle['control_artifacts'][path]})
        env.step({'tool':'read','document_id':'EMAIL-001'})
        env.reset();self.assertEqual(env.artifacts,initial);self.assertFalse(env.seen)

    def test_equivalent_set_order_and_partial_answer_credit(self):
        schema={'type':'object','properties':{'choices':{'type':'array','uniqueItems':True,'items':{'type':'string'}},'date':{'type':'string'}}}
        correct={'choices':['a','b'],'date':'2023-09-06'}
        self.assertEqual(field_accuracy({'choices':['b','a'],'date':'2023-09-06'},correct,schema),1)
        self.assertEqual(field_accuracy({'choices':['b','a'],'date':'2023-09-07'},correct,schema),.5)

    def test_unread_gold_answers_and_artifacts_do_not_earn_reward(self):
        env=self.env()
        for path,data in env.oracle['control_artifacts'].items():env.step({'tool':'write_artifact','path':path,'content':data})
        self.assertEqual(env.step({'tool':'submit','answer':control_answer(env)})['reward'],0)

    def test_irrelevant_valid_citation_reduces_precision(self):
        env=self.env();answer=control_answer(env);read_citations(env,answer)
        doc=env.documents['EMAIL-001'];loc=next(l for l in doc['locators'] if l['end']-l['start']>50)
        cite={'document_id':'EMAIL-001','locator':loc['locator'],'quote':doc['text'][loc['start']:loc['end']]}
        env.step({'tool':'read','document_id':'EMAIL-001','locator':loc['locator']})
        answer['findings']['F01']['support'].append(cite)
        self.assertLess(env.grade(answer)['findings']['F01']['support_precision'],1)

    def test_all_reviewed_alternate_proofs_are_accepted(self):
        env=self.env();count=0
        for f in env.oracle['findings'].values():
            for side in ('support_groups','counter_groups'):
                for group in f.get(side,[]):
                    for cite in group['alternatives']:
                        env.done=False;env.steps=0;env.observation_chars=0
                        read_citations(env,{'findings':{'F':{'support':[cite],'counter':[]}}})
                        coverage,precision,_=env.proof_score([cite],[group]);self.assertEqual((coverage,precision),(1,1));count+=1
        self.assertGreater(count,20)

    def test_modified_policy_fails_pinned_loading(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)
            for relative in ['benchmark/litigation_skills/tasks/CTH-LIT-08','benchmark/litigation_skills/evidence','benchmark/hidden_gold/litigation_skills']:
                shutil.copytree(ROOT/relative,target/relative)
            policy=target/'benchmark/litigation_skills/tasks/CTH-LIT-08/policy.md'
            policy.write_text(policy.read_text()+'\nUnauthorized mutation\n')
            with self.assertRaisesRegex(ValueError,'policy_sha256'):
                LitigationEnvironment('CTH-LIT-08',target,verify_sources=False)

    def test_dependency_context_is_allowlisted_read_only_and_not_source_proof(self):
        context={'CTH-LIT-03':{'intake/draft.json':{'status':'draft','clearance':None}}}
        env=LitigationEnvironment('CTH-LIT-08',ROOT,dependency_artifacts=context)
        result=env.step({'tool':'read_dependency','task_id':'CTH-LIT-03','path':'intake/draft.json'})
        self.assertEqual(result['observation']['content']['clearance'],None)
        result['observation']['content']['clearance']='cleared'
        self.assertIsNone(env.dependency_artifacts['CTH-LIT-03']['intake/draft.json']['clearance'])
        self.assertIn('error',env.step({'tool':'write_artifact','path':'intake/draft.json','content':{}})['observation'])
        with self.assertRaises(ValueError):LitigationEnvironment('CTH-LIT-08',ROOT,dependency_artifacts={'CTH-LIT-19':{}})

    def test_gym_shaped_adapter(self):
        from tools.litigation_tasks.run import TrainerEnvironment
        adapter=TrainerEnvironment('CTH-LIT-08',ROOT)
        observation,info=adapter.reset(seed=7)
        self.assertTrue(info['deterministic'])
        observation,reward,terminated,truncated,info=adapter.step({'tool':'list_artifacts'})
        self.assertEqual(reward,0);self.assertFalse(terminated or truncated)
        observation,reward,terminated,truncated,info=adapter.step({'tool':'submit','answer':{}})
        self.assertTrue(terminated);self.assertFalse(truncated)

    def test_deterministic_trajectory_replay(self):
        env=self.env();answer=control_answer(env);read_citations(env,answer)
        for path,content in env.oracle['control_artifacts'].items():env.step({'tool':'write_artifact','path':path,'content':content})
        env.step({'tool':'submit','answer':answer})
        clone=self.env()
        for transition in env.trace:
            actual=clone.step(transition['action'])
            self.assertEqual(actual['observation'],transition['observation'])
        self.assertEqual(clone.result,env.result)


class IntegrationTests(unittest.TestCase):
    def test_chained_artifacts_and_standalone_fallback(self):
        from tools.litigation_tasks.registry import ChainSession
        session=ChainSession(ROOT)
        empty=session.start('CTH-LIT-07');self.assertFalse(empty.dependency_artifacts)
        source=session.start('CTH-LIT-06');answer=control_answer(source);read_citations(source,answer)
        for path,data in source.oracle['control_artifacts'].items():source.step({'tool':'write_artifact','path':path,'content':data})
        source.step({'tool':'submit','answer':answer});self.assertTrue(source.result['passed'])
        session.publish(source)
        downstream=session.start('CTH-LIT-07');self.assertIn('CTH-LIT-06',downstream.dependency_artifacts)
        self.assertEqual(downstream.artifacts,empty.artifacts)
        self.assertIsNot(source.artifacts,downstream.dependency_artifacts['CTH-LIT-06'])

    def test_chain_rejects_future_context_and_unverified_results(self):
        from tools.litigation_tasks.registry import ChainSession
        from datetime import datetime,timezone
        session=ChainSession(ROOT)
        with self.assertRaises(ValueError):session.publish(session.start('CTH-LIT-06'))
        session.completed['CTH-LIT-06']={'cutoff':datetime(2030,1,1,tzinfo=timezone.utc),'artifacts':{}}
        with self.assertRaisesRegex(ValueError,'future'):session.start('CTH-LIT-07')

    def test_model_export_excludes_trusted_manifest_and_gold(self):
        from tools.litigation_tasks.export import export
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'public';export('CTH-LIT-08',target)
            self.assertEqual(set(p.name for p in target.iterdir()),{'task.json','documents.jsonl','fixtures.json'})
            text=(target/'task.json').read_text()+(target/'documents.jsonl').read_text()
            for token in ['source_files','accepted_answers','control_artifacts','benchmark/hidden_gold','rule_projection_omissions']:
                self.assertNotIn(token,text)

if __name__=='__main__':unittest.main()
