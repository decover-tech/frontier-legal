# Cascade Timber EML Dataset — Realism & Doctrine-Depth Pass (v3)

## Context

This is DecoverAI's synthetic demo dataset (fictional company, fictional people — no real
data) used to demo the review product and to back the "In-House Connect CLE Prep" deck
(`Simplifying eDiscovery and investigations for in-house teams`). The deck's worked-example
slides (Responsiveness, ACP, Work Product, Kovel/consultants, Bare-forwards/mixed-purpose,
the privileged-persons matrix, the A/B/C test-set concept) all lean on this dataset, so the
data needs to actually earn those teaching points, not just assert them via header tags.

Current state (110 docs): every email body is a short, single, unquoted message — even
replies with `In-Reply-To`/`References` headers show none of the prior message text, and
nothing has a signature block. That undercuts realism for a live demo audience. The user
also wants the five doctrines called out in the deck (Responsive / ACP / Work Product /
Kovel / bare-forwards) represented as clean, contrasting worked chains in the data itself —
not just one hero document per concept.

Decisions already confirmed with the user:
- Target size: **250 total documents** (140 new, on top of the existing 110).
- The 4 documents cropped verbatim into deck slides (EMAIL-003, -005, -021, -044) **will
  also** get quoting + signatures — deck screenshots for those 4 slides will need reshooting
  later; full-corpus consistency wins over screenshot stability.

## The 3 realism ideas driving this pass

1. **Real threading.** Every reply/forward gets a rendered quoted-history block beneath the
   new text, reproducing prior message(s) in the sender's own mail-client convention, nested
   one layer per hop up the `References` chain — not just headers implying a thread exists.
2. **Real signatures + per-org fingerprints.** Every substantive (non-autoreply/non-system)
   email ends in a signature matching its sender's organization — Cascade Timber corporate,
   L&L Associates outside-counsel (with a confidentiality footer), Alder Point, Bellhaven,
   GreenAcre, and IRS (with a Privacy-Act-style footer) each look distinct.
3. **Doctrine families as contrast pairs, not single hero docs.** Responsive / ACP / Work
   Product / Kovel / Bare-forward each become a small multi-email chain built around the
   *contrast* the deck teaches (protected vs. unprotected, clear-positive vs.
   clear-negative vs. genuinely-ambiguous) so a reviewer using the tool sees the distinction
   in the actual data, not just in a slide caption.

## Threading & signature spec (applies everywhere)

**Quoting convention** — pick per sender's implied mail client and keep it consistent per
person across the corpus:
- Cascade Timber corporate (Outlook): `-----Original Message-----` / `From:` / `Sent:` /
  `To:` / `Cc:` / `Subject:` block, unindented quoted body underneath.
- Alder Point / Bellhaven / GreenAcre (smaller orgs, Gmail-style): `On <date>, <Name>
  <email> wrote:` followed by `> `-prefixed quoted lines.
- L&L Associates (outside counsel, Outlook): same Original-Message block as Cascade Timber,
  but every layer re-shows the privilege banner if the original had one.
- IRS (Kevin Tran): plain Outlook-style block, minimal formatting — government client.
- Forwards use `---------- Forwarded message ----------` (Gmail-style senders) or a
  `-----Original Message-----` block (Outlook-style senders) reproducing From/Date/
  Subject/To of the original.
- For a 3+-deep thread, each new reply nests one more layer *around* the previous quoted
  block (stacked Original-Message blocks for Outlook senders; increasing `>` depth for
  Gmail-style) — i.e., actually cascades, the way real collected mail does.

**Signature bank** (representative; same shape reused per org, personalized per sender):
- Cascade Timber employee: name / title / "Cascade Timber Holdings, Inc." / phone / email,
  plus a generic corporate confidentiality line.
- L&L Associates (outside counsel): name / title / firm / direct line, plus a law-firm-style
  privileged/confidential footer on every message.
- Alder Point Partners / Bellhaven Advisory / GreenAcre: name / title / org / email, no
  disclaimer (smaller orgs, plainer signoff).
- Kevin Tran (IRS): name / "Revenue Agent, Examination Division" / "Internal Revenue
  Service" / irs.gov email, plus a government confidentiality/Privacy-Act-style footer.
- System/HR/IT/Facilities broadcast mailboxes: no personal signature, org name only.

Auto-generated content (out-of-office autoreplies, calendar invites, IT/HR broadcasts)
stays signature-light/system-styled — realism means these *shouldn't* look hand-signed.

## Doctrine-family builds (new chains, ~50 of the 140 new docs)

Each family below is a small chain designed around a **contrast pair**, directly mirroring
the deck's own framework (privileged-persons matrix, work-product include/exclude/opinion
columns, "same firm opposite answers" Kovel framing, three-tier A/B/C test-set concept):

- **Responsive** — add a clear-negative (mentions the program with no company
  participation — per the deck's own exclude list) and a genuinely-ambiguous document,
  alongside the existing EMAIL-003 clear-positive.
- **ACP** — add a mixed-purpose email (legal advice + commercial reporting in one message,
  per slide 11) and an Upjohn-flavored example (a non-executive employee getting direct
  legal advice from the GC — privilege turns on purpose, not seniority).
- **Work product** — add opinion work product (legal chronology/risk analysis, witness
  interview memo) contrasted with an ordinary-course HR investigation report that is
  *not* work product (pre-existing duty, would've happened regardless of litigation).
- **Kovel** — the centerpiece contrast: outside counsel (L&L) formally engaging a forensic
  accountant/GreenAcre to help assess the whistleblower allegations for litigation
  (protected) vs. Craig Sato (Controller) directly retaining a similar consultant for a
  routine Q3 filing, later just forwarded to Legal FYI (not protected) — plus a
  context-dependent PR-consultant example (Frank Delgado looping in comms support on
  investor messaging).
- **Bare-forward / mixed-purpose** — additional clean FYI-only forwards reaching the GC
  with zero commentary, alongside one with a single ambiguous added line, reinforcing "every
  family member is evaluated on its own content."

## Remaining new volume (~90 of the 140 new docs)

- ~50 docs deepening the existing Coastal Solar narrative: IRS extension grant/response
  from Kevin Tran, whistleblower follow-up interviews, additional privileged board
  threads, additional custodian-side business correspondence.
- ~40 noise docs in the same style as the existing 69 (calendar invites, autoreplies,
  HR/IT/expense traffic, Mountain Ridge decoy items, general chatter) to hold the
  signal-to-noise ratio roughly steady at scale (currently ~34% noise).
- A handful (3–5) of new attachments for the highest-value new chains (witness interview
  memo, forensic-accountant engagement letter, PR one-pager), built with the same
  libraries already used for the existing 22 attachments (`fpdf2`/`openpyxl`, confirmed
  installed) so they match the existing visual style (privilege banners, etc.).

## Execution approach

1. Retrofit all 110 existing `.eml` files in place: add quoted-history blocks to every
   reply/forward, and signatures to every substantive message. DocIDs, Message-IDs,
   `In-Reply-To`/`References` headers, and `X-Decover-*` tags are unchanged — only body
   text grows.
2. Author the ~140 new documents (`EMAIL-111` onward), custodian-folder-per-doc, following
   the same spec, split across the doctrine-family builds, narrative-deepening, and noise
   buckets above.
3. Regenerate `Loadfile_Cascade_Timber.csv` and `.dat` from the final `.eml` set with a
   small Python script (stdlib `email` parser, same field set/format as today) rather than
   hand-maintaining 250 rows — removes a whole class of row/file mismatch risk.
4. Update `README.md` with a new "what changed in this pass" section (new totals, new
   entities if any, the realism/doctrine changes) following the existing doc's own pattern.
5. Verify: spot-parse a sample of new/edited `.eml` files for valid RFC 5322 structure,
   confirm `Message-ID`/`In-Reply-To`/`References` linkage is internally consistent across
   the whole set, confirm loadfile row count == file count, and confirm every doctrine
   family has both sides of its contrast pair present and correctly tagged.

Given the volume (~240 files touched), this will be a long multi-batch session — I'll work
through it in the phases above and check in with progress rather than doing it all silently.
