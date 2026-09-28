# Cascade Timber Holdings — Synthetic Demo Dataset (.eml build)

**All names, companies, and events are fictional.** Built from
`Cascade Timber Data Set (1).xlsx` for demoing DecoverAI's document review,
email analytics, agentic search, and chronology-builder features. Do not use
real client data with this file.

**250 documents total** — the original 30 "hot" documents from the source
workbook (`EMAIL-001`–`EMAIL-030`, content unchanged), 80 documents added in
pass 2 (`EMAIL-031`–`EMAIL-110`), and 140 documents added in this pass
(`EMAIL-111`–`EMAIL-250`) — see "What changed in this pass (v3)" below.

## What's here

- **`Custodians/<Name>/EMAIL-0xx_<subject>.eml`** — all 250 emails as real
  RFC 5322 / MIME messages, one folder per custodian (the mailbox the
  document was collected from — not always the sender, since a mailbox
  contains received mail too; e.g. `EMAIL-053` is sent by Marcus Webb but
  filed under `Elena_Marlowe` because it's collected from her inbox).
- **`Loadfile_Cascade_Timber.csv`** — human-readable metadata index.
- **`Loadfile_Cascade_Timber.dat`** — the same index as a Concordance-style
  load file (field delimiter ASCII 20, quote ASCII 254, in-field newline
  ASCII 174).

DocID order is collection order, not chronological order — `EMAIL-031` on
extends the timeline both earlier (back to Nov 2021, pre-launch) and later
(through September 2023) than the original `EMAIL-001`–`030` range. `DATESENT`
in the load file is the authoritative chronological field.

## What changed in this pass (v3 — realism & doctrine depth)

This pass makes the data earn the teaching points in the "In-House Connect
CLE Prep" deck instead of asserting them via header tags.

### Realism retrofit (all 250 documents)

- **Real threading.** Every reply/forward whose parent is in the corpus now
  carries a rendered quoted-history block beneath the new text, nesting one
  layer per hop up the `References` chain. Quoting follows the sender's mail
  client: Outlook-style `-----Original Message-----` blocks (Cascade Timber,
  L&L Associates, IRS) vs. Gmail-style `On <date> <name> wrote:` with `>`
  prefixes (Alder Point, Bellhaven, GreenAcre, and the v3 external
  consultants). Forwards use `---------- Forwarded message ----------`
  (Gmail-style senders) or an Original-Message block (Outlook-style).
  Privilege banners re-show at every quoted layer.
- **Real signatures, per-org fingerprints.** Every substantive
  (non-autoreply/non-system) email ends in a signature matching its sender's
  org: Cascade Timber corporate block with confidentiality line; L&L block
  with law-firm privileged/confidential footer; plain blocks for Alder
  Point, Bellhaven, GreenAcre; IRS block with a Privacy-Act-style footer for
  Kevin Tran. System/HR/IT/Facilities broadcasts carry org-name-only
  signoffs; autoreplies and calendar invites stay signature-light.
- **Logo signatures for execs.** Messages from the executive/external-facing
  Cascade Timber senders (Elena Marlowe, Robert Denniston, John Ellery,
  Frank Delgado) carry the company logo as an **inline image** in their
  signature — the classic `multipart/related` + `image001.png`
  (Content-Disposition: inline) pattern seen in real Outlook collections.
  The `ATTACHMENTS` load-file column lists only true attachments
  (`Content-Disposition: attachment`), so these inline graphics don't
  inflate attachment counts — the same filtering a review platform applies.
  Source artwork is in `Logos/`.
- DocIDs, Message-IDs, `In-Reply-To`/`References` headers, and `X-Decover-*`
  tags are unchanged from pass 2 for `EMAIL-001`–`110` — only body text
  grew. This includes the four documents cropped into deck slides
  (`EMAIL-003`, `-005`, `-021`, `-044`), which now also show quoting +
  signatures (those slide screenshots need reshooting).

### Doctrine families as contrast pairs (EMAIL-111–157)

Each doctrine in the deck is now a small multi-email chain built around the
*contrast* the deck teaches, not a single hero document:

| Family | DocIDs | Contrast pair |
|---|---|---|
| Responsiveness | `EMAIL-003` (existing clear-positive); `111`–`112`; `113`–`115`; `116`–`117` | clear-negative (industry coverage mentioning the program, no company participation) and genuinely-ambiguous docs ("southern tracts file") alongside the existing clear-positive |
| Attorney-client privilege | `118`–`119`; `120`–`122`; `123`–`124`; `125`–`126` | mixed-purpose email (legal advice + commercial pricing in one message); Upjohn-flavored GC advice to a non-executive (land records administrator Hannah Cole); vs. pure logistics and purely social emails involving counsel (not privileged) |
| Work product | `127`–`130`, `134`–`136`; vs. `131`–`133` | opinion work product (draft chronology/risk analysis, witness interview memos, exposure analysis — new tag `Privileged Work Product`) vs. an ordinary-course HR investigation report that is *not* work product |
| Kovel / consultants | `137`–`141`; vs. `142`–`145`; `146`–`149` | L&L formally engaging a forensic accountant (Whitaker) at the direction of counsel (protected) vs. the Controller *directly* retaining a tax consultant for a routine Q3 filing, later forwarded to Legal FYI (not protected); plus a context-dependent PR-consultant pair (John's structuring advice privileged, direct IR engagement not) |
| Bare-forward / mixed purpose | `150`–`151`, `152`–`153`; `154`–`157` | clean FYI-only forwards reaching the GC with zero commentary (still not privileged), one forward with a single ambiguous added line, and a GC reply that confers no privilege — every family member evaluated on its own content |

### Narrative deepening (EMAIL-158–211)

- IRS examination correspondence with Agent Kevin Tran after the extension:
  production schedule, follow-up requests, production receipt.
- Whistleblower follow-up interview logistics (non-privileged scheduling).
- Additional privileged board threads: D&O notice advice, pause scenarios
  executive session, board resolution review.
- Custodian-side business correspondence: 2022 Alder Point/Bellhaven deal
  flow (broker pipeline, parcel scouting, onboarding, surveys, Q4 targets),
  Cascade internal program ops (compliance framework, revenue recognition,
  investor messaging, broker oversight), post-pause business threads, and
  non-privileged L&L administrative traffic.

### Noise (EMAIL-212–250)

39 new noise documents in the same style as the existing 69: 4 calendar
invites with real `.ics` attachments, 4 autoreplies, 4 IT notices, 4 HR
broadcasts, 4 expense/travel emails, 6 Mountain Ridge decoys, 10 general
chatter, 3 misc broadcasts. Total noise is now 82 of 250 documents (~33%),
holding the pass-2 signal-to-noise ratio roughly steady at scale.

### New entities in this pass

| Name | Role | Affiliation |
|---|---|---|
| Hannah Cole | Land Records Administrator (non-executive; Upjohn example) | Cascade Timber Holdings |
| Dana Whitaker, CPA/CFF | Forensic accountant engaged by L&L (Kovel) | Whitaker Forensic Accounting |
| Owen Larsen | Tax consultant retained directly by the Controller | Larsen Tax Advisory |
| Rosa Kim | PR consultant engaged directly by IR | Northstar Communications |

Three custodian folders were added (`Hannah_Cole`, `Craig_Sato`,
`Frank_Delgado`) — their mailboxes are now treated as collected.

### New attachments in this pass (5, embedded as real MIME parts)

| DocID | Attachment |
|---|---|
| EMAIL-129 | `Privileged_Witness_Interview_Memo_Cole.pdf` — work-product interview memo (7/21 H. Cole interview) |
| EMAIL-137 | `Kovel_Engagement_Whitaker_Forensic.pdf` — L&L's engagement letter to the forensic accountant |
| EMAIL-140 | `Whitaker_Parcel_Payment_Analysis.xlsx` — forensic payment-tracing schedule (marked prepared at direction of counsel) |
| EMAIL-144 | `Larsen_Q3_Provision_Memo.pdf` — routine tax-provision memo (no banner — the unprotected contrast) |
| EMAIL-149 | `Northstar_Coastal_Solar_Pause_OnePager.pdf` — PR messaging one-pager |
| 4 calendar invites | `invite.ics` — on EMAIL-212/213/214/215 |

### Load files are now generated, not hand-maintained

`Loadfile_Cascade_Timber.csv` and `.dat` are regenerated from the final
`.eml` set by script (stdlib `email` parser; same field set and format as
before — byte-identical for the original 110 rows). `CONTAINS_PII` remains
Yes for exactly `EMAIL-014`, `EMAIL-022`, and `EMAIL-048`.

## What was added in pass 2 (v2)

**41 new substantive documents (`EMAIL-031`–`071`)** extending the original
narrative:
- Pre-history: the 2021 business case and Alder Point's original partnership
  proposal, with privileged legal review of the deal.
- The evidence trail behind `EMAIL-003`'s eligibility concern: the original
  parcel data, and an independent land surveyor (GreenAcre) confirming the
  acreage discrepancy on 4 of 8 parcels.
- Bellhaven's *internal* knowledge of its own OR/WA registration gap
  (`EMAIL-041`/`042`, Renee Ford → Derek Holt) — predates and contradicts the
  soft-pedaled version Derek gives the client in the original `EMAIL-009`.
- The internal review build-out: paralegal/associate-level document
  collection, interim findings memos, board updates, budget/TAR workflow
  discussion — all privileged, all from L&L Associates (Grace Lin, Mia Chen,
  Alan Brooks).
- Subpoena follow-through: forwarding to outside counsel, an extension
  request/grant with IRS Agent Kevin Tran, IT's technical collection scope,
  and HR flagging a departing custodian's mailbox.
- Aftermath: investor relations fielding a question about the pause, board
  follow-up, and the Q3 financial impact.

**69 new "noise" documents (`EMAIL-072`–`110`)** — routine business traffic
with no case relevance, mixed into the same custodian mailboxes the way a
real collection would be:
- 5 calendar invites (**with real `.ics` attachments**)
- 6 out-of-office autoreplies
- 4 IT security notices, 4 HR announcements, 4 expense/travel emails
- 6 emails about **"Mountain Ridge Reforestation Credit"** — a similarly-named
  but unrelated program, included as a **false-positive test**: none of these
  should match a Coastal Solar search query
- 10 emails of general unrelated chatter (lunch plans, conference small talk,
  a fantasy football pool, etc.)

All noise documents are tagged `Not Responsive`.

### Entities introduced in pass 2

| Name | Role | Affiliation |
|---|---|---|
| Nina Alvarez | Regional Sales Rep (Southwest) | Alder Point Partners |
| Renee Ford | Compliance Officer | Bellhaven Advisory |
| Marcus Webb | Board Chair | Cascade Timber Holdings |
| Frank Delgado | VP Investor Relations | Cascade Timber Holdings |
| Craig Sato | Controller | Cascade Timber Holdings |
| Dan Osei | IT Director | Cascade Timber Holdings |
| Wendy Park | HR Director | Cascade Timber Holdings |
| Alan Brooks | Paralegal | L&L Associates |
| Mia Chen | Associate | L&L Associates |
| Kevin Tran | Revenue Agent | Internal Revenue Service |
| GreenAcre Land Survey Co. | Independent land surveyor | External vendor |

Plus several service/system mailboxes (`IT Notifications`, `Human Resources`,
`Facilities`) used for company-wide broadcast noise.

## Attachments (27 total, embedded as real MIME parts)

### Original 9 (unchanged)
| DocID | Attachment |
|---|---|
| EMAIL-001 | `Coastal_Solar_Marketing_Deck.pptx` |
| EMAIL-009 | `Bellhaven_Coastal_Solar_Placement_Agreement.pdf` |
| EMAIL-012 | `Privileged_Coastal_Solar_Risk_Assessment.pdf` |
| EMAIL-014 | `Q4_Board_Deck_DRAFT.pptx` — placeholder SSN, **PII redaction demo** |
| EMAIL-020 | `Privileged_Preliminary_Assessment_Whistleblower.pdf` |
| EMAIL-021 | `LL_Associates_Engagement_Letter.pdf` |
| EMAIL-022 | `Custodian_List.xlsx` — row 14 has a stray MRN, **PII redaction demo** |
| EMAIL-023 | `IRS_Subpoena_Coastal_Solar_Credit_Program.pdf` |
| EMAIL-024 | `Legal_Hold_Notice_Coastal_Solar.pdf` |

### Added in pass 2
| DocID | Attachment |
|---|---|
| EMAIL-033 | `Coastal_Solar_Partnership_Proposal.pptx` — Alder Point's original 2021 pitch deck |
| EMAIL-037 | `Land_Parcel_Data_Northwest.csv` — the underlying parcel/acreage data |
| EMAIL-039 | `GreenAcre_Survey_Findings.pdf` — independent surveyor's discrepancy findings |
| EMAIL-046 | `Whistleblower_Complaint_Text.pdf` — full complaint text |
| EMAIL-048 | `Custodian_List.xlsx` — **same file as EMAIL-022**; Alan Brooks' original draft (Feb 28), later forwarded to Grace Lin who flags the PII issue in EMAIL-022 (Mar 1) — a deliberate near-dupe for testing dedup/family detection |
| EMAIL-050 | `Privileged_Interim_Findings_Memo.pdf` |
| EMAIL-059 | `Custodian_Mailbox_Export_List.xlsx` — IT's technical export scope (no PII) |
| EMAIL-071 | `Q3_Financial_Impact_Coastal_Solar_Pause.xlsx` |
| 5 calendar invites | `invite.ics` — real iCalendar attachments on EMAIL-072/073/074/075/076 |

### Added in this pass (v3)
See the table in the v3 section above (EMAIL-129/137/140/144/149 plus 4
invites).

## Known entity-resolution / demo wrinkles (carried over + new)

- **Jay Whitfield** signs `EMAIL-007` as **"Kane"** from the same mailbox —
  alias/entity-resolution test case (his signature block on that message also
  reads "Kane").
- **`EMAIL-014`** (placeholder SSN) and **`EMAIL-022`/`048`** (placeholder
  MRN, same file appearing twice) are the PII/redaction demo documents.
- **`EMAIL-041`/`042`** (Bellhaven's internal awareness of its own
  registration gap) directly contradicts the softened explanation Derek Holt
  gives the client in `EMAIL-009` — a good "what did they really know"
  document pair.
- **"Mountain Ridge Reforestation Credit"** (`EMAIL-095`–`100`, plus new
  `EMAIL-232`–`237`) is a decoy program for testing search precision — it
  should never surface on a Coastal Solar query.
- 43 of 250 documents are tagged **privileged**; all carry an
  `X-Decover-Privileged: Yes` header and an in-body privilege banner. Two
  privilege flavors now exist as tags: `Privileged Legal Advice` (36) and
  `Privileged Work Product` (7, new this pass).
- 82 of 250 documents are tagged **`Not Responsive`** noise, giving the
  corpus a realistic signal-to-noise ratio for search/filter demos.
- The Kovel contrast pair is deliberate in both directions: `EMAIL-137`–`141`
  (L&L-engaged forensic accountant, protected) vs. `EMAIL-142`–`145`
  (business-retained tax consultant, not protected — even after being
  forwarded to the GC "FYI").

## Other source tabs (not rebuilt as files, still authoritative)

The original workbook's **Entities**, **Chronology**, and **Search Queries**
tabs are unchanged and still describe the core entity list, case chronology,
and sample agentic-search prompts (with expected DocID hits) for the
original 30 documents. The new entities and documents above extend, but do
not contradict, that material.
