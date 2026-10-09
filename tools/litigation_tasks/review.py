"""Bindings for independent review of both public task semantics and hidden gold."""
import hashlib,json
from pathlib import Path
from .environment import ROOT,TASKS,GOLD,digest

def semantic_digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def review_binding(task_id,root=ROOT):
    root=Path(root);directory=root/TASKS/task_id
    task=json.loads((directory/'task.json').read_text());gold=json.loads((root/GOLD/(task_id+'.json')).read_text())
    return {'oracle_semantics_sha256':semantic_digest({'findings':gold['findings'],'artifact_checks':gold['artifact_checks']}),
      'task_semantics_sha256':semantic_digest({k:v for k,v in task.items() if not k.endswith('_sha256')}),
      'policy_sha256':digest(directory/'policy.md'),'fixtures_sha256':digest(directory/'fixtures.json'),
      'bundle_manifest_sha256':digest(root/'benchmark/litigation_skills/evidence/manifest.json')}
