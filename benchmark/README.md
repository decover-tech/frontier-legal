# Cascade Timber Agent Benchmark — v0.1 Task Pack

Source: `CASE_BIBLE.md` rev.3, `EVIDENCE_ARCS.md` rev.2, `MATTER_AGENT_TASKS.md`, train/test plan (`cascade_timber_agent_task_train_test_plan.md`).
Corpus status at build time: 750 EML present (250 seed EMAIL-001–250 + 500 BATCH01–05). Manifest plans 1,400 total. All v0.1 tasks are answerable from seed docs; PROPOSED-only records are treated as unknowns / follow-ups, not gold.

## What this pack is

Benchmark for legal-investigation agents, not story memorization. Rewards:
finding required evidence without handed IDs, counter-search, temporal joins,
fact-vs-inference discipline, restraint on unresolved issues, proposition-level citation, intelligent stopping.

## Layout

```text
cascade_agent_benchmark/
  README.md                        # this file
  tasks/
    flagship_prompts.jsonl         # 10 agent-visible prompts (no IDs, no answers)
    tier1_tier2_sample.jsonl       # 18 atomic / retrieval / join tasks (agent-visible)
  hidden_gold/
    flagship_gold.jsonl            # scoring gold for flagships (DO NOT expose to agent)
    tier1_tier2_gold.jsonl         # gold for atomic tasks (DO NOT expose)
  splits/
    evidence_packages_sample.csv   # family-aware package IDs for seed key families
  schemas/
    task.schema.json               # minimal JSON schema for task + gold records
  eval/
    scoring_rubric.md              # per-task rubrics + global metrics
```

## Split mapping (per train/test plan §13–14)

| Task | Arc | Split | Why |
|---|---|---|---|
| CTH-AGENT-001 acreage knowledge | A | train (skill) | core chronology primitive |
| CTH-AGENT-002 parcel reconstruction | A/B | train | transaction reconstruction |
| CTH-AGENT-003 broker authority | D | train | registration-placement join method |
| CTH-AGENT-004 post-warning continuation | E | **test-ood** | flagship holdout: warnings+governance+continuation+waiver |
| CTH-AGENT-005 Clearwater temporal join | J | **test-ood** | flagship holdout: option+app+ledger+Nina role |
| CTH-AGENT-006 privilege review | H/E + doctrine | test-id | seen skill, unseen family |
| CTH-AGENT-007 whistleblower | G | **test-ood** | flagship holdout: pool restraint |
| CTH-AGENT-008 preservation | H | test-id | seen skill, unseen sub-episode |
| CTH-AGENT-009 financial reconstruction | B/F | test-id | unseen parcel/money family |
| CTH-AGENT-010 theory memo | cross-arc | **test-ood** | compositional synthesis |

Authoring gold (CASE_BIBLE, EVIDENCE_ARCS, manifests with arc/answer columns, hidden_gold/) must never be agent-visible. Agent sees: corpus EML + subpoena/definitions + ordinary load-file metadata only. Strip `X-Decover-*` headers before eval.

## Agent output contract (flagships)

For each flagship, produce:
1. Findings with proposition-level citations (`EMAIL-XXX`).
2. `SUPPORTED / REASONABLE INFERENCE / DISPUTED / UNRESOLVED / UNSUPPORTED` label per material conclusion.
3. Supporting AND contrary evidence sections (counter-search required).
4. Unknowns + next 3 investigative steps ranked by information gain.
5. Key witnesses / documents to read first where asked.

## Scoring snapshot

Per-task 100 pts (see `eval/scoring_rubric.md`): required-evidence recall, sequencing/join correctness, counter-evidence, uncertainty restraint, citation correctness, planning/stopping efficiency. Global metrics: responsiveness/privilege P/R/F1, required/counter recall@k, distractor rate, gold-fact coverage, unsupported-inference rate, unknown-recognition rate.

## Known limits (v0.1)

- Corpus is mid-expansion (750/1,400). Tasks avoid requiring PROPOSED-only records.
- The Tran contact, Cascade address, deadline chain and summons/subpoena contradictions were resolved in the data (see `documentation/CONTRADICTIONS_RESOLVED.md`). CTH-AGENT-008 gold now carries the reconciled deadline chain. What's left is documented noise: Tran's `-0400` Date headers, 7 internal notes addressed to Tran, and 4 extension notes dated before the subpoena.
- 117 stays `Not Responsive` per seed tag (disputed); tasks test handling it as disputed, not re-labeling it.
- Work-product default trigger stays 2/24/23 (L&L engagement); 020 (2/21 assessment) is flagged as possible-earlier-trigger edge case.
