# Cascade Timber difficulty calibration — 2026-10-08

The original one-email task saturated at 100%. The recommended harder task is
**CTH-INVENTORY-002**: 12 e-discovery collection reconciliation queries over
300 original Cascade Timber emails (82,231 input tokens in these OpenAI runs).
It tests exhaustive collection analysis, not general legal reasoning.

## Larger packet results

Two trials per model, direct OpenAI Responses API, identical observation,
24,000 maximum output tokens (including reasoning), 600-second timeout per call.
Models ran concurrently; each model's two trials ran sequentially. Sampling and
reasoning used provider defaults. Scores are mean deterministic partial rewards,
not percentage of entirely correct questions. Full success requires 100%.

| Model | Trial 1 | Trial 2 | Mean reward | Complete outputs |
|---|---:|---:|---:|---:|
| gpt-6.1-sol | 99.59% | 99.43% | 99.51% | 2/2 |
| gpt-6-astra | 99.93% | 100.00% | 99.97% | 2/2 |
| gpt-6-sol | 87.71% | 0.00% | 43.86% | 1/2 |

The second GPT-6 Sol trial exhausted the common 24,000-token allowance without
emitting a final answer. Its zero remains in the mean reward: this metric measures
success under a fixed generation budget as well as answer quality. Its completed
first trial scored 87.71%. Always interpret mean reward alongside completion rate;
a budget failure does not mean every factual answer was wrong.

Each answer is graded from original headers: count-map accuracy, document-set
F1, or ordered-list position accuracy. All 12 question scores have equal weight.
No LLM judge is used. Full outputs and question scores are in
[the machine-readable results](results/2026-10-08.json). This export omits repeated
request prompts, preserves completions, usage, response identities, run hashes,
and stop reasons, and contains no authentication headers or credentials.

The first GPT-6.1 Sol trial omitted three weekend messages and undercounted one
directed domain edge. The first GPT-6 Sol trial also missed monthly counts and
top-sender rankings. Count and edge oracles were independently cross-checked
using SQL, and the 75-email recipient-filter error was checked against original
headers. These are substantive reconciliation errors rather than citation-policy
or JSON-format penalties.

## Smaller packet calibration

CTH-INVENTORY-001 uses the same queries over 75 emails, 23,510 input tokens,
6,000 maximum output tokens and a 120-second timeout.

| Model | Trial 1 | Trial 2 | Mean reward | Complete outputs |
|---|---:|---:|---:|---:|
| gpt-6.1-sol | 100.00% | 100.00% | 100.00% | 2/2 |
| gpt-6-astra | 100.00% | 100.00% | 100.00% | 2/2 |
| gpt-6-sol | 95.83% | 100.00% | 97.92% | 2/2 |

GPT-6 Sol's first smaller-packet trial omitted EMAIL-025 and EMAIL-028 from Q05;
both are within the requested June window with Alder Point To/Cc recipients.

The 18-question factual evidence audit also used 75 emails. Every factual answer
was correct in all six trials. Initial citation penalties were grading defects:
relevant corroborating context had been omitted from the accepted citation set.
Verifier 1.0.1 corrects this, and all six saved completions regrade to 100%.
Both original and corrected evaluations are retained. That task remains useful
as a regression control but is not evidence of model separation.

## Budget and provider limitations

An initial 300-email run allowed only 8,000 output tokens. GPT-6.1 Sol exhausted
that allowance with an empty, incomplete response. The recorded reward is zero,
but it is a budget failure, not a factual-error measurement. That run was stopped
while an Astra request was in flight, so that request has no captured result.
It is excluded from the larger-packet table above. All models were then given the
same larger allowance; neither the packet nor inventory verifier was changed.

The explicitly selected OpenRouter key authenticated. All six attempted
cross-provider generation calls returned HTTP 402; a minimal diagnostic request
confirmed insufficient funded credits. The key's spending limit is not the
account's funded balance. No Claude or Gemini quality score was obtained, and
API failures are not treated as model zeros. OpenRouter support is implemented;
rerun the documented command after funding the account. Direct-provider costs
are unavailable (null), not zero; reported token usage is preserved.

## Interpretation and validation

This is an adaptive **development calibration**, not a held-out leaderboard.
The 75- and 300-email packets overlap, the larger task was selected after seeing
smaller-task saturation, and two generations per model are not independent task
samples. Model aliases and provider defaults also limit reproducibility. The
results establish useful separation on this packet, not a general model ranking.

The setup is single-turn and tool-free. Giving an agent Python or a database
would make many inventory questions straightforward; that requires a separate
tool-enabled evaluation contract. The next benchmark expansion should cover
disjoint reviewed litigation task families and repeated trials, with explicit
compute budgets. Do not claim substantive legal ability from inventory scores.

Validation: 33 unit/integration tests, positive and negative controls for all
three new task instances, independent SQL aggregate cross-check, date-weekday
consistency check, and Git whitespace checks passed. Gold stays in the trusted
trainer process. Repository development answers are public and must not be
mounted into a future tool-using agent's evaluation environment.
