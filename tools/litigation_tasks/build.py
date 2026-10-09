"""Seal public schemas and asset hashes; validate oracle provenance and controls."""
from pathlib import Path
import argparse,json,hashlib
import jsonschema
from .environment import ROOT,TASKS,GOLD,digest,norm,LitigationEnvironment
from .schema import output_schema,bounded
from .evidence import load_bundle
from .controls import control_answer,read_citations,exercise_controls


def seal(root=ROOT,task_ids=None):
    root=Path(root); bundle=load_bundle(root)
    paths=[root/TASKS/t/'task.json' for t in task_ids] if task_ids else sorted((root/TASKS).glob('*/task.json'))
    result=[]
    for path in paths:
        task=json.loads(path.read_text()); directory=path.parent
        for finding in task['findings']: finding['answer_schema']=bounded(finding['answer_schema'])
        task['artifact_schemas']={k:bounded(v) for k,v in task.get('artifact_schemas',{}).items()}
        (directory/'output_schema.json').write_text(json.dumps(output_schema(task),indent=2,ensure_ascii=False)+'\n')
        for key,asset in [('policy_sha256',directory/'policy.md'),('schema_sha256',directory/'output_schema.json'),('fixtures_sha256',directory/'fixtures.json'),('oracle_sha256',root/GOLD/(task['task_id']+'.json'))]: task[key]=digest(asset)
        task['bundle_manifest_sha256']=bundle['bundle_sha256']
        review_path=root/'benchmark/litigation_skills/reviews'/(task['task_id']+'.json')
        oracle_path=root/GOLD/(task['task_id']+'.json')
        oracle=json.loads(oracle_path.read_text())
        status='pending'
        if review_path.exists():
            review=json.loads(review_path.read_text())
            semantics=hashlib.sha256(json.dumps({'findings':oracle['findings'],'artifact_checks':oracle['artifact_checks']},sort_keys=True).encode()).hexdigest()
            if review.get('status')=='approved' and review.get('oracle_semantics_sha256')==semantics and review.get('bundle_manifest_sha256')==bundle['bundle_sha256'] and review.get('reviewer') and review.get('reviewer')!=review.get('author'):status='approved'
        if oracle.get('independent_review_status')!=status:
            oracle['independent_review_status']=status
            oracle_path.write_text(json.dumps(oracle,indent=2,ensure_ascii=False)+'\n')
            task['oracle_sha256']=digest(oracle_path)
        path.write_text(json.dumps(task,indent=2,ensure_ascii=False)+'\n'); result.append(task['task_id'])
    return result


def validate(task_id,root=ROOT,controls=True):
    env=LitigationEnvironment(task_id,root)
    errors=[]
    public_findings={f['id']:f for f in env.task['findings']}
    if set(public_findings)!=set(env.oracle['findings']):errors.append('Public and oracle finding IDs differ')
    for fid,f in env.oracle['findings'].items():
        if not f['support_groups']: errors.append(fid+': no support obligations')
        if public_findings.get(fid,{}).get('counterevidence_required') and not f.get('counter_groups'):errors.append(fid+': required counterevidence missing from oracle')
        for answer in f['accepted_answers']:
            if not jsonschema.Draft202012Validator(public_findings[fid]['answer_schema']).is_valid(answer):errors.append(fid+': accepted answer violates public schema')
        for side in ('support_groups','counter_groups'):
            for group in f.get(side,[]):
                for p in group['alternatives']:
                    doc=env.documents.get(p.get('document_id'))
                    loc=next((l for l in doc['locators'] if l['locator']==p.get('locator')),None) if doc else None
                    if not loc or norm(p['quote']) not in norm(doc['text'][loc['start']:loc['end']]): errors.append(fid+': invalid/unavailable proof '+str(p.get('document_id'))+' '+str(p.get('locator')))
    review_path=Path(root)/'benchmark/litigation_skills/reviews'/(task_id+'.json')
    review_status='pending'
    if review_path.exists():
        review=json.loads(review_path.read_text())
        semantics=hashlib.sha256(json.dumps({'findings':env.oracle['findings'],'artifact_checks':env.oracle['artifact_checks']},sort_keys=True).encode()).hexdigest()
        if review.get('oracle_semantics_sha256')!=semantics:errors.append('Independent review does not match current oracle semantics')
        if review.get('reviewer')==review.get('author') or not review.get('reviewer'):errors.append('Review is not independent')
        if review.get('bundle_manifest_sha256')!=env.task['bundle_manifest_sha256']:errors.append('Review evidence bundle mismatch')
        review_status=review.get('status','pending')
    result={'task_id':task_id,'review_status':review_status,'errors':errors,'independent_review_status':env.oracle.get('independent_review_status','pending')}
    if controls:
        result['controls']=exercise_controls(task_id,root)
        if not result['controls']['positive'].get('passed'): errors.append('Positive control failed')
        for name,score in result['controls']['negative'].items():
            if score.get('passed') or score.get('reward',1)>=result['controls']['positive'].get('reward',0): errors.append('Negative control failed: '+name)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--task',action='append'); p.add_argument('--seal',action='store_true'); p.add_argument('--skip-controls',action='store_true'); args=p.parse_args()
    ids=seal(task_ids=args.task) if args.seal else args.task or [p.parent.name for p in sorted((ROOT/TASKS).glob('*/task.json'))]
    results=[validate(t,controls=not args.skip_controls) for t in ids]
    print(json.dumps(results,indent=2)); raise SystemExit(int(any(r['errors'] for r in results)))
