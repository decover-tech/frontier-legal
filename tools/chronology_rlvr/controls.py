"""Evaluator-only chronology controls, never model evaluations."""
import json
from datetime import datetime
from tools.preservation_rlvr.environment import normalize


def oracle_answer(env):
    answer={'events':{},'order':[i['id'] for i in env._gold['events']],'resolutions':{}}
    for section in ('events','resolutions'):
        for item in env._gold[section]:
            row=dict(item['expected']);row['evidence']=[]
            if section=='resolutions':row['challenges']=[]
            cutoff=datetime.fromisoformat(item.get('cutoff',env.task['cutoff']))
            for field,groups in [('evidence',item['support'])]+([('challenges',item['challenges'])] if section=='resolutions' else []):
                for group in groups:
                    after=field=='challenges' and group['reason']=='after_cutoff'
                    candidates=[k for k in group['documents'] if (env.documents[k]['instant']>cutoff)==after]
                    key=min(candidates,key=lambda k:(env.documents[k]['instant'],k))
                    ref={'document_id':key,'quote':next(a for a in group['anchors'] if a in env.documents[key]['text'])}
                    if field=='challenges':ref['reason']=group['reason']
                    if ref not in row[field]:row[field].append(ref)
            answer[section][item['id']]=row
    return answer


def discover_and_read(env,answer):
    targets={};trace=[]
    for section in ('events','resolutions'):
        for row in answer[section].values():
            for ref in row['evidence']+row.get('challenges',[]):
                targets.setdefault(ref['document_id'],[]).append(ref['quote'])
    for key,quotes in targets.items():
        query=json.dumps(quotes[0][:160],ensure_ascii=False);offset=0
        while True:
            action={'tool':'search','query':query,'offset':offset};result=env.step(action)
            trace.append({'action':action,'result':result});assert not result['done'],result
            obs=result['observation']
            if any(h['document_id']==key for h in obs['hits']):break
            offset=obs['next_offset'];assert offset is not None,key
        offset=0
        while True:
            action={'tool':'read','document_id':key,'offset':offset};result=env.step(action)
            trace.append({'action':action,'result':result});assert not result['done'],result
            if all(env._seen(key,normalize(q)) for q in quotes):break
            offset=result['observation']['next_offset'];assert offset is not None,key
    return trace
