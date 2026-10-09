# Cascade litigation skill episodes

This suite adds 17 bounded executable episodes to the existing preservation and chronology pilots, covering the 19 skill families in `documentation/LITIGATION_SKILL_TASK_PLAN.md`. It uses only the Cascade Timber matter. These are development episodes with deterministic, evidence-based rewards, not 19 fully automated legal workflows.

All 17 new episodes are implemented and independently reviewed. See `COVERAGE.md` and `validation.json` for exact control counts. The two legacy pilots still need separate independent oracle review. Model calibration remains pending.

Each implemented new episode contains a task instruction and cutoff, supplied policy, answer and artifact schemas, standalone draft fixtures, hidden accepted answers and proof obligations, positive and adversarial controls, and an independent source/oracle review. The source snapshot includes 1,486 emails, 331 attachments, 884 inline images, 21 contracts, 38 exhibits and four supplied protocols. Three protocols expose rules only; worked determinations are excluded from the learner evidence.

## Run an episode

From the repository root with Python 3.10+ and `jsonschema` installed:

```sh
python3 -m tools.litigation_tasks.run --task CTH-LIT-08 --dry-run
python3 -m tools.litigation_tasks.run --task CTH-LIT-08 --control
python3 -m tools.litigation_tasks.run --task CTH-LIT-08 --stdio
python3 -m tools.litigation_tasks.build
python3 -m unittest discover -s tools/litigation_tasks/tests
```

`--stdio` sends the initial public observation on stdout and accepts one JSON action per stdin line. Each response includes an observation, reward and termination flag. Search is an AND of literal words or quoted phrases. Read results include the original locators and pagination. Artifact writes affect only the episode's declared in-memory paths. Tool errors consume a step. Gold feedback appears only at submission. Readiness labels and citation-bearing fixture provenance remain evaluator metadata, so they do not supply answer labels or proof locations to the learner.

```json
{"tool":"search","query":"production received","offset":0}
{"tool":"read","document_id":"EMAIL-162","locator":"line:6"}
{"tool":"list_artifacts"}
```

The actual required answer and artifact shapes appear in the initial observation. A single outer JSON Markdown fence is accepted; duplicate keys and non-finite JSON values are rejected. Output shape is part of the contract, but arbitrary prose style and rule labels are not graded.

`--control` exercises evaluator-authored answers. A 100% control score confirms expected verifier behavior; it is not a model score. Saved trajectories can be replayed with `--replay /absolute/path/to/trajectory.json`. Replay checks task and harness hashes (including provider/deadline dependencies), carried dependency snapshots, every observation, and the terminal result without API calls.

## Trainer interface

```python
from tools.litigation_tasks.run import TrainerEnvironment

env = TrainerEnvironment("CTH-LIT-08")
observation, info = env.reset(seed=0)
observation, reward, terminated, truncated, info = env.step(action)
```

The adapter uses Gymnasium's five-value step convention without requiring the Gym package. It accepts all 19 family IDs; `CTH-LIT-09` delegates to `CTH-PRESERVATION-001`, and `CTH-LIT-10` delegates to `CTH-CHRONOLOGY-001`. Those two pilots retain their existing schemas and graders. Their historical scores are not recalculated under the new grader.

For new episodes, reward combines answer-field accuracy, required evidence coverage, citation precision and contrary-evidence handling. Evidence must have been read and quoted from an eligible exact source location. Multiple reviewed equivalent passages are accepted. Unordered answer sets are order-independent. Findings contribute 80% and artifact checks 20%; artifact credit is gated by the overall evidence-backed finding score, so copying an unsupported answer or artifact earns zero. Required conflicts lower credit when omitted. Incorrect substantive fields receive partial credit, while an invalid final schema receives zero.

`ChainSession` in `tools.litigation_tasks.registry` lets verified completed new episodes supply read-only artifacts to declared downstream dependencies. Use `session.start(task_id)`, run the episode, and `session.publish(env)`. A downstream episode can use `read_dependency` with the predecessor ID and artifact path. Future-cutoff context is rejected. Prior artifacts are not source evidence and cannot satisfy citations. Standalone fixtures remain explicit task inputs; absent dependencies use those fixtures. Legacy pilots are available through the trainer adapter but do not publish state into this chain adapter.

## Compare models

Paid calls are opt-in:

```sh
python3 -m tools.litigation_tasks.run --task CTH-LIT-08 \
  --model PROVIDER/MODEL_SLUG \
  --key-file ~/.claude/keys.txt \
  --max-output-tokens 16384 --episode-output-tokens 131072
```

This mode uses the existing OpenRouter transport. Credentials are read at request time and excluded from result files. Runs record model, requested budgets, reported usage/cost, latency, actions, observations and deterministic reward. Use equal budgets and multiple runs when comparing models. Infrastructure failures and token exhaustion must be reported separately from substantive accuracy. No frontier scores for these new episodes are asserted by this build.

## Isolation and evidence limits

The Python environment is a trusted evaluator interface, not an operating-system sandbox. Run it outside the learner's filesystem/process boundary. Do not mount the whole repository or its hidden gold, controls, review notes, extraction manifest or research into a learner container. `python3 -m tools.litigation_tasks.export --task CTH-LIT-08 /new/public-directory` exports only the public observation, eligible extracted documents and fixtures. No original-file provenance paths or full hidden protocol examples are exported.

Attachment availability is gated by the parent email date; that date is not an inferred creation or execution date. Undated standalone documents are supplied references, and do not establish when a historical actor had access to them. Native PDF text and OCR are distinguished. There are 34 OCR-transcribed PDF pages; OCR is not globally human-verified, 81 inline-image instances have no detected text, and some embedded visual media are unprocessed. Missing extracted content never proves a fact was absent. See `evidence/coverage.json`.

The independent reviews are source/oracle checks by a different agent, not an assertion of licensed legal review. The supplied protocols govern these exercises; no current jurisdictional law was researched or certified. Free-form advocacy quality, all modes of each reference skill, production/sending, live calendars, user authority and external systems are outside these episodes. Exact-proof alternatives remain a reviewed finite set and may need expansion after blinded model calibration. One matter provides no held-out matter generalization claim. Split all variants from this matter together when constructing larger training/evaluation collections.
