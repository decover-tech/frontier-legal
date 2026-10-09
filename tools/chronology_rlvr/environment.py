"""Trusted chronology verifier using the unchanged preservation search/read interface."""
import json
from datetime import date, datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path
from tools.rlvr.audit import evidence_text
from tools.rlvr.environment import ROOT, sha256
from tools.preservation_rlvr.environment import PreservationEnvironment, f1

VERSION = 'evidence-chronology/1.0.0'
DEFAULT_TASK = ROOT/'benchmark/rlvr/chronology/CTH-CHRONOLOGY-001.json'


class ChronologyEnvironment(PreservationEnvironment):
    """Reuse bounded tool transport; load only this task's policy/schema/oracle."""
    def __init__(self, task_path=DEFAULT_TASK, root=ROOT):
        self.root = Path(root).resolve()
        raw = Path(task_path).read_bytes()
        self.task = json.loads(raw); self.task_hash = sha256(raw)
        if self.task['verifier'] != VERSION:
            raise ValueError('Unsupported verifier')
        self.policy = self._asset(self.task['policy_path'],self.task['policy_sha256'],'benchmark/rlvr/chronology').decode()
        self.schema = json.loads(self._asset(self.task['output_schema'],self.task['schema_sha256'],'benchmark/rlvr/chronology'))
        self._gold = json.loads(self._asset(self.task['oracle_path'],self.task['oracle_sha256'],'benchmark/hidden_gold/chronology'))
        self.documents = {}
        for source in self.task['sources']:
            raw = self._asset(source['source_path'],source['source_sha256'],'data/emails/Custodians')
            if Path(source['source_path']).suffix != '.eml':
                raise ValueError('Expected original email')
            text = evidence_text(raw); msg = BytesParser(policy=policy.default).parsebytes(raw)
            if len(msg.get_all('Date',[])) != 1:
                raise ValueError('Ambiguous source date')
            instant = parsedate_to_datetime(str(msg['Date']))
            if instant.utcoffset() is None:
                raise ValueError('Source date lacks timezone')
            key = source['document_id']
            if key in self.documents:
                raise ValueError('Duplicate document ID')
            self.documents[key] = {'text':text,'instant':instant,'date':str(msg['Date']),
                                   'from':str(msg.get('From','')),'subject':str(msg.get('Subject',''))}
        self.events = {i['id']:i for i in self.task['milestones']}
        self.resolutions = {i['id']:i for i in self.task['resolution_questions']}
        if set(self.events) != {i['id'] for i in self._gold['events']} or set(self.resolutions) != {i['id'] for i in self._gold['resolutions']}:
            raise ValueError('Oracle/task mismatch')
        for item in self._gold['events']+self._gold['resolutions']:
            if item['id'] in self.resolutions and item['cutoff'] != self.resolutions[item['id']]['cutoff']:
                raise ValueError('Oracle cutoff mismatch')
            for group in item['support']+item.get('challenges',[]):
                actual = sorted(k for k,v in self.documents.items() if any(a in v['text'] for a in group['anchors']))
                if actual != group['documents'] or not actual:
                    raise ValueError('Oracle evidence anchor mismatch')
        self.done = True

    def reset(self):
        self.done,self.steps,self.observation_chars = False,0,0
        self.read_chunks,self.read_ranges,self.trace = {},{},[]
        public = {'task_id':self.task['task_id'],'suite_task_number':2,'instruction':self.task['instruction'],
                  'collection_size':len(self.documents),'evidence_scope':self.task['evidence_scope'],
                  'cutoff':self.task['cutoff'],'policy':self.policy,'milestones':self.task['milestones'],
                  'resolution_questions':self.task['resolution_questions'],'limits':self.task['limits'],
                  'output_schema':self.schema,
                  'tools':{'search':{'example':{'tool':'search','query':'"registration" renewal','offset':0},'semantics':'Case-insensitive AND of literal words or quoted phrases over headers/body. Eight results per page sorted by document ID. Use next_offset.'},
                           'read':{'example':{'tool':'read','document_id':'EMAIL-003','offset':0},'semantics':'Read one paged email; follow next_offset. Citations must quote returned read text, not search snippets.'},
                           'submit':{'example':{'tool':'submit','answer':{'events':{},'order':[],'resolutions':{}}},'semantics':'End the episode with the supported chronology and resolutions.'}},
                  'transport':'One JSON action per turn; one outer Markdown JSON fence is accepted. Invalid actions consume a step. No intermediate grading feedback.'}
        self.observation_chars = len(json.dumps(public,ensure_ascii=False))
        return public

    def _finish(self, code):
        return {**super()._finish(code),'verifier_version':VERSION}

    @staticmethod
    def _day(value):
        if not isinstance(value,str):
            return False
        try:
            return date.fromisoformat(value).isoformat() == value
        except ValueError:
            return False

    def _refs_valid(self, refs, challenge=False):
        if not isinstance(refs,list) or len(refs) > (5 if challenge else 6):
            return False
        keys = {'document_id','quote'} | ({'reason'} if challenge else set())
        reasons = self.schema['$defs']['resolution']['properties']['challenges']['items']['properties']['reason']['enum']
        for ref in refs:
            if not isinstance(ref,dict) or set(ref)!=keys or not isinstance(ref['document_id'],str) or not isinstance(ref['quote'],str) or not 20<=len(ref['quote'])<=800:
                return False
            if challenge and ref['reason'] not in reasons:
                return False
        return len({json.dumps(r,sort_keys=True) for r in refs}) == len(refs)

    def _event_valid(self, row):
        properties = self.schema['$defs']['event']['properties']
        if not isinstance(row,dict) or set(row)!=set(properties):
            return False
        return (all(self._day(row[k]) for k in ('event_start','event_end','reported_on'))
                and row['event_start']<=row['event_end'] and isinstance(row['actor'],str)
                and row['precision'] in properties['precision']['enum']
                and row['nature'] in properties['nature']['enum'] and self._refs_valid(row['evidence']))

    def _resolution_valid(self, row):
        properties = self.schema['$defs']['resolution']['properties']
        if not isinstance(row,dict) or set(row)!=set(properties):
            return False
        if row['conclusion'] not in properties['conclusion']['enum'] or not (row['event_date'] is None or self._day(row['event_date'])):
            return False
        rules = row['rules']
        if not isinstance(rules,list) or any(not isinstance(r,str) or r not in properties['rules']['items']['enum'] for r in rules) or len(set(rules))!=len(rules):
            return False
        return self._refs_valid(row['evidence']) and self._refs_valid(row['challenges'],True)

    def verify(self, answer):
        base = {'reward':0.0,'success':False,'failure_codes':[],'verifier_version':VERSION}
        if not isinstance(answer,dict) or set(answer)!={'events','order','resolutions'} or not isinstance(answer['events'],dict) or not isinstance(answer['resolutions'],dict):
            return {**base,'failure_codes':['INVALID_SUBMISSION']}
        order = answer['order']
        if (set(answer['events'])-set(self.events) or set(answer['resolutions'])-set(self.resolutions)
                or not isinstance(order,list) or any(not isinstance(x,str) or x not in self.events for x in order)
                or len(order)!=len(set(order))):
            return {**base,'failure_codes':['INVALID_SUBMISSION']}
        cutoff = datetime.fromisoformat(self.task['cutoff']); events = {}; resolutions = {}
        for item in self._gold['events']:
            row=answer['events'].get(item['id'])
            if not self._event_valid(row):
                events[item['id']]={'reward':0.0,'failure':'MISSING_OR_MALFORMED_EVENT'};continue
            expected=item['expected'];coverage,precision=self._references(row['evidence'],item['support'],cutoff)
            timing=sum(row[k]==expected[k] for k in ('event_start','event_end','precision'))/3
            report_time=float(row['reported_on']==expected['reported_on'])
            actor=float(row['actor'].strip().casefold()==expected['actor'])
            nature=row['nature']==expected['nature']
            score=coverage*(.45*timing+.15*report_time+.15*actor+.25*precision) if nature else 0.0
            events[item['id']]={'reward':round(score,12),'timing':timing,'report_time':report_time,
                               'actor':actor,'nature_correct':nature,'support_coverage':coverage,'evidence_precision':precision}
        for item in self._gold['resolutions']:
            row=answer['resolutions'].get(item['id'])
            if not self._resolution_valid(row):
                resolutions[item['id']]={'reward':0.0,'failure':'MISSING_OR_MALFORMED_RESOLUTION'};continue
            expected=item['expected'];at=datetime.fromisoformat(item['cutoff'])
            coverage,precision=self._references(row['evidence'],item['support'],at)
            cc,cp=self._references(row['challenges'],item['challenges'],at,True)
            rules=f1(row['rules'],expected['rules']);event_date=float(row['event_date']==expected['event_date'])
            score=coverage*(.20*event_date+.20*rules+.30*precision+.30*cc*cp) if row['conclusion']==expected['conclusion'] else 0.0
            resolutions[item['id']]={'reward':round(score,12),'support_coverage':coverage,'evidence_precision':precision,
                                    'conflict_resolution':cc*cp,'rule_selection':rules,'event_date':event_date}
        positions={key:index for index,key in enumerate(order)}
        pairs=self._gold['order_pairs']
        order_score=sum(min(events[a]['reward'],events[b]['reward']) if a in positions and b in positions and positions[a]<positions[b] else 0.0 for a,b in pairs)/len(pairs)
        event_mean=sum(r['reward'] for r in events.values())/len(events)
        resolution_mean=sum(r['reward'] for r in resolutions.values())/len(resolutions)
        reward=round(.55*event_mean+.15*order_score+.30*resolution_mean,12)
        success=all(r['reward']==1 for r in list(events.values())+list(resolutions.values())) and abs(order_score-1)<1e-12
        return {**base,'reward':reward,'success':success,'events':events,'resolutions':resolutions,
                'components':{'events':event_mean,'ordering':order_score,'resolutions':resolution_mean},
                'failure_codes':[] if success else ['INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY']}
