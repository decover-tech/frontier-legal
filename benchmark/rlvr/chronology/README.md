# Task 2 — evidence chronology

`CTH-CHRONOLOGY-001` implements **find relevant evidence → reconstruct what
happened → resolve conflicting evidence → apply a supplied rule → produce a
supported answer** using only Cascade Timber email evidence.

It pins 1,486 existing emails by SHA-256 and asks the agent to reconstruct 14
milestones, put them in order, and resolve five disputed inferences. Task 1 is
the [preservation audit](../preservation/README.md). These are two development
episodes, not 19 completed skill families or new matter datasets.

## What makes the task demanding

| Evidence arc | Required work | Common error the verifier catches |
|---|---|---|
| Broker registration | Reconcile the pending-renewal report, claimed renewal, verification gap and later restatement | Treating repetition as independent proof; inventing a precise issuance date |
| Q4 held-file queue | Reconstruct a held batch, conditional release route, continuing hold and later acreage tie-out | Substituting a report date for the event date; treating permission or a tie-out as transmission |
| Remediation pilot | Separate scheduling, first pass, second review, retrospective report and auditor assessment | Using the planned date as completed execution; treating completed review as closure of acreage exceptions |
| Earlier checkpoint | Reassess the pilot using only evidence available by August 21 | Using September completion as proof at the earlier checkpoint |
| Historical controls | Determine what the later pilot establishes about earlier quarterly work | Backdating remediation as proof that historical controls operated |

The model receives milestone descriptions in alphabetical order, the five
questions, the six supplied rules, output schema and tool contract. It must
retrieve its own evidence. The brief supplies no answer dates, selected document
IDs, source paths or oracle. Milestone descriptions deliberately define the
requested events; this version tests reconstruction, not open-ended issue spotting.

## Environment and answer contract

```python
from tools.chronology_rlvr.environment import ChronologyEnvironment

env = ChronologyEnvironment()
observation = env.reset()
result = env.step({"tool": "search", "query": "registration renewal"})
# Read discovered document IDs with read; paginate using next_offset.
# Finish with submit(answer={"events": ..., "order": ..., "resolutions": ...}).
```

`search` performs case-insensitive AND matching of literal words or quoted
phrases over headers and decoded bodies. Results sort by document ID, with eight
hits per page. `read` returns up to 6,000 characters. The episode budget is 120
actions and 300,000 observation characters, including the initial brief. There
is no intermediate grading feedback. Invalid actions consume a step and allow
recovery. `reset` clears the episode's reading history.

Each event contains event-date bounds, date precision, report date, actor email,
event nature and supporting quotations. Each resolution contains a conclusion,
an established event date or null, applied rule IDs, supporting quotations and
challenged quotations with rejection reasons. The `order` array lists event IDs.

The supplied policy distinguishes statements, instructions, conditional
authorizations, completed actions, status reports and assessments. Its explicit
date convention resolves relative phrases such as past-tense "this week."
Cutoffs are inclusive and timezone-aware; calendar dates use sender-local time.
The main cutoff is September 8, 2023; the earlier pilot checkpoint is August 21.

Citations must contain decision-bearing clauses from text actually returned by
`read`; search snippets alone earn no evidence credit. Equivalent quoted copies
are enumerated from the pinned corpus and checked for availability by the cutoff.
Verbatim quotation matching normalizes case and whitespace. A single outer
Markdown JSON fence is accepted. Duplicate JSON keys, unknown IDs and extra
fields are rejected. Missing items score zero.

## Verifiable reward

No model judge is used. The evaluator checks structured facts and cited clauses
against a hash-pinned development oracle.

| Component | Episode weight | Calculation |
|---|---:|---|
| Milestones | 55% | Mean supported event score over all 14 milestones |
| Ordering | 15% | Mean over 91 supported precedence constraints |
| Disputed inferences | 30% | Mean supported resolution score over all five questions |

An event earns `support_coverage × (0.45 × timing + 0.15 × report_date +
0.15 × actor + 0.25 × evidence_precision)`. Timing is the fraction of correct
start date, end date and precision. Incorrect event nature gates the event to
zero: a correctly dated claim cannot earn credit as an established completed act.

A resolution earns `support_coverage × (0.20 × event_date + 0.20 × rule_F1 +
0.30 × evidence_precision + 0.30 × challenge_coverage × challenge_precision)`.
An incorrect conclusion gates the resolution to zero. Adding unrelated citations
or every rule reduces precision rather than guaranteeing full credit.

Each correctly ordered pair earns the lower of its two event scores. Missing,
unread or unsupported events therefore cannot earn free ordering credit. Full
success requires every event, resolution and precedence constraint to receive
full credit. Report graded reward and complete success separately, along with
steps, tokens, latency and cost. Provider failures are unscored, while exhausted
task budgets are scored failures.

## Run and validate

From the repository root, using Python 3.10+:

```bash
python3 -m unittest discover -s tools/chronology_rlvr/tests -v
python3 -m tools.chronology_rlvr.run --dry-run
python3 -m tools.chronology_rlvr.run --self-test
```

Reproduce the five-model pilot's 149 recorded transitions and final scores
without credentials or provider calls:

```bash
python3 -m tools.chronology_rlvr.replay benchmark/rlvr/chronology/results/frontier-five-2026-10-08-trajectories.json
```

The self-test searches for, reads and submits an evaluator-authored answer. Its
1.0 reward is a verifier control, not a model score. The control takes 39 actions;
an empty submission earns zero. The 30 tests cover event/report date confusion,
relative date precision, same-day ordering, attribution, evidence cutoffs,
unsupported conclusions, fabricated/unread/stuffed citations, limits, source
integrity and mocked provider handling. See [validation.json](validation.json).

For a live episode, provide credentials through the environment or the explicit
`--openrouter-key-file` argument:

```bash
python3 -m tools.chronology_rlvr.run \
  --model openrouter:YOUR_MODEL_ID \
  --reasoning-effort low \
  --max-output-tokens 16384 \
  --episode-output-tokens 131072
```

The runner uses the existing OpenRouter adapter and normal text JSON actions;
native function calling is not required. Every response, tool result, token
report, cost and relevant code hash is saved under a new ignored
`output/rlvr/chronology/<run-id>` directory. The default per-request socket
inactivity and wall deadlines are 180 and 300 seconds; the hard deadline requires
POSIX. Missing usage ends an episode as an unscored request error. No live model
calls were made while building or validating this task.

## Assets and review status

- [Task manifest](CTH-CHRONOLOGY-001.json), [policy](policy.md) and [output schema](output_schema.json).
- [Environment](../../../tools/chronology_rlvr/environment.py), [runner](../../../tools/chronology_rlvr/run.py) and [tests](../../../tools/chronology_rlvr/tests/test_chronology.py).
- [Evaluator review](../../hidden_gold/chronology/REVIEW.md), containing answers and source references.

This is a development task. A first [five-model pilot](FRONTIER_FIVE_2026-10-08_RUN2.md)
is complete; independent oracle review, alternative-citation review and broader
frontier-model calibration remain pending. The author-built oracle
requires specific decision-bearing clauses; independent review may identify
additional acceptable evidence. A perfect control does not show that a model can
solve the task, and added complexity does not establish model separation.

The oracle and authoring script are visible in this repository, so this is not a
secret held-out evaluation set. For training, expose only the serialized
observation/action interface and isolate evaluator assets. Split related email
threads and near-duplicates together. The trusted Python environment is not an
OS sandbox and must not share its filesystem with an evaluated agent.

The evidence scope is original email headers and decoded plain-text bodies.
Referenced attachments and authoring documents are not additional evidence. The
rules are benchmark conventions and do not decide legal liability or actual
regulatory issuance. Source emails and the existing inventory and preservation
runners were not changed to build Task 2.
