"""Generate a checkpoint report without confusing controls with model scores."""
import json
from pathlib import Path
from .registry import registry
from .build import validate
from .environment import ROOT


def report(root=ROOT):
    root=Path(root);rows=registry(root);results=[]
    for row in rows:
        if row['implementation']=='litigation_tasks_v1':results.append(validate(row['task_id'],root))
    mapped={r['task_id']:r for r in results}
    summary={'kind':'development_verifier_controls_not_model_evaluation','target_new_episodes':17,
      'implemented_new_episodes':len(results),'existing_pilot_aliases':2,'family_count':19,
      'independently_approved_new_episodes':sum(r['review_status']=='approved' and not r['errors'] for r in results),
      'positive_controls_passed':sum(r['controls']['positive'].get('passed',False) for r in results),
      'negative_controls':sum(len(r['controls']['negative']) for r in results),
      'negative_controls_lower_reward':sum(n.get('reward',1)<r['controls']['positive'].get('reward',0) for r in results for n in r['controls']['negative'].values()),
      'api_calls':0,'results':results}
    target=root/'benchmark/litigation_skills'
    (target/'registry.json').write_text(json.dumps(rows,indent=2)+'\n')
    (target/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# Skill-family coverage','',f"Checkpoint: {len(results)} / 17 new episodes implemented; {summary['independently_approved_new_episodes']} independently approved. Two existing pilot aliases bring implemented family coverage to {len(results)+2} / 19.",'',
      'Control scores below validate the harness, not frontier-model performance. All new episodes are development-only and bounded initial skill episodes.','',
      '| Family | Skill | Package | Independent review | Positive control | Adversarial controls |',
      '|---|---|---|---|---|---|']
    for row in rows:
        key=row['task_id'];r=mapped.get(key)
        if r:
            positive=r['controls']['positive']['reward'];negative=r['controls']['negative']
            dropped=sum(v.get('reward',1)<positive for v in negative.values())
            lines.append(f"| {key} | {row['skill']} | [Implemented](tasks/{key}/task.json) | {r['review_status']} | {positive:.0%} | {dropped}/{len(negative)} reduced score |")
        elif row['implementation']=='existing_pilot_alias':
            lines.append(f"| {key} | {row['skill']} | Existing `{row['episode_id']}` | Legacy review pending | Existing tests | Existing controls |")
        else:lines.append(f"| {key} | {row['skill']} | Pending | Pending | — | — |")
    lines+=['','The new-task reviews are independent agent source/oracle reviews, not licensed legal opinions. The two legacy pilots retain their original graders and need separate oracle review. Extraction has explicit OCR and missing-media limits; see `evidence/coverage.json`. No new model scores or held-out matter generalization are claimed.','']
    (target/'COVERAGE.md').write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))
    return summary

if __name__=='__main__':
    result=report();raise SystemExit(int(any(r['errors'] for r in result['results'])))
