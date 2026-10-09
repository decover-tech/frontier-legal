# Evaluator review — CTH-CHRONOLOGY-001

**Contains answers. Do not expose this directory or the task manifest to an evaluated agent.**

Status: author-checked against the pinned email text; independent review pending.
The supplied chronology rules are task conventions, not conclusions about actual law.

## Expected chronology

| Milestone | Event bounds | Reported on | Actor | Nature |
|---|---|---|---|---|
| `renewal_pending` | 2022-09-15 – 2022-09-15 | 2022-09-15 | dholt@bellhavenadvisory.com | `status_report` |
| `marketing_continue` | 2022-09-16 – 2022-09-16 | 2022-09-16 | pshah@alderpointpartners.com | `instruction` |
| `held_files_excluded` | 2022-11-08 – 2022-11-08 | 2022-11-09 | hcole@cascadetimber.com | `completed_action` |
| `h1_conditional_route` | 2022-11-15 – 2022-11-15 | 2022-11-15 | pshah@alderpointpartners.com | `conditional_authorization` |
| `h1_still_held` | 2022-11-15 – 2022-11-15 | 2022-11-15 | hcole@cascadetimber.com | `status_report` |
| `h1_tieout` | 2022-11-17 – 2022-11-17 | 2022-11-17 | snguyen@cascadetimber.com | `completed_action` |
| `claimed_renewal` | 2022-12-19 – 2022-12-20 | 2022-12-20 | dholt@bellhavenadvisory.com | `attributed_claim` |
| `verification_gap` | 2023-01-10 – 2023-01-10 | 2023-01-10 | pshah@alderpointpartners.com | `status_report` |
| `renewal_restatement` | 2023-06-25 – 2023-06-25 | 2023-06-25 | dholt@bellhavenadvisory.com | `attributed_claim` |
| `pilot_scheduling` | 2023-08-18 – 2023-08-18 | 2023-08-18 | snguyen@cascadetimber.com | `instruction` |
| `pilot_first_pass` | 2023-09-05 – 2023-09-05 | 2023-09-05 | hcole@cascadetimber.com | `completed_action` |
| `pilot_second_review` | 2023-09-06 – 2023-09-06 | 2023-09-06 | csato@cascadetimber.com | `completed_action` |
| `pilot_report_to_auditor` | 2023-09-07 – 2023-09-07 | 2023-09-07 | snguyen@cascadetimber.com | `status_report` |
| `auditor_scope` | 2023-09-08 – 2023-09-08 | 2023-09-08 | bmoss@mosslane-cpa.com | `assessment` |

There are 91 precedence constraints: nonoverlapping date bounds establish 90,
and the November 15 timestamps establish the conditional route before the hold
response. The 14 event slots do not require unsupported ordering within an interval.

## Expected resolutions

| Inference | Conclusion | Actual date | Required rules |
|---|---|---|---|
| `registration_issuance` | `unverified_not_proven_false` | null | T2, T3, T4, T6 |
| `h1_transmittal` | `not_established` | null | T3, T5, T6 |
| `pilot_exceptions` | `contradicted` | null | T3, T4, T5, T6 |
| `historical_quarterly_tests` | `not_established` | null | T1, T3, T5, T6 |
| `pilot_asof_august` | `not_established` | null | T1, T3, T4, T6 |

The five actual-date answers are all null in this development episode. That is a
label imbalance, not a corpus-wide inference rule. A held-out suite should include
separate, source-supported positive cases and varied checkpoints; it must not
claim discrimination from this episode alone.

## Evidence groups

Each numbered support group is independently required by this version of the
oracle. Any enumerated document containing its anchor is accepted if the citation
was read and the source is available by the applicable cutoff. The listed anchors
are exact decision-bearing clauses, with case/whitespace normalization allowed.
A later forward cannot establish availability at an earlier checkpoint.
Alternative acceptable passages still require independent review.

### renewal_pending

Holt reports pending renewal and asks that marketing wait.

Support group 1: [EMAIL-009](../../../data/emails/Custodians/Derek_Holt/EMAIL-009_RE_%20Engagement%20_%20Coastal%20Solar%20credit%20placements.eml), [EMAIL-010](../../../data/emails/Custodians/Tom_Reyes/EMAIL-010_RE_%20Bellhaven%20registration.eml), [EMAIL-011](../../../data/emails/Custodians/Priya_Shah/EMAIL-011_RE_%20Bellhaven%20registration.eml), [EMAIL-1421](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1421_RE_Bellhaven_registration.eml), [EMAIL-1422](../../../data/emails/Custodians/Priya_Shah/EMAIL-1422_RE_Bellhaven_registration.eml), [EMAIL-1423](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1423_RE_Bellhaven_registration.eml), [EMAIL-1424](../../../data/emails/Custodians/Priya_Shah/EMAIL-1424_RE_Bellhaven_registration.eml), [EMAIL-1425](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1425_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1426](../../../data/emails/Custodians/Derek_Holt/EMAIL-1426_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1427](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1427_Fwd_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1428](../../../data/emails/Custodians/Priya_Shah/EMAIL-1428_Re_Fwd_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1429](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1429_RE_Bellhaven_registration.eml), [EMAIL-1430](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1430_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1431](../../../data/emails/Custodians/Derek_Holt/EMAIL-1431_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1432](../../../data/emails/Custodians/Priya_Shah/EMAIL-1432_Re_Fwd_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1433](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1433_Re_Fwd_RE_Engagement_Coastal_Solar_credit_placements.eml), [EMAIL-1434](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1434_RE_Bellhaven_registration.eml)

> our broker registration in a couple of the Northwest states is still pending renewal

### marketing_continue

Shah instructs Reyes to continue marketing.

Support group 1: [EMAIL-011](../../../data/emails/Custodians/Priya_Shah/EMAIL-011_RE_%20Bellhaven%20registration.eml), [EMAIL-1421](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1421_RE_Bellhaven_registration.eml), [EMAIL-1422](../../../data/emails/Custodians/Priya_Shah/EMAIL-1422_RE_Bellhaven_registration.eml), [EMAIL-1423](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1423_RE_Bellhaven_registration.eml), [EMAIL-1424](../../../data/emails/Custodians/Priya_Shah/EMAIL-1424_RE_Bellhaven_registration.eml), [EMAIL-1429](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1429_RE_Bellhaven_registration.eml), [EMAIL-1434](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1434_RE_Bellhaven_registration.eml)

> Let's keep going — we're already behind on Q3 targets

### held_files_excluded

The three held Q4 files were excluded from the outgoing batch, as confirmed the following day.

Support group 1: [EMAIL-1476](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1476_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1477](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1477_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1478](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1478_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1479](../../../data/emails/Custodians/Priya_Shah/EMAIL-1479_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1480](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1480_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1481](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1481_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1482](../../../data/emails/Custodians/Priya_Shah/EMAIL-1482_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Nothing from that subfolder went into yesterday's outgoing batch.

### h1_conditional_route

Shah authorizes a conditional route for the corrected H1 packet.

Support group 1: [EMAIL-1482](../../../data/emails/Custodians/Priya_Shah/EMAIL-1482_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> H1 can move on the corrected county figure once Sarah checks the tie-out and Hannah has the owner's acknowledgment in the packet.

### h1_still_held

Cole reports the H1 release box still blank and no entry in the next courier run.

Support group 1: [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Sarah's tie-out is still open, so the release box is blank and I haven't put it in the next courier run.

### h1_tieout

Nguyen completes the H1 acreage tie-out, preserving the limits on submission.

Support group 1: [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> I've checked H1's revised application acreage against the county copy and the owner's acknowledgment. Those figures agree.

Support group 2: [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Please enter the actual transmittal date when it goes, not today's date by default.

### claimed_renewal

The underlying renewal occurrence claimed in Holt's contemporaneous December message: retain its supported date range and attribution.

Support group 1: [EMAIL-045](../../../data/emails/Custodians/Derek_Holt/EMAIL-045_Registration%20finalized.eml)

> our OR/WA broker registration renewal finalized this week.

### verification_gap

Shah says registration has not been confirmed.

Support group 1: [EMAIL-018](../../../data/emails/Custodians/Priya_Shah/EMAIL-018_RE_%20Broker%20licensing%20check-in.eml)

> Haven't confirmed. I'll ask Derek again

### renewal_restatement

Holt restates the December claim for the record in response to the subpoena context; date this communication, not a new renewal.

Support group 1: [EMAIL-029](../../../data/emails/Custodians/Derek_Holt/EMAIL-029_Registration%20status.eml)

> our OR/WA broker registration was finalized in December 2022.

### pilot_scheduling

Nguyen issues the instruction scheduling the pilot; date the scheduling communication, not the future target.

Support group 1: [EMAIL-1501](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1501_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1502](../../../data/emails/Custodians/Craig_Sato/EMAIL-1502_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1503](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1503_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> I'll schedule the pilot for September 5 after the initial production work.

### pilot_first_pass

Cole completes the pilot first pass; reconcile the contemporaneous update with Nguyen's later dated report.

Support group 1: [EMAIL-1503](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1503_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> The pilot first pass is done.

Support group 2: [EMAIL-1505](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1505_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> the archived-packet pilot ran September 5 with Craig's second review on September 6.

### pilot_second_review

Sato reports the second review and its findings about the substantive exceptions.

Support group 1: [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> Second review completed this morning.

Support group 2: [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> The arithmetic ties; the two substantive exceptions are still open.

### pilot_report_to_auditor

Nguyen sends the retrospective pilot summary to the auditor.

Support group 1: [EMAIL-1505](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1505_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> the archived-packet pilot ran September 5 with Craig's second review on September 6.

Support group 2: [EMAIL-1505](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1505_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> We are not presenting it as the missing workpapers for the 2022 quarters or as a test of every packet.

### auditor_scope

Moss describes the supported scope of the remediation pilot.

Support group 1: [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> We'll describe the scope as a three-packet remediation pilot, with one document-reference exception corrected and two acreage reconciliations still open.

### registration_issuance

Assess whether the record establishes the actual OR/WA issuance date in light of Holt's December and June statements and the coverage follow-ups. Classify the finding and give an actual date only if supported.

Checkpoint: `2023-09-08T23:59:59-07:00`.

Support group 1: [EMAIL-045](../../../data/emails/Custodians/Derek_Holt/EMAIL-045_Registration%20finalized.eml)

> our OR/WA broker registration renewal finalized this week.

Support group 2: [EMAIL-018](../../../data/emails/Custodians/Priya_Shah/EMAIL-018_RE_%20Broker%20licensing%20check-in.eml)

> Haven't confirmed. I'll ask Derek again

Support group 3: [EMAIL-761](../../../data/emails/Custodians/IT_Notifications/EMAIL-761_Broker_coverage_worksheet_issuance_unverified.eml)

> The broker coverage worksheet still has the issuance date blank for Bellhaven's Oregon and Washington entries.

Support group 4: [EMAIL-768](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-768_Renewal_ISSUANCE_certificate_OR_WA_issuance_date_only.eml)

> Filing receipts show only when an application was submitted and won't answer the question on their own.

Challenge 1, `repetition_not_independent_proof`: [EMAIL-029](../../../data/emails/Custodians/Derek_Holt/EMAIL-029_Registration%20status.eml)

> our OR/WA broker registration was finalized in December 2022.

### h1_transmittal

Does the record establish that H1 was actually transmitted on the day of Nguyen's tie-out? Distinguish commercial forecasting, permission and completed transmission.

Checkpoint: `2023-09-08T23:59:59-07:00`.

Support group 1: [EMAIL-1482](../../../data/emails/Custodians/Priya_Shah/EMAIL-1482_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> H1 can move on the corrected county figure once Sarah checks the tie-out and Hannah has the owner's acknowledgment in the packet.

Support group 2: [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Sarah's tie-out is still open, so the release box is blank and I haven't put it in the next courier run.

Support group 3: [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Please enter the actual transmittal date when it goes, not today's date by default.

Challenge 1, `forecast_not_execution`: [EMAIL-1479](../../../data/emails/Custodians/Priya_Shah/EMAIL-1479_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1480](../../../data/emails/Custodians/Jay_Whitfield/EMAIL-1480_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1481](../../../data/emails/Custodians/Tom_Reyes/EMAIL-1481_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1482](../../../data/emails/Custodians/Priya_Shah/EMAIL-1482_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1483](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1483_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1484](../../../data/emails/Custodians/Craig_Sato/EMAIL-1484_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1485](../../../data/emails/Custodians/Robert_Denniston/EMAIL-1485_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml), [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> Keep the commercial forecast at nine for now; it shows the upside if the documents arrive.

Challenge 2, `tieout_not_transmittal`: [EMAIL-1486](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1486_Re_Fwd_RE_Fwd_Fwd_Q4_submissions_packet_support.eml)

> I've checked H1's revised application acreage against the county copy and the owner's acknowledgment. Those figures agree.

### pilot_exceptions

Does the second-review completion establish that the two acreage exceptions were closed on that date?

Checkpoint: `2023-09-08T23:59:59-07:00`.

Support group 1: [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> The arithmetic ties; the two substantive exceptions are still open.

Support group 2: [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> We'll describe the scope as a three-packet remediation pilot, with one document-reference exception corrected and two acreage reconciliations still open.

Challenge 1, `review_completion_not_exception_closure`: [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> Second review completed this morning.

### historical_quarterly_tests

Does the September pilot establish when the historical 2022 quarterly controls were performed?

Checkpoint: `2023-09-08T23:59:59-07:00`.

Support group 1: [EMAIL-1498](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1498_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1499](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1499_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1500](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1500_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1501](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1501_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1502](../../../data/emails/Custodians/Craig_Sato/EMAIL-1502_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1503](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1503_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> A pilot on archived packets can show the new procedure operating in September. It cannot establish that the quarterly control operated in 2022 or earlier this year.

Support group 2: [EMAIL-1505](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1505_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1506](../../../data/emails/Custodians/Brenda_Moss/EMAIL-1506_RE_FW_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> We are not presenting it as the missing workpapers for the 2022 quarters or as a test of every packet.

Challenge 1, `later_pilot_not_historical_proof`: [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> Second review completed this morning.

### pilot_asof_august

At this earlier checkpoint, was pilot execution already established, and what actual execution date could be assigned?

Checkpoint: `2023-08-21T23:59:59-07:00`.

Support group 1: [EMAIL-1501](../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1501_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1502](../../../data/emails/Custodians/Craig_Sato/EMAIL-1502_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1503](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1503_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> I'll schedule the pilot for September 5 after the initial production work.

Support group 2: [EMAIL-1502](../../../data/emails/Custodians/Craig_Sato/EMAIL-1502_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> I can do the second review on September 6.

Challenge 1, `after_cutoff`: [EMAIL-1503](../../../data/emails/Custodians/Hannah_Cole/EMAIL-1503_RE_FW_RE_Remediation_workplan_203_follow_up.eml), [EMAIL-1504](../../../data/emails/Custodians/Craig_Sato/EMAIL-1504_RE_FW_RE_Remediation_workplan_203_follow_up.eml)

> The pilot first pass is done.

## Review focus

- Confirm event time, report time and attribution from original and quoted headers.
- Check that the December phrase supports a date interval under T2, not a specific issuance day.
- Check the November 15 timestamps and the distinction between an acreage check and actual transmittal.
- Confirm that the first pass, second review and later report are separate events.
- Assess completeness of alternative evidence and reasonable rule selections; the current oracle is authored, not independently adjudicated.
- Keep source text and oracle assets separate in deployment. This repository is development material, not secret evaluation data.

## Rebuild

From the repository root:

```bash
PYTHONPATH=. python3 benchmark/hidden_gold/chronology/build_assets.py
```

The builder pins existing sources from Task 1, writes the Task 2 oracle and schema,
and updates their hashes in its manifest. It does not write source emails.
After changing task assets, rerun the tests and end-to-end control and refresh the
validation record. Never rebuild labels in response to a model score without review.
