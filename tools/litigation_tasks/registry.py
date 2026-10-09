"""19 skill families: 17 new episodes plus two unchanged existing pilots."""
from copy import deepcopy
from pathlib import Path
import json
from .environment import LitigationEnvironment,ROOT,TASKS
SKILLS=['cold-start-interview','customize','matter-intake','matter-workspace','demand-received','demand-intake','demand-draft','subpoena-triage','legal-hold','chronology','claim-chart','deposition-prep','privilege-log-review','brief-section-drafter','matter-update','matter-briefing','portfolio-status','oc-status','matter-close']
ALIASES={'CTH-LIT-09':('preservation','CTH-PRESERVATION-001'), 'CTH-LIT-10':('chronology','CTH-CHRONOLOGY-001')}


def registry(root=ROOT,require_all=False):
    entries=[]
    for i,skill in enumerate(SKILLS,1):
        task_id=f'CTH-LIT-{i:02d}'
        if task_id in ALIASES:
            family,legacy=ALIASES[task_id]
            entries.append({'task_id':task_id,'skill':skill,'implementation':'existing_pilot_alias','episode_id':legacy,
              'package':f'benchmark/rlvr/{family}/{legacy}.json','independent_review_status':'pending_legacy_review'})
        else:
            path=Path(root)/TASKS/task_id/'task.json'
            if not path.exists():
                if require_all:raise ValueError('Missing task family '+task_id)
                entries.append({'task_id':task_id,'skill':skill,'implementation':'pending','episode_id':task_id})
                continue
            task=json.loads(path.read_text())
            entries.append({'task_id':task_id,'skill':skill,'implementation':'litigation_tasks_v1','episode_id':task_id,
              'package':str(path.relative_to(root)), 'availability':task['availability'],
              'cutoff':task['cutoff'],'dependencies':task.get('dependencies',[]),'findings':len(task['findings'])})
    return entries


class ChainSession:
    """Completed episode artifacts become optional, read-only downstream context.

    Standalone source-grounded fixtures remain authoritative task inputs. A prior
    work product is not primary evidence and cannot satisfy a source citation.
    Only declared dependencies with a nonfuture cutoff may flow downstream.
    """
    def __init__(self,root=ROOT):self.root=Path(root);self.completed={}
    def start(self,task_id):
        task=json.loads((self.root/TASKS/task_id/'task.json').read_text())
        from datetime import datetime
        cutoff=datetime.fromisoformat(task['cutoff']);context={}
        for parent in task.get('dependencies',[]):
            if parent not in self.completed:continue
            previous=self.completed[parent]
            if previous['cutoff']>cutoff:raise ValueError('Dependency would leak future context')
            context[parent]=deepcopy(previous['artifacts'])
        return LitigationEnvironment(task_id,self.root,dependency_artifacts=context)
    def publish(self,env):
        if not env.done or not env.result or not env.result.get('passed'):raise ValueError('Only verified completed episodes may publish')
        self.completed[env.task['task_id']]={'cutoff':env.cutoff,'artifacts':deepcopy(env.artifacts)}


class LegacyAdapter:
    """Normalize the two existing pilot APIs without changing their evaluators."""
    def __init__(self,task_id,root=ROOT):
        family,episode=ALIASES[task_id]
        if family=='preservation':
            from tools.preservation_rlvr.environment import PreservationEnvironment as Implementation
        else:
            from tools.chronology_rlvr.environment import ChronologyEnvironment as Implementation
        self.environment=Implementation(Path(root)/'benchmark/rlvr'/family/(episode+'.json'),root=Path(root))
        self.task=deepcopy(self.environment.task);self.task['family_id']=task_id
    @property
    def steps(self):return self.environment.steps
    @property
    def done(self):return self.environment.done
    def reset(self):
        observation=self.environment.reset();observation['family_id']=self.task['family_id'];return observation
    def step(self,action):
        result=self.environment.step(action)
        observation=result.get('observation',result)
        return {'observation':observation,'reward':result.get('reward',0.0),'done':result['done']}


def make_environment(task_id,root=ROOT):
    return LegacyAdapter(task_id,root) if task_id in ALIASES else LitigationEnvironment(task_id,root)
