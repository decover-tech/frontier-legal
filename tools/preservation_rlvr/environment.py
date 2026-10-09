"""Trusted evaluator and bounded search/read interface for a preservation audit.

Only reset()/step() observations go to the model. Never expose this process,
repository, oracle, source paths or result files to an untrusted agent shell.
"""
import json
import re
import shlex
import unicodedata
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path

from tools.rlvr.audit import evidence_text
from tools.rlvr.environment import ROOT, _unique_object, sha256

VERSION = 'preservation-audit/1.0.0'
DEFAULT_TASK = ROOT / 'benchmark/rlvr/preservation/CTH-PRESERVATION-001.json'


def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())


def parse_json(value):
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or len(value) > 65536:
        raise ValueError('Invalid action size/type')
    text = value.strip()
    # A single outer fence is transport decoration in this new task, not legal skill.
    if text.startswith('```'):
        match = re.fullmatch(r'```(?:json)?\s*\n([\s\S]*?)\n```', text)
        if not match:
            raise ValueError('Invalid fence')
        text = match.group(1)
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))


def f1(actual, expected):
    return 2 * len(set(actual) & set(expected)) / (len(actual) + len(expected)) if actual or expected else 1.0


class PreservationEnvironment:
    def __init__(self, task_path=DEFAULT_TASK, root=ROOT):
        self.root = Path(root).resolve()
        raw = Path(task_path).read_bytes()
        self.task = json.loads(raw)
        self.task_hash = sha256(raw)
        if self.task['verifier'] != VERSION:
            raise ValueError('Unsupported verifier')
        self.policy = self._asset(self.task['policy_path'], self.task['policy_sha256'], 'benchmark/rlvr/preservation').decode()
        self.schema = json.loads(self._asset(self.task['output_schema'], self.task['schema_sha256'], 'benchmark/rlvr/preservation'))
        self._gold = json.loads(self._asset(self.task['oracle_path'], self.task['oracle_sha256'], 'benchmark/hidden_gold/preservation'))
        self.documents = {}
        for source in self.task['sources']:
            raw = self._asset(source['source_path'], source['source_sha256'], 'data/emails/Custodians')
            if Path(source['source_path']).suffix != '.eml':
                raise ValueError('Expected original email')
            text = evidence_text(raw)
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            if len(msg.get_all('Date', [])) != 1:
                raise ValueError('Ambiguous source date')
            instant = parsedate_to_datetime(str(msg['Date']))
            if instant.utcoffset() is None:
                raise ValueError('Source date lacks timezone')
            doc_id = source['document_id']
            if doc_id in self.documents:
                raise ValueError('Duplicate document ID')
            self.documents[doc_id] = {'text': text, 'instant': instant, 'date': str(msg['Date']),
                                      'from': str(msg.get('From', '')), 'subject': str(msg.get('Subject', ''))}
        self.checkpoints = {i['id']: i for i in self.task['checkpoints']}
        if {i['id'] for i in self._gold['items']} != set(self.checkpoints):
            raise ValueError('Oracle/checkpoint mismatch')
        for item in self._gold['items']:
            if item['cutoff'] != self.checkpoints[item['id']]['cutoff']:
                raise ValueError('Oracle cutoff mismatch')
            for group in item['support'] + item['challenges']:
                actual = sorted(k for k, v in self.documents.items() if any(a in v['text'] for a in group['anchors']))
                if actual != group['documents'] or not actual:
                    raise ValueError('Oracle evidence anchor mismatch')
        self.done = True

    def _asset(self, path, digest, permitted):
        resolved = (self.root / path).resolve()
        if not resolved.is_relative_to((self.root / permitted).resolve()):
            raise ValueError('Asset outside permitted directory')
        raw = resolved.read_bytes()
        if sha256(raw) != digest:
            raise ValueError('Pinned asset hash mismatch')
        return raw

    def reset(self):
        self.done, self.steps, self.observation_chars = False, 0, 0
        self.read_chunks = {}
        self.read_ranges = {}
        self.trace = []
        public = {
            'task_id': self.task['task_id'], 'instruction': self.task['instruction'],
            'collection_size': len(self.documents), 'evidence_scope': self.task['evidence_scope'],
            'policy': self.policy, 'checkpoints': self.task['checkpoints'],
            'limits': self.task['limits'], 'output_schema': self.schema,
            'tools': {
                'search': {'example': {'tool': 'search', 'query': '"Nina Alvarez" export', 'offset': 0},
                           'semantics': 'Case-insensitive AND of literal words or quoted phrases over email headers/body. Results sorted by document ID; paginate with next_offset. No regex or filesystem paths.'},
                'read': {'example': {'tool': 'read', 'document_id': 'EMAIL-003', 'offset': 0},
                         'semantics': 'Read one paged email; use next_offset for more. Citations must quote a passage returned by read, not only search.'},
                'submit': {'example': {'tool': 'submit', 'answer': {'assessments': {}}},
                           'semantics': 'End the episode. Fill assessments using the schema. Up to six support passages and five challenge passages per assessment.'}},
            'transport': 'Return one JSON action per turn. A single outer Markdown JSON fence is accepted. Tool errors consume a step but allow recovery. There is no intermediate verifier feedback.',
        }
        self.observation_chars = len(json.dumps(public, ensure_ascii=False))
        return public

    def _finish(self, code):
        self.done = True
        return {'done': True, 'reward': 0.0, 'success': False, 'failure_codes': [code],
                'verifier_version': VERSION, 'steps': self.steps}

    def step(self, action):
        if self.done:
            raise RuntimeError('Call reset; episode already finished')
        self.steps += 1
        if self.steps > self.task['limits']['max_steps']:
            return self._finish('STEP_LIMIT')
        try:
            obj = parse_json(action)
            if not isinstance(obj, dict):
                raise ValueError()
            tool = obj.get('tool')
            if tool == 'submit':
                if set(obj) != {'tool', 'answer'}:
                    raise ValueError()
                self.done = True
                result = self.verify(obj['answer'])
                self.trace.append({'step': self.steps, 'tool': 'submit'})
                return {'done': True, 'steps': self.steps, **result}
            if tool == 'search':
                if set(obj) - {'tool', 'query', 'offset'} or not isinstance(obj.get('query'), str) or not 1 <= len(obj['query']) <= 200:
                    raise ValueError()
                terms = [normalize(t) for t in shlex.split(obj['query'])]
                if not terms or any(not t for t in terms):
                    raise ValueError()
                offset = obj.get('offset', 0)
                if type(offset) is not int or offset < 0:
                    raise ValueError()
                matches = [(k, d) for k, d in sorted(self.documents.items()) if all(t in normalize(d['text']) for t in terms)]
                size = self.task['limits']['search_page_size']
                hits = []
                for key, doc in matches[offset:offset+size]:
                    # Snippets are discovery aids; dates and subject lines alone aren't proof.
                    flat = ' '.join(doc['text'].split())
                    start = max(0, normalize(flat).find(terms[0]) - 60)
                    hits.append({'document_id': key, 'date': doc['date'], 'from': doc['from'],
                                 'subject': doc['subject'], 'snippet': flat[start:start+280]})
                observation = {'hits': hits, 'total': len(matches), 'next_offset': offset+size if offset+size < len(matches) else None}
            elif tool == 'read':
                if set(obj) - {'tool', 'document_id', 'offset'} or obj.get('document_id') not in self.documents:
                    raise ValueError()
                key, offset = obj['document_id'], obj.get('offset', 0)
                if type(offset) is not int or offset < 0:
                    raise ValueError()
                text = self.documents[key]['text']
                if offset >= len(text):
                    raise ValueError()
                end = min(len(text), offset+self.task['limits']['read_page_chars'])
                observation = {'document_id': key, 'offset': offset, 'text': text[offset:end],
                               'next_offset': end if end < len(text) else None}
            else:
                raise ValueError()
        except (ValueError, TypeError, KeyError, RecursionError):
            observation = {'error': 'INVALID_ACTION', 'help': 'Use search(query, offset), read(document_id, offset), or submit(answer).'}
            tool = 'invalid'
        size = len(json.dumps(observation, ensure_ascii=False))
        if self.observation_chars + size > self.task['limits']['max_observation_chars']:
            return self._finish('OBSERVATION_LIMIT')
        self.observation_chars += size
        if tool == 'read' and 'text' in observation:
            self.read_chunks.setdefault(observation['document_id'], []).append(observation['text'])
            self.read_ranges.setdefault(observation['document_id'], []).append((observation['offset'], observation['offset']+len(observation['text'])))
        self.trace.append({'step': self.steps, 'action': obj if tool != 'invalid' else 'invalid', 'observation_chars': size})
        if self.steps == self.task['limits']['max_steps']:
            return self._finish('STEP_LIMIT')
        return {'done': False, 'reward': 0.0, 'observation': observation,
                'steps_remaining': self.task['limits']['max_steps']-self.steps}

    def _valid_item(self, value):
        spec = next(iter(self.schema['properties']['assessments']['properties'].values()))['properties']
        if not isinstance(value, dict) or set(value) != set(spec):
            return False
        for field, rule in spec.items():
            v = value[field]
            if 'enum' in rule and v not in rule['enum']:
                return False
            if field in ('effective_date', 'known_by') and v is not None and not isinstance(v, str):
                return False
            if field == 'responsible' and not isinstance(v, str):
                return False
        rules = value['rules']
        if not isinstance(rules, list) or any(not isinstance(v, str) or v not in self.policy_rule_ids for v in rules) or len(rules) != len(set(rules)):
            return False
        for field in ('evidence', 'challenges'):
            refs = value[field]
            if not isinstance(refs, list) or len(refs) > (6 if field == 'evidence' else 5):
                return False
            for ref in refs:
                keys = {'document_id', 'quote'} | ({'reason'} if field == 'challenges' else set())
                if not isinstance(ref, dict) or set(ref) != keys or not isinstance(ref['document_id'], str) or not isinstance(ref['quote'], str) or not 20 <= len(ref['quote']) <= 800:
                    return False
                if field == 'challenges' and ref['reason'] not in spec[field]['items']['properties']['reason']['enum']:
                    return False
            if len({json.dumps(r, sort_keys=True) for r in refs}) != len(refs):
                return False
        return True

    policy_rule_ids = {'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7'}

    def _seen(self, document_id, quote):
        merged = []
        for start, end in sorted(self.read_ranges.get(document_id, [])):
            if merged and start <= merged[-1][1]:
                merged[-1][1] = max(end, merged[-1][1])
            else:
                merged.append([start, end])
        text = self.documents.get(document_id, {}).get('text', '')
        return any(quote in normalize(text[a:b]) for a, b in merged)

    def _references(self, refs, groups, cutoff, challenge=False):
        covered, valid = set(), 0
        for ref in refs:
            doc = self.documents.get(ref['document_id'])
            quote = normalize(ref['quote'])
            seen = self._seen(ref['document_id'], quote)
            if not doc or not seen or quote not in normalize(doc['text']):
                continue
            matched = []
            for index, group in enumerate(groups):
                if challenge and ref['reason'] != group['reason']:
                    continue
                after = challenge and group['reason'] == 'after_cutoff'
                if (doc['instant'] > cutoff) != after:
                    continue
                if ref['document_id'] in group['documents'] and any(normalize(anchor) in quote for anchor in group['anchors']):
                    matched.append(index)
            if matched:
                valid += 1
                covered.update(matched)
        return len(covered)/len(groups), valid/len(refs) if refs else 0.0

    def verify(self, answer):
        base = {'reward': 0.0, 'success': False, 'failure_codes': [], 'verifier_version': VERSION}
        if not isinstance(answer, dict) or set(answer) != {'assessments'} or not isinstance(answer['assessments'], dict) or set(answer['assessments']) - set(self.checkpoints):
            return {**base, 'failure_codes': ['INVALID_SUBMISSION']}
        scores = {}
        for item in self._gold['items']:
            value = answer['assessments'].get(item['id'])
            if not self._valid_item(value):
                scores[item['id']] = {'reward': 0.0, 'failure': 'MISSING_OR_MALFORMED_ASSESSMENT'}
                continue
            expected = item['expected']
            fields = sum(value[k] == expected[k] for k in ('status', 'scope', 'responsible', 'next_action'))/4
            chronology = sum(value[k] == expected[k] for k in ('effective_date', 'known_by'))/2
            cutoff = datetime.fromisoformat(item['cutoff'])
            coverage, precision = self._references(value['evidence'], item['support'], cutoff)
            conflict_coverage, conflict_precision = self._references(value['challenges'], item['challenges'], cutoff, True)
            rules = f1(value['rules'], item['rules'])
            components = {'finding': fields, 'chronology': chronology, 'evidence_precision': precision,
                          'conflict_resolution': conflict_coverage*conflict_precision, 'rule_selection': rules}
            raw = .25*fields + .20*chronology + .25*precision + .20*components['conflict_resolution'] + .10*rules
            reward = round(raw*coverage, 12) if value['status'] == expected['status'] else 0.0
            scores[item['id']] = {'reward': reward, 'support_coverage': coverage, 'components': components}
        reward = round(sum(s['reward'] for s in scores.values())/len(scores), 12)
        success = all(abs(s['reward']-1) < 1e-12 for s in scores.values())
        return {**base, 'reward': reward, 'success': success, 'assessments': scores,
                'failure_codes': [] if success else ['INCOMPLETE_OR_UNSUPPORTED_AUDIT']}
