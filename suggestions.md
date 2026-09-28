# Cascade Timber Demo: Training-Value Assessment and Suggestions

I scored the Cascade Timber Demo folder against the rubric's default profile: **legal evidence reasoning, trained by supervised fine-tuning**. It comes out at **Q ≈ 49/100** (plausibly 45–55 given reviewer judgment), in the **"Below 50: low current training value"** band.

**Decision: blocked for training.** It's a well-built demo and evaluation corpus, but it isn't yet a training dataset.

## What was checked

Automated checks over all 250 emails, both load files, the workbook, the privilege log and the Definitions files, plus a targeted read of about 25 key emails. This was not the random sample of 100–200 examples the rubric asks for, so the ratings are diagnostic. No model uplift was tested, so the validated training score (T) and dollar value are **UNKNOWN**.

## Eligibility gates

| Gate | Status | Evidence |
|---|---|---|
| Permission and provenance | UNKNOWN | Everything is fictional and DecoverAI-owned, but no generator or model versions or hashes are recorded |
| Evaluation isolation | FAIL | There's no train/eval split, and it's one matter, so it can't test transfer to new matters |
| Material correctness | FAIL | Unresolved contradictions (listed below) |
| Usable task structure | FAIL | There are no training examples (input, evidence, target), only one tag per document |
| Domain boundaries | FAIL | The subpoena cites 26 U.S.C. § 7602, but under that section the IRS issues a summons, not a "subpoena duces tecum". That teaches a false real-law fact. |

## Score by dimension

| Dimension | Weight | Rating | Points | Basis |
|---|---:|---:|---:|---|
| Task relevance | 15 | 3 | 9 | Covers responsiveness, privilege, work product, Kovel, chronology, aliases, dedup and PII. There's no map of where the baseline model fails. |
| Correctness | 20 | 2 | 8 | Contradictions: Tran has two sets of contact details (irs.gov/(202) in 12 emails vs irs-example.gov/(503) in the subpoena). Cascade's address differs: 1200 Forest Park Way in 160 signatures vs 601 SW Second Ave in the subpoena. The deadlines don't add up (027/056/057/158). 205 attributes $2.4M to "the Northwest batches", 136 to "4 of 8 parcels", and the bible's 8-parcel total is $4.45M. The README says 041/042 contradict 009, but the bible says 009 is candid. |
| Supervision | 15 | 1 | 3 | One mixed tag per document, so the 43 privileged documents carry no responsiveness or issue label, and there are no category 1–5 labels. Only 7 gold queries exist, covering docs 001–030, and they're stale. Example: "Privilege Review" lists 5 hits against 43 privileged docs, and "Alder Point personnel" includes Cascade's EMAIL-004. The privilege log has 1,009 rows full of people who aren't in the corpus (Maya Chen, Oliver Grant, Mateo Ruiz…). |
| Reasoning depth | 15 | 3 | 9 | Real cross-document joins: 003→184→115/117, 009/041→045 vs 018, and $512K vs $2.4M. Most joins in the bible's 7 disputed questions depend on documents that don't exist yet (the "[PROPOSED]" ones). |
| Creativity and coverage | 10 | 3 | 6 | Doctrine contrast pairs, the Mountain Ridge decoy, the Kane alias, a deliberate near-duplicate and PII traps. It's one matter with no coverage matrix. |
| Realism | 10 | 3 | 6 | Threading, per-org signatures, inline logos, time zones correct for daylight saving, about 33% noise. But the new text in each email is very short (median 32 words; 190 of 250 are under 40), and the admissions are convenient ("keep this between us"). |
| Cleanliness and integrity | 10 | 3 | 6 | Structure is clean: 250/250 parse, no duplicate IDs or Message-IDs, 89/89 In-Reply-To and 106/106 References links resolve, and the load file has 250/250 rows. But 250/250 files carry the answer in X-Decover-Tag/X-Decover-Privileged headers. |
| Reproducibility | 5 | 2 | 2 | The version passes are documented in the README, but the generation scripts, hashes and DOCUMENT_MANIFEST.csv aren't in the folder. |
| **Q** | | | **49** | |

## The folder's parts, ranked by training value

1. **The EML corpus:** the core asset. It's structurally sound and its doctrine contrasts are well designed.
2. **CASE_BIBLE + EVIDENCE_ARCS:** the design and the reconciliation work. They're the fastest route to gold targets, but the rubric doesn't credit promised features.
3. **The four Definitions files:** usable as labeling protocols once the summons/subpoena mislabel is fixed.
4. **The workbook's Search Queries and Chronology tabs:** stale; they only cover documents 001–030.
5. **The privilege log:** mostly out-of-corpus people, so it would teach the wrong entities.

## Five fixes with the most impact

1. **Strip the X-Decover-\* headers** from anything a model sees, and move the labels to a separate file.
2. **Create about 150–200 task/evidence/target examples:** multi-label responsiveness categories, privilege basis, chronology and grounded question answering, including examples where the right answer is to abstain. Have an expert review them.
3. **Resolve the contradictions:** Tran's contact details, Cascade's address, the deadline chain, and the $2.4M basis. Also decide the 116/117 family: 117 says "Nothing on the Coastal Solar side", which is arguably responsive under the subject-matter definition. Relabeling it would also end the split tags within that thread.
4. **Rename the "subpoena" to a summons**, or state explicitly that the subpoena framing is fictional.
5. **Build a second, independent matter for evaluation**, and add hashes, generator versions and the manifest.

## Expected outcome

Once fixes 1–3 are done, I'd expect the score to move into the **65–79 "promising, needs repair"** band. That's an estimate, not a measurement.
