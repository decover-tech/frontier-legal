#!/usr/bin/env python3
"""Generate Logs/rewrite/specs/RW-P1.json (mechanical fixes) from Logs/rewrite/audit.csv.

P1 = placeholder / wrong quoted history (re-rendered from the real In-Reply-To parent), wrong-org or
non-canonical signatures (canonical block re-appended), and subject parcel IDs that disagree with the
body + attachment (subject follows the body). Bodies are kept verbatim ("body": null).
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PARCEL_RE = re.compile(r"\b(?:NW|KW|RM)-\d{2}\b")
MECH = {"placeholder_quote", "wrong_quote_date", "quote_style_mismatch", "stale_quote", "orphan_quote",
        "wrong_org_sig", "noncanonical_sig", "missing_sig", "subject_parcel_mismatch",
        "attachment_content_parcel_mismatch"}

rows = list(csv.DictReader(open(os.path.join(HERE, "audit.csv"), encoding="utf-8")))
entries, skipped = [], []
for r in rows:
    defects = set(r["defects"].split(";")) - {""}
    fixes = sorted(defects & MECH)
    if not fixes:
        continue
    e = {"email": r["docid"], "body": None, "expect_sha": r["core_sha"], "fixes": fixes}
    if defects & {"subject_parcel_mismatch", "attachment_content_parcel_mismatch"}:
        subj_p = sorted(set(PARCEL_RE.findall(r["subject"])))
        body_p = set(filter(None, r["body_parcels"].split(";")))
        att_p = set(filter(None, r["attachment_parcels"].split(";")))
        target = (body_p | att_p)
        if len(subj_p) == 1 and len(target) == 1:
            t = target.pop()
            e["subject"] = r["subject"].replace(subj_p[0], t)
            e["note"] = f"subject parcel {subj_p[0]} -> {t} (body {sorted(body_p)}, attachment {sorted(att_p)})"
        else:
            skipped.append((r["docid"], r["parcel_note"]))
            e["fixes"] = [f for f in fixes if f not in ("subject_parcel_mismatch", "attachment_content_parcel_mismatch")]
            e["note"] = "subject/body parcel mismatch left for P2 (body and attachment disagree)"
            if not e["fixes"]:
                continue
    entries.append(e)

spec = {
    "rewrite_id": "RW-P1",
    "bible_refs": ["§0 seed locked", "§2 parcel table (NW-01..08, KW-01/02)", "Arc J guard (KW post-3/16/22)"],
    "rationale": ("Mechanical repairs only — no new prose. (1) Quoted history rebuilt from the real In-Reply-To parent "
                  "with thread_kit.quote_block in the sender's client style, replacing 'From: EMAIL-NNN / Subject: (prior "
                  "subject)' and 'On <date>, EMAIL-NNN wrote:' placeholders and their wrong dates at every nesting level. "
                  "(2) Signature blocks that carry another org (e.g. L&L lawyers with the Cascade block) or a variant block "
                  "replaced with the sender's canonical corpus signature. (3) Subject parcel ID aligned to the parcel the "
                  "body and attachment name (subject was the templated field; body/attachment carry the substance). "
                  "In-Reply-To links themselves are headers and stay as-is, even where incoherent (see audit info flags)."),
    "emails": entries,
}
out = os.path.join(HERE, "specs", "RW-P1.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(spec, open(out, "w"), indent=1, ensure_ascii=False)
print(f"wrote {out}: {len(entries)} emails, {sum(1 for e in entries if e.get('subject'))} subject fixes; skipped subject fixes: {skipped}")
