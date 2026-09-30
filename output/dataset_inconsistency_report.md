# Dataset inconsistency report

Review date: September 28, 2026. Updated September 29, 2026 with a status per finding and a resolution log (end of file). Sources are the fictional demonstration dataset in `data/`; this is a document-consistency review, not a determination of legal liability.

Scope: inventoried and parsed 1,454 email messages, 375 attachment occurrences, 21 contract documents (9 DOCX and 12 PDF), and 38 standalone email exhibits. Extracted contract and exhibit text; OCRed the four image-only executed contracts. Examined relevant email bodies and attachment contents, compared indexed contract copies against their email attachments by SHA-256, and visually checked selected scanned pages. This is a targeted substantive review following a corpus-wide inventory, not an exhaustive line-by-line review of every attachment or a forensic authenticity examination. No source files were modified during the review; the fixes are listed in the resolution log.

Findings distinguish direct conflicts, unresolved reconciliation issues, and missing supporting detail.

## 1. Clearwater options have incompatible “executed” dates and payment terms — high confidence

**Status: RESOLVED (2026-09-29).** EX-003/EX-004 rebuilt as conformed copies of the executed scans. See the resolution log.

| Parcel | Standalone email exhibit | Executed contract in contracts/ |
|---|---|---|
| KW-01 | April 4, 2022; $12,000 due August 17, 2022 | Effective January 10, 2023; owner signed January 6 and Tom Reyes January 10; three $4,000 installments |
| KW-02 | April 11, 2022; $12,000 due August 24, 2022; Tom signature undated | Effective September 20, 2022; owner signed September 19 and Tom September 20; three $4,000 installments |

In both long-form contracts, the first installment is due within five business days of the effective date, with later installments at 180 and 270 days, subject to deferral/prepayment provisions. These differ materially from the lump-sum August deadlines in the exhibits. The exhibit copies also lack an owner execution block, despite their “EXECUTED COPY” footer.

Sources: [EX-003](<../data/emails/Exhibits/EX-003_Option_KW-01_Clearwater.pdf>), [EX-004](<../data/emails/Exhibits/EX-004_Option_KW-02_Clearwater.pdf>); [KW-01_Option_executed_scan.pdf](<../data/contracts/KW01-OPTION/KW-01_Option_executed_scan.pdf>) and [KW-02_Option_executed_scan.pdf](<../data/contracts/KW02-OPTION/KW-02_Option_executed_scan.pdf>), pp. 1–2 and 4. Emails [EMAIL-402](<../data/emails/Custodians/Jay_Whitfield/EMAIL-402_Clearwater_file_note_dates_log_no_conclusion.eml>), [EMAIL-407](<../data/emails/Custodians/Human_Resources/EMAIL-407_Nina_Clearwater_correspondence_Route_97.eml>), [EMAIL-394](<../data/emails/Custodians/Mia_Chen/EMAIL-394_KW_payment_ledger_Clearwater.eml>), and [EMAIL-446](<../data/emails/Custodians/HR/EMAIL-446_KW_option_agreement_KW_01_dated_post_3_16_22.eml>) support the later signing chronology. EMAIL-402 explicitly says neither option was signed as of July 13, 2022.

**Implication:** do not use the April exhibit dates or August deadlines as settled facts. Establish which document family is authoritative and whether any earlier agreement actually existed.

## 2. Four credit certificates use more acreage than the recorded easements — high confidence

**Status: BY DESIGN, kept.** This is the planted Arc A/B conflict. The figures match `CASE_BIBLE.md` §2 exactly (1,990 claimed, 1,809 supported, 181 over, $2.40M face).

| Parcel | Certificate acreage | Recorded acreage | Excess | Excess / recorded | Credit face |
|---|---:|---:|---:|---:|---:|
| NW-03 | 320 | 273 | 47 | 17.22% | $620,000 |
| NW-04 | 340 | 288 | 52 | 18.06% | $580,000 |
| NW-06 | 260 | 222 | 38 | 17.12% | $640,000 |
| NW-07 | 275 | 231 | 44 | 19.05% | $560,000 |
| Total | 1,195 | 1,014 | 181 | 17.85% | $2,400,000 |

Sources: easements [EX-022](<../data/emails/Exhibits/EX-022_Easement_NW-03.pdf>), [EX-023](<../data/emails/Exhibits/EX-023_Easement_NW-04.pdf>), [EX-025](<../data/emails/Exhibits/EX-025_Easement_NW-06.pdf>), [EX-026](<../data/emails/Exhibits/EX-026_Easement_NW-07.pdf>) versus certificates [EX-030](<../data/emails/Exhibits/EX-030_Certificate_NW-03.pdf>), [EX-031](<../data/emails/Exhibits/EX-031_Certificate_NW-04.pdf>), [EX-033](<../data/emails/Exhibits/EX-033_Certificate_NW-06.pdf>), [EX-034](<../data/emails/Exhibits/EX-034_Certificate_NW-07.pdf>), all p. 1. The other four NW exhibit pairs match in acreage.

The program agreement requires eligibility consistent with county records and independent verification where obtained ([EX-001](<../data/emails/Exhibits/EX-001_Partnership_Agreement_CTH_AlderPoint.pdf>), §§2–3). [EMAIL-003](<../data/emails/Custodians/Tom_Reyes/EMAIL-003_Land parcel eligibility _ need a second look.eml>) raises the acreage concern on March 2, 2022; [EMAIL-015](<../data/emails/Custodians/Tom_Reyes/EMAIL-015_Parcel eligibility follow-up.eml>) says re-verification never occurred, and [EMAIL-016](<../data/emails/Custodians/Priya_Shah/EMAIL-016_RE_ Parcel eligibility follow-up.eml>) directs proceeding as-is. This creates a substantive conflict between represented screening and the documented process. The $2.4 million is full credit face on the four parcels, not established loss or liability; [EMAIL-1462](<../data/emails/Custodians/Craig_Sato/EMAIL-1462_RE_FW_RE_IRS_subpoena_heads_up.eml>) and [EMAIL-1466](<../data/emails/Custodians/Grace_Lin/EMAIL-1466_RE_FW_RE_FW_NW_exposure_schedule_for_board_call.eml>) expressly make that distinction.

## 3. Original parcel data and later NW exhibits use unreconciled identifiers and figures — high confidence as a mapping gap

**Status: OPEN, decision required.** EMAIL-037/039 are seed and locked. The bible's NW-01–08 table was written without a mapping to the seed IDs or acreage. See the resolution log.

The CSV attached to [EMAIL-037](<../data/emails/Custodians/Nina_Alvarez/EMAIL-037_RE_ Parcel data request _ Northwest batch.eml>) uses NW-1042, NW-1043, NW-1051, NW-1052, NW-1067, NW-1071, NW-1088 and NW-1093. The survey attached to [EMAIL-039](<../data/emails/Custodians/Tom_Reyes/EMAIL-039_RE_ Survey request _ Coastal Solar parcels.eml>) identifies NW-1051, NW-1052, NW-1071 and NW-1093 as the four problem parcels. Later exhibits and [EMAIL-1462](<../data/emails/Custodians/Craig_Sato/EMAIL-1462_RE_FW_RE_IRS_subpoena_heads_up.eml>) instead use NW-01–NW-08 and identify NW-03, NW-04, NW-06 and NW-07.

The four original reported/recorded acreage pairs are 340/298, 275/231, 410/355 and 302/260. The later four pairs are 320/273, 340/288, 260/222 and 275/231. Only one pair matches exactly. No explicit crosswalk was located in the reviewed material. Do not merge these records by ordinal position or assume a mere rename.

There is also a small numeric conflict within the original sources: GreenAcre summarizes the excess as 12–18%, but 275 versus 231 is **19.05% above county acreage**. A different denominator might explain the range, but the survey does not specify one.

## 4. Bellhaven authority assurances conflict with continued marketing during the acknowledged gap — high confidence

**Status: conduct conflict BY DESIGN (Arc D), kept. Filing-date tension RESOLVED:** EX-017/018 re-dated to Aug 23/25, 2022.

The September 2 placement agreement requires authorization before solicitation (§2). Batch agreements also represent current authority and require a pause upon lapse. Yet [EMAIL-009](<../data/emails/Custodians/Derek_Holt/EMAIL-009_RE_ Engagement _ Coastal Solar credit placements.eml>) says Northwest renewals are pending and requests a marketing hold; [EMAIL-010](<../data/emails/Custodians/Tom_Reyes/EMAIL-010_RE_ Bellhaven registration.eml>) says marketing is already underway; [EMAIL-011](<../data/emails/Custodians/Priya_Shah/EMAIL-011_RE_ Bellhaven registration.eml>) directs continuation; and [EMAIL-044](<../data/emails/Custodians/Tom_Reyes/EMAIL-044_FW_ Following up _ registration and marketing status.eml>) confirms in November that marketing never paused. [EMAIL-1431](<../data/emails/Custodians/Derek_Holt/EMAIL-1431_RE_Engagement_Coastal_Solar_credit_placements.eml>) also routes Northwest leads directly to Derek while renewal work continues.

Sources: [Bellhaven_Coastal_Solar_Placement_Agreement.pdf](<../data/contracts/seed/Bellhaven_Coastal_Solar_Placement_Agreement.pdf>); batch agreements [EX-005](<../data/emails/Exhibits/EX-005_Placement_Batch1_Bellhaven.pdf>), [EX-006](<../data/emails/Exhibits/EX-006_Placement_Batch2_Bellhaven.pdf>), [EX-007](<../data/emails/Exhibits/EX-007_Placement_Batch3_Bellhaven.pdf>), [EX-008](<../data/emails/Exhibits/EX-008_Placement_Batch4_Bellhaven.pdf>); cited emails. This is a conflict between documented assurances/instructions and conduct, without independently deciding what registration the law required.

A separate chronology tension: [EMAIL-041](<../data/emails/Custodians/Derek_Holt/EMAIL-041_OR_WA broker registration renewal _ status.eml>) says renewal filings are already delayed by state processing on September 10, whereas the supplied filing receipts date receipt to November 14 (Oregon, [EX-017](<../data/emails/Exhibits/EX-017_RenewalFiling_Oregon.pdf>)) and November 15 (Washington, [EX-018](<../data/emails/Exhibits/EX-018_RenewalFiling_Washington.pdf>)). Earlier filings or resubmissions could explain this, but are not established by those receipts.

December finalization statements in [EMAIL-045](<../data/emails/Custodians/Derek_Holt/EMAIL-045_Registration finalized.eml>) and [EMAIL-029](<../data/emails/Custodians/Derek_Holt/EMAIL-029_Registration status.eml>) are consistent with each other. Later requests for issuance certificates ([EMAIL-761](<../data/emails/Custodians/IT_Notifications/EMAIL-761_Broker_coverage_worksheet_issuance_unverified.eml>), [EMAIL-768](<../data/emails/Custodians/Sarah_Nguyen/EMAIL-768_Renewal_ISSUANCE_certificate_OR_WA_issuance_date_only.eml>), [EMAIL-828](<../data/emails/Custodians/HR/EMAIL-828_Placement_date_vs_authority_matrix_join_record.eml>)) show a documentation gap, not proof those statements were false. Filing receipts expressly are not good-standing certificates.

## 5. Buyer amounts and batch labels do not reconcile across document families — confirmed mismatch; transaction identity unresolved

**Status: PARTLY RESOLVED.** Lots 1, 2 and 4 now match the executed agreements, and every lot has a date. The batch labels in email subjects stay unreconciled because the headers are locked.

| Buyer | Executed long-form contract | Standalone purchase exhibit(s) |
|---|---|---|
| Cascade Pension Partners | $1,250,000 face × $0.90 = $1,125,000 | Lot 2: $1,200,000 × $0.90 = $1,080,000 |
| North Fork Energy Fund | $900,000 face × $0.92 = $828,000 | Lot 4: $1,100,000 × $0.88 = $968,000; Lot 6: $1,050,000 × $0.89 = $934,500 |
| Blue River Capital | $1,100,000 face × $0.89 = $979,000 | Lot 1: $1,500,000 × $0.92 = $1,380,000; Lot 5: $1,000,000 × $0.91 = $910,000 |

Sources: [CPP_Credit_Purchase_Agreement_executed_scan.pdf](<../data/contracts/CSC-CPA-BELLHAVEN/CPP_Credit_Purchase_Agreement_executed_scan.pdf>), [Bellhaven_CSC_Purchase_Agreement_North_Fork_EXECUTED.pdf](<../data/contracts/CSC-CPA-BELLHAVEN/Bellhaven_CSC_Purchase_Agreement_North_Fork_EXECUTED.pdf>), [Blue River CPA signed.pdf](<../data/contracts/CSC-CPA-BELLHAVEN/Blue River CPA signed.pdf>), §3 and Schedule 1; [EX-012](<../data/emails/Exhibits/EX-012_Purchase_Lot2.pdf>), [EX-014](<../data/emails/Exhibits/EX-014_Purchase_Lot4.pdf>), [EX-016](<../data/emails/Exhibits/EX-016_Purchase_Lot6.pdf>), [EX-011](<../data/emails/Exhibits/EX-011_Purchase_Lot1.pdf>), [EX-015](<../data/emails/Exhibits/EX-015_Purchase_Lot5.pdf>).

These could be separate purchases, so differing values alone do not prove a contract error. However, the corpus lacks a reliable transaction crosswalk. [EMAIL-603](<../data/emails/Custodians/Dana_Whitaker/EMAIL-603_Placement_agreement_Bellhaven_batch_6.eml>) expressly acknowledges CPP was misfiled under batch 6 rather than batch 5. [EMAIL-704](<../data/emails/Custodians/Wendy_Park/EMAIL-704_Placement_agreement_Bellhaven_batch_5.eml>) calls the November 9, 2022 CPP agreement a batch 5 lot, while the standalone Batch 5 placement agreement ([EX-009](<../data/emails/Exhibits/EX-009_Placement_Batch5_Bellhaven.pdf>)) is dated January 9, 2023. [EMAIL-627](<../data/emails/Custodians/Robert_Denniston/EMAIL-627_Placement_agreement_Bellhaven_batch_4.eml>) calls the November 21 North Fork agreement batch 4; the Batch 4 placement agreement ([EX-008](<../data/emails/Exhibits/EX-008_Placement_Batch4_Bellhaven.pdf>)) is dated December 5 and quotes $0.89, whereas North Fork's signed price is $0.92. Later administrative grouping is possible, but these records should not be joined on batch number without reconciliation.

## 6. Emails overstate what the Clearwater supporting attachments contain — high confidence

**Status: RESOLVED.** Attachments on 23 emails were rebuilt (plan ATT-003). See the addendum.

[EMAIL-394](<../data/emails/Custodians/Mia_Chen/EMAIL-394_KW_payment_ledger_Clearwater.eml>) describes a ledger with three $4,000 installments, but its `KW-01_ledger.csv` has only one row: `KW-01,12000,per bank feed (verify)`. [EMAIL-443](<../data/emails/Custodians/John_Ellery/EMAIL-443_KW_payment_ledger_Clearwater.eml>) describes compiled ledger lines with two unmatched dates, but `KW-02_ledger.csv` likewise contains one $12,000 row and no bank date.

[EMAIL-449](<../data/emails/Custodians/John_Ellery/EMAIL-449_KW_credit_application_KW_02.eml>) describes a packet containing the executed option, county filing and field notes, but its `KW-02_application.txt` consists only of “APPLICATION KW-02: assembled from option + field notes.” [EMAIL-430](<../data/emails/Custodians/Mia_Chen/EMAIL-430_KW_credit_application_KW_01.eml>) has a similarly skeletal KW-01 attachment. These attachments do not substantiate actual installment payments, filing dates, or a complete application packet. This is likely demo placeholder content, but it materially limits reconstruction of the chronology.

## 7. Q4 issue descriptions confuse acreage and easement problems — confirmed and corrected in-thread

**Status: BY DESIGN, no change.** It is corrected in-thread.

[EMAIL-1442](<../data/emails/Custodians/Tom_Reyes/EMAIL-1442_RE_Q4_placement_targets.eml>) distinguishes three acreage discrepancies from two Lane/Klamath easement-documentation issues. [EMAIL-1451](<../data/emails/Custodians/Priya_Shah/EMAIL-1451_Fwd_Q4_submissions_packet_support.eml>) calls the latter “two Lane acreage ones.” [EMAIL-1452](<../data/emails/Custodians/Tom_Reyes/EMAIL-1452_Re_Fwd_Q4_submissions_packet_support.eml>) explicitly corrects Priya: the two Lane/Klamath files concern easements; the three acreage files are separate.

[EMAIL-1453](<../data/emails/Custodians/Tom_Reyes/EMAIL-1453_Fwd_Fwd_Q4_submissions_packet_support.eml>) requests that the three acreage files not be submitted without confirmation. [EMAIL-1454](<../data/emails/Custodians/Hannah_Cole/EMAIL-1454_RE_Fwd_Fwd_Q4_submissions_packet_support.eml>) says those three were excluded from that week's batch and the other six would proceed. Therefore, the earlier instruction to proceed with all nine is not proof all nine were ultimately submitted. Adding a county filing to the two easement folders also does not, by itself, establish that the missing recorded easements were obtained.

## 8. An email subject cites a notice that had not happened yet — high confidence

**Status: DOCUMENTED, not edited.** It is a Subject-header anachronism, and headers are locked (same treatment as EMAIL-1075/1087/1091/1114 in `documentation/CONTRADICTIONS_RESOLVED.md` §3).

[EMAIL-793](<../data/emails/Custodians/Derek_Holt/EMAIL-793_Broker_renewal_status_OR_WA_pending_per_9_15_notice.eml>) is dated September 8, 2022, but its subject is “Broker renewal status — OR/WA (pending, per 9/15 notice).” The actual September 15 notice is [EMAIL-009](<../data/emails/Custodians/Derek_Holt/EMAIL-009_RE_ Engagement _ Coastal Solar credit placements.eml>). This is a seven-day forward reference, likely a generated-subject or dating error. The generic body does not explain it.

## 9. Exhibit status labels contradict document content; referenced details are absent — high confidence

**Status: RESOLVED.** Footers now follow the document status, numbers and dates are supplied, EX-001 has its Section 6, and missing exhibits are marked "not reproduced".

[EX-002](<../data/emails/Exhibits/EX-002_Partnership_Agreement_DRAFTv3.pdf>) explicitly says “DRAFT v3,” “not executed,” and “comments pending,” but its footer says “EXECUTED COPY.” That footer should not be used as execution evidence.

The certificate exhibits say certificate number and delivery date are “as shown,” but do not supply actual numbers or dates. The easement exhibits refer to recording stamps, parcel numbers and legal-description exhibits that are not supplied on their single pages. [EX-001](<../data/emails/Exhibits/EX-001_Partnership_Agreement_CTH_AlderPoint.pdf>) references termination under Section 6 but ends at Section 5, and refers to an Exhibit C not included in that PDF. These are incomplete demonstration records; their headings cannot substitute for the missing underlying evidence.

## 10. README and current collection disagree — high confidence

**Status: RESOLVED.** `data/emails/README.md` and the top-level `README.md` are updated.

[README.md](<../data/emails/README.md>) repeatedly describes 250 emails through EMAIL-250 and a timeline through September 2023. The current folder and CSV loadfile each contain **1,454** messages, with IDs extending to EMAIL-1474 and dates through **December 22, 2023**. Twenty ID numbers are absent (1413–1420, 1435–1440, 1455–1460); this is a numbering gap, not proof of missing evidence.

The README also calls EMAIL-041/042 a direct contradiction of EMAIL-009. Reading the messages, all three describe pending renewal, a weeks-long expectation, and holding marketing. EMAIL-042 indicates selective omission of backlog detail, but the stronger contradiction is the continuation of marketing documented in EMAIL-010/011/044. The README overstates what this particular pair establishes.

## Explained differences and findings not treated as contradictions

- **CPP negotiated price:** draft $0.89 becomes signed $0.90; [EMAIL-601](<../data/emails/Custodians/Elena_Marlowe/EMAIL-601_Placement_agreement_Bellhaven_batch_5.eml>) flags ongoing price negotiation and [EMAIL-704](<../data/emails/Custodians/Wendy_Park/EMAIL-704_Placement_agreement_Bellhaven_batch_5.eml>) confirms $0.90.
- **North Fork negotiated size:** draft $1,000,000 becomes signed $900,000; [EMAIL-627](<../data/emails/Custodians/Robert_Denniston/EMAIL-627_Placement_agreement_Bellhaven_batch_4.eml>) expressly explains the reduction.
- **Blue River refund window:** draft 90 days becomes signed 120 days; [EMAIL-661](<../data/emails/Custodians/Dan_Osei/EMAIL-661_Placement_agreement_Bellhaven_batch_5.eml>) raises the issue and [EMAIL-639](<../data/emails/Custodians/Elena_Marlowe/EMAIL-639_Placement_agreement_Bellhaven_batch_6.eml>) confirms negotiation. Use the signed agreement, not the draft.
- **KW-01 closing period:** 60 days becomes 90 days in v4 and the executed agreement; [EMAIL-447](<../data/emails/Custodians/Dan_Osei/EMAIL-447_Nina_Clearwater_correspondence_Route_97.eml>) and [EMAIL-446](<../data/emails/Custodians/HR/EMAIL-446_KW_option_agreement_KW_01_dated_post_3_16_22.eml>) explain the change.
- **Jay/Kane signature:** [EMAIL-007](<../data/emails/Custodians/Jay_Whitfield/EMAIL-007_RE_ Broker network _ Bellhaven.eml>) explains the alternate name/account use; the README identifies it as an intentional entity-resolution test.
- **December registration versus January uncertainty:** one person's lack of confirmation is not proof registration remained pending.
- **Subpoena deadline:** [EMAIL-158](<../data/emails/Custodians/John_Ellery/EMAIL-158_Coastal Solar examination _ production schedule.eml>) explicitly references a June 20 interim extension and a revised August 31 deadline; earlier June references should not alone be labeled an impossible timeline.
- **Contract-copy integrity:** every email attachment identified by `data/contracts/INDEX.csv` matched its corresponding local contract file byte-for-byte. The main conflicts are between different document families, not silent differences in those indexed copies.

## Recommended reconciliation order

1. Designate the authoritative Clearwater executed agreements and resolve the incompatible April exhibits.
2. Obtain a parcel-ID crosswalk and reconcile the two acreage datasets against original county and survey records.
3. Build a buyer/contract/lot/batch/certificate crosswalk before combining prices or calculating totals.
4. Replace placeholder ledgers, applications and exhibit references with complete supporting records, and obtain dated registration issuance evidence.
5. Correct stale README counts, the future-referencing email subject and draft/executed labels. Preserve originals and record corrections separately.

---

## Resolution log (September 29, 2026)

Rule applied: planted conflicts that the case bible or evidence arcs require stay in place (findings 2, 4 conduct, 7). Generator errors in unlocked material are fixed. Seed emails (EMAIL-001–250) and all email headers stay locked, so defects there are documented, not edited. The standalone exhibits in `data/emails/Exhibits/` are not attached to any email, so rebuilding them changes no email. They are now built from one spec, `tools/exhibit_kit/build_exhibits.py`. Placement batches EX-005–010, the Larsen confirmations and the Moss letter are unchanged originals.

| # | Action | Files |
|---|---|---|
| 1 | EX-003/004 conformed to the executed scans. KW-01 is effective 1/10/23 (owner 1/6/23, optionee 1/10/23), with a 90-day closing and 148.62 ac. KW-02 is effective 9/20/22 (owner 9/19/22, optionee 9/20/22), with a 60-day closing and 111.87 ac. Both have a $12,000 fee paid as three $4,000 installments (within 5 business days, then the 180th and 270th days, with deferral and prepayment rights) and $1,150 per net acre. The Clearwater owner signature block (Gordon L. Pruitt) is added. The Nina "sourcing contact" line and the lump-sum August deadlines are removed. The footer now reads "CONFORMED COPY OF EXECUTED AGREEMENT". | EX-003, EX-004, `Exhibit_Manifest.csv` |
| 3 | No edit. The seed CSV/survey (NW-1042…1093; pairs 340/298, 275/231, 410/355, 302/260 = 183 ac over) and the bible table (NW-01–08; 181 ac over, which ties to seed EMAIL-140) can't both be the same four parcels. Only 275/231 (NW-07) matches. **Decision needed:** either add a dated crosswalk record, which would be a new PROPOSED fact that must keep the NW-07 recorder mapping join-dependent (bible §6 Q5), or keep it as a documented seed-versus-bible gap. GreenAcre's "12–18%" against 19.05% is in seed EMAIL-039 and stays as is. | — |
| 4 | EX-017 (OR) re-dated to Aug 23, 2022 and EX-018 (WA) to Aug 25, 2022, both before EMAIL-041 (9/10/22, "stuck behind a state processing backlog"). Receipt numbers and fees are added. The footer now reads "FILE-STAMPED RECEIPT". Issuance stays matrix-dependent. | EX-017, EX-018, manifest |
| 5 | Lot 1 now matches Blue River's executed CPA ($1.1M × 0.89 = $979,000; 12/6/22; 120-day refund window). Lot 2 matches CPP ($1.25M × 0.90 = $1,125,000; 11/9/22). Lot 4 matches North Fork ($900K × 0.92 = $828,000; 11/21/22). Each of these lots names its long-form source. Lots 3, 5 and 6 keep their amounts and now carry dates (12/13, 12/20 and 12/15/22) instead of "2022-Q4 cycle". Seller is now shown as CTH by Alder as Administrator, as in the long forms. **Not fixed (headers locked):** "batch N" and "buyer lot N" in generated Subjects are templated. For example, North Fork appears as batch 4 (627) and batch 6 (637, 681); Blue River as batch 5 (661) and batch 6 (639); and a "certificate delivery" to CPP lot 4 is dated 5/11/22, before Bellhaven was engaged (689). Batch 4's 12/5/22 agreement (EX-008) still post-dates the North Fork signing that EMAIL-627 files under batch 4. Don't join on batch or lot number. | EX-011–016, manifest |
| 6 | See addendum below. | — |
| 8 | No edit (Subject header). | — |
| 9 | Footers now follow the document status: draft, recorded, issued, file-stamped or conformed. EX-002 reads "DRAFT -- NOT EXECUTED". EX-001 gains §6 Pause and Termination, and Exhibit C is described as "to be agreed" (the framework was approved 1/24–25/22 per EMAIL-185/186) and marked not attached. Easements gain recording numbers and dates (2021). Certificates gain numbers (CSC-NW-0x-2022-000n) and issue dates (10/4–11/15/22, after the Bellhaven batches began and before the 12/5/22 year-end figures in EMAIL-193). Assessor parcel numbers are **deliberately not supplied**, so the NW-07 recorder mapping stays a join. | EX-001, 002, 020–035, manifest |
| 10 | `data/emails/README.md` gains a current-state note (1,454 messages, EMAIL-001–1474, the unused-ID ranges, 11/2/21–12/22/23, headers stripped). Its EMAIL-041/042 claim is corrected to selective omission; the conduct conflict is 010/011/044. The top-level `README.md` now has the time span (to Dec 2023), a Known issues section that separates resolved from open items, and a layout with the real paths (`benchmark/`, `definitions/`, `documentation/`, `logs/`). | READMEs |

Checks: no tracked doc, gold or benchmark file cites the replaced exhibit values. All 28 rebuilt exhibits were re-extracted with `pdftotext` and read.

### Addendum: finding 6 (Clearwater attachments, plan `tools/doc_kit/plans/ATT-003.json`)

Stub attachments were replaced on 23 emails. The splice changed only the attachment part: headers, bodies, MIME boundaries and inline logos are byte-identical to the backups.
- **Ledgers (CSV):** 391, 394, 401, 429, 433, 434, 443, 444.
- **Dates logs (CSV):** 402, 403, 421, 424, 425, 435, 445, 448.
- **Application packets:** 396, 412, 430, 431, 441, 442, 449. These changed from `.txt` to `.pdf` with the same name stem, and the load file rows were updated to match.

New library documents: KW01/KW02-LEDGER, KW01/KW02-APP and CW-DATESLOG.

Chosen [PROPOSED] facts:
- **Payments:** $4,000 each, three per parcel, no lump sum.
  - KW-02 (effective 9/20/22): check 10417, recorded 9/23/22, cleared 9/27/22; check 10602 recorded 3/15/23; check 10688 recorded 6/14/23.
  - KW-01 (effective 1/10/23): check 10511, recorded 1/17/23, cleared 1/19/23. The second payment was deferred by a 7/6/23 notice under §3.3.
- **Applications:** KW-02 signed 10/11/22; KW-01 signed 3/7/23.
- **The 140/141 join:** exactly two payments post-date an application, KW-02 payments 2 and 3. You only see this by combining a ledger with a packet or with the dates log; no single attachment states it. EMAIL-443's "two unmatched dates" are those two payments, which have no bank-feed date.

Tooling changes:
- `doc_kit.py` gains a `splice` apply mode, `append_docs` and `guard_exempt`.
- `thread_kit.py` falls back to `documentation/DOCUMENT_MANIFEST.csv`.

### Open items found during the fixes (not edited)

- **Seed EMAIL-140 conflicts with the bible.** Its schedule lists Clearwater as payee on NW parcels dated 2/14/22, before the 3/16/22 lead. The seed is locked, so this needs a bible-level decision.
- **EMAIL-437 (9/13/22)** is titled "Handoff note — Clearwater files complete", nine months before the actual 6/29/23 handoff.
- **L&L/Whitaker timing:** Whitaker's 8/14/23 finding predates L&L's logged receipt of the KW ledger and packet (438: none as of 7/5; 420: received 9/22). Also, 411 (9/21) relies on copies that 420 logs a day later.
- **Early "per the bank feed" claims:** 401, 429 and 434 (Jul–Aug 2022) cite the bank feed before either option was signed. Their ledgers show no bank activity.
- **EMAIL-422 (6/1/23):** Tom says the ledger has bank-feed lines, but none exist for KW-02 payments 2 and 3. Bank records are an intended unknown, so this stays open.
- **EMAIL-403:** Nina (Alder) sends the dates log directly to L&L.
- **Custodian folders:** some emails sit in odd folders, for example 433/424 under Kevin_Tran, 401 under Brenda_Moss and 391 under Dana_Whitaker.
- **Manifest attachment counts:** `expected_attachment_count` is 0 for carriers that do have an attachment (e.g. 443, 449).
