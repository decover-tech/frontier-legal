#!/usr/bin/env python3
"""Rebuild standalone exhibits in data/emails/Exhibits/ (fpdf2, same layout as the originals).

The exhibits are not attached to any email, so they can be regenerated without touching the corpus.
Only the exhibits listed in SPECS are built here; the placement batches (EX-005..010), the Larsen
confirmations and the Moss engagement letter are unchanged originals.

Figures are reconciled to the executed contracts in data/contracts/ (tools/doc_kit/library/*.json)
and to CASE_BIBLE.md §2. See output/dataset_inconsistency_report.md ("Resolution log") for why.

Usage: python3 tools/exhibit_kit/build_exhibits.py [EX-003 EX-004 ...]   (default: all in SPECS)
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "emails" / "Exhibits"
SUBTITLE = "FICTIONAL DEMONSTRATION DOCUMENT -- USA v. Cascade Timber Holdings, Inc."
BUILD_DATE = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)

# Footer label per exhibit status (was "EXECUTED COPY" on every exhibit, including the draft).
STATUS_LABEL = {
    "executed": "EXECUTED COPY",
    "conformed": "CONFORMED COPY OF EXECUTED AGREEMENT",
    "draft": "DRAFT -- NOT EXECUTED",
    "file-stamped": "FILE-STAMPED RECEIPT",
    "recorded": "RECORDED COPY",
    "issued": "ISSUED CERTIFICATE",
}


class Exhibit(FPDF):
    def __init__(self, ex_id, label):
        super().__init__(format="A4", unit="mm")
        self.ex_id, self.label = ex_id, label
        self.set_margins(11, 10, 11)
        self.set_auto_page_break(True, 20)
        self.set_creation_date(BUILD_DATE)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120)
        self.cell(0, 10, f"Exhibit {self.ex_id} | {self.label} | Page {self.page_no()}/{{nb}}", align="C")


def render(filename, ex_id, status, title, blocks, meta_title=None):
    """blocks: list of ("h", text) heading, ("p", text) paragraph, ("sig", [lines]) signature block."""
    pdf = Exhibit(ex_id, STATUS_LABEL[status])
    pdf.set_title(meta_title or title.replace(" -- ", " — "))
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100)
    pdf.cell(0, 5, SUBTITLE, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0)
    pdf.ln(2)
    for kind, body in blocks:
        if kind == "h":
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, body, new_x="LMARGIN", new_y="NEXT")
        elif kind == "p":
            pdf.set_font("Helvetica", "", 9.5)
            pdf.multi_cell(0, 5, body, align="J", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "sig":
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 9.5)
            for line in body:
                pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(OUT / filename))


# ---------------------------------------------------------------- specs

SPECS = {}


def spec(ex_id, filename, status, title, blocks, meta_title=None):
    SPECS[ex_id] = dict(filename=filename, ex_id=ex_id, status=status, title=title,
                        blocks=blocks, meta_title=meta_title)


# EX-001: Section 6 was referenced but missing; Exhibit C was referenced but not included.
spec("EX-001", "EX-001_Partnership_Agreement_CTH_AlderPoint.pdf", "executed",
     "COASTAL SOLAR PROGRAM AGREEMENT", [
         ("p", 'This Coastal Solar Program Agreement (the "Agreement") is entered into as of December 22, 2021, by and '
               'between Cascade Timber Holdings, Inc., an Oregon corporation ("CTH"), and Alder Point Partners, LLC '
               '("Alder Point").'),
         ("h", "1. PROGRAM ADMINISTRATION"),
         ("p", "Alder Point shall administer the Coastal Solar Credit Program, including parcel assembly, submission "
               "packets, and placement coordination, subject to CTH oversight and to the compliance framework to be "
               "agreed by the parties and attached as Exhibit C."),
         ("h", "2. PARCEL ELIGIBILITY"),
         ("p", "All parcels submitted under the Program shall meet applicable program eligibility standards as "
               "reflected in county records and independent survey verification where obtained."),
         ("h", "3. REPRESENTATIONS"),
         ("p", "3.1 CTH represents it has authority to enter this Agreement. 3.2 Alder Point represents that its "
               "eligibility screening meets applicable program standards (the \"Screening Representation\"). Alder "
               "Point shall maintain screening procedures and make underlying records available to CTH compliance "
               "on request."),
         ("h", "4. COMPENSATION"),
         ("p", "Alder Point shall receive an administrative fee of eight percent (8%) of placement proceeds, "
               "accounted for as an operating expense of the Program and not netted against recognized revenue."),
         ("h", "5. TERM"),
         ("p", "Initial term through December 31, 2023, unless paused or terminated under Section 6."),
         ("h", "6. PAUSE AND TERMINATION"),
         ("p", "CTH may pause new submissions or placements under the Program, or terminate this Agreement, on thirty "
               "(30) days' written notice to Alder Point, or immediately on written notice if Alder Point materially "
               "breaches Section 3. Section 3.2 (records) and Section 4 (as to proceeds received before the "
               "effective date of any pause or termination) survive."),
         ("sig", ["/s/ Elena Marlowe", "Elena Marlowe, Chief Executive Officer, CTH", "Date: December 22, 2021"]),
         ("sig", ["/s/ Priya Shah", "Priya Shah, VP Business Development, Alder Point (authorized signatory)",
                  "Date: December 22, 2021"]),
         ("sig", ["[Exhibit C (compliance framework) is not attached to this copy.]"]),
     ])

# EX-002: content is a draft; only the footer label was wrong.
spec("EX-002", "EX-002_Partnership_Agreement_DRAFTv3.pdf", "draft",
     "COASTAL SOLAR PROGRAM AGREEMENT -- DRAFT v3 (redline excerpt)", [
         ("p", "DRAFT v3 -- circulated December 15, 2021. Brackets show proposed language under review; not executed."),
         ("p", "[3.2 Alder Point represents that its eligibility screening meets applicable program standards.] -- "
               "inserted per CTH legal review (see transmittal). Alder Point comments pending in margin: \"confirm "
               "operations can support before signing.\""),
         ("p", "Margin note (handwritten transcription): \"E -- added per J.E. 12/10 memo. P.S. to confirm.\""),
     ])


# EX-003/004: conformed to the executed scans in data/contracts/KW0x-OPTION (the April 2022 dates and
# lump-sum August deadlines contradicted the executed agreements and EMAIL-402).
def option(ex_id, filename, parcel, eff, acres, closing_days, adjoining, owner_date, optionee_date):
    spec(ex_id, filename, "conformed", f"OPTION AGREEMENT -- {parcel} (Clearwater Land LLC)", [
        ("p", f'This Option Agreement is entered into as of {eff} (the "Effective Date"), by and between Clearwater '
              f'Land LLC, an Oregon limited liability company, owner of record of certain Klamath County land off '
              f'Route 97 ("Owner"), and Alder Point Partners ("Optionee"), with respect to parcel {parcel} '
              f'(Assessor acreage {acres} acres), as described in Exhibit A (legal description and tax lot). '
              f'{adjoining}'),
        ("h", "1. OPTION TERM"),
        ("p", "Twelve (12) months from the Effective Date, with one six (6) month extension at Optionee's election."),
        ("h", "2. OPTION FEE (SCHEDULE 1)"),
        ("p", "Option Fee of $12,000, payable in three Option Payments of $4,000 each: the Initial Option Payment "
              "within five (5) business days after the Effective Date; the Second Option Payment on or before the "
              "180th day after the Effective Date; and the Third Option Payment on or before the 270th day after the "
              "Effective Date, subject to Optionee's deferral right (Section 3.3, deferred payments capped at the "
              "end of the Option Term) and prepayment right (Section 3.4). Option Payments are credited against the "
              "Purchase Price at Closing."),
        ("h", "3. PURCHASE PRICE; CLOSING"),
        ("p", f"$1,150 per acre of Net Acreage as shown on the Survey. Closing within {closing_days} days after "
              f"Optionee's Exercise Notice. Owner may continue existing grazing use until Closing."),
        ("sig", ["OWNER: CLEARWATER LAND LLC, an Oregon limited liability company", "/s/ Gordon L. Pruitt",
                 "Gordon L. Pruitt, Managing Member", f"Date: {owner_date}"]),
        ("sig", ["OPTIONEE: ALDER POINT PARTNERS", "/s/ Tom Reyes", "Tom Reyes, Land Acquisition Manager",
                 f"Date: {optionee_date}"]),
        ("sig", ["[Conformed summary of the wet-signed agreement; the executed scan controls. "
                 "Exhibit A not reproduced.]"]),
    ])


option("EX-003", "EX-003_Option_KW-01_Clearwater.pdf", "KW-01", "January 10, 2023", "148.62", "ninety (90)",
       "The Property adjoins other land of Owner to the south, which is the subject of a separate Option "
       "Agreement between the Parties dated September 20, 2022.", "January 6, 2023", "January 10, 2023")
option("EX-004", "EX-004_Option_KW-02_Clearwater.pdf", "KW-02", "September 20, 2022", "111.87", "sixty (60)",
       "The Property adjoins other land of Owner to the north, which is the subject of a separate option "
       "agreement being negotiated between the Parties.", "September 19, 2022", "September 20, 2022")


# EX-011..016: lots 1, 2 and 4 conformed to the executed long-form agreements in
# data/contracts/CSC-CPA-BELLHAVEN; lots 3, 5, 6 keep their amounts but get real dates.
def lot(ex_id, n, buyer, face, cents, cash, date, refund_days, buyer_sig, seller_date=None, note=None):
    body = [
        ("p", f"Agreement dated {date} for purchase of Coastal Solar credits with aggregate face value of {face} for "
              f"cash consideration of {cash} (Unit Price ${cents / 100:.2f} per $1.00 of face), delivery by credit "
              f"certificate per the parcel schedule in Exhibit A. Seller: Cascade Timber Holdings, Inc., by Alder "
              f"Point Partners, as Administrator; Bellhaven Advisory, as Placement Agent."),
        ("p", "Seller disclosure: credits derive from conservation parcels described in Exhibit A; eligibility "
              "determinations were made by the program administrator. Buyer acknowledges it has reviewed the "
              "marketing kit version referenced in Exhibit B."),
        ("p", f"Remedies: failure of delivered credits entitles Buyer to replacement credits or refund of allocable "
              f"cash consideration, at Seller election, on a Refund Request made within {refund_days} of final "
              f"determination."),
    ]
    if note:
        body.append(("p", note))
    body += [
        ("sig", ["/s/ Priya Shah", "Priya Shah, VP Business Development, Alder Point, as Administrator",
                 f"Date: {seller_date or date}"]),
        ("sig", [f"/s/ {buyer_sig[0]}", f"{buyer_sig[0]}, {buyer_sig[1]}, {buyer}, Buyer", f"Date: {date}"]),
    ]
    spec(ex_id, f"{ex_id}_Purchase_Lot{n}.pdf", "executed",
         f"CREDIT PURCHASE AGREEMENT -- {buyer} (Lot {n})", body)


CONFORMED = "Short-form exhibit copy of the executed long-form Credit Purchase Agreement ({}); the long form controls."
lot("EX-011", 1, "Blue River Capital", "$1,100,000", 89, "$979,000", "December 6, 2022", "one hundred twenty (120) days",
    ("A. Patel", "Managing Director"), "December 5, 2022", CONFORMED.format("Blue River CPA signed.pdf"))
lot("EX-012", 2, "Cascade Pension Partners", "$1,250,000", 90, "$1,125,000", "November 9, 2022", "ninety (90) days",
    ("J. Orr", "Director of Investments"), "November 8, 2022",
    CONFORMED.format("CPP_Credit_Purchase_Agreement_executed_scan.pdf"))
lot("EX-013", 3, "Willamette Family Holdings", "$950,000", 93, "$883,500", "December 13, 2022", "ninety (90) days",
    ("S. Grant", "authorized signatory"))
lot("EX-014", 4, "North Fork Energy Fund", "$900,000", 92, "$828,000", "November 21, 2022", "ninety (90) days",
    ("D. Liu", "Portfolio Manager"), None,
    CONFORMED.format("Bellhaven_CSC_Purchase_Agreement_North_Fork_EXECUTED.pdf"))
lot("EX-015", 5, "Blue River Capital", "$1,000,000", 91, "$910,000", "December 20, 2022", "one hundred twenty (120) days",
    ("A. Patel", "Managing Director"))
lot("EX-016", 6, "North Fork Energy Fund", "$1,050,000", 89, "$934,500", "December 15, 2022", "ninety (90) days",
    ("D. Liu", "Portfolio Manager"))


# EX-017/018: re-dated before EMAIL-041 (9/10/22 "renewal filings ... stuck behind a state processing
# backlog"); the November dates post-dated that seed email. Receipt numbers supplied.
def receipt(ex_id, filename, state, received, receipt_no, fee):
    spec(ex_id, filename, "file-stamped", f"BROKER REGISTRATION RENEWAL -- {state} FILING RECEIPT", [
        ("p", f"File-stamped receipt confirming application by Bellhaven Advisory for renewal of broker "
              f"registration in {state}, received {received}. THIS RECEIPT IS NOT A CERTIFICATE OF GOOD STANDING. "
              f"Issuance, if granted, issues separately."),
        ("p", f"Receipt No. {receipt_no}. Renewal fee paid: {fee}. Status inquiries reference this receipt number."),
    ])


receipt("EX-017", "EX-017_RenewalFiling_Oregon.pdf", "Oregon", "August 23, 2022", "OR-BR-2022-08-3317", "$300.00")
receipt("EX-018", "EX-018_RenewalFiling_Washington.pdf", "Washington", "August 25, 2022", "WA-BRK-22-041958",
        "$275.00")

# EX-020..035: NW easements and certificates (acreage and face per CASE_BIBLE §2, unchanged).
# Placeholders ("as shown") replaced with recording/certificate numbers and dates. Assessor parcel numbers
# are deliberately NOT supplied: mapping a recorder parcel number to NW-07 must stay a join on the county
# filing (CASE_BIBLE §6 Q5).
NW = [  # parcel, claimed, recorded, face, recording no., recorded, certificate issued
    ("NW-01", 210, 210, "$590,000", "2021-003184", "March 9, 2021", "October 4, 2022"),
    ("NW-02", 185, 185, "$520,000", "2021-003185", "March 9, 2021", "October 4, 2022"),
    ("NW-03", 320, 273, "$620,000", "2021-005907", "May 4, 2021", "October 18, 2022"),
    ("NW-04", 340, 288, "$580,000", "2021-007442", "June 15, 2021", "October 18, 2022"),
    ("NW-05", 195, 195, "$550,000", "2021-007460", "June 15, 2021", "November 1, 2022"),
    ("NW-06", 260, 222, "$640,000", "2021-009811", "August 3, 2021", "November 1, 2022"),
    ("NW-07", 275, 231, "$560,000", "2021-010236", "August 17, 2021", "November 15, 2022"),
    ("NW-08", 205, 205, "$490,000", "2021-012570", "October 5, 2021", "November 15, 2022"),
]
for i, (p, claimed, rec, face, rec_no, rec_date, issued) in enumerate(NW):
    spec(f"EX-{20 + i:03d}", f"EX-{20 + i:03d}_Easement_{p}.pdf", "recorded", f"CONSERVATION EASEMENT -- {p} (recorded)", [
        ("p", f"Conservation easement recorded with the county recorder covering parcel {p}, legal description in "
              f"Exhibit A. Recorded acreage: {rec} acres."),
        ("p", "Grantor warrants the acreage stated from the county filing of record. Survey verification, if any, "
              "attaches as Exhibit B."),
        ("p", f"Recording No. {rec_no}, recorded {rec_date}. Assessor parcel number per Exhibit A."),
        ("sig", ["[Exhibits A and B are not reproduced in this exhibit copy.]"]),
    ])
    spec(f"EX-{28 + i:03d}", f"EX-{28 + i:03d}_Certificate_{p}.pdf", "issued", f"CREDIT CERTIFICATE -- {p}", [
        ("p", f"Certificate evidencing Coastal Solar credits with face value {face} attributable to parcel {p}, "
              f"computed at the batch per-acre rate on claimed acreage of {claimed} acres. Delivery of this "
              f"certificate is the revenue-recognition event."),
        ("p", f"Certificate No. CSC-{p}-2022-{i + 1:04d}. Issued {issued}. Delivery to a purchaser is evidenced by "
              f"the delivery receipt, not by this certificate. Undelivered lots remain deferred revenue."),
    ])


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(SPECS)
    for ex in wanted:
        s = SPECS[ex]
        render(s["filename"], s["ex_id"], s["status"], s["title"], s["blocks"], s["meta_title"])
        print("built", s["filename"])
