"""Export a model-safe task snapshot; keep evaluators and original repo separate."""
import argparse,json
from pathlib import Path
from .environment import LitigationEnvironment

def export(task_id,destination):
    env=LitigationEnvironment(task_id);destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=False)
    (destination/'task.json').write_text(json.dumps(env.reset(),ensure_ascii=False,indent=2)+'\n')
    with (destination/'documents.jsonl').open('w') as stream:
        for doc in env.documents.values():stream.write(json.dumps(doc,ensure_ascii=False)+'\n')
    (destination/'fixtures.json').write_text(json.dumps({'artifacts':env.artifacts},indent=2)+'\n')
    return {'task_id':task_id,'documents':len(env.documents),'destination':str(destination)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--task',required=True);p.add_argument('destination',type=Path);a=p.parse_args()
    print(json.dumps(export(a.task,a.destination)))
