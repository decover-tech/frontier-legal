# USA v. Cascade Timber Holdings, Inc. — Synthetic Matter

A fictional eDiscovery matter built by DecoverAI to demo document review and to benchmark
legal-investigation agents. The company, people and events are all invented; none of it is
real data.

**The matter:** Cascade Timber Holdings ran a Coastal Solar Credit Program from January 2022.
Alder Point Partners administered it and Bellhaven Advisory brokered it. The credits rested on
parcel acreage and eligibility, and people raised doubts about both early on. The IRS later
opened an inquiry, and L&L Associates came in as outside counsel. The corpus follows who knew
what and when, sales representations, credit valuation and revenue, broker authority, the
whistleblower, privilege and preservation.

## Repository layout

| Path | What it is |
|---|---|
| `CASE_BIBLE.md` | Canonical facts (rev.3): locked seed facts, actors, parcel and money math, chronology. Fact tags: `[ESTABLISHED]`, `[PROPOSED]`, `[DISPUTED]`, `[INFERENCE]`. |
| `EVIDENCE_ARCS.md` | Evidence arcs A–J (rev.2): beginning, turning points, competing readings, the joins each arc needs, and what stays unresolved. |
| `DOCUMENT_MANIFEST.csv` | Plan for all 1,400 documents (250 seed plus 1,150 new): family, threading, custodian, arc, event and evidentiary role. |
| `Cascade_Timber_EML_Dataset_Plan.md` | Realism spec: quoted threading, per-org signatures, doctrine contrast chains. |
| `MATTER_AGENT_TASKS.md` | The matter agent split into 18 discrete investigation tasks, from orientation to narrative. |
| `EVENT_LEDGER_BATCH0N.md` | Events introduced in each generation batch. |
| `FINANCIAL_LEDGER_BATCH0N.md` | Amounts introduced in each batch, kept consistent with the bible's money math. |
| `CONTINUITY_BATCH0N.md` | Per-batch QA: manifest fixes, knowledge-cutoff scans, threading and attachment checks. |
| `Definitions/` | Review protocol: responsiveness, attorney–client privilege, work product, subpoena. |
| `Logs/` | Demo privilege log (`.xlsx`, plus a PDF export of the Privileged tab). |
| `cascade_agent_benchmark/` | Agent benchmark v0.1: tasks, hidden gold, splits, schema, scoring rubric. See its [README](cascade_agent_benchmark/README.md). |
| `suggestions.md` | Assessment of training value, with known corpus defects and suggested fixes. |

These paths are git-ignored and exist only locally:

- `Data/`: the rendered corpus (`data/emails/`, with EML files by custodian) and `Cascade Timber Data Set.xlsx`.
- `Production/`: production output.
- `BATCH*_METADATA.csv`: per-batch working metadata.

## Status

- **Seed:** `EMAIL-001`–`EMAIL-250`. Don't change these; the bible's locked facts cite them.
- **Generated:** batches 1–6 cover November 2021 to March 27, 2023, so 850 EML files exist.
- **Planned:** 1,400 documents in the manifest. Batches 7 onward cover the period after the subpoena.

## Rules for generating a batch

1. **Don't contradict the bible.** Every new record cites a bible section and fact tag. Seed facts are locked.
2. **No retrospective knowledge.** A document can't mention anything its author couldn't have known yet, such as the subpoena, L&L, the Clearwater/KW parcels or the pause. Each batch runs a banned-term scan, and the continuity report records it.
3. **No single document decides an issue.** Conclusions have to come from joining several documents. For example, a recorder notice gives only the parcel number, so you need the county filing to map it.
4. **Threads point backward only.** `In-Reply-To` and `References` point to earlier documents. Quoting follows each sender's mail client (Outlook or Gmail style), and signatures match each org's fingerprint.
5. **Close each batch with three files:** its event ledger, its financial ledger and its continuity report.

## Keeping authoring and evaluation separate

Agents under evaluation must never see the authoring material. That covers `CASE_BIBLE.md`,
`EVIDENCE_ARCS.md`, the manifest's arc and role columns, the ledgers and
`cascade_agent_benchmark/hidden_gold/`. Agents get the EML corpus, the definitions and subpoena,
and ordinary load-file metadata, minus the `TAG`/`PRIVILEGED` columns. The emails no longer carry
`X-Decover-*` headers; the seed labels are in `benchmark/hidden_gold/seed_header_labels.csv`.
