#!/usr/bin/env python3
"""Build Logs/rewrite/specs/RW-P2-J.json — arc J (Clearwater / KW-01, KW-02) prose rewrites.

Bodies are written against the carried library version (tools/doc_kit/library/KW0*-OPTION.json,
plan ATT-001) and seeds 175/176 (lead), 198 (handoff), 140/141 (payments post-date applications).
expect_sha and post-P1 subjects are filled from audit.csv / RW-P1.json so the spec guards concurrent edits.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
audit = {r["docid"]: r for r in csv.DictReader(open(os.path.join(HERE, "audit.csv"), encoding="utf-8"))}
p1_subject = {e["email"]: e["subject"] for e in json.load(open(os.path.join(HERE, "specs", "RW-P1.json")))["emails"] if e.get("subject")}

B = {}
N = {}

# ---- option agreements (body must match the attached version) ------------------------------------
B["EMAIL-413"] = ("Tom — attached is a first cut of the KW-01 option on the APP-OPT form, working from the owner call and your walk on the 22nd. "
                  "Economics as discussed: $12,000 option fee in three $4,000 installments, 12-month term with one six-month extension, "
                  "60-day closing window. Acreage, legal description, tax lot and price are still blank until the county filings come back, "
                  "and the owner needs to tell us whether the old grazing lease was ever released. Mark it up and I'll turn it.")
N["EMAIL-413"] = "KW01-OPTION v1 (3/29/22) terms and blanks; walk 3/22 per library; lead 3/16 (176)"
B["EMAIL-415"] = ("Priya — first draft of the KW-02 option attached, same form and economics as KW-01 ($12,000 fee in three installments, "
                  "$1,150 per net acre, 60-day close). Unlike KW-01 the county filings were already in hand, so the legal description, "
                  "tax lot and Assessor acreage are filled in, along with the grazing-lease disclosure. The open item is access to the south "
                  "parcel over the ranch track. Nothing needed from you yet; sending so you have it before Monday.")
N["EMAIL-415"] = "KW02-OPTION v1 (5/6/22); Sunday send acknowledged; subject per P1 (KW-02)"
B["EMAIL-414"] = ("Priya — v2 of the KW-01 option, building on Nina's first draft. The county filings came through, so the legal description, "
                  "tax lot and Assessor acreage (148.62 ac) are now in, and the price is set at $1,150 per net acre to match KW-02. "
                  "Added the grazing-lease disclosure and release mechanics in 6.2, and updated the recital about the adjoining parcel since "
                  "KW-02 is now being negotiated. No change to the fee or term.")
N["EMAIL-414"] = "KW01-OPTION v2 (7/5/22) change notes; parent 413 is Nina's v1 (coherent after P1 subject fix)"
B["EMAIL-408"] = ("Nina — current KW-01 draft attached so you have the same version I do: still v2 from July, nothing has moved since. "
                  "The owner's counsel has it and hasn't come back with comments yet. If Gordon asks, the business terms haven't changed — "
                  "fee, term and price are as he saw them. I'll send the next turn when their markup lands.")
N["EMAIL-408"] = "v2 still current on 8/31/22 (ATT-001 note); owner counsel comments arrive 9/9–9/14"
B["EMAIL-440"] = ("Tom — owner's counsel came back on KW-02 and I've folded their comments into the attached v2: initial option payment due in "
                  "five business days instead of ten, deferred payments capped at the end of the option term, the owner keeps the existing "
                  "grazing use until closing, and notices copy their counsel. They also agreed the ranch-track access, as an easement across "
                  "the owner's land to the north at closing. I think it's ready to sign if you are.")
N["EMAIL-440"] = "KW02-OPTION v2 (9/9/22) change notes; relayed by Nina per ATT-001; subject per P1"
B["EMAIL-417"] = ("Priya — KW-01 v3 attached with the owner's counsel comments accepted (Oyler & Beck in Klamath Falls). Same changes they asked "
                  "for on KW-02: initial payment due in five business days, deferred payments capped at the end of the term, existing grazing "
                  "use can continue until closing, and a notice copy to their counsel. Price and acreage are unchanged from v2. KW-02 should be "
                  "signed next week; KW-01 will trail it.")
N["EMAIL-417"] = "KW01-OPTION v3 (9/14/22); KW-02 executed 9/20/22; subject per P1"
B["EMAIL-399"] = ("Priya — you asked where KW-01 stands. Current draft attached; it's still v3 with the owner's counsel comments from mid-September. "
                  "No new markup since. KW-02 is signed and in the file; KW-01 is waiting on the owner's side, not ours. I'll chase Gordon "
                  "again next week.")
N["EMAIL-399"] = "v3 still current 10/19/22 (ATT-001); KW-02 exec 9/20/22"
B["EMAIL-427"] = ("Alan — as requested for the collection, the executed KW-02 option (Clearwater) from the Alder file. This is the scanned copy "
                  "with both signatures — the owner signed September 19, 2022 and I countersigned on the 20th. The KW-01 executed copy and the "
                  "drafts for both parcels will come to you in a separate batch so the versions don't get mixed.")
N["EMAIL-427"] = "KW02-OPTION exec scan; counsel-channel collection copy (ATT-001)"
B["EMAIL-409"] = ("Dana — Alan asked me to send the executed KW-02 option straight to you for your review set, so it's attached. Effective date "
                  "September 20, 2022; the owner signed the day before. It's the same scan Alan has from the collection. If you need the drafts "
                  "or anything else from the Alder side, tell Alan and he'll route the request.")
N["EMAIL-409"] = "KW02-OPTION exec; Whitaker allowed after 7/27/23; routing back through L&L preserved"
B["EMAIL-392"] = ("Note to file — saving the executed KW-02 option scan here with the rest of my Clearwater records so both signed options are "
                  "in one place for the collection. Effective 9/20/22 on the v2 terms; owner signed 9/19. The executed KW-01 copy is going to "
                  "Priya separately today.")
N["EMAIL-392"] = "sent-to-self rewritten as a note to file; KW02 exec; pairs with 446 same day"
B["EMAIL-446"] = ("Priya — executed KW-01 option for the program file set. Effective January 10, 2023, on the v4 terms — the only change from v3 "
                  "was the 90-day closing window. Owner signed January 6 and I countersigned on the 10th. You should already have the executed "
                  "KW-02 from last September; let me know if that one's missing and I'll resend.")
N["EMAIL-446"] = "KW01-OPTION exec (1/10/23) on v4 terms; change note v4 = closing 60→90 days"
B["EMAIL-432"] = ("Tom — attached is the executed KW-02 option as it appears in the set we received. Before we treat it as the operative copy, "
                  "could you confirm it's complete — no side letters, amendments or extension notices — and whether Alder still holds the "
                  "wet-ink original? A short call this week is fine; no need to write anything up.")
N["EMAIL-432"] = "L&L to Alder (third party; gold = vitiated): confirmation request only, hedged, call redirect; subject per P1"
B["EMAIL-423"] = ("Grace — following our call, attached is the last KW-02 draft before signing: v2 with the owner's counsel comments folded in "
                  "(initial payment in five business days, deferred payments capped at the end of the term, ranch-track access easement at closing). "
                  "It was signed on these terms on September 20, 2022. The earlier v1 is in the set Alan already has.")
N["EMAIL-423"] = "KW02-OPTION v2 as drafting history (ATT-001); subject per P1"
B["EMAIL-436"] = ("Dana — for the drafting timeline, attached is the first KW-02 draft (v1, dated May 6, 2022) from the Alder set. Unlike the first "
                  "KW-01 draft it already carries the county legal description and Assessor acreage. Please slot it in as a dated source only; "
                  "we can talk through where it fits when we speak Tuesday.")
N["EMAIL-436"] = "KW02-OPTION v1 to Kovel accountant at counsel direction (gold ACP/WP); no characterization"

# ---- dates log ----------------------------------------------------------------------------------
B["EMAIL-445"] = ("Priya — starting a dates log for the Clearwater pair now so nobody has to rebuild it later. So far: Nina's lead on 3/16, my "
                  "walk on 3/22, county filings requested 3/23, first KW-01 option draft 3/29. Option and packet dates go in as they happen. "
                  "Dates and document names only — it's a log, not a memo.")
N["EMAIL-445"] = "dates from 176, library v1 (walk 3/22, filings requested 3/23, draft 3/29); Saturday send"
B["EMAIL-425"] = ("Tom — dates log updated on my side: lead call 3/16, your walk 3/22, KW-01 draft 3/29, KW-02 draft 5/6. I haven't put anything "
                  "on the packet line yet — I'll wait until the KW-02 packet is actually together rather than guess at a date. Sheet attached.")
N["EMAIL-425"] = "dates per library versions; precedes 412 (packet assembled 6/21)"
B["EMAIL-402"] = ("Priya — Clearwater dates log refreshed. New since April: KW-02 first draft 5/6, and KW-01 v2 on 7/5 with the county legal "
                  "description and Assessor acreage filled in. Nina is keeping the packet dates; I'll drop them in when she sends them. "
                  "Nothing signed on either parcel yet.")
N["EMAIL-402"] = "KW02 v1 5/6, KW01 v2 7/5 per library; no executions before 9/20/22"
B["EMAIL-424"] = ("Nina — attached is the Clearwater dates log as it appears in the Alder files we've been given. Could you confirm the lead-call "
                  "date and tell us where the option and packet dates are kept? We're only after the source for each line, not any commentary. "
                  "If it's easier, I'm happy to take it by phone.")
N["EMAIL-424"] = "L&L to Alder (third party; gold = vitiated): source request only; pre-departure (Nina)"

# ---- status / receipt notes ---------------------------------------------------------------------
B["EMAIL-419"] = ("Tom — quick status on KW-02: the owner's counsel has the v1 draft and says comments are coming, but nothing yet. The open "
                  "point on our side is still access to the south parcel over the ranch track. No dates to add to the log this week.")
N["EMAIL-419"] = "interim status 8/16/22; v1 access open, owner counsel comments land 9/9 (library)"
B["EMAIL-422"] = ("Priya — status on KW-02 since you asked: nothing new since the option was signed last September. Installments are on the "
                  "option schedule and the ledger has the bank-feed lines; the application packet copy is in Nina's Southwest folder. "
                  "Happy to walk you through the file if you want it before month-end.")
N["EMAIL-422"] = "interim status 6/1/23; no dates asserted beyond exec 9/20/22"
B["EMAIL-405"] = ("Tom — interim note on the Clearwater KW-02 file. We have the option drafts and the executed copy from the Alder set; we don't "
                  "yet have the ledger lines or the application packet. Could you point us to where those sit? Easier to walk through on a call "
                  "than by email — Monday or Tuesday works on my end.")
N["EMAIL-405"] = "L&L to Alder (third party; gold = vitiated); Saturday send; request only"
B["EMAIL-398"] = ("Tom — confirming we received the copy of the Clearwater folder (KW-01 and KW-02) you sent over yesterday. We'll log it as "
                  "received today. If we have questions about what's in it, I'd rather cover them on a call next week than trade emails.")
N["EMAIL-398"] = "receipt the day after Nina's 6/29 handoff (198); third party; call redirect"
B["EMAIL-438"] = ("Tom — following up on KW-01. From the folder you sent we have v1 through v4 and the executed copy, but not the ledger lines or "
                  "the application packet copy. If those are in Nina's handoff folder, a pointer to the location is enough and we'll pull them "
                  "from there.")
N["EMAIL-438"] = "KW01 versions v1–v4 + exec per library; request only; third party"
B["EMAIL-420"] = ("Tom — received the second Clearwater set (ledger exports and application packet copies for KW-01 and KW-02) and logged it "
                  "today. Nothing further needed from you for now. If we have questions about sources, Alan will set up a short call.")
N["EMAIL-420"] = "receipt only (role: review-channel receipt); third party"

# ---- Kovel / counsel-internal -------------------------------------------------------------------
B["EMAIL-400"] = ("Grace — the Route 97 file set from Alder is logged against our index: KW-01 v1–v4 plus executed, KW-02 v1–v2 plus executed, and "
                  "the ledger exports for both. We still need the as-filed application copies before the sequencing schedule can be relied on; "
                  "the packet copies in the Alder set are assembled versions and may not match what was submitted. No analysis in this note.")
N["EMAIL-400"] = "Kovel to counsel (gold ACP/WP); inventory only; application dates not asserted; Labor Day send"
B["EMAIL-411"] = ("Grace — dates-only note for KW-01/02 as requested. We've lined up each option's effective date (KW-02 September 20, 2022; "
                  "KW-01 January 10, 2023) against the installment schedule in the executed agreements and the ledger lines. Application dates "
                  "are still taken from Alder's packet copies rather than the as-filed record, so we're not relying on them yet. No "
                  "characterization here; the sourced schedule will follow.")
N["EMAIL-411"] = "Kovel dates-only note; exec dates from library; leaves Q4 open (§6)"
B["EMAIL-426"] = ("Grace — update on the Route 97 tracing inputs. Tom Reyes sent the KW-02 application packet copy on the 2nd; it's the assembled "
                  "version from Alder's folder, not the as-filed copy. We've added it to the source index as that. The as-filed copies for both "
                  "parcels are still outstanding, and until we have them the application column of the schedule stays provisional.")
N["EMAIL-426"] = "Kovel update; ties to 442 (10/2/23); application column provisional"
B["EMAIL-443"] = ("Grace — I've compiled the KW-02 ledger lines from the Alder production set into the attached sheet. Amounts are as recorded; "
                  "two lines don't have a matching bank-feed date, so I've left them flagged rather than guess. The source for each line is "
                  "in the index on the team drive.")
N["EMAIL-443"] = "paralegal compilation at counsel direction (gold ACP/WP); Saturday; flags kept from original text"
B["EMAIL-450"] = ("Alan — please log receipt of the KW-01 Clearwater set that came in with Tom's last batch, and file it with the KW-02 materials "
                  "under the same index. No need to copy Dana on the logistics; I'll send her what she needs once I've been through it.")
N["EMAIL-450"] = "counsel-internal receipt (gold ACP/WP); role: Kovel agent not looped on admin"
B["EMAIL-393"] = ("Tom — one housekeeping question for our records: which copy of the Clearwater files should we treat as Alder's master? We have "
                  "two versions of the KW-02 packet, one from Nina's handoff folder and one from the Southwest drive, and they aren't labeled "
                  "the same way. A quick call is easier than email if you have ten minutes this week.")
N["EMAIL-393"] = "record note to third party (gold vitiated); duplicate-source question, no conclusion"

# ---- ledger lines -------------------------------------------------------------------------------
B["EMAIL-391"] = ("Priya — I've set up a ledger line for KW-02 now so the Clearwater pair sits side by side. The $12,000 is the option fee we're "
                  "proposing (same as KW-01, in three installments). Nothing has been paid; the date column says 'per bank feed' until the "
                  "option is signed and payments actually go out. The draft option should be with you next week.")
N["EMAIL-391"] = "ledger placeholder before KW-02 v1 (5/6/22); no payment asserted"
B["EMAIL-433"] = ("Tom — KW-01 ledger tab attached, copying Priya so finance has the same sheet. The $12,000 is the option fee as drafted (three "
                  "$4,000 installments). Nothing has gone out — the option isn't signed — so the date column stays 'per bank feed' and will "
                  "fill in from the bank feed once payments start.")
N["EMAIL-433"] = "KW-01 unsigned until 1/10/23; no payment asserted"
B["EMAIL-444"] = ("Tom — KW-02 ledger lines as of today, attached. Amounts follow the option schedule and dates come from the bank feed. Two lines "
                  "I couldn't tie to a bank-feed date, so they're flagged rather than filled in. Priya's team should confirm those before "
                  "anyone relies on the sheet.")
N["EMAIL-444"] = "post-exec ledger; keeps original 'two lines flagged' detail; no dates asserted"
B["EMAIL-394"] = ("Nina — KW-01 is signed: the owner on the 6th, me on Tuesday. I've set up the attached ledger line for the $12,000 fee in three $4,000 "
                  "installments. The first is due within five business days of signing; dates will come from the bank feed as they post. Can "
                  "you let Gordon know the countersigned scan is on its way to him?")
N["EMAIL-394"] = "KW01 exec 1/6 + 1/10/23; initial payment 5 business days (v3/v4 term)"

# ---- application packets -------------------------------------------------------------------------
B["EMAIL-412"] = ("Tom — KW-02 application packet assembled from the v1 option draft, the county filings and your field notes from the March walk. "
                  "It hasn't been filed. I'd like you to look it over before it goes to Priya, especially the parcel description pages. The "
                  "filing copy will follow once it's final.")
N["EMAIL-412"] = "packet assembled 6/21/22 (existing fact); not filed; no application date asserted; subject per P1"
B["EMAIL-449"] = ("Priya — KW-02 application packet attached, now with the executed option (9/20) in place of the draft, plus the county filing "
                  "and field notes. Nina pulled it together. It's ready to go in on your sign-off; I'll put the filing copy on this thread once "
                  "it's submitted.")
N["EMAIL-449"] = "post-exec packet; submission date not asserted (Q4 join stays open)"
B["EMAIL-441"] = ("Tom — for the files, the KW-02 application packet as it sits in the Southwest folder. It's the same set Priya's team submitted; "
                  "I haven't changed anything. If anyone asks for the as-filed copy, Priya's team has that one.")
N["EMAIL-441"] = "Nina pre-departure; assembled vs as-filed distinction; subject per P1"
B["EMAIL-442"] = ("Dana — sending this to you directly, as Alan asked last week: the KW-02 application packet from the Alder file. It's the "
                  "assembled copy Nina kept in the Southwest folder, not the as-filed version, which should be on the program side. I don't have "
                  "a separate transmittal for it.")
N["EMAIL-442"] = "to Kovel accountant at L&L's request; feeds 426"
B["EMAIL-396"] = ("Priya — for the Alder records pull, the KW-02 application packet from my folder. It's the assembled copy, not the as-filed one; "
                  "your team has that. It's the same copy counsel's team received earlier this month.")
N["EMAIL-396"] = "Sunday send; assembled vs as-filed; subject per P1"
B["EMAIL-430"] = ("Note to self — saved a copy of the KW-01 application packet (executed option from 1/10, county filing, field notes) to the "
                  "Southwest folder next to the KW-02 set, so both Clearwater packets are in one place. The as-filed copy is with Priya's team.")
N["EMAIL-430"] = "sent-to-self rewritten as note to self; subject per P1"
B["EMAIL-431"] = ("Note to file: pulled Nina's KW-01 application packet from the handoff folder and saved a copy with my KW records so the pair "
                  "sits together. Nothing edited. Ask Priya whether the as-filed version differs from this assembled copy.")
N["EMAIL-431"] = "sent-to-self as note to file; post-handoff (198); subject per P1"

# ---- Route 97 correspondence --------------------------------------------------------------------
B["EMAIL-395"] = ("Priya — back from Klamath. The two Clearwater parcels Nina flagged off Route 97 walked well, and the owner (Clearwater Land LLC) "
                  "wants to move. Nina is working up the first option draft from the owner call, and I've asked the county for the filings. "
                  "Expect a KW-01 draft for you in the next couple of weeks, with KW-02 after that.")
N["EMAIL-395"] = "walk wk of 3/21 (175/176); KW01 v1 3/29 already exists — sent to Tom; Priya gets v2"
B["EMAIL-406"] = ("Nina — can you chase the owner for the tax lot numbers on the north parcel? The draft has them blank, and the recorder search is "
                  "slow without them. Once we have those I can get the legal description into KW-01.")
N["EMAIL-406"] = "library v1 tax_lot '[pending — Owner to provide parcel numbers]'"
B["EMAIL-407"] = ("Priya — KW-02 is signed. The owner signed yesterday and I countersigned this afternoon; the scan will follow once I'm back at a "
                  "scanner. KW-01 is still with the owner's counsel on the v3 markup, so it'll trail by a few weeks at least.")
N["EMAIL-407"] = "KW02 exec 9/19–9/20/22; KW01 v3 9/14 (library)"
B["EMAIL-418"] = ("Priya — no movement on KW-01. The owner's counsel has had v3 since mid-September and hasn't sent any further comments; the ball "
                  "is on their side. KW-02 is unaffected. I'll try Gordon directly next week.")
N["EMAIL-418"] = "KW01 v3 current until v4 12/19/22"
B["EMAIL-447"] = ("Priya — owner's counsel wants 90 days to close on KW-01 instead of 60. Nothing else is changing. I'll have v4 out to them Monday, and "
                  "if they're good with it we should finally get signatures on KW-01 in January.")
N["EMAIL-447"] = "Saturday 12/17/22; v4 12/19 (Mon) closing 60→90; exec 1/10/23"
B["EMAIL-410"] = ("Tom — Gordon asked for a copy of the countersigned KW-02 for his lawyer, so I sent him the scan from the shared drive. He also "
                  "asked about timing on KW-01; I told him it's with Oyler & Beck and that you'd follow up. Nothing else from him.")
N["EMAIL-410"] = "post-exec KW-02 courtesy copy; owner counsel Oyler & Beck (library v3)"
B["EMAIL-404"] = ("Nina — the owner's counsel should have both drafts by now. If you speak to Gordon this week, the open point on our side is still "
                  "KW-02 access over the ranch track; everything else in the drafts is where we left it on the call.")
N["EMAIL-404"] = "Saturday 9/3/22; access open until v2 9/9 (library)"

entries = []
for k, body in B.items():
    r = audit[k]
    fixes = [f for f in r["defects"].split(";") if f in ("boilerplate", "short_body", "send_to_self", "subject_parcel_mismatch")]
    e = {"email": k, "body": body, "expect_sha": r["core_sha"], "fixes": fixes, "note": N[k]}
    if k in p1_subject:
        e["subject"] = p1_subject[k]
    entries.append(e)
entries.sort(key=lambda e: audit[e["email"]]["date"])
spec = {
    "rewrite_id": "RW-P2-J",
    "bible_refs": ["§0 Clearwater lead 3/16/22 (176) + handoff 6/29/23 (198) [ESTABLISHED]", "§2 Clearwater pair KW-01/02 post-3/16/22",
                   "§6 Q4 intent stays join-only", "§9 knowledge ledger", "library KW01-OPTION / KW02-OPTION (ATT-001)"],
    "rationale": ("Arc J spine emails rewritten in the senders' voices. Option-carrying emails now describe the exact library version they carry "
                  "(v1 blanks, v2 county data + price, v3/v2 owner-counsel comments, v4 closing window, executed scans with signature dates). "
                  "Ledger emails assert no payment dates: amounts from the option schedule only; dates remain 'per bank feed'. Application "
                  "emails distinguish assembled copies from as-filed copies and never state a submission date, so the §6 Q4 join (option "
                  "dates + application dates + ledger + Nina's role) stays open. Counsel/Kovel emails are inventory, receipt or source "
                  "requests: no characterization and no 'intent'. Sent-to-self emails become notes to file. Skipped: 437 (subject asserts "
                  "'files complete' on 9/13/22, which conflicts with seed 198's 6/29/23 handoff), 416 (L&L on Clearwater 3 days after "
                  "engagement; premature), 428 (a 'late activity' note would need a new fact), 434/429/401/403/448/421/435/439 "
                  "(near-duplicates of the rewritten ledger, log and route notes; left for a later pass)."),
    "emails": entries,
}
json.dump(spec, open(os.path.join(HERE, "specs", "RW-P2-J.json"), "w"), indent=1, ensure_ascii=False)
print(f"wrote RW-P2-J.json with {len(entries)} entries")
