# Cascade Timber litigation skill task plan

Prepared: 2026-10-08. Status: implementation plan; tasks have not been executed.

## Objective and scope

Build a task suite covering all 19 skills in `claude-for-legal/litigation-legal/skills`, using only the Cascade Timber dataset. Add the docket-watcher as an optional twentieth workflow. Extend the existing 28-task benchmark rather than replace it.

“Task” means a reproducible benchmark/workflow specification with a prompt, permitted inputs, expected artifacts, dependencies, and evaluator-only acceptance criteria. It does not mean creating separate application chats or deploying agents.

The repository describes a fictional matter, USA v. Cascade Timber Holdings, Inc., concerning the Coastal Solar Credit Program. Local inventory confirmed 1,454 EML files, 38 standalone exhibit PDFs, and 21 contract files plus their index. Existing documentation contains stale inventory figures; derive coverage from files, not prose counts.

## Dataset boundary

- Evidence: `data/emails/Custodians/**/*.eml`, their MIME attachments, `data/emails/Exhibits/`, and `data/contracts/`.
- Review protocols: the four DOCX files under `definitions/`. Extract and inspect these before writing substantive task specifications. Treat them as the benchmark's supplied protocols, not independently verified current law.
- Metadata: allowlisted load-file fields DOCID, CUSTODIAN, DATESENT, TIMESENT, FROM, TO, CC, SUBJECT, ATTACHMENTS, MESSAGEID, FILEPATH. Exclude TAG, PRIVILEGED, and CONTAINS_PII labels from runner inputs. Inspect exhibit and contract indexes before admitting their columns.
- Exclude from runner access: `documentation/`, `output/`, `logs/`, `tools/`, `benchmark/hidden_gold/`, `benchmark/GOLD_LABELS.csv`, existing scoring files, and any other authoring or answer material. Task authors/evaluators may use these to locate candidate evidence; every answer must still be supported by an allowed source.
- No internet, live legal research, connected mailboxes, live dockets, other matters, or new fictional source documents. If an authority, pleading, demand, docket, or outcome is absent, record the limitation and produce only the supported portion.
- Mountain Ridge records already in the corpus remain as negative controls. Do not treat them as Coastal Solar evidence or create another matter from them.
- Task instructions may specify output format, audience, witness, and an explicit dataset cutoff. These are evaluation parameters, not new evidence. Never invent house preferences, conflicts clearance, settlement authority, or procedural posture.
- Each run uses an isolated writable output directory and read-only evidence bundle. Do not write to global Claude configuration, alter source files, issue notices, send messages, or calendar real deadlines.

## Shared task contract

Each specification records:

1. ID, skill, title, prompt, task family, difficulty, split, and dataset commit/hash manifest.
2. Evidence scope and explicit as-of cutoff; distinguish document date, event date, inferred date, and later recollection. Avoid hindsight in historical runs. Use the dataset cutoff, not the execution date, for stale/deadline checks.
3. Required input artifacts, prerequisite tasks, and whether the run is standalone or chained.
4. Expected output paths/schema, permitted state changes, and missing-input behavior.
5. Evaluator-only supporting/counter-evidence, required joins, unknowns, forbidden overclaims, and task-specific scoring.

Use the current task schema as the base and add a separate workflow schema for these fields. Keep public prompts and private gold in separate files. For retrieval tasks, prompts do not reveal required evidence IDs; targeted document review tasks may name IDs explicitly.

## Coverage matrix: one primary task per skill

| ID | Skill | Cascade Timber task and inputs | Deliverable and acceptance focus | Dependencies |
|---|---|---|---|---|
| CTH-LIT-01 | cold-start-interview | Prepare a matter-scoped setup from permitted records; identify Cascade, counsel, document sources, and questions the dataset cannot answer. | Draft profile plus unanswered setup questions. No inferred user identity, house risk appetite, authority ladder, or claim that setup is complete when required answers are missing. | Evidence inventory |
| CTH-LIT-02 | customize | Given the draft profile and a source-backed correction identified during evidence review, propose a narrow update. | Before/after diff, source citation, downstream effects; preserve unknown preferences and unrelated sections. Select the correction only after validating it in source records. | 01, source validation |
| CTH-LIT-03 | matter-intake | Assemble intake for the Coastal Solar examination from initiating records, engagement, parties, dates, and preservation correspondence. | Draft matter.md, history.md, and ledger row; conflicts status remains unknown/pending unless supported. Do not certify clearance or invent pleaded claims from the matter caption. | 01 |
| CTH-LIT-04 | matter-workspace | Organize the single Cascade matter in a sandbox workspace using intake artifacts. | Manifest, active-matter pointer, isolated output paths; one stable slug and ledger entry. No additional clients or cross-matter reads. | 03 draft artifacts |
| CTH-LIT-05 | demand-received | Search for an actual inbound demand and distinguish it from the IRS summons, inquiries, and ordinary commercial correspondence. | If present, sourced demand triage and options; otherwise missing-trigger report with search coverage. Never rebrand a summons as a private demand. | Inventory, 03 |
| CTH-LIT-06 | demand-intake | Assess readiness for a Cascade preservation demand concerning third-party records, using the preservation correspondence. The task requests preparation, not an assertion that a demand was historically sent. | Draft intake with recipients/scope supported by records; flag missing signer, tone, response period, instructions, and strategic choices. | 03, 09 preservation analysis |
| CTH-LIT-07 | demand-draft | Turn the supported portions of 06 into a preservation-letter draft only to the extent the intake permits. | Internal review draft and checklist, or a precise missing-input handoff. No invented recipient address, legal authority, deadline, or send event. Word output only after the underlying content is ready. | 06 |
| CTH-LIT-08 | subpoena-triage | Classify and scope the actual IRS instrument under the supplied protocol; reconstruct requests, service/receipt, and extension correspondence. | Request matrix, sourced deadline chain, objections/questions framework, preservation and review plan. Distinguish the administrative summons from an ordinary civil subpoena; do not import FRCP 45 assumptions. | Protocol extraction, 03 |
| CTH-LIT-09 | legal-hold | Reconstruct preservation preparation, formal hold, collection, departing custodians, and third-party gaps. | Hold-status matrix and proposed refresh scope/notice; distinguish a drafted notice from proven issuance, acknowledgment, or preservation. Release mode should identify any missing release basis. | 03, 08; reuse CTH-AGENT-008 |
| CTH-LIT-10 | chronology | Build the acreage-warning, Clearwater, broker-authority, continuation/pause, and examination timelines. | Source-cited events with event/document dates, contrary evidence, gaps, and privilege flags. Do not merge parcel ID systems without a crosswalk. | Evidence inventory; reuse AGENT-001/003/005/008 |
| CTH-LIT-11 | claim-chart | Use civil mode to map the competing Coastal Solar factual theories to issues and evidence. Chart legal elements only if supplied authority and pleadings support them. | Issue/proof matrix, support and counter-evidence, gap list, sources CSV; explicitly label it provisional issue mapping where pleaded counts or controlling elements are absent. Patent mode is out of scope for this dataset. | 08, 10; reuse AGENT-004/005/009/010 |
| CTH-LIT-12 | deposition-prep | Prepare a Tom Reyes witness dossier and examination outline based on warnings, subsequent conduct, and conflicting explanations. | Witness timeline, prioritized topics/questions, exhibit list, exact quotations, and gaps. Do not invent a scheduled deposition, testimony, or a 30(b)(6) designation. | 10, 11; reuse AGENT-001/004 |
| CTH-LIT-13 | privilege-log-review | Review actual corpus emails/attachments covering GC advice, bare forwards, outside counsel, Whitaker, Larsen, third parties, and mixed-purpose communications. | Separate ACP, work-product, and consultant analyses, rationale and uncertainty per record/attachment. Build a source-grounded draft log rather than trust the documented stale demo log. | Protocols, entity map; reuse AGENT-006 and atomic contrast tasks |
| CTH-LIT-14 | brief-section-drafter | Draft a record-supported statement of facts on warnings and continued operations, using the task's specified defense perspective and fairly addressing contrary evidence. | Draft factual section with pinpoint citations and drafting notes; distinguish this requested writing exercise from an actual filed brief. No fabricated court, motion, local rules, or legal authorities. | 10, 11, 13; reuse AGENT-004/010 |
| CTH-LIT-15 | matter-update | Apply one source-backed development after an earlier cutoff to the draft matter state. Select the event from permitted records during authoring. | New history entry and minimal ledger diff, source citation, risk/materiality questions; no automatic reserve or settlement decision and no rewriting earlier history. | 03, 10 |
| CTH-LIT-16 | matter-briefing | Brief Cascade's status at the selected end-of-corpus cutoff. | Posture, recent changes, documented deadlines, evidence for/against, and open questions. Explicitly distinguish historical intake from subsequent updates. | 03, 10, 15; reuse AGENT-010 |
| CTH-LIT-17 | portfolio-status | Produce a one-matter portfolio report for Cascade alone. | One-row ledger, documented hold/deadline/conflict gaps, missing financial/risk fields; no fake portfolio distribution, reserve value, or other clients. | 03, 09, 15 |
| CTH-LIT-18 | oc-status | Prepare a status-request draft for L&L based on actual unresolved issues and the selected cutoff. | Local email draft covering developments, preservation, deadlines, and open evidence requests. Use verified contact details or placeholders; no invented budget or real sending. | 16, 17 |
| CTH-LIT-19 | matter-close | Evaluate whether the record supports closing the examination/matter. | Closure-readiness report. If no final resolution is supported, leave matter state unchanged and identify needed records; no fabricated settlement, dismissal, final IRS resolution, or hold release. | 16, 09; reuse CTH-T2-017 |

The listed dependencies permit draft handoffs without asserting that intake approval or conflicts clearance occurred. The runner must retain incomplete/blocked status where necessary. A correct abstention is a successful benchmark outcome, not a task failure.

## Optional agent task

**CTH-LIT-20 — docket-watcher, offline variant.** Inventory whether actual docket entries exist. If present, compare two cutoff snapshots and report new entries plus source-grounded candidate dates. If absent, report that docket monitoring is unsupported and separately summarize procedural correspondence without calling it a court docket. No connectors, background scheduling, or calendar writes. Do not count this as a twentieth skill.

## Build phases and completion criteria

### Phase 1 — inventory and safe evidence bundle

- Pin dataset and reference-plugin commits; hash each source and extracted attachment.
- Parse all 1,454 emails; preserve headers, bodies, quoted context, thread links, attachment relationships, and extraction errors. Hash-deduplicate identical attachments/contracts without losing carrying-email provenance.
- Extract the four protocols and document text; OCR scanned contracts where required. Record page/paragraph locators and extraction coverage. A missing text layer is not missing evidence.
- Build an entity/alias table from records and validate parcel/program identifiers, date conflicts, and contract version sequence.
- Package only approved evidence and sanitized metadata into an isolated runner input tree. Remove filenames' answer-like authoring annotations only through a documented mapping if needed; never silently alter source content.
- Exit: inventory reconciles; every inclusion/exclusion is explicit; label/hidden-gold access is denied; OCR and parse failures are visible.

### Phase 2 — specify all 19 tasks

- Write public task specifications for CTH-LIT-01–19 and optional 20.
- For each, audit actual evidence availability and assign `ready`, `partial`, or `missing-trigger`; update conditional tasks after the audit rather than assume nonexistent documents.
- Reuse existing benchmark evidence packages and assertions where they still match the expanded corpus. Revalidate seed-era “unknowns” against later records before carrying them into new gold.
- Write an evaluator-only acceptance checklist for each task, including its required/contrary evidence and legitimate abstentions.
- Exit: every skill has a specification, declared input/output contract, prerequisites, and acceptance criteria.

### Phase 3 — author high-value evidence tasks first

Implement 08–14 first: summons triage, preservation, chronology, proof mapping, witness prep, privilege review, and factual drafting. These exercise the dataset's strongest evidence chains. Keep drafts and proposed actions explicit.

- Pilot retrieval tasks without evidence IDs in the prompt.
- Inspect outputs for counter-evidence, attachment-level analysis, version accuracy, and citation entailment.
- Exit: seven complete task packages with reviewed gold; defects trace to a prompt, extraction, retrieval, or reasoning stage.

### Phase 4 — author setup and lifecycle tasks

Implement 01–07 and 15–19, consuming validated artifacts where appropriate. Treat absent profile choices, demand triggers, and closure records as designed missing-input cases. Do not add new fictional facts merely to make a skill run end to end.

- Reconcile workspace/intake/ledger semantics in the task harness: one matter ID, one ledger, history retained, no silent directory moves on closure.
- Separate `drafted`, `approved`, `issued`, and `acknowledged` hold states in expected artifacts.
- Exit: 19 task packages; full coverage includes readiness and abstention tests, not necessarily positive execution of every skill mode.

### Phase 5 — evaluation and chained pilot

- Run standalone tasks against evaluator-owned prerequisite fixtures built only from allowed evidence. Run a second chained suite against actual upstream outputs to measure error propagation.
- Pilot chain: intake draft → workspace → summons triage → hold analysis → chronology → privilege/proof mapping → witness/brief draft → update → briefing/status → OC draft → closure-readiness.
- Assign task splits by evidence family/thread, including identical attachments, not random documents. Because everything concerns one matter, report only within-matter performance. Full-corpus retrieval runs are a separate evaluation track, not evidence-isolated held-out generalization.
- Exit: all artifacts validate, citations are checked against sources, no evidence/gold leakage, and supported/partial/abstained results are reported separately.

## Proposed files

```text
benchmark/litigation_skills/
  README.md
  schemas/workflow_task.schema.json
  tasks/CTH-LIT-01.json ... CTH-LIT-19.json
  tasks/CTH-LIT-20.json                  # optional agent
  fixtures/                            # source-grounded prerequisite states
  splits.json
benchmark/hidden_gold/litigation_skills/
  CTH-LIT-01.json ... CTH-LIT-19.json
benchmark/eval/litigation_skill_rubric.md
tools/litigation_tasks/
  build_evidence_bundle.py
  validate_tasks.py
  validate_outputs.py
output/litigation_skills/<run-id>/       # generated outputs; never runner evidence
```

## Evaluation

Use the existing 100-point rubric for evidence-heavy tasks: required evidence, temporal joins, supporting and contrary evidence, uncertainty, citations, required content, investigation planning, efficiency, and restraint. Add task-specific artifact/state checks rather than forcing retrieval metrics onto setup or workspace tasks.

Required pass conditions across the suite:

- Every material factual statement has an accurate source locator or is labeled unknown/inference/disputed.
- No hidden-label access, fabricated evidence/authority/outcome, unauthorized external action, or silent source edits.
- Monetary figures preserve distinctions between credit face value, cash, revenue, and exposure; preliminary estimates are not reserves or liability findings.
- Broker renewal filing, issuance, and actual placement dates are distinct. Parcel identifier systems and Coastal Solar/Mountain Ridge records remain separate.
- Whistleblower identity, preservation completeness, privilege uncertainty, and final resolution are not asserted beyond the available record.
- Task outputs distinguish source facts, evaluation instructions, proposed drafts, and completed historical actions.

Reviewer acceptance is required before new gold is called authoritative. Existing machine-generated labels and authoring intent are candidate supervision only.

## Current completion

- Completed: reference skill inventory, repository/benchmark inspection, local corpus counts, and this plan.
- Next: Phase 1 extraction and evidence-availability audit, followed by all 19 public task specifications.
- Not performed: substantive corpus review, task/gold authoring, plugin installation, task execution, or creation of separate application tasks.

### RLVR pilot follow-up — 2026-10-08

The initial plan above remains the broader litigation-suite roadmap. A smaller
infrastructure pilot is now implemented separately in `benchmark/rlvr/` and
`tools/rlvr/`: CTH-DATE-001 extracts the sent date from EMAIL-003, with a pinned
source hash, binary verifier, single-turn environment, and OpenAI/Anthropic/
Gemini REST adapters. All 18 tests passed. One live attempt each on gpt-6.1-sol,
gpt-6-astra, and gpt-6-sol earned 1.0; Anthropic/Gemini adapters were tested with
fixtures only because their credentials were unavailable. No frontier ranking
or RL training claim follows from this one-email smoke test. See
`benchmark/rlvr/README.md` for commands and result conventions.
