# Matter Agent Tasks — USA v. Cascade Timber Holdings, Inc.

> Design principle: no monolithic "legal AI agent." A **matter agent composed of discrete legal-investigation tasks**, each producing an auditable intermediate result that feeds the next task.
> Grounding: bible rev.3 (CASE_BIBLE.md), arcs rev.2 (EVIDENCE_ARCS.md), DOCUMENT_MANIFEST v2, Definitions/*.docx. Many conclusions are deliberately **join-dependent** — e.g., Clearwater intent requires option dates + application dates + ledger data + Nina Alvarez's role; broker-authority analysis requires filing date + issuance date + placement dates. The agent must not decide such issues from one email alone.

## Core agent tasks

| Task | What the agent has to accomplish | Expected output |
|---|---|---|
| **1. Matter orientation** | Understand parties, entities, roles, program, subpoena posture, relevant dates and terminology. | Matter map / case summary |
| **2. Entity resolution** | Resolve people, organizations, aliases and relationships; e.g. Jay Whitfield/Kane, CTH vs Alder, consultants, brokers. | Entity graph |
| **3. Chronology construction** | Extract events, normalize dates, link events to evidence and identify conflicting versions. | Evidence-backed chronology |
| **4. Issue spotting** | Identify legal/factual issues such as parcel eligibility, scienter, sales representations, broker authority, accounting, privilege, preservation. | Issue tree |
| **5. Responsiveness review** | Determine whether each document responds to subpoena categories and explain why. | Responsive / non-responsive + request category + rationale |
| **6. Privilege review** | Determine ACP/work-product/Kovel status based on sender, recipient, purpose, timing and disclosure. | Privilege determination + basis |
| **7. Evidence extraction** | Extract factual propositions from documents without jumping to conclusions. | Structured facts with citations |
| **8. Knowledge analysis** | Determine who knew what, when, and through which communication chain. | Knowledge matrix |
| **9. Contradiction detection** | Identify documents or witnesses that conflict materially. | Contradiction pairs/clusters |
| **10. Evidence joining** | Combine multiple documents necessary to establish or undermine a proposition. | Multi-document evidence chains |
| **11. Scienter analysis** | Separate innocent explanations, warnings, continued conduct and concealment indicators. | Evidence-for / evidence-against scienter |
| **12. Transaction reconstruction** | Rebuild individual parcel/credit transactions from source records. | Parcel/transaction ledger |
| **13. Financial exposure analysis** | Connect acreage discrepancies to credits, revenue, reserves and potential exposure. | Exposure model with source citations |
| **14. Witness preparation** | Generate witness-specific timelines, knowledge, contradictions and likely examination topics. | Witness dossier |
| **15. Investigation gap analysis** | Identify unanswered questions and missing documents required to resolve them. | Gap / follow-up request list |
| **16. Preservation analysis** | Reconstruct subpoena, hold, collection, custodians, third-party preservation and production activity. | Preservation timeline + risk flags |
| **17. Legal theory building** | Organize evidence supporting and undermining competing case theories. | Plaintiff/government vs defense theory matrix |
| **18. Case narrative generation** | Turn verified events and evidence chains into a coherent factual story. | Citation-backed narrative |

Tasks are progressively harder (orientation → extraction → joins → theory → narrative).

---

## 1. Matter understanding agent

> "Read the corpus and construct the world of the case."

Identify: Cascade Timber Holdings, Alder Point Partners, Bellhaven Advisory, L&L Associates, IRS / Kevin Tran, consultants (Whitaker, Larsen, Northstar), buyers and landowners, employees and roles.

Legal conclusions depend on **who someone is in relation to the client**. Alder Point is a potentially contestable affiliate but, absent a joint-defense arrangement, currently a third party for privilege purposes.

**Task: build a matter entity graph:** `Person → Employer → Role → Relationship to CTH → Custodian → Legal significance`. E.g. `John Ellery → CTH → General Counsel → Client counsel → Custodian → privilege hub`; `Derek Holt → Bellhaven → Managing Director → third-party broker → Custodian → registration evidence`.

## 2. Chronology agent (foundational)

Create events such as: `2022-02-14 — Nina Alvarez tells Tom Reyes acreage may be inaccurate. Evidence: EMAIL-037. Issue: parcel eligibility / knowledge. Confidence: high.` And: `2022-10-04 — GC recommends pausing. 2022-10-05/06 — Management decides not to pause. Issues: scienter / advice of counsel / governance.`

Distinguish **event date** vs document date vs retrospective recollection vs inferred date vs disputed date. E.g., formal board pause action is inferred as June 30 from a June 29 draft referring to a meeting "tomorrow."

## 3. Legal issue spotting agent

> "What factual and legal issues emerge from these documents?"

Target discovery (cf. ten evidence arcs): parcel eligibility/acreage, knowledge/scienter, broker registration, sales representations, advice of counsel, revenue recognition, internal controls, Clearwater sequencing, whistleblower handling, privilege, work product, Kovel, preservation, IRS production completeness.

Strong form per issue: `Issue ├── Elements/questions ├── Evidence supporting ├── Evidence opposing ├── Disputed facts ├── Missing evidence └── Key witnesses`.

## 4. Responsiveness agent

> "Is this responsive to the subpoena? If so, to which request and why?"

Five subpoena categories: transactions/eligibility, marketing/sales, counterparties, Alder/Bellhaven relationships, tax/accounting/banking. Output e.g.: `{"responsive": true, "request": ["RFP-1", "RFP-4"], "issues": ["parcel eligibility", "Alder Point"], "reason": "Discusses acreage verification for a program parcel.", "confidence": 0.94}`. Benchmark: Mountain Ridge false positives (similar concepts, different program).

## 5. Privilege agent (benchmark-grade)

Ask: sender? recipients? roles? confidential? primary purpose legal advice? third party present? third party necessary to legal advice? waived? Nuanced set: CTH↔GC, CTH↔outside counsel, CTH+Alder, counsel+forensic accountant (Whitaker/Kovel-protected), controller+ordinary tax consultant (Larsen/unprotected), counsel+PR consultant (Kim/path-dependent), bare FYI forwards to GC. Require **explanation**, not classification — e.g., privileged because post-retention client-counsel communication requesting advice on regulatory exposure with no vitiating third party.

## 6. Work-product agent (separate from ACP)

> "Was this document created because of anticipated litigation or investigation?"

Anchor: February 24, 2023 (outside counsel retention), with a possible earlier February 21 trigger (Ellery assessment "in anticipation of potential regulatory inquiry"). Test: ordinary-course vs fact work product vs opinion work product vs pre-existing record later sent to counsel vs regulatory correspondence vs investigation material.

## 7. "Who knew what when?" agent

Per-actor knowledge history (e.g., Tom Reyes: Mar-2022 acreage warning → Sep-2022 registration concern → Oct-2022 continuation → Jun-22-2023 "reads worse now" → Jul-2023 "keep between us"). Output: `| Person | Fact known | Date learned | Source | Action afterward |`. Ground truth: bible §9 knowledge ledger.

## 8. Contradiction-detection agent

E.g., registration "finalized" (Dec 20 2022) vs "haven't confirmed" (Jan 10 2023) vs post-subpoena "finalized" restatement (Jun 25 2023) — conflict preserved, not resolved. Others: Lane/Klamath vs Mountain Ridge; $512K incremental vs $2.4M full-parcel; spot-check occurrence; "routine review" language vs removal. Distinguish **true contradiction** vs additional information vs different scope vs different time period.

## 9. Multi-document evidence-joining agent (most advanced)

Forbidden from single-document conclusions. Clearwater: Nina's identification → application date → option date → ledger → investigator analysis; only the join supports sequencing/intent reasoning. Evaluation form: **find the minimum document set necessary to support proposition X.**

## 10. Parcel reconstruction agent

Per parcel: owner, claimed/supported acreage, difference, application/survey dates, easement, credit amount, buyer, certificate, known internal concerns. Expected structure: 1,990 claimed / 1,809 supported / 181-acre overstatement (bible §2).

## 11. Financial tracing agent

`Parcel → acreage → credits → face value → buyer → discount → cash → broker fee → Alder fee → recognized/deferred revenue → reserve`. Spine: ~$6.8M recognized, ~$1.4M deferred, ~$2.4M exposure on four parcels. Capability tested: **explain where every number came from.**

## 12. Competing-case-theory agent

Construct **both sides with citations**: government theory (repeated warnings, corroborating survey, unresolved registration, declined pause, revenue-target continuation) vs defense theory (curable/incremental discrepancies, reliance on administrators/advisors, incomplete-not-false records, pre-hold preservation, eventual pause/investigation). Must not collapse ambiguity into certainty.

## 13. Witness agent

Per witness: role, knowledge, key documents, problematic statements, contradictions, examination topics. E.g., Tom Reyes (EMAIL-003/028/044/115/117/184; "push those through"; "keep this between us"; Lane/Klamath vs Mountain Ridge). Two directions: depose the witness vs prepare the witness for an IRS interview.

## 14. Investigation-planning agent

> "What should we investigate next?"

Gaps (bible §7/§11): renewal filing/issuance records, bank/escrow/GL, buyer complaints, Clearwater source documents, spot-check records, whistleblower access logs, board records, auditor conclusions. Rank follow-ups by **information gain** — e.g., registration issuance records first (resolve authorization-gap question affecting dozens of transactions).

## 15. Evidence-to-element agent

Map evidence against a proposition, e.g., "Management knowingly continued despite eligibility concerns": `| Required proposition | Supporting | Contrary | Status |` (knowledge: 037/003/039 vs scope ambiguity → Supported; materiality: 136/193 vs incremental theory → Disputed; pause advice: 012 → Strong; continuation: 014/184 vs reliance theory → Supported; deceptive intent: 115/140-141 vs alternatives → Unresolved).

## 16. Preservation / collection agent

Reconstruct: subpoena → deletion suspended (206/207) → departure handled → hold → custodians → collection → TAR/review → rolling production → receipt. Favorable facts (pre-hold suspension) alongside gaps (no third-party Bellhaven hold). Litigation-team-grade task.

## 17. Constrained "smoking guns" agent

> "Find the 10 documents I should read first."

Each with: why it matters, issue, people, hurts-or-helps CTH, **what must be read with it**. Must not equate bad-sounding with dispositive — e.g., EMAIL-115 vs competing EMAIL-117 + required parcel mapping.

## 18. Autonomous investigation agent

Loop: read corpus → issues → hypotheses → supporting search → **contrary-evidence search** → missing facts → further searches → joins → confidence update → report. Answers: **what happened, what is established, what is uncertain, what counsel investigates next** — not "what does EMAIL-003 say."

---

## Five flagship benchmarks (jointly covering retrieval, planning, entity resolution, temporal reasoning, joins, numerical/legal/adversarial reasoning, citation fidelity)

1. Build the complete "who knew what when" chronology.
2. Determine which Northwest parcels have eligibility problems and quantify exposure.
3. Determine whether placements occurred while OR/WA broker authority was unresolved.
4. Evaluate knowing continuation after warnings, with contrary evidence identified.
5. End-to-end privilege/work-product review, including Kovel, third-party waiver, and bare-forward edge cases.
