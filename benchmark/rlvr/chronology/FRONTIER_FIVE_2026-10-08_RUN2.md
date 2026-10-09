# Chronology Task 2 — five-model comparison, October 8, 2026

One episode per model on `CTH-CHRONOLOGY-001`, using the supplied funded
credential. The earlier HTTP 402 attempts remain separately recorded and
are excluded from performance scores. This is a development-task pilot,
not an estimate across independent tasks or a statistically reliable ranking.

| Model | Reward | Full success | Steps | Input tokens | Output tokens | Reported cost | Elapsed |
|---|---:|---|---:|---:|---:|---:|---:|
| GPT-6 Astra | 85.24% | No | 25 | 356,788 | 3,397 | $0.7893 | 1.4 min |
| Grok 4.7 | 68.50% | No | 63 | 1,422,816 | 4,880 | $0.8259 | 2.0 min |
| Claude Opus 5.5 | 68.45% | No | 29 | 503,118 | 9,083 | $2.1941 | 2.5 min |
| GLM 5.3 Prime | 43.13% | No | 29 | 365,823 | 15,551 | $0.4214 | 2.8 min |
| Gemini 3.1 Pro Preview | 0.00% | No | 3 | 13,382 | 2,872 | $0.0612 | 0.5 min |

Reward is a graded evidence score, not the percentage of independent tasks solved.
Input tokens are cumulative across turns, including repeated context. Reported
output tokens include provider-reported reasoning usage. Unknown cost is not zero.

## Score components

| Model | Milestones (55%) | Ordering (15%) | Resolutions (30%) | Full-credit events / 14 | Full-credit resolutions / 5 |
|---|---:|---:|---:|---:|---:|
| GPT-6 Astra | 95.54% | 91.21% | 63.39% | 12 | 0 |
| Grok 4.7 | 85.71% | 73.08% | 34.64% | 11 | 0 |
| Claude Opus 5.5 | 88.10% | 77.20% | 28.06% | 10 | 0 |
| GLM 5.3 Prime | 56.25% | 30.29% | 25.50% | 7 | 0 |
| Gemini 3.1 Pro Preview | 0.00% | 0.00% | 0.00% | 0 | 0 |

## Transport and budget diagnostics

| Model | Search | Read | Submit | Invalid actions | Truncated responses | Responses above requested output cap | Terminal failure codes |
|---|---:|---:|---:|---:|---:|---:|---|
| GPT-6 Astra | 11 | 13 | 1 | 0 | 0 | 0 | INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY |
| Grok 4.7 | 43 | 17 | 1 | 2 | 0 | 0 | INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY |
| Claude Opus 5.5 | 8 | 15 | 1 | 5 | 0 | 0 | INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY |
| GLM 5.3 Prime | 10 | 13 | 1 | 5 | 0 | 0 | INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY |
| Gemini 3.1 Pro Preview | 2 | 0 | 1 | 0 | 0 | 0 | INCOMPLETE_OR_UNSUPPORTED_CHRONOLOGY |

Tool and episode budget exhaustion count as task failures. Provider request
errors are unscored. Identical requested reasoning effort and token caps do
not imply identical provider implementations; observed deviations are above.

## Interpretation and verifier review

All five models returned terminal submissions without provider errors, truncated
responses or observed output-cap overruns. None achieved full-task success.
Every one of the 149 environment transitions reproduced exactly in offline replay.

Four models matched every event-date bound, precision and report date. Their
score differences came primarily from evidence coverage, citation matching,
event classification and resolution requirements. This run does not establish
that the date-reconstruction portion alone is hard enough to distinguish them.

| Model | Event dates and precision / 14 | Report dates / 14 | Event classifications / 14 | Resolution conclusions / 5 |
|---|---:|---:|---:|---:|
| GPT-6 Astra | 14 | 14 | 14 | 5 |
| Claude Opus 5.5 | 14 | 14 | 13 | 4 |
| Gemini 3.1 Pro Preview | 3 | 3 | 11 | 3 |
| Grok 4.7 | 14 | 14 | 13 | 4 |
| GLM 5.3 Prime | 14 | 14 | 12 | 4 |

These are diagnostic field matches, not alternative reward scores. They do not
waive evidence requirements. Gemini submitted after two searches and no reads,
so its required read-evidence coverage was zero.

The deterministic verifier needs an independent alternative-evidence review.
For example, GPT cited EMAIL-1506 stating that the NW-04 and NW-07 acreage
reconciliations remained open, but the oracle requires a different clause from
the auditor assessment for that support group. This is plausible support that
deserves review. Additional relevant context and reasonable rule selections can
also lose credit under the fixed rubric. Raw scores and the frozen oracle have
not been changed in response to these results.

Treat this as a useful diagnostic pilot. Review evidence equivalence and label
distinctions before interpreting the spread as a reliable model ranking or using
these rewards for training.

## Conditions and reproducibility

- Same task, source pins, policy, output schema, verifier and initial observation for all five models.
- Low reasoning effort; 16,384 output tokens per request and 131,072 per episode.
- 120 actions and 300,000 observation characters per episode.
- Per-request socket inactivity timeout 180 seconds; hard wall timeout 300 seconds.
- OpenRouter provider fallback disabled; no automatic request retries or output repair.
- Every returned environment transition reproduced exactly in offline replay.
- The answer key and task rules were frozen before these runs; independent oracle review remains pending.

Batch: `20261009T020421Z-frontier-five-5bba54`.
Known reported cost subtotal: **$4.2919**.

[Machine-readable comparison and provenance](results/frontier-five-2026-10-08-run2.json).

[Committed response and tool-result traces](results/frontier-five-2026-10-08-trajectories.json)
reproduce all 149 transitions and the five terminal scores without API calls:

```bash
python3 -m tools.chronology_rlvr.replay benchmark/rlvr/chronology/results/frontier-five-2026-10-08-trajectories.json
```

Recorded code hashes describe the working-tree files used for the live run. The
PR includes the required provider reasoning/budget support while excluding
unrelated inventory CLI changes. Offline replay in the clean PR checkout confirms
identical initial observations, tool results and scores; it does not rerun remote
model generation. No labels or rewards were adjusted after seeing these responses.

Raw responses, tool observations, usage and scripts: `output/rlvr/chronology/20261009T020421Z-frontier-five-5bba54`.
Credentials were supplied only through process memory/environment, not saved in these artifacts.
