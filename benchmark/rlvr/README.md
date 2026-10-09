# Cascade Timber RLVR pilot

Four single-turn development tasks, all restricted to original Cascade Timber
emails, with deterministic rewards and a multi-provider single-turn runner.
Use **CTH-INVENTORY-002** for difficulty calibration; the original date task
is only an infrastructure smoke test. No training run or held-out ranking is claimed.

| Task | Evidence | Scored questions | Purpose |
|---|---:|---:|---|
| CTH-DATE-001 | 1 email | 1 | Sent-date smoke test |
| CTH-AUDIT-001 | 75 emails | 18 | Cross-document factual reasoning and citations |
| CTH-INVENTORY-001 | 75 emails | 12 | Collection reconciliation calibration |
| CTH-INVENTORY-002 | 300 emails | 12 | Larger collection reconciliation challenge |

Two additional [evidence-agent tasks](AGENT_TASKS.md) provide multi-turn search,
read and submit environments over the 1,486-email corpus: a six-checkpoint
preservation audit and a chronology with 14 milestones and five disputed
inferences. See the [chronology five-model pilot](chronology/FRONTIER_FIVE_2026-10-08_RUN2.md)
for measured rewards, reproducible response traces and verifier-review limitations.

## Quick start

Run from the repository root with Python 3.10+:

```bash
python3 -m unittest discover -s tools/rlvr/tests -v
python3 -m tools.rlvr.run --self-test
python3 -m tools.rlvr.run --dry-run
python3 -m tools.rlvr.run --model openai:YOUR_MODEL_ID --repetitions 3
```

For a cross-provider comparison, supply model IDs available to your accounts:

```bash
python3 -m tools.rlvr.run \
  --model openai:YOUR_OPENAI_MODEL_ID \
  --model anthropic:YOUR_ANTHROPIC_MODEL_ID \
  --model gemini:YOUR_GEMINI_MODEL_ID \
  --repetitions 3 --max-output-tokens 1024 --timeout 45
```

Set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY` (or
`GOOGLE_API_KEY`) in the environment through your normal secret manager.
For OpenRouter, set `OPENROUTER_API_KEY` or explicitly pass
`--openrouter-key-file /path/to/keys.txt`. The selected file must contain exactly
one unique OpenRouter credential. It is read only for OpenRouter calls, never
copied to results. The runner never automatically searches credential files.
Only selected providers receive the public observation (the selected synthetic emails
and task instruction); no external research tools are enabled. Each selected
model/repetition makes one potentially billable request, with no automatic
retries. Missing credentials and API/network errors are recorded separately.

No packages are required for offline execution. HTTPS uses `SSL_CERT_FILE` if
set, otherwise the installed `certifi` bundle if available, otherwise system
trust. If Python cannot find trusted roots, install `certifi` or configure
`SSL_CERT_FILE`; TLS verification is never disabled.

## Harder calibration tasks

```bash
python3 -m tools.rlvr.run --task benchmark/rlvr/tasks/CTH-INVENTORY-002.json --self-test
python3 -m tools.rlvr.run \
  --task benchmark/rlvr/tasks/CTH-INVENTORY-002.json \
  --model openrouter:openai/gpt-6.1-sol \
  --model openrouter:anthropic/claude-opus-5.5 \
  --model openrouter:google/gemini-3.1-pro-preview \
  --openrouter-key-file ~/.claude/keys.txt \
  --repetitions 2 --max-output-tokens 24000 --timeout 600
```

Model availability and funded account credits are required. OpenRouter records
its returned routing provider, model identity and usage cost; provider fallback
is disabled. HTTP 402 is an unscored provider error, never a model score of zero.

The harder tasks present fixed shuffled packets of 75 or 300 messages with original
Date/From/To/Cc/Subject headers and complete decoded plain-text bodies, including
quoted history. Attachments, labels, source filenames and gold are withheld.
Each source is SHA-256 pinned. The 300-message packet contains the original 75
plus a reproducible 225-document sample of remaining Cascade source files.
Selection is recorded in its manifest; it overlaps the smaller development packet.
For the 300-message packet, reserve 24,000 output tokens: reasoning tokens can
consume the budget before the final JSON is emitted. Record incomplete responses
as budget failures; do not describe them as factual errors.
These remain single-turn, tool-free evaluations;
they measure a different capability from agents allowed to write parsing code.

**Inventory:** the evaluator computes every expected answer from original RFC
headers, never from a model judge or authored legal interpretation. Questions
cover monthly volumes, sender-domain counts, outbound disclosures, recipient
filters, top senders, weekends, timezone date changes, directed organization
edges, internal messages and ordered chronology. Quoted messages must not be
counted as new documents. The 12 question scores are averaged equally:

- Count mappings: correctly counted keys divided by the union of expected and submitted keys.
- Document sets: precision/recall F1; both empty earns 1.
- Ordered arrays: correctly positioned entries divided by the longer array length.

Missing or malformed individual answers earn zero. Duplicate entries are
invalid; extra mapping keys and list entries reduce reward. Whole-output JSON
errors, duplicate keys and unknown question IDs earn zero. Full success requires
all 12 questions to score 1. Partial reward provides an RL training signal.
`InventoryEnvironment.reset()` / `.step()` use the same episode contract as the
date pilot. Expected answers stay in the trusted evaluator process.

**Evidence audit:** 18 structured questions cover event/message dates, elapsed
days, conflicting financial measures, organizations, and distinguishing plans
from completed actions. Per-question reward is 70% for an entirely correct value
and 30% for citation coverage times precision, conditional on value correctness.
Quoted copies satisfy anchors. Reviewed contextual citations are accepted for
precision but cannot replace required anchors. The private authoring oracle is
hash-pinned in `benchmark/hidden_gold/rlvr/`; it still needs independent human
review. It is public repository development material, not secret test data.
Version 1.0.1 fixes overly narrow contextual citation acceptance found during
calibration. Original 1.0.0 score differences were verifier artifacts and must
not be treated as model differences; all six factual-audit completions score
100% after correction. See the [calibration report](CALIBRATION_2026-10-08.md) for the harder inventory runs.

A single fixed packet is insufficient for a general ranking. Build independently
reviewed, disjoint held-out families before using these for trainer selection;
repeated generations are trials of the same task, not new independent tasks.

## Date task and reward contract

`tasks/CTH-DATE-001.json` pins EMAIL-003 to its SHA-256 and records the corpus
commit. The model gets the original EML contents, not load-file labels, source
path, authoring notes, hidden gold, or the calculated answer. The expected date
is calculated only by the trusted evaluator using Python's RFC email parser.
There must be one Date header and an explicit timezone; invalid evidence is an
environment error, not a model failure. The sender's local calendar date is
used without converting to UTC.

The entire completion must be a JSON object with exactly one key, `sent_date`,
whose value is a real ISO calendar date. Whitespace is accepted. Code fences,
explanation, extra fields, duplicate keys, impossible dates, and wrong dates
earn zero. The correct answer earns one. No model judge or matching prose is
involved. Refusals and token-truncated/empty answers earn zero; transport errors
have no reward and are counted separately.

Task `split: smoke` is intentionally public/development-only. Do not advertise
this email or its publicly reproducible oracle as held-out test data. Tests
contain synthetic Date-header edge cases solely to validate parser/verifier
behavior; model evaluation evidence remains the actual Cascade email.

## Trainer integration

```python
from tools.rlvr.environment import DateEnvironment

env = DateEnvironment()
observation = env.reset()
# Call your model using ONLY observation["messages"].
completion = your_model(observation["messages"])
result = env.step(completion)
reward = result["reward"]  # 0.0 or 1.0; result["done"] is True
```

The environment and verifier run in the trainer process. They are not a
security sandbox for shell-capable agents. For this pilot the remote model has
no filesystem access and receives only serialized messages. Do not mount the
whole repository, results, verifier, or hidden-gold files into a future agent
environment. Multi-step tool environments, train/test family splits, bulk task
generation, and trainer-specific PPO/GRPO adapters are future work.

## Saved results

Each invocation creates a fresh directory under `output/rlvr/<run-id>/`:

- `run.json`: task/source hashes, corpus commit, Python harness hashes, schema
  hash, requested models, token/time limits, and provider-default settings.
- `observation.json`: exact public model input.
- `records.jsonl`: one flushed record per API attempt, including the request
  body (no authentication headers), completion, model-reported identity,
  response ID where available, usage, stop reason, latency, reward or error.
- `summary.json`: attempted/scored/error counts and mean reward, success rate,
  latency and tokens per model. Errors are excluded from reward denominators.
- `self_test.json`: offline positive/negative controls, explicitly not model
  scores (self-test mode only).

Results are git-ignored. `cost_usd: null` means unpriced, not free; the runner
preserves provider usage for later pricing, including cache/reasoning details
when returned. Billing semantics differ, so it does not invent cost estimates.
Provider defaults for sampling and reasoning are recorded, not assumed equal.
Use pinned model IDs when available. An alias plus response-reported model
does not guarantee a permanently reproducible backend. These development
tasks supply no confidence interval or claim of generalization.

Exit codes: 0 = run completed (even if a model answered incorrectly); 2 = CLI
error or at least one provider error. Source validation errors stop before
model calls. Ctrl-C stops the run; completed JSONL records remain available.

## API references

- [OpenAI text generation / Responses](https://developers.openai.com/api/docs/guides/text)
- [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create)
- [Gemini generateContent](https://ai.google.dev/api/generate-content)
- [OpenRouter chat completions](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion)

The adapters use these REST APIs directly. OpenAI storage is explicitly
disabled. Output-format enforcement is deliberately prompt-only for all
providers so schema adherence is evaluated consistently by our verifier.
