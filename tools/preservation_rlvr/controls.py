"""Evaluator-only controls. These read the oracle and are NEVER model scores."""
from datetime import datetime


def oracle_answer(env):
    assessments = {}
    for item in env._gold['items']:
        cutoff = datetime.fromisoformat(item['cutoff'])
        value = dict(item['expected'], rules=item['rules'], evidence=[], challenges=[])
        for name, groups in [('evidence', item['support']), ('challenges', item['challenges'])]:
            for group in groups:
                after = name == 'challenges' and group['reason'] == 'after_cutoff'
                doc_id = next(k for k in group['documents'] if (env.documents[k]['instant'] > cutoff) == after)
                anchor = next(a for a in group['anchors'] if a in env.documents[doc_id]['text'])
                ref = {'document_id': doc_id, 'quote': anchor}
                if name == 'challenges':
                    ref['reason'] = group['reason']
                if ref not in value[name]:
                    value[name].append(ref)
        assessments[item['id']] = value
    return {'assessments': assessments}


def discover_and_read(env, answer):
    """Scripted search/read replay using oracle targets, explicitly a verifier control."""
    records, read = [], set()
    for item in answer['assessments'].values():
        for ref in item['evidence'] + item['challenges']:
            doc_id = ref['document_id']
            if doc_id in read:
                continue
            # Search short quoted evidence fragments; walk pages until the target is found.
            import json
            query = json.dumps(ref['quote'][:160], ensure_ascii=False)
            offset = 0
            while True:
                action = {'tool': 'search', 'query': query, 'offset': offset}
                result = env.step(action); records.append({'action': action, 'result': result})
                assert not result['done'], result
                observation = result['observation']
                if any(hit['document_id'] == doc_id for hit in observation['hits']):
                    break
                offset = observation['next_offset']
                assert offset is not None, doc_id
            offset = 0
            while offset is not None:
                action = {'tool': 'read', 'document_id': doc_id, 'offset': offset}
                result = env.step(action); records.append({'action': action, 'result': result})
                assert not result['done'], result
                offset = result['observation']['next_offset']
            read.add(doc_id)
    return records
