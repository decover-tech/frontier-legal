"""Evaluator-only asset authoring, run from repository root. Contains answers."""
import json
from pathlib import Path
from tools.rlvr.environment import sha256
from tools.rlvr.audit import evidence_text
root=Path.cwd();dest=root/'benchmark/rlvr/chronology';gold_path=root/'benchmark/hidden_gold/chronology/CTH-CHRONOLOGY-001.json'
parent=json.loads((root/'benchmark/rlvr/preservation/CTH-PRESERVATION-001.json').read_text())
sources=parent['sources'];docs={}
for s in sources:
 raw=(root/s['source_path']).read_bytes();assert sha256(raw)==s['source_sha256'];docs[s['document_id']]=evidence_text(raw)
def group(anchor):
 anchors=anchor if isinstance(anchor,list) else [anchor]
 ids=sorted(k for k,v in docs.items() if any(a in v for a in anchors));assert ids,anchors
 return {'anchors':anchors,'documents':ids}
def challenge(anchor,reason):return {**group(anchor),'reason':reason}
def event(key,prompt,start,end,reported,actor,nature,anchors):
 return {'id':key,'prompt':prompt,'expected':{'event_start':start,'event_end':end,'precision':'day' if start==end else 'interval','reported_on':reported,'actor':actor,'nature':nature},'support':[group(a) for a in anchors]}
A="our broker registration in a couple of the Northwest states is still pending renewal"
B="Let's keep going — we're already behind on Q3 targets"
C="Nothing from that subfolder went into yesterday's outgoing batch."
D="H1 can move on the corrected county figure once Sarah checks the tie-out and Hannah has the owner's acknowledgment in the packet."
E="Sarah's tie-out is still open, so the release box is blank and I haven't put it in the next courier run."
F="I've checked H1's revised application acreage against the county copy and the owner's acknowledgment. Those figures agree."
G="our OR/WA broker registration renewal finalized this week."
H="Haven't confirmed. I'll ask Derek again"
I="our OR/WA broker registration was finalized in December 2022."
J="I'll schedule the pilot for September 5 after the initial production work."
K="The pilot first pass is done."
L="the archived-packet pilot ran September 5 with Craig's second review on September 6."
M="Second review completed this morning."
N="We'll describe the scope as a three-packet remediation pilot, with one document-reference exception corrected and two acreage reconciliations still open."
O="The broker coverage worksheet still has the issuance date blank for Bellhaven's Oregon and Washington entries."
P="Filing receipts show only when an application was submitted and won't answer the question on their own."
Q="Please enter the actual transmittal date when it goes, not today's date by default."
R="Keep the commercial forecast at nine for now; it shows the upside if the documents arrive."
S="The arithmetic ties; the two substantive exceptions are still open."
U="A pilot on archived packets can show the new procedure operating in September. It cannot establish that the quarterly control operated in 2022 or earlier this year."
V="We are not presenting it as the missing workpapers for the 2022 quarters or as a test of every packet."
W="I can do the second review on September 6."
events=[
 event('renewal_pending','Holt reports pending renewal and asks that marketing wait.','2022-09-15','2022-09-15','2022-09-15','dholt@bellhavenadvisory.com','status_report',[A]),
 event('marketing_continue','Shah instructs Reyes to continue marketing.','2022-09-16','2022-09-16','2022-09-16','pshah@alderpointpartners.com','instruction',[B]),
 event('held_files_excluded','The three held Q4 files were excluded from the outgoing batch, as confirmed the following day.','2022-11-08','2022-11-08','2022-11-09','hcole@cascadetimber.com','completed_action',[C]),
 event('h1_conditional_route','Shah authorizes a conditional route for the corrected H1 packet.','2022-11-15','2022-11-15','2022-11-15','pshah@alderpointpartners.com','conditional_authorization',[D]),
 event('h1_still_held','Cole reports the H1 release box still blank and no entry in the next courier run.','2022-11-15','2022-11-15','2022-11-15','hcole@cascadetimber.com','status_report',[E]),
 event('h1_tieout','Nguyen completes the H1 acreage tie-out, preserving the limits on submission.','2022-11-17','2022-11-17','2022-11-17','snguyen@cascadetimber.com','completed_action',[F,Q]),
 event('claimed_renewal','The underlying renewal occurrence claimed in Holt\'s contemporaneous December message: retain its supported date range and attribution.','2022-12-19','2022-12-20','2022-12-20','dholt@bellhavenadvisory.com','attributed_claim',[G]),
 event('verification_gap','Shah says registration has not been confirmed.','2023-01-10','2023-01-10','2023-01-10','pshah@alderpointpartners.com','status_report',[H]),
 event('renewal_restatement','Holt restates the December claim for the record in response to the subpoena context; date this communication, not a new renewal.','2023-06-25','2023-06-25','2023-06-25','dholt@bellhavenadvisory.com','attributed_claim',[I]),
 event('pilot_scheduling','Nguyen issues the instruction scheduling the pilot; date the scheduling communication, not the future target.','2023-08-18','2023-08-18','2023-08-18','snguyen@cascadetimber.com','instruction',[J]),
 event('pilot_first_pass','Cole completes the pilot first pass; reconcile the contemporaneous update with Nguyen\'s later dated report.','2023-09-05','2023-09-05','2023-09-05','hcole@cascadetimber.com','completed_action',[K,L]),
 event('pilot_second_review','Sato reports the second review and its findings about the substantive exceptions.','2023-09-06','2023-09-06','2023-09-06','csato@cascadetimber.com','completed_action',[M,S]),
 event('pilot_report_to_auditor','Nguyen sends the retrospective pilot summary to the auditor.','2023-09-07','2023-09-07','2023-09-07','snguyen@cascadetimber.com','status_report',[L,V]),
 event('auditor_scope','Moss describes the supported scope of the remediation pilot.','2023-09-08','2023-09-08','2023-09-08','bmoss@mosslane-cpa.com','assessment',[N]),
]
cutoff='2023-09-08T23:59:59-07:00'
claims=[
 {'id':'registration_issuance','cutoff':cutoff,'prompt':'Assess whether the record establishes the actual OR/WA issuance date in light of Holt\'s December and June statements and the coverage follow-ups. Classify the finding and give an actual date only if supported.',
  'expected':{'conclusion':'unverified_not_proven_false','event_date':None,'rules':['T2','T3','T4','T6']},'support':[group(G),group(H),group(O),group(P)],'challenges':[challenge(I,'repetition_not_independent_proof')]},
 {'id':'h1_transmittal','cutoff':cutoff,'prompt':'Does the record establish that H1 was actually transmitted on the day of Nguyen\'s tie-out? Distinguish commercial forecasting, permission and completed transmission.',
  'expected':{'conclusion':'not_established','event_date':None,'rules':['T3','T5','T6']},'support':[group(D),group(E),group(Q)],'challenges':[challenge(R,'forecast_not_execution'),challenge(F,'tieout_not_transmittal')]},
 {'id':'pilot_exceptions','cutoff':cutoff,'prompt':'Does the second-review completion establish that the two acreage exceptions were closed on that date?',
  'expected':{'conclusion':'contradicted','event_date':None,'rules':['T3','T4','T5','T6']},'support':[group(S),group(N)],'challenges':[challenge(M,'review_completion_not_exception_closure')]},
 {'id':'historical_quarterly_tests','cutoff':cutoff,'prompt':'Does the September pilot establish when the historical 2022 quarterly controls were performed?',
  'expected':{'conclusion':'not_established','event_date':None,'rules':['T1','T3','T5','T6']},'support':[group(U),group(V)],'challenges':[challenge(M,'later_pilot_not_historical_proof')]},
 {'id':'pilot_asof_august','cutoff':'2023-08-21T23:59:59-07:00','prompt':'At this earlier checkpoint, was pilot execution already established, and what actual execution date could be assigned?',
  'expected':{'conclusion':'not_established','event_date':None,'rules':['T1','T3','T4','T6']},'support':[group(J),group(W)],'challenges':[challenge(K,'after_cutoff')]},
]
pairs=[]
for a in events:
 for b in events:
  if a['expected']['event_end']<b['expected']['event_start']:pairs.append([a['id'],b['id']])
pairs.append(['h1_conditional_route','h1_still_held'])
gold={'task_id':'CTH-CHRONOLOGY-001','review_status':'author_checked_independent_review_pending','events':events,'resolutions':claims,'order_pairs':pairs}
gold_path.write_text(json.dumps(gold,indent=2)+'\n')
ref={'type':'object','additionalProperties':False,'required':['document_id','quote'],'properties':{'document_id':{'type':'string'},'quote':{'type':'string','minLength':20,'maxLength':800}}}
reasons=sorted({g['reason'] for c in claims for g in c['challenges']})
cr=json.loads(json.dumps(ref));cr['required'].append('reason');cr['properties']['reason']={'enum':reasons}
props={'event_start':{'type':'string','format':'date'},'event_end':{'type':'string','format':'date'},'precision':{'enum':['day','interval']},'reported_on':{'type':'string','format':'date'},'actor':{'type':'string'},'nature':{'enum':['attributed_claim','instruction','conditional_authorization','status_report','completed_action','assessment']},'evidence':{'type':'array','maxItems':6,'items':ref}}
rprops={'conclusion':{'enum':['established','not_established','contradicted','unverified_not_proven_false']},'event_date':{'type':['string','null'],'format':'date'},'rules':{'type':'array','uniqueItems':True,'items':{'enum':['T1','T2','T3','T4','T5','T6']},'maxItems':6},'evidence':{'type':'array','maxItems':6,'items':ref},'challenges':{'type':'array','maxItems':5,'items':cr}}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','type':'object','additionalProperties':False,'required':['events','order','resolutions'],'properties':{'events':{'type':'object','additionalProperties':False,'properties':{i['id']:{'$ref':'#/$defs/event'} for i in sorted(events,key=lambda i:i['id'])}},'order':{'type':'array','uniqueItems':True,'maxItems':len(events),'items':{'enum':sorted(i['id'] for i in events)}},'resolutions':{'type':'object','additionalProperties':False,'properties':{i['id']:{'$ref':'#/$defs/resolution'} for i in claims}}},'$defs':{'event':{'type':'object','additionalProperties':False,'required':list(props),'properties':props},'resolution':{'type':'object','additionalProperties':False,'required':list(rprops),'properties':rprops}}}
(dest/'output_schema.json').write_text(json.dumps(schema,indent=2)+'\n')
task={'task_id':'CTH-CHRONOLOGY-001','suite_task_number':2,'title':'Task 2 — evidence chronology','version':'1.0.0','split':'development','verifier':'evidence-chronology/1.0.0','cutoff':cutoff,
 'instruction':'Search the pinned Cascade Timber email-text collection and reconstruct the requested milestones across registration, the Q4 held-file queue and the remediation pilot. Separate event time from report time, preserve date uncertainty and attribution, order the events, and resolve the five proposed inferences under the supplied chronology rules. No additional events, external research, attachment contents or authoring notes are evidence.',
 'milestones':[{k:i[k] for k in ['id','prompt']} for i in sorted(events,key=lambda i:i['id'])],
 'resolution_questions':[{k:i[k] for k in ['id','cutoff','prompt']} for i in claims],
 'limits':{'max_steps':120,'max_observation_chars':300000,'search_page_size':8,'read_page_chars':6000},
 'policy_path':'benchmark/rlvr/chronology/policy.md','policy_sha256':sha256((dest/'policy.md').read_bytes()),'output_schema':'benchmark/rlvr/chronology/output_schema.json','schema_sha256':sha256((dest/'output_schema.json').read_bytes()),
 'oracle_path':str(gold_path.relative_to(root)),'oracle_sha256':sha256(gold_path.read_bytes()),'sources':sources,'evidence_scope':parent['evidence_scope']}
(dest/'CTH-CHRONOLOGY-001.json').write_text(json.dumps(task,indent=2)+'\n')
print('Built',len(events),'milestones,',len(claims),'resolutions,',len(pairs),'order constraints on',len(sources),'pinned emails.')
