# Frontier Legal

A legal-agent evaluation benchmark built around a Matter, *USA v. Cascade Timber Holdings, Inc.*, built by DecoverAI. It is
an email corpus with planted evidence chains, designed for training and evaluating models on
**legal evidence reasoning**: responsiveness, privilege, chronology, knowledge analysis and
joins across several documents. All companies, people and events are fictional.

> **Not ready for training.** The internal assessment ([`suggestions.md`](suggestions.md))
> scores it Q ≈ 49/100, in the band marked "blocked for training". It's sound as a demo and
> an evaluation seed, but the answers leak through headers, there are few supervised
> targets, some facts contradict each other, and there's only one matter. Read
> [Known issues](#known-issues) before you use it.

## At a glance

| | |
|---|---|
| Documents rendered | 1,486 RFC 5322 `.eml` (250 seed, 1,150 generated in batches, 86 in 7 threads from `thread_kit`) |
| Documents planned | 1,486 (`DOCUMENT_MANIFEST.csv`; thread rows have `status=thread-expansion`) |
| Time span | Nov 2021 – Dec 2023 |
| Custodians | 26 mailboxes |
| Organizations | Cascade Timber (client), Alder Point Partners (administrator), Bellhaven Advisory (broker), L&L Associates (outside counsel), GreenAcre (surveyor), Moss & Lane (auditors), IRS, consultants, buyers |
| Labels | Seed documents only: 1 review tag each, plus privileged and PII flags |
| Benchmark | 51 distinct tasks: 10 flagship, 18 atomic/retrieval/join, 6 RLVR pilots and 17 litigation skill episodes |
| Matters | 1 |

## All tasks

The catalog follows the linked task-table format in [FrontierSWE v2](https://github.com/Proximal-Labs/frontier-swe-v2).
It covers **51 distinct tasks** in this repository. The 19 litigation skill family IDs
include two aliases for existing pilots: `CTH-LIT-09` maps to `CTH-PRESERVATION-001`
and `CTH-LIT-10` maps to `CTH-CHRONOLOGY-001`; those episodes are counted once.

### Flagship investigations (10)

Agent-visible prompts are in [the flagship task pack](benchmark/tasks/flagship_prompts.jsonl).
These use the [evidence-based scoring rubric](benchmark/eval/scoring_rubric.md).

| Task ID | Task | Category | Split |
|---|---|---|---|
| CTH-AGENT-001 | [Acreage knowledge chain](benchmark/tasks/flagship_prompts.jsonl#L1) | knowledge chronology | `train` |
| CTH-AGENT-002 | [Northwest parcel reconstruction](benchmark/tasks/flagship_prompts.jsonl#L2) | transaction reconstruction | `train` |
| CTH-AGENT-003 | [Broker registration and authority](benchmark/tasks/flagship_prompts.jsonl#L3) | registration authority | `train` |
| CTH-AGENT-004 | [Post-warning program continuation](benchmark/tasks/flagship_prompts.jsonl#L4) | autonomous investigation | `test_ood` |
| CTH-AGENT-005 | [Clearwater transaction sequencing](benchmark/tasks/flagship_prompts.jsonl#L5) | temporal join | `test_ood` |
| CTH-AGENT-006 | [Privilege and work-product review](benchmark/tasks/flagship_prompts.jsonl#L6) | privilege review | `test_id` |
| CTH-AGENT-007 | [Whistleblower complaint and insider pool](benchmark/tasks/flagship_prompts.jsonl#L7) | whistleblower credibility | `test_ood` |
| CTH-AGENT-008 | [Examination and preservation timeline](benchmark/tasks/flagship_prompts.jsonl#L8) | preservation analysis | `test_id` |
| CTH-AGENT-009 | [Financial trail and exposure](benchmark/tasks/flagship_prompts.jsonl#L9) | financial reconstruction | `test_id` |
| CTH-AGENT-010 | [Matter theory memo](benchmark/tasks/flagship_prompts.jsonl#L10) | case theory memo | `test_ood` |

### Atomic, retrieval and join tasks (18)

Agent-visible prompts are in [the atomic task pack](benchmark/tasks/tier1_tier2_sample.jsonl).
These use the same evidence-based rubric; difficulty and split are recorded per prompt.

| Task ID | Task | Category | Split |
|---|---|---|---|
| CTH-T1-001 | [Responsiveness: transaction email](benchmark/tasks/tier1_tier2_sample.jsonl#L1) | responsiveness | `train` |
| CTH-T1-002 | [Responsiveness: disputed program scope](benchmark/tasks/tier1_tier2_sample.jsonl#L2) | responsiveness | `train` |
| CTH-T1-003 | [Privilege: counsel risk memo](benchmark/tasks/tier1_tier2_sample.jsonl#L3) | privilege single | `train` |
| CTH-T1-004 | [Privilege: bare forward](benchmark/tasks/tier1_tier2_sample.jsonl#L4) | privilege single | `train` |
| CTH-T1-005 | [Kovel retention contrast](benchmark/tasks/tier1_tier2_sample.jsonl#L5) | kovel contrast | `train` |
| CTH-T0-006 | [Entity and employer resolution](benchmark/tasks/tier1_tier2_sample.jsonl#L6) | entity resolution | `train` |
| CTH-T0-007 | [Event date versus document date](benchmark/tasks/tier1_tier2_sample.jsonl#L7) | date extraction | `train` |
| CTH-R-008 | [Acreage verification retrieval](benchmark/tasks/tier1_tier2_sample.jsonl#L8) | retrieval | `train` |
| CTH-R-009 | [Broker authority retrieval](benchmark/tasks/tier1_tier2_sample.jsonl#L9) | retrieval | `train` |
| CTH-T2-010 | [Registration-status contradiction](benchmark/tasks/tier1_tier2_sample.jsonl#L10) | contradiction | `train` |
| CTH-T2-011 | [Investor-description change](benchmark/tasks/tier1_tier2_sample.jsonl#L11) | contradiction | `validation` |
| CTH-T2-012 | [Parcel-scope competing explanations](benchmark/tasks/tier1_tier2_sample.jsonl#L12) | contradiction | `train` |
| CTH-T2-013 | [Broker-gap evidence join](benchmark/tasks/tier1_tier2_sample.jsonl#L13) | evidence join | `train` |
| CTH-T2-014 | [Acreage concern chronology](benchmark/tasks/tier1_tier2_sample.jsonl#L14) | chronology | `train` |
| CTH-T2-015 | [Notice and subsequent action](benchmark/tasks/tier1_tier2_sample.jsonl#L15) | knowledge | `train` |
| CTH-T1-016 | [Responsiveness versus privilege](benchmark/tasks/tier1_tier2_sample.jsonl#L16) | responsiveness | `validation` |
| CTH-T2-017 | [Abstention on examination closure](benchmark/tasks/tier1_tier2_sample.jsonl#L17) | negative control | `validation` |
| CTH-T2-018 | [Program-separation distractor control](benchmark/tasks/tier1_tier2_sample.jsonl#L18) | distractor control | `train` |

### Executable RLVR pilots (6)

These tasks have deterministic verifiers. The first four are single-turn;
preservation and chronology are multi-turn search/read/submit episodes.
See the [RLVR runner](benchmark/rlvr/README.md) and [evidence-agent interface](benchmark/rlvr/AGENT_TASKS.md).

| Task ID | Task | Category | Mode |
|---|---|---|---|
| CTH-DATE-001 | [Sent-date extraction](benchmark/rlvr/tasks/CTH-DATE-001.json) | Date extraction | Single-turn smoke test |
| CTH-AUDIT-001 | [Evidence audit (75 emails, 18 questions)](benchmark/rlvr/tasks/CTH-AUDIT-001.json) | Cross-document reasoning | Single-turn development |
| CTH-INVENTORY-001 | [Collection reconciliation (75 emails)](benchmark/rlvr/tasks/CTH-INVENTORY-001.json) | Collection inventory | Single-turn development |
| CTH-INVENTORY-002 | [Collection reconciliation (300 emails)](benchmark/rlvr/tasks/CTH-INVENTORY-002.json) | Collection inventory | Single-turn development |
| CTH-PRESERVATION-001 | [Preservation audit (CTH-LIT-09 / legal-hold)](benchmark/rlvr/preservation/CTH-PRESERVATION-001.json) | Preservation | Multi-turn development |
| CTH-CHRONOLOGY-001 | [Evidence chronology (CTH-LIT-10 / chronology)](benchmark/rlvr/chronology/CTH-CHRONOLOGY-001.json) | Chronology | Multi-turn development |

### Litigation skill episodes (17 new; 19 families with pilot aliases)

These bounded development episodes have deterministic evidence and artifact checks.
The [registry](benchmark/litigation_skills/registry.json) is authoritative for task packages,
pilot aliases and dependencies. See [suite usage](benchmark/litigation_skills/README.md)
and [coverage and review status](benchmark/litigation_skills/COVERAGE.md).
They evaluate supplied-policy exercises within one matter; the legacy preservation
and chronology pilots still need separate independent oracle review.

| Task ID | Task | Skill family |
|---|---|---|
| CTH-LIT-01 | [Matter-scoped setup with unresolved operator profile](benchmark/litigation_skills/tasks/CTH-LIT-01/task.json) | `cold-start-interview` |
| CTH-LIT-02 | [Narrow board-reporting correction with preserved unknowns](benchmark/litigation_skills/tasks/CTH-LIT-02/task.json) | `customize` |
| CTH-LIT-03 | [Historical intake with conflicted readiness and preservation state](benchmark/litigation_skills/tasks/CTH-LIT-03/task.json) | `matter-intake` |
| CTH-LIT-04 | [Single-matter sandbox organization preserving intake history](benchmark/litigation_skills/tasks/CTH-LIT-04/task.json) | `matter-workspace` |
| CTH-LIT-05 | [Actual purchaser refund demand with executed-version and trigger conflicts](benchmark/litigation_skills/tasks/CTH-LIT-05/task.json) | `demand-received` |
| CTH-LIT-06 | [Third-party preservation demand readiness](benchmark/litigation_skills/tasks/CTH-LIT-06/task.json) | `demand-intake` |
| CTH-LIT-07 | [Preservation drafting gate and safe handoff](benchmark/litigation_skills/tasks/CTH-LIT-07/task.json) | `demand-draft` |
| CTH-LIT-08 | [IRS instrument version, deadline and production triage](benchmark/litigation_skills/tasks/CTH-LIT-08/task.json) | `subpoena-triage` |
| CTH-LIT-11 | [Provisional issue chart with contrary proof](benchmark/litigation_skills/tasks/CTH-LIT-11/task.json) | `claim-chart` |
| CTH-LIT-12 | [Tom Reyes source-founded examination outline](benchmark/litigation_skills/tasks/CTH-LIT-12/task.json) | `deposition-prep` |
| CTH-LIT-13 | [Privilege family and consultant-purpose review](benchmark/litigation_skills/tasks/CTH-LIT-13/task.json) | `privilege-log-review` |
| CTH-LIT-14 | [Defense factual section with explicit concessions](benchmark/litigation_skills/tasks/CTH-LIT-14/task.json) | `brief-section-drafter` |
| CTH-LIT-15 | [Append a supported discovery and remediation update](benchmark/litigation_skills/tasks/CTH-LIT-15/task.json) | `matter-update` |
| CTH-LIT-16 | [Read-only counsel briefing with stale snapshot and current evidence](benchmark/litigation_skills/tasks/CTH-LIT-16/task.json) | `matter-briefing` |
| CTH-LIT-17 | [One-matter portfolio rollup with unknowns and qualified anomalies](benchmark/litigation_skills/tasks/CTH-LIT-17/task.json) | `portfolio-status` |
| CTH-LIT-18 | [Review-only outside-counsel status request and run summary](benchmark/litigation_skills/tasks/CTH-LIT-18/task.json) | `oc-status` |
| CTH-LIT-19 | [Closure-readiness handoff without unsupported archive or hold release](benchmark/litigation_skills/tasks/CTH-LIT-19/task.json) | `matter-close` |

`CTH-LIT-19` tests closure readiness with a missing trigger; its inclusion does not imply that closure is authorized.

## Model leaderboard

Completed October 9, 2026: **10 chronology episodes per model, 50 episodes total**, using
only Cascade Timber. Scores are mean deterministic verifier rewards, expressed as
percentages. Each episode starts with fresh context and allows up to 300 actions;
requested reasoning effort is low, with 16,384 output tokens per request and 131,072
output tokens per episode.

| Rank | Model | Episodes | Mean score | Sample SD (percentage points) | Worst–best score | Total cost (USD) |
|---|---|---|---|---|---|---|
| 1 | GPT-6 Astra | 10 | **83.99%** | 1.30 | 81.46–85.80% | $6.51 |
| 2 | Grok 4.7 | 10 | **64.21%** | 9.56 | 49.51–77.40% | $21.52 |
| 3 | Claude Opus 5.5 | 10 | **56.03%** | 29.92 | 0.00–79.69% | $128.91 |
| 4 | GLM 5.3 Prime | 10 | **38.60%** | 26.74 | 0.00–58.55% | $11.18 |
| 5 | Gemini 3.1 Pro Preview | 10 | **0.00%** | 0.00 | 0.00–0.00% | $0.60 |

All **50 episodes were scored**, with **0 full passes** and **3,014 transitions verified
by replay**. Total recorded provider cost was **$168.72**, including work performed
before four interrupted episodes were resumed from their saved conversations with
the original cumulative budgets. The other 46 completed episodes were preserved.
The pinned source and action-limit change are recorded in the
[result summary](benchmark/rlvr/chronology/results/chronology-10x5-2026-10-09.json);
[individual episode scores](benchmark/rlvr/chronology/results/chronology-10x5-2026-10-09-episodes.csv)
are also available.

These development results measure performance on one task in one synthetic matter.
The chronology oracle still needs independent equivalent-evidence review, and strict
action formatting and accepted-evidence matching affect scores. Two Claude episodes
reached the action limit with zero scores; Gemini read no source documents in its ten
episodes. Sample SD describes variation across episodes and is not a confidence
interval. Equal requested reasoning effort does not imply equal compute across providers.

## Why the corpus is interesting

- **You have to join documents.** The corpus is built so that no single document settles an
  issue. Take the question of whether an acreage problem was known before the applications
  were filed: answering it takes option dates, application dates, ledger entries and one
  employee's role, all from different documents.
- **The past is never written from hindsight.** Each batch is scanned for terms its authors
  couldn't have known yet, such as the subpoena, counsel's engagement or the pause. The
  results are in `CONTINUITY_BATCH0N.md`. A model can't pick up the answer from a document
  that was written "too early".
- **Doctrines come as contrast pairs.** Privilege, work product, Kovel consultants, bare
  forwards and responsiveness each appear as small chains: a clear positive, a clear negative
  and a genuinely ambiguous case.
- **Some readings are left open on purpose.** Several issues are `[DISPUTED]` by design,
  for example EMAIL-117 (a clerical error or a cover story?). The right output is to state the
  uncertainty, not to force a label.
- **The email looks like real collected mail.** Quoted history nests one level per reply,
  quoting follows each sender's mail client (Outlook or Gmail), each organization has its own
  signature, time zones follow daylight saving, and about a third of the corpus is routine
  noise, decoys and near-duplicates.
- **Long threads, not just pairs.** The first four expanded threads (THR-001–004) run 12–14 messages
  each, with forks, reply-alls that add or drop people, side forwards and unanswered
  questions. With the density extensions, the longest coherent reply chain is 14 deep.
- **Denser evidence chains.** THR-005–007 add 32 emails and eight supporting text records
  for held Q4 packets, source-credit allocations to buyers, and a dated remediation pilot.
  See [the expansion register](documentation/DENSITY_EXPANSION.md) for new fictional
  facts, counterevidence and questions deliberately left unresolved.
- **Real contracts, versioned.** KW-01/02 option agreements go from drafts (DOCX) to wet-signed
  scans (PDF, no text layer). The Bellhaven credit purchase agreements and the pre-broker
  template also carry their version history. Each email carries the version that existed on
  its date, and the copies in `data/contracts/` are byte-identical to the attachments, so
  hash deduplication links them.
- **Signature logos.** Outlook-style orgs (Cascade Timber, L&L, Moss & Lane, Whitaker) carry
  an inline logo in an HTML part, and quoted signatures keep theirs, so long threads pile up
  `image001.png`, `image002.png` and so on. Inline logos aren't counted as attachments. The
  seed keeps its original structure.

## Layout

```text
data/emails/                          # corpus (tracked; new files need `git add -f`, see .gitignore)
  Custodians/<Name>/EMAIL-NNN_<subject>.eml
  Loadfile_Cascade_Timber.{csv,dat}   # load file: all 1,486; newest 32 have blank review labels
  README.md                           # corpus build notes (v3 realism pass)
data/emails/Exhibits/                 # 38 standalone exhibit PDFs + ../Exhibit_Manifest.csv (not attached to emails)
definitions/                          # labeling protocols: Responsiveness, ACP, Work Product, Subpoena (summons)
logs/                                 # batch ledgers, continuity reports, thread logs, demo privilege log (untracked)
benchmark/                            # tasks, hidden gold, splits, schema, rubric, GOLD_LABELS.csv
documentation/                        # AUTHORING ONLY:
  CASE_BIBLE.md  EVIDENCE_ARCS.md     #   ground-truth world model; arcs A–J, planned joins and open questions
  DOCUMENT_MANIFEST.csv               #   1,454-row plan with arc, event and evidentiary role
  CONTRADICTIONS_RESOLVED.md          #   decisions and edits for the four known contradictions
  MATTER_AGENT_TASKS.md  suggestions.md  Cascade_Timber_EML_Dataset_Plan.md
output/dataset_inconsistency_report.md  # document-consistency review + resolution log
data/contracts/                       # standalone contract collection (every version) + INDEX.csv → carrying emails
tools/exhibit_kit/                    # rebuilds the standalone exhibits from one spec
tools/doc_kit/                        # attachment builder: versioned library docs → PDF/DOCX/XLSX, scans, apply to emails, publish
  library/  plans/                    # document content + version history; email→version attach plans (ATT-00N)
tools/thread_kit/                     # thread expander: context, validate, render, rollback, scan, logos
  rules.json                          # knowledge cutoffs, participant windows, logo orgs (AUTHORING ONLY)
  logos/                              # org logos (full size + signature size)
```

## Supervision available today

| Source | Coverage | Form |
|---|---|---|
| `benchmark/hidden_gold/seed_header_labels.csv` and the load file's `TAG`/`PRIVILEGED` columns | Seed EMAIL-001–250 | One mixed tag per document, such as `Not Responsive`, `Routine`, `Privileged Legal Advice`, `Knowledge/Scienter` or `Red Flag`. This isn't multi-label, and privileged documents carry no responsiveness label. |
| `documentation/DOCUMENT_MANIFEST.csv` | All 1,454 rows | `arc`, `event_id` and `intended_evidentiary_role`. These are authoring intent, not reviewed gold. |
| `benchmark/hidden_gold/` | 28 tasks, all answerable from seed documents | Required, counter, distractor and context evidence IDs; gold facts and inferences; `must_include`, `must_not_claim` and `must_qualify` lists; unknowns. The schema is in `schemas/task.schema.json`. |
| `CASE_BIBLE.md` / `EVIDENCE_ARCS.md` | The whole matter | Prose ground truth with `[ESTABLISHED]`, `[PROPOSED]`, `[DISPUTED]` and `[INFERENCE]` tags. This is the fastest source for writing new (task, evidence, target) examples. |

The emails carry no label headers: the `X-Decover-*` headers were stripped from the original 1,454 files and are absent from the 32 additions. DocIDs
live in the filenames (`EMAIL-NNN_<subject>.eml`) and the load file. Document-level labels for the whole
original corpus are in `benchmark/GOLD_LABELS.csv` (machine-drafted, expert review pending).
The newest 32 documents are unreviewed and not included in those labels or existing
hash-pinned benchmark snapshots; their load-file label columns are blank.

## Splits and leakage

- **Don't split at random.** Documents in a thread or evidence chain answer each other.
  `benchmark/splits/evidence_packages_sample.csv` defines packages by family
  that must stay together, currently 17 of them.
- Task splits are `train`, `test_id` (a skill seen in training, on an unseen family) and
  `test_ood` (held-out flagship compositions). The mapping is in the
  [benchmark README](benchmark/README.md).
- **All of it is one matter.** A held-out split measures generalization within this matter,
  not transfer to a new one. Building a second, independent matter for evaluation is still
  open.
- **Keep the model away from:** the load file's `TAG` and `PRIVILEGED` columns (withhold them; the emails themselves no longer
  carry label headers),
  `CASE_BIBLE.md`, `EVIDENCE_ARCS.md`, the manifest's `arc`/`event_id`/role columns, the
  ledgers and `hidden_gold/`. The model may see the EML bodies, the Definitions files and
  ordinary load-file metadata.

## Known issues

These come from `suggestions.md` and from `output/dataset_inconsistency_report.md`. The benchmark tasks
don't depend on them.

- **Resolved (2026-09-28):** the § 7602 summons/subpoena framing, the two Kevin Tran identities,
  the two Cascade addresses and the deadline chain. See `documentation/CONTRADICTIONS_RESOLVED.md`.
- **Resolved (2026-09-29):** the standalone exhibits in `data/emails/Exhibits/` now agree with the
  executed contracts and seed emails (Clearwater option dates and installments, buyer lot amounts,
  OR/WA filing-receipt dates, status footers, placeholder numbers). Rebuilt by
  `tools/exhibit_kit/build_exhibits.py`; the resolution log is at the end of the inconsistency report.
- **Still open, by design or header-locked:**
  - The seed parcel CSV and GreenAcre survey (EMAIL-037/039) use NW-1042…NW-1093 and different
    acreage pairs from the NW-01…NW-08 table in `CASE_BIBLE.md` §2. No crosswalk exists; don't
    merge them by position.
  - "Batch N" and "buyer lot N" in generated email subjects are templated labels that don't track
    the exhibits or the executed agreements. Join buyer records on buyer, date and amount, not on
    batch or lot number.
  - EMAIL-793 (9/8/22) has a subject that cites the 9/15 notice; four generated "extension chain"
    notes predate the summons. Both are Subject-header anachronisms, kept because headers are locked.
- **The privilege log is out of step with the corpus.** Most of its 1,009 rows name people who
  don't appear in the corpus.
- **Workbook search queries and chronology are stale.** They cover only EMAIL-001–030.
- **Emails are short and convenient.** Replies average about 32 new words, and some
  admissions are too tidy (e.g. "keep this between us"). The `thread_kit` threads push back
  on this: they have longer replies, a validator that flags tidy admissions, and hedged
  readings that stay open.
- **Generation isn't reproducible.** No generator or model versions or file hashes are
  recorded.

## Using it

For the single-turn, multi-model RLVR tasks (date extraction, evidence audit, and
collection reconciliation), see
[`benchmark/rlvr/README.md`](benchmark/rlvr/README.md). It includes an offline
self-test, OpenAI/Anthropic/Gemini/OpenRouter adapters, deterministic scoring, and saved
JSON run records.

1. Parse the `.eml` files with any MIME library. Use `DATESENT`, or the `Date:` header, for
   chronology. The DocID order follows collection order, not time.
2. Withhold the load file's `TAG`/`PRIVILEGED` columns and `benchmark/GOLD_LABELS.csv` from model inputs. The
   `.eml` files are already clean: there are no `X-Decover-*` headers.
3. Build examples by evidence package, not by document, and hold out whole packages.
4. For any label beyond the seed tags, generate targets from `CASE_BIBLE.md` and the
   benchmark gold, and have an expert review them. Treat `[PROPOSED]` facts as unknowns
   until the documents that support them exist.
5. Score with `benchmark/eval/scoring_rubric.md`. It covers evidence recall,
   join correctness, counter-evidence, restraint on uncertain points, citation accuracy and
   stopping efficiency.

## Status and roadmap

- All 1,400 planned documents are rendered. Thread expansion has added 54 more: THR-001
  Clearwater scouting (EMAIL-1401–1412), THR-002 Bellhaven registration (1421–1434), THR-003
  Q4 push-through (1441–1454) and THR-004 the $2.4M estimate (1461–1474). Their specs and
  reports are in `Logs/threads/`.
- The authorized density pass adds THR-005–007 (EMAIL-1475–1506), bringing the total to
  1,486 messages. All original emails remain byte-identical. Story specs, a metadata
  synchronization/checking script and validation results are in
  `tools/thread_kit/expansions/`; [the authoring register](documentation/DENSITY_EXPANSION.md)
  explains the additions and their limits.
- The top fixes for training readiness, from `suggestions.md`:
  1. Move labels out of the headers.
  2. Write 150–200 examples reviewed by experts, with multi-label responsiveness, privilege
     basis, chronology and grounded QA, including examples where the right answer is to
     abstain.
  3. Resolve the contradictions listed above.
  4. Fix the summons/subpoena mislabel.
  5. Add a second matter for evaluation, plus hashes.
