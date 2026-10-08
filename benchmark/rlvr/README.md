# Cascade Timber RLVR pilot

One real dataset email, one sent-date extraction task, a binary deterministic
verifier, and a multi-provider single-turn runner. This is an infrastructure
smoke test, not a meaningful frontier-model ranking or a training run.

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
The runner does not discover keys from files or store keys in results.
Only selected providers receive the public observation (the synthetic email
and task instruction); no external research tools are enabled. Each selected
model/repetition makes one potentially billable request, with no automatic
retries. Missing credentials and API/network errors are recorded separately.

No packages are required for offline execution. HTTPS uses `SSL_CERT_FILE` if
set, otherwise the installed `certifi` bundle if available, otherwise system
trust. If Python cannot find trusted roots, install `certifi` or configure
`SSL_CERT_FILE`; TLS verification is never disabled.

## Task and reward contract

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
does not guarantee a permanently reproducible backend. This one-case smoke
test supplies no confidence interval or claim of generalization.

Exit codes: 0 = run completed (even if a model answered incorrectly); 2 = CLI
error or at least one provider error. Source validation errors stop before
model calls. Ctrl-C stops the run; completed JSONL records remain available.

## API references

- [OpenAI text generation / Responses](https://developers.openai.com/api/docs/guides/text)
- [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create)
- [Gemini generateContent](https://ai.google.dev/api/generate-content)

The adapters use these REST APIs directly. OpenAI storage is explicitly
disabled. Output-format enforcement is deliberately prompt-only for all three
providers so schema adherence is evaluated consistently by our verifier.
