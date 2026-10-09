"""Bounded, tool-only episode. Evaluator data never enters model observations.

This is an in-process evaluation interface, not an OS security boundary: keep
this module and its trusted repository outside the model's filesystem sandbox.
"""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib,json,re,shlex,unicodedata
import jsonschema
from .evidence import load_bundle

ROOT=Path(__file__).resolve().parents[2]
TASKS=Path('benchmark/litigation_skills/tasks')
GOLD=Path('benchmark/hidden_gold/litigation_skills')

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(text): return ' '.join(unicodedata.normalize('NFKC',text).split())
def strict_json(value):
    def pairs(items):
        result={}
        for key,item in items:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=item
        return result
    try:
        if isinstance(value,str):
            text=value.strip()
            if text.startswith('```json\n') and text.endswith('\n```'):text=text[8:-4]
            elif text.startswith('```\n') and text.endswith('\n```'):text=text[4:-4]
            result=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))
        else:result=json.loads(json.dumps(value,allow_nan=False))
        stack=[(result,0)]
        while stack:
            item,depth=stack.pop()
            if depth>64:raise ValueError('Invalid or excessively nested JSON')
            if isinstance(item,dict):stack.extend((v,depth+1) for v in item.values())
            elif isinstance(item,list):stack.extend((v,depth+1) for v in item)
        return result
    except RecursionError as error:
        raise ValueError('Invalid or excessively nested JSON') from error

def pointer(obj,path):
    if path=='': return obj
    if not path.startswith('/'): raise ValueError('Invalid JSON pointer')
    for p in path[1:].split('/'):
        p=p.replace('~1','/').replace('~0','~')
        obj=obj[int(p)] if isinstance(obj,list) else obj[p]
    return obj

def leaves(obj,path=''):
    if isinstance(obj,dict) and obj:
        return [(p,v) for k,v in obj.items() for p,v in leaves(v,path+'/'+k.replace('~','~0').replace('/','~1'))]
    # Arrays are a coherent set/list answer, not positional token overlap.
    return [(path,obj)]

def schema_at(schema,path):
    for piece in path.lstrip('/').split('/') if path else []:
        piece=piece.replace('~1','/').replace('~0','~')
        schema=schema.get('properties',{}).get(piece,schema.get('items',{}))
    return schema

def equivalent(a,b,schema=None):
    schema=schema or {}
    if type(a) is not type(b): return False
    if isinstance(a,dict):
        return set(a)==set(b) and all(equivalent(a[k],b[k],schema.get('properties',{}).get(k,{})) for k in a)
    if isinstance(a,list):
        if schema.get('uniqueItems'):
            return len(a)==len(b) and all(any(equivalent(x,y,schema.get('items',{})) for y in b) for x in a)
        return len(a)==len(b) and all(equivalent(x,y,schema.get('items',{})) for x,y in zip(a,b))
    return a==b

def field_accuracy(answer,expected,schema=None):
    vals=leaves(expected)
    good=0
    for p,v in vals:
        try: good += equivalent(pointer(answer,p),v,schema_at(schema or {},p))
        except (KeyError,IndexError,TypeError,ValueError): pass
    return good/len(vals)

class LitigationEnvironment:
    def __init__(self,task_id,root=ROOT,*,verify_sources=True,require_pins=True,dependency_artifacts=None):
        self.root=Path(root).resolve()
        self.dependency_artifacts=deepcopy(dependency_artifacts or {})
        if not re.fullmatch(r'CTH-LIT-\d{2}',task_id): raise ValueError('Unknown task identifier')
        self.directory=self.root/TASKS/task_id
        self.task=strict_json((self.directory/'task.json').read_text())
        if self.task['task_id'] != task_id: raise ValueError('Task ID mismatch')
        self.schema=strict_json((self.directory/'output_schema.json').read_text())
        self.fixtures=strict_json((self.directory/'fixtures.json').read_text())
        self.policy=(self.directory/'policy.md').read_text()
        oracle_path=self.root/GOLD/(task_id+'.json')
        self.oracle=strict_json(oracle_path.read_text())
        if self.oracle['task_id'] != task_id: raise ValueError('Oracle ID mismatch')
        bundle=load_bundle(self.root,verify_sources=verify_sources)
        pins={'bundle_manifest_sha256':bundle['bundle_sha256'], 'policy_sha256':digest(self.directory/'policy.md'),
          'schema_sha256':digest(self.directory/'output_schema.json'),'fixtures_sha256':digest(self.directory/'fixtures.json'),
          'oracle_sha256':digest(oracle_path)}
        for k,v in pins.items():
            if require_pins and self.task.get(k)!=v: raise ValueError('Task asset hash mismatch: '+k)
        self.all_documents=bundle['documents']
        self.coverage=bundle['coverage']
        self.cutoff=datetime.fromisoformat(self.task['cutoff'])
        if not self.cutoff.tzinfo: raise ValueError('Cutoff needs timezone')
        self.documents={k:d for k,d in self.all_documents.items() if self.eligible(d)}
        if set(self.dependency_artifacts)-set(self.task.get('dependencies',[])): raise ValueError('Undeclared dependency')
        self.schemas=self.task.get('artifact_schemas',{})
        for path in self.schemas:
            if not path or Path(path).is_absolute() or '..' in Path(path).parts: raise ValueError('Unsafe artifact path')
            jsonschema.Draft202012Validator.check_schema(self.schemas[path])
        if set(self.fixtures.get('artifacts',{}))-set(self.schemas): raise ValueError('Undeclared fixture')
        jsonschema.Draft202012Validator.check_schema(self.schema)
        self.reset()

    def eligible(self,doc):
        d=doc
        if doc.get('parent_email_id'):
            d=self.all_documents.get(doc['parent_email_id'])
            if d is None: return False
        stamp=d.get('source_date')
        return not stamp or datetime.fromisoformat(stamp)<=self.cutoff

    def reset(self):
        self.steps=0; self.observation_chars=0; self.done=False; self.seen={}; self.trace=[]
        self.artifacts=deepcopy(self.fixtures.get('artifacts',{}))
        self.result=None
        visible={k:deepcopy(self.task[k]) for k in ('task_id','skill','title','version','split','cutoff','instruction','dependencies','findings','limits','state_invariants') if k in self.task}
        public={'task':visible,'policy':self.policy,'output_schema':deepcopy(self.schema),
          'artifact_schemas':deepcopy(self.schemas),'fixture_provenance':[{k:deepcopy(item[k]) for k in ('artifact_path','description') if k in item} for item in self.fixtures.get('provenance',[])],
          'evidence':{'eligible_document_count':len(self.documents),
          'extraction_notice':'OCR is unverified unless explicitly reviewed. Missing text is not evidence of absence. Undated standalone documents are supplied references; their presence does not prove historical availability. Attachments use parent email date for cutoff eligibility.'},
          'output_conventions':{'calendar_dates':'Use YYYY-MM-DD for calendar-date answer fields.','categorical_values':'Use the named alternatives in the public schema.','citations':'Copy source text verbatim; whitespace differences are normalized.'},
          'dependency_artifacts':{k:list(v) for k,v in self.dependency_artifacts.items()},
          'tools':['search','read','list_artifacts','read_artifact','write_artifact','read_dependency','submit']}
        self.observation_chars=len(json.dumps(public,ensure_ascii=False))
        return public

    def step(self,action):
        if self.done:raise RuntimeError('Episode has ended')
        self.steps+=1
        original=action
        def finish(code):
            self.done=True
            self.result={'reward':0.0,'passed':False,'error':code,'steps':self.steps}
            return self.result
        if self.steps>self.task['limits']['max_steps']:
            obs=finish('step_budget_exceeded')
        elif self.observation_chars>self.task['limits']['max_observation_chars']:
            obs=finish('observation_budget_exceeded')
        else:
            try:
                if isinstance(action,str) and len(action)>150000:raise ValueError('Action exceeds 150000 characters')
                action=strict_json(action)
                if len(json.dumps(action,ensure_ascii=False))>150000:raise ValueError('Action exceeds 150000 characters')
                if not isinstance(action,dict):raise ValueError('Action must be an object')
                tool=action.get('tool')
                if tool=='submit':
                    self.done=True;self.result=self.grade(action.get('answer'));obs=self.result
                else:obs=self.dispatch(tool,action)
            except (ValueError,KeyError,IndexError,TypeError,RecursionError,jsonschema.ValidationError) as error:
                obs={'error':str(error).split('\n')[0][:350]}
                if isinstance(action,dict) and action.get('tool')=='submit':
                    self.done=True;self.result={'reward':0.0,'passed':False,'error':'format_failure','detail':obs['error']};obs=self.result
            if not self.done:
                size=len(json.dumps(obs,ensure_ascii=False))
                if self.observation_chars+size>self.task['limits']['max_observation_chars']:obs=finish('observation_budget_exceeded')
                else:self.observation_chars+=size
                if not self.done and self.steps>=self.task['limits']['max_steps']:obs=finish('step_budget_exceeded')
        # Raw transport text preserves malformed actions for deterministic replay.
        # Non-JSON Python objects are outside the wire contract and explicitly flagged.
        replayable=True
        if isinstance(original,str):recorded=original[:150001]
        else:
            try:recorded=json.loads(json.dumps(original,allow_nan=False))
            except (TypeError,ValueError,RecursionError):recorded=None;replayable=False
        self.trace.append({'action':recorded,'observation':deepcopy(obs),'done':self.done,'replayable':replayable})
        return {'observation':obs,'done':self.done,'reward':self.result['reward'] if self.done and self.result else 0.0}

    def dispatch(self,tool,a):
        if tool=='search':
            query=a.get('query','')
            if not isinstance(query,str) or not 1<=len(query)<=300: raise ValueError('Query must be 1–300 characters')
            terms=[norm(t).casefold() for t in shlex.split(query)]
            if not terms: raise ValueError('Empty search')
            hits=[]
            for key,doc in self.documents.items():
                if all(term in norm(doc['text']).casefold() for term in terms):
                    loc=next((l for l in doc['locators'] if any(t in norm(doc['text'][l['start']:l['end']]).casefold() for t in terms)),None)
                    hits.append({'document_id':key,'kind':doc['kind'],'source_date':doc['source_date'],
                      'parent_email_id':doc.get('parent_email_id'),'locator':loc['locator'] if loc else None,
                      'snippet':doc['text'][loc['start']:loc['end']][:450] if loc else ''})
            offset=a.get('offset',0)
            if type(offset)!=int or offset<0: raise ValueError('Invalid offset')
            size=self.task['limits']['search_page_size']
            return {'hits':hits[offset:offset+size],'total':len(hits),'next_offset':offset+size if offset+size<len(hits) else None}
        if tool=='read':
            key=a['document_id']
            if key not in self.documents: raise ValueError('Unknown or unavailable document')
            doc=self.documents[key]; offset=a.get('offset',0)
            if type(offset)!=int or offset<0: raise ValueError('Invalid offset')
            low,high=0,len(doc['text'])
            if a.get('locator') is not None:
                loc=next((l for l in doc['locators'] if l['locator']==a['locator']),None)
                if not loc: raise ValueError('Unknown locator')
                low,high=loc['start'],loc['end']
            start=min(low+offset,high); end=min(start+self.task['limits']['read_page_chars'],high)
            self.seen.setdefault(key,[]).append((start,end))
            return {'document_id':key,'kind':doc['kind'],'source_date':doc['source_date'],'parent_email_id':doc.get('parent_email_id'),
              'text':doc['text'][start:end],'start':start,'end':end,
              'next_offset':end-low if end<high else None,
              'locators':[deepcopy(l) for l in doc['locators'] if l['start']<end and l['end']>start],
              'attachment_ids':doc.get('attachment_ids',[]),'extraction':deepcopy(doc['extraction'])}
        if tool=='read_dependency':
            task_id=a['task_id'];path=a['path']
            if task_id not in self.dependency_artifacts or path not in self.dependency_artifacts[task_id]: raise ValueError('Unknown dependency artifact')
            return {'task_id':task_id,'path':path,'content':deepcopy(self.dependency_artifacts[task_id][path]),'provenance':'prior_episode_artifact_not_primary_evidence'}
        if tool=='list_artifacts': return {'paths':list(self.schemas),'present':list(self.artifacts)}
        if tool=='read_artifact':
            if a['path'] not in self.schemas: raise ValueError('Unknown artifact path')
            return {'path':a['path'],'content':deepcopy(self.artifacts.get(a['path']))}
        if tool=='write_artifact':
            path=a['path']
            if path not in self.schemas: raise ValueError('Unknown artifact path')
            content=strict_json(a['content']); jsonschema.validate(content,self.schemas[path])
            self.artifacts[path]=deepcopy(content)
            return {'path':path,'written':True}
        raise ValueError('Unknown tool')

    def valid_citation(self,c):
        if not isinstance(c,dict) or set(c)!={'document_id','locator','quote'}: return False
        key=c['document_id']; doc=self.documents.get(key)
        if not doc or not isinstance(c['quote'],str) or len(re.sub(r'\s','',c['quote']))<20: return False
        loc=next((l for l in doc['locators'] if l['locator']==c['locator']),None)
        if not loc or norm(c['quote']) not in norm(doc['text'][loc['start']:loc['end']]): return False
        merged=[]
        for lo,hi in sorted(self.seen.get(key,[])):
            if merged and lo<=merged[-1][1]: merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
            else: merged.append((lo,hi))
        return any(norm(c['quote']) in norm(doc['text'][max(lo,loc['start']):min(hi,loc['end'])]) for lo,hi in merged if hi>loc['start'] and lo<loc['end'])

    def proof_score(self,citations,groups):
        if not groups: return (1.0,1.0 if not citations else 0.0,[])
        hit=set(); relevant=set()
        for i,c in enumerate(citations):
            if not self.valid_citation(c): continue
            for j,g in enumerate(groups):
                if any(c['document_id']==p.get('document_id') and c['locator']==p.get('locator') and norm(p['quote']) in norm(c['quote']) for p in g['alternatives']):
                    hit.add(j); relevant.add(i)
        return len(hit)/len(groups),len(relevant)/len(citations) if citations else 0.0,[g['id'] for j,g in enumerate(groups) if j in hit]

    def grade(self,answer):
        answer=strict_json(answer); jsonschema.validate(answer,self.schema)
        scores={}
        for f in self.task['findings']:
            key=f['id']; submitted=answer['findings'][key]; expected=self.oracle['findings'][key]
            accuracy=max(field_accuracy(submitted['answer'],a,f['answer_schema']) for a in expected['accepted_answers'])
            support,sp,matched=self.proof_score(submitted['support'],expected['support_groups'])
            counter,cp,cm=self.proof_score(submitted['counter'],expected.get('counter_groups',[]))
            # Required conflicts are part of the reasoning, not bonus points.
            conflict_factor=(0.6+0.4*counter*cp) if expected.get('counter_groups') else cp
            value=accuracy*support*sp*conflict_factor
            scores[key]={'score':value,'answer_accuracy':accuracy,'support_coverage':support,'support_precision':sp,'counter_coverage':counter,'counter_precision':cp}
        findings=sum(s['score'] for s in scores.values())/len(scores)
        checks=[]
        for check in self.oracle.get('artifact_checks',[]):
            ok=False
            try:
                current=pointer(self.artifacts[check['path']],check['pointer']); kind=check['kind']
                if kind=='equals': ok=equivalent(current,check['value'],schema_at(self.schemas[check['path']],check['pointer']))
                elif kind=='equals_finding':
                    expected=pointer(answer['findings'][check['finding']]['answer'],check['answer_pointer']); ok=equivalent(current,expected,schema_at(next(f['answer_schema'] for f in self.task['findings'] if f['id']==check['finding']),check['answer_pointer']))
                elif kind=='preserve': ok=current==pointer(self.fixtures['artifacts'][check['path']],check['pointer'])
                elif kind=='append_only':
                    initial=pointer(self.fixtures['artifacts'][check['path']],check['pointer']); ok=isinstance(current,list) and current[:len(initial)]==initial and len(current)>=len(initial)+check.get('min_new',1)
                else: raise ValueError('Unknown artifact check')
            except (KeyError,TypeError,ValueError,IndexError): pass
            checks.append(bool(ok))
        valid_artifacts=all(path in self.artifacts and jsonschema.Draft202012Validator(schema).is_valid(self.artifacts[path]) for path,schema in self.schemas.items())
        artifact=(sum(checks)/len(checks) if checks else float(not self.schemas))*float(valid_artifacts)
        reward=findings*(0.8+0.2*artifact) if self.schemas else findings
        return {'reward':round(reward,8),'passed':reward>=1-1e-9,'findings':scores,
          'artifact_score':artifact,'artifact_checks_passed':sum(checks),'artifact_checks_total':len(checks),
          'steps':self.steps,'observation_chars':self.observation_chars}
