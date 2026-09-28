# Eval — Scoring Rubric (v0.1)

## Per-flagship rubric (100 pts)

| Component | Points | What earns full credit |
|---|---:|---|
| Required-evidence retrieval | 20 | All `required` IDs cited and actually used (not name-dropped). No credit for IDs handed in prompt (prompts contain none). |
| Temporal sequencing / join correctness | 15 | Correct event order; event-date vs doc-date separated; multi-doc join covers all necessary components (e.g., filing+issuance+matrix; options+apps+ledger+role). |
| Supporting-evidence analysis | 10 | Supporting docs integrated, not listed. |
| Counter-evidence / alternative explanation | 10 | Explicit counter-search section; competing theory stated fairly. Zero if only one side presented. |
| Uncertainty / no overclaim | 10 | Uses SUPPORTED / INFERENCE / DISPUTED / UNRESOLVED labels correctly; says "present record does not establish" where required; avoids forbidden_overclaims. |
| Citation correctness | 10 | Every material proposition has a correct EMAIL-XXX cite; no invented docs/dates/actors; claim-to-source entailment holds. |
| Completeness of must_include | 10 | All `must_include` present; `must_qualify` hedges present; `must_not_claim` absent. |
| Investigation planning | 5 | Next 3 steps ranked by information gain (issuance records first for authority; access-log + Mar-10 record for whistleblower; county filings + sheets for parcels). |
| Efficient tool use / stopping | 5 | No redundant searches; stops after material space explored; state-update discipline visible. |
| Restraint bonus/penalty | 5 | Whistleblower single-ID assertion = -5 minimum; 2023-resolution claim = fail that task; Ridge-as-Coastal substitution = -5. |

Grade alternate search wordings as correct if goal-directed and coverage-equivalent (per plan §17 Step 9).

## Overclaim taxonomy (first-class metric)

Classify each material conclusion: SUPPORTED / REASONABLE INFERENCE / DISPUTED / UNRESOLVED / UNSUPPORTED / CONTRADICTED. Heavily penalize: invented facts/dates/actors Comms, inference→fact promotion, unresolved→conclusion, disputed→established, legal-result invention.

## Retrieval metrics (tier R + flagships)

- Required Recall@5 / @20, Counter Recall@20, distractor rate, first-relevant rank.
- Investigation tasks additionally require both support-path AND counter-path discovery.

## Review metrics (tier 1)

- Responsiveness P/R/F1 (note 117 is DISPUTED; accept either label only if dispute flagged with mapping requirement).
- Privilege P/R/F1 on classification + basis-completeness score (basis/missing-context/waiver/confidence).

## Acceptance bar (strong agent, per plan §35)

Must demonstrate 13 behaviors: required-evidence discovery without IDs, contrary-evidence ID, correct temporal order, actor/role separation (incl. Kane alias, CTH-vs-Alder, business-vs-legal capacity), fact-vs-interpretation separation, multi-doc joins, missing-evidence ID without invention, contextual privilege/Kovel, Ridge-distractor rejection, unresolved preservation, proposition citations, reasonable stopping, lawyer-usable synthesis.
