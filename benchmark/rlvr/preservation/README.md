# CTH-PRESERVATION-001 — preservation audit with evidence retrieval

A new, isolated development task implementing:

**Find relevant evidence → reconstruct what happened → resolve conflicting
evidence → apply a supplied rule → produce a supported answer.**

The task pins **1,486 existing Cascade Timber emails** by SHA-256. It adds no new
matter events or source evidence. The only authored material is a clearly labeled
benchmark policy, output contract and evaluator oracle. The existing inventory
runner, tasks and scores are unchanged. The provider adapter adds explicit
reasoning-effort controls and output-budget diagnostics for the new agent runners.

## What the agent does

The agent initially receives the policy, six checkpoint questions, tool contract
and output schema. It receives no preselected evidence packet, source filenames,
load-file labels, authoring notes or answer key. It must search and read the
collection through two bounded tools before submitting an audit.

| Assessment | Question | Checkpoint |
|---|---|---|
| C01 | Identify technical safeguards that preceded the formal hold, preserving their actual scope | June 13, 2023 |
| C02 | Determine whether Nina Alvarez's export completion was documented at the earlier checkpoint | July 7, 2023 |
| C03 | Reassess the export and access restrictions using the later available record | July 26, 2023 |
| C04 | Distinguish an Alder individual's acknowledgment from company-wide implementation | June 14, 2023 |
| C05 | Determine whether Cascade's controls establish preservation on Bellhaven's own systems | November 10, 2023 |
| C06 | Test the inference that account disablement proves mailbox deletion | July 26, 2023 |

Cutoffs are inclusive, timezone-aware instants in the task manifest. Event time
and the time a source became available are separate. A message written later may
report an earlier event; it cannot retroactively resolve an earlier documentation
gap. Generic attestations, unfinished exports, operational handoffs and unrelated
completed batches provide misleading alternatives in the original collection.

## Files

- [Task manifest](CTH-PRESERVATION-001.json): checkpoints, limits and pinned sources.
- [Supplied policy](policy.md): seven explicit benchmark rules; not governing law.
- [Output schema](output_schema.json): supported assessment structure.
- [Validation record](validation.json): task/code hashes, 21 tests and the 25-step oracle control.
- [Environment](../../../tools/preservation_rlvr/environment.py): search/read/submit and deterministic reward.
- [Runner](../../../tools/preservation_rlvr/run.py): separate multi-turn model loop.
- [Authoring review and oracle](../../hidden_gold/preservation/REVIEW.md): evaluator-only development material, containing answers.

## Episode contract

```python
from tools.preservation_rlvr.environment import PreservationEnvironment

env = PreservationEnvironment()
observation = env.reset()
# Send only observation to the model.
result = env.step({"tool": "search", "query": '"Nina Alvarez" export', "offset": 0})
# Read discovered document IDs; paginate with next_offset.
# Continue until the agent sends {"tool":"submit","answer":{"assessments": ...}}.
```

Search is deterministic, case-insensitive AND matching of literal words or quoted
phrases over public headers and decoded bodies. Results sort by document ID, with
eight hits per page. Reads return 6,000 characters per page. The episode allows
80 actions and 180,000 returned observation characters, including the initial
brief. Invalid actions consume a step and can be corrected; there is no
intermediate answer-checking tool or reward feedback.

Each final assessment contains a status, scope, event date or date bound,
confirmation-availability date, responsible person, next action, rule IDs,
supporting quotations and explicitly resolved challenges. A citation must quote
a passage actually returned by `read`. Reading adjacent pages permits a quote
spanning the page boundary. Search snippets alone do not count as reading evidence.

A single outer JSON Markdown fence is accepted as transport decoration for this
new task. Duplicate JSON keys, unknown assessment IDs, fabricated citations and
extra assessment fields are rejected. This does not change the original inventory
benchmark's strict output contract.

## Deterministic reward

There is no model judge. An author-built, hash-pinned oracle specifies the expected
facts, rule selections and accepted evidence groups. Equivalent quoted copies
are enumerated from the pinned collection and checked against source anchors.
Message dates constrain citation availability. Verbatim decision-bearing clauses
must appear in the cited quotation; case and whitespace normalization are allowed.

Each assessment has five component scores:

| Component | Weight | Calculation |
|---|---:|---|
| Finding | 25% | Exact status, scope, responsible person and action: fraction correct |
| Chronology | 20% | Event date/bound and earliest qualifying confirmation date: fraction correct |
| Evidence precision | 25% | Valid supporting passages / submitted supporting passages |
| Conflict resolution | 20% | Required challenge coverage × valid challenge precision |
| Rule selection | 10% | F1 against required policy rule IDs |

The weighted sum is multiplied by required support-group coverage. An incorrect
status gates the entire assessment to zero. Missing or malformed assessments
score zero. An answer with no read supporting evidence scores zero even if its
other fields match the oracle. Unrelated citation additions lower precision;
submissions cannot earn full credit by citing every document or every rule.

The episode reward is the mean of six assessment rewards. Full success requires
all six to receive 1.0. Report both graded reward and complete-task success,
alongside tool steps, tokens, latency and cost. Tool/episode budget exhaustion is
a scored failure; provider errors are unscored and must not be averaged as zeros.

## Run locally

From the repository root, with Python 3.10+:

```bash
python3 -m unittest discover -s tools/preservation_rlvr/tests -v
python3 -m tools.preservation_rlvr.run --dry-run
python3 -m tools.preservation_rlvr.run --self-test
```

`--self-test` performs a scripted search/read/submit episode using evaluator-only
oracle targets. Its perfect reward is a verifier control, **not a model result**.
The initial end-to-end control completed in 25 actions. The empty control scored
zero, and 21 tests covered temporal leakage, conflicting records, precise event
bounds, unsupported scope, fabricated/unread citations, citation stuffing, tool
limits, hash integrity and provider-error handling.

For a live model episode, supply the credential through the environment or an
explicit credential-file argument:

```bash
python3 -m tools.preservation_rlvr.run \
  --model openrouter:YOUR_MODEL_ID \
  --reasoning-effort low \
  --max-output-tokens 8192 \
  --episode-output-tokens 98304
```

The runner sends JSON actions through the model's normal text interface; it does
not require provider-specific function calling. It uses the existing OpenRouter
adapter with fallback disabled and explicit effort. It saves every raw response,
usage record and tool result under a new ignored `output/rlvr/preservation/<run-id>`
directory. API keys are never placed in observations or trace files. Per-request
socket inactivity and wall deadlines default to 180 and 300 seconds; the hard
deadline currently requires POSIX. The episode output-token budget includes
provider-reported reasoning tokens. Unknown token usage prevents reliable budget
accounting and ends the episode as an unscored request error.

## Limits and review status

This is one development episode, not a held-out benchmark or a claim that frontier
models score lower on it. No live model calls or training runs were made when
building this task. Difficulty must be calibrated with the same policy, tools,
limits and verifier across models.

The oracle has been checked against source passages by its author but still needs
independent review, particularly for alternative acceptable citations. The oracle
is visible in this repository, so it is not secret evaluation data. A future
training deployment must isolate evaluator assets and split related threads and
near-duplicates together. The environment is trusted trainer code, not an OS
sandbox: expose only its serialized observation/action interface to agents.

Only email headers and decoded plain-text bodies are in scope. Referenced
attachments, manifests, portals and commercial file handoffs are not treated as
unseen proof. Those exclusions are explicit in the task policy. The supplied rules
grade documentation and reasoning; they do not decide legal liability or sanctions.
