"""Evaluator-only positive/negative controls. Never expose this to task agents."""
from copy import deepcopy
from .environment import LitigationEnvironment,ROOT,pointer


def set_pointer(obj,path,value):
    if path=='': return deepcopy(value)
    parts=path[1:].split('/'); last=parts.pop().replace('~1','/').replace('~0','~')
    parent=pointer(obj,'/'+('/'.join(parts))) if parts else obj
    parent[int(last) if isinstance(parent,list) else last]=deepcopy(value)
    return obj


def control_answer(env):
    return {'findings':{key:{'answer':deepcopy(f['accepted_answers'][0]),
      'support':unique([g['alternatives'][0] for g in f['support_groups']]),
      'counter':unique([g['alternatives'][0] for g in f.get('counter_groups',[])])}
      for key,f in env.oracle['findings'].items()}}


def unique(items):
    result=[]
    for i in items:
        if i not in result: result.append(deepcopy(i))
    return result


def read_citations(env,answer):
    citations=unique([c for f in answer['findings'].values() for side in ('support','counter') for c in f[side]])
    for c in citations:
        offset=0
        while True:
            result=env.step({'tool':'read','document_id':c['document_id'],'locator':c['locator'],'offset':offset})
            if result['done']: return
            offset=result['observation'].get('next_offset')
            if offset is None: break


def run_control(task_id,root=ROOT,mutation=None):
    env=LitigationEnvironment(task_id,root=root)
    answer=control_answer(env); artifacts=deepcopy(env.oracle.get('control_artifacts',{}))
    if not mutation or mutation['kind']!='unread_citations': read_citations(env,answer)
    if mutation:
        kind=mutation['kind']; fid=mutation.get('finding')
        if kind=='answer_field': answer['findings'][fid]['answer']=set_pointer(answer['findings'][fid]['answer'],mutation['pointer'],mutation['value'])
        elif kind=='drop_counter': answer['findings'][fid]['counter']=[]
        elif kind=='fabricate_quote': answer['findings'][fid]['support'][0]['quote']='This fabricated passage was never contained in the Cascade record.'
        elif kind=='artifact_field': artifacts[mutation['path']]=set_pointer(artifacts[mutation['path']],mutation['pointer'],mutation['value'])
        elif kind=='post_cutoff_citation':
            citation=mutation.get('citation') or mutation.get('proof')
            answer['findings'][fid]['support'][0]=deepcopy(citation)
        elif kind!='unread_citations': raise ValueError('Unknown control mutation '+kind)
    for path,content in artifacts.items():
        if env.done: return env.result
        result=env.step({'tool':'write_artifact','path':path,'content':content})
        # A rejected invalid write leaves the prior fixture in place and must not pass.
    if env.done: return env.result
    return env.step({'tool':'submit','answer':answer})['observation']


def exercise_controls(task_id,root=ROOT):
    env=LitigationEnvironment(task_id,root=root)
    return {'positive':run_control(task_id,root),
      'negative':{m['name']:run_control(task_id,root,m) for m in env.oracle.get('negative_controls',[])}}
