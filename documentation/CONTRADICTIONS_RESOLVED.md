# CONTRADICTIONS_RESOLVED.md: four known contradictions

Sources: `documentation/suggestions.md` (Correctness and Domain-boundaries rows) and the README "Known issues".
Ground truth: `CASE_BIBLE.md` rev.3 and `EVIDENCE_ARCS.md` rev.2. Date: 2026-09-28.

**Where the contradictions actually were.** The outlier values (26 U.S.C. § 7602, 601 SW Second Ave,
`kevin.tran.exam@irs-example.gov`) are **not in EMAIL-023 or its PDF attachment**. They are in the reference
document `definitions/Subpoena_Enhanced.docx`, and the three other `definitions/*.docx` files repeat the
subpoena's ZIP code 97204 in their header blocks. The EMAIL-023 attachment
`IRS_Subpoena_Coastal_Solar_Credit_Program.pdf` gives no statute, no Cascade street address and no
contact details for Tran.

**Edit method.** Emails: only the decoded text/plain part, plus the text/html part where one exists, kept in
sync. Each part was re-encoded with its original charset and CTE (quoted-printable or 8bit), and the new
payload was spliced into the raw file. Every header, MIME boundary, inline image and attachment is
byte-identical; the check compared the before and after state for all changed files. DOCX: string
replacement inside single `<w:t>` runs of `word/document.xml`. Every other zip entry was copied
byte-for-byte with the same order and compression. The files were rendered with LibreOffice to confirm
they still open.

---

## 1. Kevin Tran: one IRS identity

**Decision.** There is one canonical identity, based in the IRS Portland field office (bible §5 Places).

| Field | Canonical value | Why |
|---|---|---|
| Name / title | Kevin Tran, Revenue Agent, Examination Division, Internal Revenue Service | Seed signature 057/158–162 |
| Email | `kevin.tran@irs.gov` | Locked: it appears in the From/To headers of about 20 emails, and headers may not change |
| Phone | **(503) 555-0148** | The 503 area code puts him in Portland, as the bible requires. The number is the one already on the summons document. 555-01xx is the reserved fictional range. |
| Disclaimer | IRS Privacy Act / 26 U.S.C. § 6103 notice (seed 057 wording) | |

**Three variants were found, not two:**
1. The seed signature `(202) 555-0131 | kevin.tran@irs.gov`: 7 occurrences in 6 emails, including quoted layers.
2. The generated emails carried a **Cascade Timber signature block** for Tran ("Revenue Agent / Cascade
   Timber Holdings, Inc. / 1200 Forest Park Way… / (503) 555-0100 | kevin.tran@irs.gov" + Cascade
   confidentiality footer): 5 emails, one with an HTML part. Nothing quotes these emails.
3. The summons document: `kevin.tran.exam@irs-example.gov`, (503) 555-0148.

**Files changed (11 emails + 1 DOCX):**
- Phone (202) 555-0131 → (503) 555-0148, own text and quoted layers: EMAIL-057, 158, 159, 160, 161, 162 (162 twice).
- Cascade block → canonical IRS signature + IRS disclaimer: EMAIL-1051 (plain + HTML), 1052, 1065, 1125, 1135.
- `definitions/Subpoena_Enhanced.docx`: `kevin.tran.exam@irs-example.gov` → `kevin.tran@irs.gov`.

**Result.** `(202) 555-0131`: 0 occurrences. `irs-example`: 0. Tran-with-Cascade-signature: 0.
`(503) 555-0148`: 13 occurrences in email text.

**Left as documented noise (header-locked):**
- Tran's seed emails (057, 158, 160, 162) carry `-0400` Date offsets, which is Eastern time. For a
  Portland agent this is a client or server time-zone artifact. It is not an identity fact, and changing
  it would mean editing the Date header.
- Some generated internal preservation or review notes are addressed *to* Tran in their headers:
  EMAIL-1070, 1102, 1107, 1119, 1124 (dated 5/23/23), 1126, 1130. Several Tran-sent generated notes also
  read like internal review-team text, for example EMAIL-1051/1058 "segregating potentially privileged
  material… for counsel's call". These are generator routing defects. Fixing them would require header
  changes or rewriting the body content, so they are out of scope here.

## 2. Cascade Timber address

**Decision.** The canonical address is **1200 Forest Park Way, Suite 900, Portland, OR 97209**. It appears
1,714 times across 699 emails, with no competing street address anywhere in the email corpus.

**Files changed (0 emails, 4 DOCX):**
- `definitions/Subpoena_Enhanced.docx`: "601 SW Second Avenue, Suite 1800, Portland, OR 97204" → canonical.
- `definitions/Responsiveness.docx`, `Work_Product.docx`, `Attorney_Client_Privilege.docx`: header block
  "Attn: Legal Department, Portland, OR 97204" → "… 97209".
- The IRS's own place of production, "1220 SW 3rd Ave, Portland, OR 97204", is the IRS address, not
  Cascade's, so it was kept.

**Not a contradiction:** EMAIL-943's quoted history ends in a truncated line, "1200 Forest Park Way,
Suite 900, Portland". It is the same address, cut off by the quote.

**Left as documented noise (out of scope, reported):** about 98 generated emails give **external** senders
the Cascade signature block with the generic (503) 555-0100 number. Affected senders: Grace Lin
(42 emails), Alan Brooks (26), Mia Chen (19), Dan Whitaker (11); EMAIL-1138 is one example. The address
itself is canonical in all of them. The defect is the sender's organization, not a second address, so it
belongs to the `thread_kit rewrite` signature pass.

## 3. Deadline chain

**What didn't add up.** The instrument issued 5/23 with a 21-day return (6/13). A one-week extension was
requested 5/25 and granted 5/31, which gives 6/20. Then **EMAIL-027 (6/21)** works to "the three-week
deadline", one day after 6/20 had passed. **EMAIL-158 (7/5)** said "The extension granted May 31 sets the
production deadline for August 31, 2023", which a one-week extension cannot produce.

**Decision: resolve with the smallest seed edit, and keep the locked phrases.** "1-week ext (056/057)",
"three-week deadline" (027) and "Aug-31 schedule" (158) are all locked in bible §0/§3/§4, so none of them
was reworded. The only arithmetic error is 158 attributing 8/31 to the May 31 grant. The intended
timeline, now stated in bible §0:

| Date | Event | Evidence |
|---|---|---|
| 5/23/23 | Summons ("subpoena") issued; 21-day return, due 6/13 | 023 (+ PDF), 054/055 |
| 5/25 → 5/31 | One-week extension requested, then granted: due **6/20** | 056 / 057 |
| 6/13 | Legal hold issued on the original return date (a bad fact, deliberately kept) | 024 |
| 6/20 | Interim three-week extension agreed by phone: due **7/11** | 027 "three-week deadline" (6/21); 065 "extended deadline" (6/24) |
| late June | Call sets the final deadline of **8/31** with rolling production | 158 "confirming our call last week" |
| 7/5–7/6 | Written confirmation; schedule due 7/14; first batch week of 7/24 | 158 / 159 |
| 7/31 | Bridge memo memorializes the chain with dates | 1138 |

**Files changed (3 emails):**
- EMAIL-158 and the quoted copy in EMAIL-159: "The extension granted May 31 sets the production deadline
  for August 31, 2023." → "Following the one-week extension granted May 31 and the three-week interim
  extension of June 20, the production deadline is now August 31, 2023." Nothing else quotes this sentence.
- EMAIL-1138, "Interim bridge memo — extension chain (dated)", plain + HTML. It was a placeholder with no
  dates; it now gives the dated chain (5/25, 5/31, 6/13 → 6/20, 6/20 → 7/11, late-June call, 7/5 → 8/31).
  Nothing quotes this email. Grace Lin's misattributed Cascade signature on it was left alone (see §2 noise).

The bridge stays join-required, as Arc H and the CTH-AGENT-008 gold require: 057 + 027/065 + 158/159 +
1138. No single memo decides it, and no memo is backdated (1138 is dated after the events it records).

**Left as documented noise (header-locked):** four generated "Review timeline note (internal) —
extension chain (dated)" emails predate the instrument: EMAIL-1087 (2/24/23), 1091 (4/24/23),
1114 (5/15/23) and 1075 (5/22/23). The anachronism is in the Subject header. Their bodies are generic
("…against the current deadline"). They need to be re-dated, re-subjected or dropped at the generator
level, not patched in their bodies.

## 4. "Subpoena" versus 26 U.S.C. § 7602

**Real law:** § 7602(a) authorizes the IRS to examine records and to **summon** persons to produce them.
An administrative summons is enforced in federal district court under §§ 7402(b) and 7604. In a civil
examination the IRS does not issue a "subpoena duces tecum"; a subpoena would come from a grand jury or
a court (for example the Tax Court), not from a revenue agent.

**Options weighed:**
- **(b) Rename to "summons" everywhere: rejected.** It is not achievable under the header lock, because
  "subpoena" appears in locked Subject headers (e.g. EMAIL-023 "IRS subpoena received", 056/057, 204/205).
  It would also touch hundreds of bodies, the rules.json `\bsubpoena` cutoff, the bible and the benchmark
  prompts and gold. That is the most change for no accuracy gain over (a).
- **(c) Keep everything and add a disclaimer: rejected.** The document would still state, as an operative
  instrument, that § 7602 authorizes a subpoena duces tecum. That teaches a false real-law fact, which
  violates the domain-boundaries gate.
- **(a) Fix the instrument and its citation: chosen.** No statute authorizes an IRS revenue agent to issue
  a civil subpoena, so "cite an appropriate authority for a subpoena" is not possible. The accurate fix is
  to re-frame the formal instrument as what § 7602 actually authorizes, a **summons**, and to treat
  "subpoena" in correspondence as the colloquial shorthand that business people, and often lawyers, use
  for an IRS summons. This is realistic and changes no email.

**Files changed (0 emails, 2 DOCX):**
- `definitions/Subpoena_Enhanced.docx`:
  - title "SUBPOENA DUCES TECUM" → "SUMMONS"
  - "YOU ARE HEREBY COMMANDED" → "YOU ARE HEREBY SUMMONED AND REQUIRED" (Form 2039 wording)
  - "Failure to comply with this subpoena" → "…this summons"
  - caption "In the matter of: UNITED STATES v. CASCADE TIMBER HOLDINGS, INC." → "…CASCADE TIMBER
    HOLDINGS, INC." An administrative summons is captioned with the taxpayer; "United States v." implies
    a pending lawsuit.
  - one sentence added to the synthetic-document footer stating the real-law rule and the corpus's
    informal "subpoena" usage
  - the § 7602 and §§ 7402(b)/7604(a) citations were already correct for a summons and were kept
- `definitions/Responsiveness.docx`: "the IRS Subpoena Duces Tecum (Case No. EX-2023-04471)" → "the IRS
  summons issued under 26 U.S.C. § 7602 (Case No. EX-2023-04471; called 'the subpoena' in the corpus and
  below)".
- `CASE_BIBLE.md` §0 records the framing.
- `rules.json`: unchanged. The `\bsubpoena` cutoff term still matches the corpus wording, and "summons"
  appears in no email.

**Left as documented noise / follow-up (PDF, not regenerated):** the EMAIL-023 attachment
`IRS_Subpoena_Coastal_Solar_Credit_Program.pdf` is titled "SUBPOENA DUCES TECUM" on IRS letterhead and
says "Failure to comply with this subpoena…". It cites no statute, so it asserts no false citation, but
it is now out of step with the summons framing. **Recommended:** regenerate it with the title "SUMMONS"
and the wording "this summons". Only the attachment payload would change; there is no `tools/doc_kit`
library entry for it yet. The filename `Subpoena_Enhanced.docx` was also kept, to avoid breaking references.

---

## Summary of changes

| Item | Emails changed | Other files |
|---|---|---|
| 1 Tran identity | 11: 057, 158, 159, 160, 161, 162, 1051, 1052, 1065, 1125, 1135 | Subpoena_Enhanced.docx |
| 2 Cascade address | 0 | 4 × definitions/*.docx |
| 3 Deadline chain | 3: 158, 159 (also in item 1), 1138 | — |
| 4 Summons framing | 0 | Subpoena_Enhanced.docx, Responsiveness.docx |
| **Total** | **12 unique emails** (seed: 057, 158–162; generated: 1051, 1052, 1065, 1125, 1135, 1138) | 4 DOCX; CASE_BIBLE.md (§0, §5, §8, §11); EVIDENCE_ARCS.md (Arc H, conflict flags) |

Benchmark gold that references these items (not edited here):
- `benchmark/hidden_gold/flagship_gold.jsonl` CTH-AGENT-008: `must_qualify` "Tran canonical-contact
  duality as open defect"; `unknowns` "interim 6/13->8/31 bridge memos".
- `benchmark/README.md` line 64: the Tran, address and deadline items are described as preserved noise.
