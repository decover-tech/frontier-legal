# Cascade Timber: Synthetic Legal-Investigation Corpus

A synthetic eDiscovery matter, *USA v. Cascade Timber Holdings, Inc.*, built by DecoverAI. It is
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
| Documents rendered | 1,454 RFC 5322 `.eml` (250 seed, 1,150 generated in batches, 54 in 4 long threads from `thread_kit`) |
| Documents planned | 1,454 (`DOCUMENT_MANIFEST.csv`; thread rows have `status=thread-expansion`) |
| Time span | Nov 2021 – Dec 2023 |
| Custodians | 26 mailboxes |
| Organizations | Cascade Timber (client), Alder Point Partners (administrator), Bellhaven Advisory (broker), L&L Associates (outside counsel), GreenAcre (surveyor), Moss & Lane (auditors), IRS, consultants, buyers |
| Labels | Seed documents only: 1 review tag each, plus privileged and PII flags |
| Benchmark | 28 tasks, 10 flagship and 18 atomic, with separate hidden gold |
| Matters | 1 |

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
- **Long threads, not just pairs.** Four expanded threads (THR-001–004) run 12–14 messages
  each, with forks, reply-alls that add or drop people, side forwards and unanswered
  questions. The longest reply chain is 12 deep.
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
  Loadfile_Cascade_Timber.{csv,dat}   # load file: all 1,454 (DOCID, dates, parties, TAG, PRIVILEGED, CONTAINS_PII, …)
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

The emails carry no label headers: the `X-Decover-*` headers were stripped from all 1,454 files. DocIDs
live in the filenames (`EMAIL-NNN_<subject>.eml`) and the load file. Document-level labels for the whole
corpus are in `benchmark/GOLD_LABELS.csv` (machine-drafted, expert review pending).

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
- The top fixes for training readiness, from `suggestions.md`:
  1. Move labels out of the headers.
  2. Write 150–200 examples reviewed by experts, with multi-label responsiveness, privilege
     basis, chronology and grounded QA, including examples where the right answer is to
     abstain.
  3. Resolve the contradictions listed above.
  4. Fix the summons/subpoena mislabel.
  5. Add a second matter for evaluation, plus hashes.
