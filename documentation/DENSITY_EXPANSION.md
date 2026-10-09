# Case density expansion — 8 October 2026

All people, transactions and events in this collection are fictional. This is an
authoring register, not case evidence. The email collection now contains **1,486
messages**, including **32 additions (EMAIL-1475–1506)** in three connected threads.
The original 1,454 emails and their attachments are byte-for-byte unchanged.

The additions average roughly 113 words of new body text. They use operational
questions, partial answers, conditional approvals, version differences and
follow-up records rather than adding isolated admissions. Eight distinct plain
text attachments supply queue notes, receipt extracts, allocation and settlement
records, and pilot workpapers; forwarded copies bring the total to ten attachment
instances. These are readable text records, not placeholder PDFs or spreadsheets.

## 1. Held Q4 files — THR-005 / EMAIL-1475–1486

Anchor: EMAIL-1454, Hannah's 8 November 2022 separation of three acreage-mismatch
files from the six outgoing packets. The expansion runs 8–17 November 2022.

**New fictional facts:** local queue references Q4-H1/H2/H3 distinguish these files
from the original Northwest eight. H1 involves an old listing figure; H2 possible
overlapping survey areas; H3 a cropped county scan that still differs when a full
copy arrives. The two easement files in the other six receive recorded exhibit
and map copies, filling the missing-document gap without determining eligibility.

Priya keeps a nine-file commercial forecast while Tom asks for a six-file firm
number. Jay declines to promise conditional inventory. H1's owner accepts the
county figure, Priya gives conditional release instructions, and Sarah later
checks the corrected acreage against the source records. H2/H3 stay unreleased.
Craig separates packet submission, issuance and delivery in the revenue forecast.
Rob asks for a bridge between the forecasts and leaves H1 conditional pending the
review. Sarah identifies her check as a targeted exception check, distinct from
the framework's quarterly sample work.

**Still unknown:** whether H1 was actually submitted or delivered after permission;
any subsequent release of H2/H3; whole-packet eligibility; performance of the
historical quarterly control. A missing transmittal is not evidence of a later
submission. The queue references do not establish a mapping to NW-01–NW-08.

## 2. Parcel-to-buyer reconciliation — THR-006 / EMAIL-1487–1496

Anchor: EMAIL-704, CPP's executed-agreement and status request. The expansion runs
14–21 August 2023. Executed buyer amounts and prices follow the existing
CSC-CPA-BELLHAVEN library. Source certificate identifiers and issuance dates
follow EX-028–035. The allocations and delivery/receipt entries are newly authored
facts, not information extracted from the previously existing contracts.

| Buyer | Agreement date | Delivered | Allocated source face | Total face | Funded cash |
|---|---|---|---|---:|---:|
| Cascade Pension Partners | 9 Nov 2022 | 16 Nov 2022 | NW-03 620,000; NW-02 520,000; NW-01 110,000 | 1,250,000 | 1,125,000 |
| North Fork Energy Fund | 21 Nov 2022 | 29 Nov 2022 | NW-06 640,000; NW-07 260,000 | 900,000 | 828,000 |
| Blue River Capital | 6 Dec 2022 | 14 Dec 2022 | NW-04 580,000; NW-07 300,000; NW-05 220,000 | 1,100,000 | 979,000 |

CPP's saved receipt set is missing the source page for the last 110,000. Tom's
earlier reservation sheet wrongly places some NW-07 with CPP; Craig notices the
over-allocation. A dated administration register and Hannah's source-reference
check correct the entry to NW-01. The two NW-07 allocations total its 560,000 face.
The original disputed four total 2.40 million face across the three buyers;
clean-parcel slices total 850,000, making 3.25 million purchased face overall.

**Cash bridge:** 2,932,000 funded less 175,920 Bellhaven fees and 234,560 Alder fees
leaves 2,521,520. Fee rates remain 6% and 8% of cash, expensed separately; gross
face remains the corpus's recognition policy. This three-purchase subset is not
the 6.8 million annual reconciliation. The remaining Northwest face is 1.30 million;
other/Southwest annual face remains 2.25 million. No new annual revenue is added.

CPP says it reviewed the May checklist and asks which screening occurred. Its
missing source-page question is answered; its eligibility question remains open.
The buyer transmission includes only its own extract, suppressing the internal
multi-buyer quoted chain. No refund amount, disallowance determination, realized
tax loss, reliance adjudication or penalty estimate is established.

## 3. Observable remediation — THR-007 / EMAIL-1497–1506

Anchor: EMAIL-932, Moss & Lane's request for a workplan and historical workpapers.
The expansion runs 14 August–8 September 2023.

**New fictional facts:** Sarah plans a purposive records pilot on archived NW-02,
NW-04 and NW-07 packets, intentionally covering different issue types. Hannah
inventories sources before testing; the pilot runs 5 September, Craig performs a
second reference/arithmetic review on 6 September, and the auditor responds on
8 September. The comparisons use existing model/exhibit pairs: 185/185, 340/288,
275/231 acres. An incorrect NW-07 exhibit link is corrected from the paper binder,
with the initial link and first-pass result preserved. The acreage mismatch stays
open. Application-copy authenticity limitations are recorded rather than silently
converting assembled copies into as-filed evidence.

**Scope limits:** this new pilot is evidence of narrow September remediation work,
not proof that the original quarterly tests ran. It does not establish a population
failure rate, authenticate every application, map the disputed recorder notice,
clear parcel eligibility, authorize a restart, or settle the accounting contingency.
The quarterly calendars and packs remain historical evidence to be assessed
separately; no retrospective absence-confession memo is introduced.

## Compatibility and reproduction

Seeds, existing contracts and exhibits, the 181-acre/approximately 512,000 increment
claim, the 2.4 million full-parcel ceiling, Clearwater's separate KW chronology,
registration issuance uncertainty, complainant anonymity and the open IRS
examination remain intact. No crosswalk is supplied between the seed survey's
NW-1042-style references and the model's NW-01-style references. Do not merge those
records by position. These authored additions are claims and records to weigh, not
automatic determinations of liability or privilege.

Story specs and their deterministic source are in
`tools/thread_kit/expansions/`. Render each THR-005/006/007 spec through
`thread_kit.py render` only on an unexpanded copy; the renderer refuses used IDs.
Then run `check_density_expansion.py --sync-loadfiles`. On an already expanded
copy, run the checker without rendering. A pre-expansion SHA256 snapshot can be
passed with `--baseline` to verify originals; the initial verification checked all
1,454 original emails. MIME rendering itself uses random boundaries/image IDs;
the story specs are reproducible, but a fresh render is not byte-identical.

The manifest and CSV/DAT load files include every new record. New TAG, PRIVILEGED
and CONTAINS_PII columns are **blank pending review**. Existing document gold labels,
evidence splits and hash-pinned RLVR tasks retain their previous scope. These new
records have no expert-reviewed labels or new benchmark targets. Changes to future
full-corpus tasks should use a new pinned collection version.

Validation checks spec chronology and participant access, message references,
attachment counts and identical forwarded copies, label blanks, load-file/manifest
agreement, allocation and settlement arithmetic, and controlled external excerpts.
Its result is saved in `tools/thread_kit/expansions/validation.json`.

There are zero new thread mismatches. The corpus-wide scan still reports the 330
pre-existing subject/thread mismatches; this addition does not repair those older
generated records. The offline RLVR verifier self-test also passed without a model
evaluation or external API call.

## Read representative additions

- [H1 correction permission and limits — EMAIL-1486](../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)
- [CPP source allocation response — EMAIL-1495](../data/emails/Custodians/Tom_Reyes/EMAIL-1495_Fwd_RE_Fwd_Re_Placement_agreement_Bellhaven_batch_5.eml)
- [Auditor's remediation scope response — EMAIL-1506](../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)
