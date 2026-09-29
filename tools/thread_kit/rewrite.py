#!/usr/bin/env python3
"""rewrite — audit and repair templated generated emails (EMAIL-251..1400) in place.

Invoked through thread_kit:

  thread_kit.py audit [--csv Logs/rewrite/audit.csv]
        classify generated emails by defect type and priority (P1 mechanical, P2 spine prose,
        P3 noise) and write the CSV.
  thread_kit.py rewrite <spec.json> [--dry-run] [--show N] [--force]
        replace each listed email's own new text (or keep it, for mechanical fixes), re-append
        the sender's canonical signature, re-render quoted history from the real In-Reply-To
        parent, optionally change the Subject (file slug + manifest + load files follow), and
        cascade re-rendered quoting to every later email that quotes a rewritten one.
  thread_kit.py rewrite-rollback <RW-ID>
        restore files, manifest rows and load-file rows from Logs/rewrite/backup/<RW-ID>/.

Spec format (Logs/rewrite/specs/RW-*.json):

  {"rewrite_id": "RW-P2-J", "bible_refs": [...], "rationale": "...",
   "emails": [{"email": "EMAIL-408",
               "body": "new text only (no signature / quote)"  | null to keep the current text,
               "subject": "new subject" (optional),
               "banner": "keep" (default) | "none" | "acp" | "wp",
               "expect_sha": "sha1[:12] of the current new text (guards concurrent edits)",
               "fixes": ["placeholder_quote", ...], "note": "..."}]}

Invariants enforced: seed EMAIL-001..250 never written (a seed that quotes a rewritten email is
reported); every non-MIME header except Subject (when asked) kept byte-identical; attachments
kept byte-identical; MIME rebuilt with thread_kit.build_mime so signature logos match the body.
"""
import csv
import email
import hashlib
import io
import json
import os
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from email import policy
from email.message import EmailMessage

import thread_kit as tk

RW_DIR = os.path.join(tk.ROOT, "Logs", "rewrite")
LOADFILE_CSV = os.path.join(tk.CORPUS, "Loadfile_Cascade_Timber.csv")
LOADFILE_DAT = os.path.join(tk.CORPUS, "Loadfile_Cascade_Timber.dat")
GEN_LO, GEN_HI = 251, 1400
PARCEL_RE = re.compile(r"\b(?:NW|KW|RM)-\d{2}\b")
PLACEHOLDER_RE = re.compile(r"^[> ]*From: EMAIL-\d+\s*$|\(prior subject\)|^[> ]*On [^\n]*EMAIL-\d+ wrote:", re.M)
MIME_HDRS = {"content-type", "content-transfer-encoding", "mime-version", "content-disposition"}
DAT_SEP = "þ\u0014þ"


# ---------------------------------------------------------------- body anatomy

def sha(s):
    return hashlib.sha1(s.strip().encode("utf-8")).hexdigest()[:12]


def banner_values():
    return list(tk.RULES["banners"].values())


def anatomy(doc, people, names):
    """Split a doc's own new text into banner / core prose / signature block."""
    nt = doc.new_text
    lines = nt.splitlines()
    banner = None
    if lines and lines[0].strip().startswith("***") and lines[0].strip().endswith("***"):
        banner = lines[0].strip()
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    canon = (people.get(doc.from_addr, {}) or {}).get("signature") or ""
    text = "\n".join(lines)
    sig, core, sig_kind = None, text, "missing"
    if canon and text.rstrip().endswith(canon.rstrip()):
        core = text.rstrip()[: -len(canon.rstrip())]
        sig, sig_kind = canon, "canonical"
    else:
        si = None
        for i in range(len(lines) - 1, max(-1, len(lines) - 22), -1):
            ln = lines[i].strip()
            if not ln:
                continue
            if any(ln == n or ln.startswith(n + ",") or ln.startswith(n + " |") for n in names) or \
                    ln in tk.ORGS.values() or ln in ("Human Resources",):
                si = i
        if si is not None and si > 0:
            core = "\n".join(lines[:si])
            sig = "\n".join(lines[si:]).strip()
            sig_kind = classify_sig(doc, sig)
    return {"banner": banner, "core": core.strip(), "sig": sig, "sig_kind": sig_kind, "canon": canon}


def classify_sig(doc, sig):
    dom = doc.from_addr.split("@")[-1]
    own = tk.ORGS.get(dom)
    others = [o for d, o in tk.ORGS.items() if d != dom and (o in sig or (d == "cascadetimber.com" and "Forest Park Way" in sig))]
    if others and own not in others:
        return "wrong_org"
    first = (doc.from_name or "").split()[0] if doc.from_name else ""
    if first and first not in sig.splitlines()[0]:
        return "other_name"
    return "variant"


def words(s):
    return len(re.findall(r"\w+", s or ""))


def norm_template(s):
    s = s.lower()
    s = PARCEL_RE.sub("<p>", s.upper()).lower()
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"\b(nina|tom|priya|jay|hannah|sarah|john|grace|mia|alan|derek|renee|craig|robert|elena|frank|marcus|wendy|dan|deb|owen|brenda|dana|kevin|rosa)\b", "<n>", s)
    return re.sub(r"\s+", " ", s).strip()


def quote_kind(doc):
    if re.match(r"^\s*(fw|fwd)\s*:", doc.subject, re.I) or "---------- Forwarded message" in doc.body[:len(doc.new_text) + 200]:
        return "forward"
    return "reply"


def parsed_quote_headers(body):
    """(style, from_addr_or_docid, date_str) for every quote header in order of appearance."""
    out = []
    for m in re.finditer(r"^[> ]*-----Original Message-----\s*\n((?:[> ]*\w[\w-]*: .*\n)+)", body, re.M):
        blk = m.group(1)
        f = re.search(r"From: (.*)", blk)
        s = re.search(r"Sent: (.*)", blk)
        out.append(("outlook", f.group(1).strip() if f else "", s.group(1).strip() if s else "", m.start()))
    for m in re.finditer(r"^[> ]*On (.+?) wrote:\s*$", body, re.M):
        lead = m.group(1)
        mm = re.match(r"(\w{3}, \w{3} \d{1,2}, \d{4}(?: at \d{1,2}:\d{2} [AP]M)?),? (.*)$", lead)
        out.append(("gmail", mm.group(2).strip() if mm else lead, mm.group(1) if mm else "", m.start()))
    for m in re.finditer(r"^[> ]*---------- Forwarded message -+\s*\n((?:[> ]*\w[\w-]*: .*\n)+)", body, re.M):
        blk = m.group(1)
        f = re.search(r"From: (.*)", blk)
        s = re.search(r"Date: (.*)", blk)
        out.append(("gmail-fwd", f.group(1).strip() if f else "", s.group(1).strip() if s else "", m.start()))
    return sorted(out, key=lambda x: x[3])


def expected_date_str(style, dt):
    dt = dt.astimezone(tk.TZ)
    return tk.outlook_sent(dt) if style == "outlook" else tk.gmail_date(dt)


# ---------------------------------------------------------------- audit

def audit(docs, people, manifest, out_csv):
    names = sorted({p["name"] for p in people.values() if p.get("name")}, key=len, reverse=True)
    idx = tk.by_msgid(docs)
    kids = tk.children_map(docs)
    gen = sorted((d for d in docs.values() if GEN_LO <= tk.num(d.docid) <= GEN_HI), key=lambda d: tk.num(d.docid))
    anat = {d.docid: anatomy(d, people, names) for d in gen}
    clusters = defaultdict(list)
    for d in gen:
        clusters[norm_template(anat[d.docid]["core"])].append(d.docid)
    cid = {}
    for n, (k, v) in enumerate(sorted(clusters.items(), key=lambda kv: -len(kv[1])), 1):
        for x in v:
            cid[x] = (f"C{n:03d}", len(v))
    rows = []
    for d in gen:
        a = anat[d.docid]
        r = manifest.get(d.docid, {})
        arc = r.get("arc", "")
        defects = []
        # boilerplate / short
        c, size = cid[d.docid]
        if size >= 3:
            defects.append("boilerplate")
        wc = words(a["core"])
        if wc < 25:
            defects.append("short_body")
        # parcels
        subj_p = set(PARCEL_RE.findall(d.subject))
        body_p = set(PARCEL_RE.findall(a["core"]))
        att_p, attc_p = set(), set()
        for fn, ct, data in d.attachments:
            att_p |= set(PARCEL_RE.findall(fn or ""))
            if ct.startswith("text/"):
                attc_p |= set(PARCEL_RE.findall(data.decode("utf-8", "ignore")))
        parcel_note = ""
        if subj_p and (body_p or att_p) and not (subj_p & (body_p | att_p)):
            defects.append("subject_parcel_mismatch")
            parcel_note = f"subject {sorted(subj_p)} body {sorted(body_p)} att {sorted(att_p)}"
        elif body_p and att_p and not (body_p & att_p):
            parcel_note = f"body {sorted(body_p)} vs att {sorted(att_p)}"
            defects.append("body_attachment_parcel_mismatch")
        if attc_p and (subj_p | body_p) and not (attc_p & (subj_p | body_p | att_p)):
            defects.append("attachment_content_parcel_mismatch")
            parcel_note = (parcel_note + "; " if parcel_note else "") + f"attachment text {sorted(attc_p)} vs subject {sorted(subj_p)} body {sorted(body_p)}"
        # self-send
        to_addrs = {x for _, x in d.to}
        rc = to_addrs | {x for _, x in d.cc}
        if d.from_addr in to_addrs:
            defects.append("send_to_self" if rc == {d.from_addr} else "self_in_to")
        # quoting
        parent = idx.get(d.irt)
        qnote = []
        if PLACEHOLDER_RE.search(d.body):
            defects.append("placeholder_quote")
            ph_ids = re.findall(r"(?:From: |, )(EMAIL-\d+)(?: wrote:)?\s*$", d.body, re.M)
            if parent and ph_ids and ph_ids[0] != parent.docid:
                qnote.append(f"placeholder names {ph_ids[0]} but In-Reply-To is {parent.docid}")
        if parent:
            chain = list(reversed(tk.ancestors(d, idx)))  # parent, grandparent, ...
            hdrs = parsed_quote_headers(d.body[len(d.new_text):])
            bad_dates = 0
            for (style, frm, ds, _), anc in zip(hdrs, chain):
                if not ds:
                    continue
                exp = expected_date_str("outlook" if style == "outlook" else "gmail", anc.date)
                if style == "gmail" and " at " not in ds:
                    exp = exp.split(" at ")[0]
                if ds.strip() != exp:
                    bad_dates += 1
            if bad_dates:
                defects.append("wrong_quote_date")
                qnote.append(f"{bad_dates} quoted header date(s) differ from the real ancestor")
            if hdrs:
                st = hdrs[0][0]
                want = "outlook" if people.get(d.from_addr, {}).get("client") == "outlook" else "gmail"
                if (st == "outlook") != (want == "outlook"):
                    defects.append("quote_style_mismatch")
            if d.date <= parent.date:
                defects.append("child_not_after_parent")
            exp_body = d.new_text + "\n\n" + tk.quote_block(tk.Msg.from_doc(parent), people.get(d.from_addr, {}).get("client", "gmail"), quote_kind(d))
            if "placeholder_quote" not in defects and exp_body.strip() != d.body.strip():
                defects.append("stale_quote")
        elif tk.QUOTE_RE.search(d.body):
            defects.append("orphan_quote")
        # signatures
        if a["sig_kind"] == "wrong_org":
            defects.append("wrong_org_sig")
        elif a["sig_kind"] in ("other_name", "variant"):
            defects.append("noncanonical_sig")
        elif a["sig_kind"] == "missing":
            defects.append("missing_sig")
        # context flags (not fixed by rewrite)
        info = []
        folder_people = {people.get(x, {}).get("custodian_folder") for x in d.participants}
        if d.custodian not in folder_people:
            info.append("custodian_not_participant")
        if parent and not tk.coherent(d, parent):
            info.append("irt_subject_incoherent")
        if parent and d.from_addr not in parent.participants:
            info.append("irt_sender_not_on_parent")
        seed_kids = [k for k in kids.get(d.docid, []) if tk.num(k) <= tk.SEED_MAX]
        if seed_kids:
            info.append("quoted_by_seed:" + ",".join(seed_kids))
        for s in tk.RULES["senders"]:
            if d.from_addr == s["address"] and d.date.date() > datetime.fromisoformat(s["not_after"]).date():
                info.append("sender_after_departure")
        mech = {"placeholder_quote", "wrong_quote_date", "quote_style_mismatch", "stale_quote", "orphan_quote",
                "wrong_org_sig", "noncanonical_sig", "missing_sig", "subject_parcel_mismatch",
                "attachment_content_parcel_mismatch"}
        tiers = []
        if mech & set(defects):
            tiers.append("P1")
        prose = {"boilerplate", "short_body"} & set(defects)
        if prose and arc and arc != "N":
            tiers.append("P2")
        elif prose:
            tiers.append("P3")
        rows.append({
            "docid": d.docid, "date": d.date.astimezone(tk.TZ).strftime("%Y-%m-%d %H:%M"), "arc": arc,
            "from": d.from_addr, "to": ";".join(sorted(to_addrs)), "subject": d.subject,
            "attachments": ";".join(fn or "" for fn, _, _ in d.attachments), "custodian": d.custodian,
            "priority": tiers[0] if tiers else "", "tiers": ";".join(tiers), "defects": ";".join(defects),
            "cluster": c, "cluster_size": size, "core_words": wc, "sig_kind": a["sig_kind"],
            "in_reply_to": parent.docid if parent else "", "children": ";".join(sorted(kids.get(d.docid, []), key=tk.num)),
            "subject_parcels": ";".join(sorted(subj_p)), "body_parcels": ";".join(sorted(body_p)),
            "attachment_parcels": ";".join(sorted(att_p | attc_p)), "parcel_note": parcel_note, "quote_note": "; ".join(qnote), "info": ";".join(info),
            "core_sha": sha(a["core"]), "role": r.get("intended_evidentiary_role", ""),
            "core_text": a["core"][:300].replace("\n", " "),
        })
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summarize(rows, clusters)
    print(f"\nwrote {os.path.relpath(out_csv, tk.ROOT)} ({len(rows)} rows)")
    return rows


def summarize(rows, clusters):
    dc = Counter(x for r in rows for x in r["defects"].split(";") if x)
    print(f"generated emails audited: {len(rows)}")
    print("\n## defect counts (an email can carry several)")
    for k, v in dc.most_common():
        print(f"  {k:32} {v}")
    big = sorted((v for v in clusters.values() if len(v) >= 3), key=len, reverse=True)
    print(f"\n## boilerplate: {len(big)} clusters of >=3 identical (normalized) bodies covering {sum(map(len, big))} emails; largest: "
          + ", ".join(str(len(v)) for v in big[:10]))
    wc = sorted(r["core_words"] for r in rows)
    print(f"core-text words: median {wc[len(wc) // 2]}, p25 {wc[len(wc) // 4]}, p75 {wc[3 * len(wc) // 4]}")
    pc = Counter(r["priority"] or "clean" for r in rows)
    print("\n## priority (highest tier per email): " + ", ".join(f"{k}={v}" for k, v in sorted(pc.items())))
    tc = Counter(t for r in rows for t in r["tiers"].split(";") if t)
    print("   tier membership: " + ", ".join(f"{k}={v}" for k, v in sorted(tc.items())))
    p2 = Counter(r["arc"] for r in rows if "P2" in r["tiers"])
    print("   P2 by arc: " + ", ".join(f"{k}={v}" for k, v in sorted(p2.items())))
    ic = Counter(x.split(":")[0] for r in rows for x in r["info"].split(";") if x)
    print("\n## context flags (not fixed by rewrite): " + ", ".join(f"{k}={v}" for k, v in ic.items()))


# ---------------------------------------------------------------- MIME splice

def raw_header_fields(raw):
    """-> (list of (lower_name, bytes incl. continuation lines), body bytes)."""
    i = raw.find(b"\n\n")
    head, body = raw[: i + 1], raw[i + 2:]
    fields = []
    for line in head.split(b"\n")[:-1]:
        if line[:1] in (b" ", b"\t") and fields:
            fields[-1] = (fields[-1][0], fields[-1][1] + b"\n" + line)
        else:
            fields.append((line.split(b":", 1)[0].decode().strip().lower(), line))
    return fields, body


def encoded_subject(subject):
    em = EmailMessage(policy=policy.default)
    em["Subject"] = subject
    b = em.as_bytes(policy=policy.default.clone(linesep="\n"))
    return b[: b.find(b"\n\n")]


def splice(raw, plain, attachments, new_subject=None):
    """Rebuild MIME with thread_kit.build_mime; keep every non-MIME header's raw bytes."""
    gen = tk.build_mime([], plain, attachments)
    gfields, gbody = raw_header_fields(gen)
    fields, _ = raw_header_fields(raw)
    out, inserted = [], False
    for name, b in fields:
        if name in MIME_HDRS:
            if not inserted:
                out += [gb for _, gb in gfields]
                inserted = True
            continue
        if name == "subject" and new_subject is not None:
            out.append(encoded_subject(new_subject))
        else:
            out.append(b)
    if not inserted:
        out += [gb for _, gb in gfields]
    return b"\n".join(out) + b"\n\n" + gbody


def leaf_parts_ok(path):
    """True if every leaf part is the plain body, html alternative, inline logo or an attachment."""
    with open(path, "rb") as f:
        m = email.message_from_binary_file(f, policy=policy.default)
    for part in m.walk():
        if part.is_multipart():
            continue
        ct, disp = part.get_content_type(), part.get_content_disposition()
        if disp == "attachment" or (ct == "image/png" and disp == "inline") or (ct in ("text/plain", "text/html") and disp is None):
            continue
        return False
    return True


# ---------------------------------------------------------------- rewrite planning

class Plan:
    def __init__(self):
        self.new_text = {}       # docid -> own new text (banner + body + signature)
        self.subject = {}        # docid -> new subject
        self.body = {}           # docid -> full plain body
        self.reason = {}         # docid -> "spec" | "cascade"
        self.issues = []         # (level, docid, message)
        self.seed_reports = []
        self.order = []
        self.noquote = set()     # docids rendered without quoted history (incoherent parent link)


def compose_new_text(banner, body, sig):
    return "\n\n".join(x for x in (banner, body, sig) if x)


def topo_desc(roots, kids, docs):
    """All descendants of roots, parents before children, siblings in date order."""
    seen, out = set(), []

    def walk(x):
        for c in sorted(kids.get(x, []), key=lambda c: (docs[c].date, tk.num(c))):
            if c in seen:
                continue
            seen.add(c)
            out.append(c)
            walk(c)
    for r in roots:
        walk(r)
    return out


def build_plan(spec, docs, people, manifest, force=False):
    P = Plan()
    err = lambda k, m: P.issues.append(("ERROR", k, m))
    warn = lambda k, m: P.issues.append(("WARN", k, m))
    info = lambda k, m: P.issues.append(("INFO", k, m))
    names = sorted({p["name"] for p in people.values() if p.get("name")}, key=len, reverse=True)
    idx = tk.by_msgid(docs)
    kids = tk.children_map(docs)
    entries = spec.get("emails", [])
    if not spec.get("rewrite_id"):
        err("-", "spec needs rewrite_id (e.g. RW-P1)")
    seen = set()
    for e in entries:
        k = e.get("email", "")
        if k in seen:
            err(k, "listed twice")
            continue
        seen.add(k)
        d = docs.get(k)
        if not d:
            err(k, "not in corpus")
            continue
        if tk.num(k) <= tk.SEED_MAX:
            err(k, "seed email — locked")
            continue
        if not leaf_parts_ok(d.path):
            err(k, "unexpected MIME leaf part — would be dropped by a rebuild; skipping")
            continue
        a = anatomy(d, people, names)
        if e.get("expect_sha") and e["expect_sha"] != sha(a["core"]):
            msg = f"current text changed since the spec was written (sha {sha(a['core'])} != {e['expect_sha']})"
            if e.get("body") is None:
                info(k, msg + " — keeping the current text (mechanical fix only)")
            elif force:
                warn(k, msg + " — --force: replacing anyway")
            else:
                err(k, msg + " — re-read the email and refresh the spec (another edit landed)")
                continue
        sender = people.get(d.from_addr) or {}
        sig = sender.get("signature")
        if not sig:
            warn(k, f"no canonical signature for {d.from_addr}; keeping the existing block")
            sig = a["sig"]
        bmode = e.get("banner", "keep")
        banner = a["banner"] if bmode == "keep" else (None if bmode in ("none", None) else tk.RULES["banners"].get(bmode))
        if bmode not in ("keep", "none", None) and not banner:
            err(k, f"banner must be keep|none|{'|'.join(tk.RULES['banners'])}")
        body = a["core"] if e.get("body") is None else e["body"].strip()
        P.new_text[k] = compose_new_text(banner, body, sig)
        P.reason[k] = "spec"
        if e.get("subject") and e["subject"].strip() != d.subject:
            P.subject[k] = e["subject"].strip()
        if e.get("body") is not None:
            validate_body(P, d, body, P.subject.get(k, d.subject), sender, a)
    # subject propagation to descendants sharing the old base subject
    for k in list(P.subject):
        old_base = tk.base_subject(docs[k].subject).lower()
        new_base = tk.base_subject(P.subject[k])
        for c in topo_desc([k], kids, docs):
            cd = docs[c]
            if tk.base_subject(cd.subject).lower() != old_base or c in P.subject:
                continue
            if tk.num(c) <= tk.SEED_MAX:
                P.seed_reports.append(f"{c} (seed) carries subject '{cd.subject}' of rewritten {k} — not changed")
                continue
            prefix = cd.subject[: len(cd.subject) - len(tk.base_subject(cd.subject))]
            P.subject[c] = prefix + new_base
            P.reason.setdefault(c, "cascade")
            info(c, f"subject follows parent thread: '{cd.subject}' -> '{P.subject[c]}'")
    # render bodies: targeted emails, then every descendant, parents first
    changed_roots = sorted(P.new_text, key=lambda x: (docs[x].date, tk.num(x)))
    order = []
    for k in changed_roots:
        if k not in order:
            order.append(k)
    for c in topo_desc(changed_roots, kids, docs) + [x for x in P.subject if x not in P.new_text]:
        if c not in order:
            order.append(c)
    # make sure parents precede children in the final order
    pos = {}
    final = []

    def place(x):
        if x in pos:
            return
        p = idx.get(docs[x].irt)
        if p and p.docid in order:
            place(p.docid)
        pos[x] = len(final)
        final.append(x)
    for x in order:
        place(x)
    cur_body = {}
    cur_subject = {}

    def body_of(did):
        return cur_body.get(did, docs[did].body)

    def subject_of(did):
        return cur_subject.get(did, docs[did].subject)
    for x in final:
        d = docs[x]
        if tk.num(x) <= tk.SEED_MAX:
            P.seed_reports.append(f"{x} (seed) quotes a rewritten email — left untouched")
            continue
        parent = idx.get(d.irt)
        nt = P.new_text.get(x, d.new_text)
        if x in P.subject:
            cur_subject[x] = P.subject[x]
        coherent = parent and tk.base_subject(subject_of(x)).lower() == tk.base_subject(subject_of(parent.docid)).lower()
        if parent and not coherent and not spec.get("quote_incoherent", False):
            # unrelated In-Reply-To link: headers stay, but no quoted history is surfaced
            full = nt + "\n"
            P.noquote.add(x)
        elif parent:
            pm = tk.Msg.from_doc(parent)
            pm.body = body_of(parent.docid)
            pm.subject = subject_of(parent.docid)
            client = (people.get(d.from_addr) or {}).get("client") or tk.client_for(d.from_addr)
            full = nt + "\n\n" + tk.quote_block(pm, client, quote_kind(d)) + "\n"
        else:
            if tk.QUOTE_RE.search(d.body) and x not in P.new_text:
                continue
            full = nt + "\n"
        if full.strip() == d.body.strip() and x not in P.subject:
            continue
        cur_body[x] = full
        P.body[x] = full
        P.reason.setdefault(x, "cascade")
    P.order = [x for x in final if x in P.body or x in P.subject]
    return P


def validate_body(P, d, body, subject, sender, a):
    k = d.docid
    err = lambda m: P.issues.append(("ERROR", k, m))
    warn = lambda m: P.issues.append(("WARN", k, m))
    dt = d.date.astimezone(tk.TZ)
    if tk.QUOTE_RE.search(body):
        err("body contains quoted-history markers — write only the new text")
    sig = sender.get("signature") or ""
    if d.from_addr in body.lower() or (sig and sig.split("\n")[0] in body.split("\n")[-3:]):
        err("body appears to include a signature — the tool appends it")
    wc = words(body)
    if wc < 25:
        warn(f"only {wc} words")
    if not (40 <= wc <= 150):
        warn(f"{wc} words — P2 target is 40–150")
    for t in tk.RULES["tidy_admissions"]:
        if t.lower() in body.lower():
            warn(f"'{t}' reads as a too-tidy admission")
    text = f"{subject}\n{body}"
    for h in tk.in_period(tk.RULES["terms"], text, dt):
        err(f"knowledge cutoff: /{h['pattern']}/ not allowed before {h['not_before']} ({h['anchor']})")
    for h in tk.RULES["never"]:
        if re.search(h["pattern"], text, re.I):
            err(f"banned by design: /{h['pattern']}/ — {h['reason']}")
    for addr in d.participants:
        for pr in tk.RULES["participants"]:
            if re.search(pr["address_pattern"], addr) and dt.date() < datetime.fromisoformat(pr["not_before"]).date():
                warn(f"pre-existing header issue: {addr} before {pr['not_before']} ({pr['anchor']})")
    for s in tk.RULES["senders"]:
        if d.from_addr == s["address"] and dt.date() > datetime.fromisoformat(s["not_after"]).date():
            err(f"{s['address']} cannot send after {s['not_after']} — don't write new prose for this email")
    for fig in re.findall(r"\$\s?\d[\d,.]*\s?[KMB]?\b", body):
        f = fig.replace(" ", "")
        if f not in tk.RULES["known_figures"]:
            warn(f"figure {f} is not in the bible money ledger")
    for pid in set(PARCEL_RE.findall(body)):
        if pid not in tk.RULES["known_parcels"] and not pid.startswith("RM"):
            warn(f"parcel id {pid} is not a bible parcel")
    bp = set(PARCEL_RE.findall(body))
    sp = set(PARCEL_RE.findall(subject))
    ap = {p for fn, _, _ in d.attachments for p in PARCEL_RE.findall(fn or "")}
    if bp and sp and not (bp & sp):
        err(f"body parcels {sorted(bp)} don't match subject parcels {sorted(sp)}")
    if bp and ap and not (bp & ap):
        err(f"body parcels {sorted(bp)} don't match attachment parcels {sorted(ap)}")
    if re.search(r"\battach", body, re.I) and not d.attachments:
        warn("body mentions an attachment but the email carries none")
    if d.attachments and not re.search(r"\battach|enclos|\bsee the\b|\bfile\b|\bsheet\b|\blog\b|\bdraft\b|\bschedule\b|\bcopy\b", body, re.I):
        warn(f"email carries {[x[0] for x in d.attachments]} but the body doesn't point to it")
    if "RM-" in body and any(p.startswith(("NW", "KW")) for p in bp):
        err("Mountain Ridge decoy IDs mixed with NW/KW parcels")


# ---------------------------------------------------------------- apply

def new_path_for(d, subject):
    base = os.path.basename(d.path)
    if subject is None:
        return d.path
    return os.path.join(os.path.dirname(d.path), f"{d.docid}_{tk.slug(subject)}.eml")


def overlay(P, docs):
    """Apply a plan in memory (bodies + subjects) so a later spec can be dry-run on top of it."""
    for x in P.order:
        if x in P.body:
            docs[x].body = P.body[x]
        if x in P.subject:
            docs[x].display_path = new_path_for(docs[x], P.subject[x])
            docs[x].subject = P.subject[x]


def run(spec_path, dry, show, force, only=None, after=()):
    spec = json.load(open(spec_path))
    docs = tk.load_corpus()
    manifest, fields = tk.load_manifest()
    people = tk.build_people(docs)
    for prior in after or ():
        if not dry:
            sys.exit("--after is for dry runs only; apply specs one at a time in order")
        PP = build_plan(json.load(open(prior)), docs, people, manifest, force)
        overlay(PP, docs)
        print(f"(overlaid {os.path.basename(prior)}: {len(PP.order)} emails)")
    P = build_plan(spec, docs, people, manifest, force)
    tk.report_issues(P.issues)
    for s in P.seed_reports:
        print(f"SEED  {s}")
    n_spec = sum(1 for x in P.order if P.reason.get(x) == "spec")
    n_cas = len(P.order) - n_spec
    print(f"-- plan: {n_spec} targeted emails, {n_cas} cascade re-renders, {len(P.subject)} subject changes, "
          f"{len(P.noquote & set(P.order))} rendered without quoted history (incoherent parent)")
    if any(i[0] == "ERROR" for i in P.issues):
        if dry:
            print("(dry run: ERRORs above would abort a real run)")
        else:
            sys.exit("rewrite aborted: fix ERRORs first")
    rid = spec.get("rewrite_id", "RW-UNNAMED")
    outputs = {}
    for x in P.order:
        d = docs[x]
        raw = open(d.path, "rb").read()
        plain = P.body.get(x, d.body)
        subj = P.subject.get(x) or (d.subject if after else None)
        data = splice(raw, plain, d.attachments, subj)
        check_output(raw, data, plain, d, subj)
        outputs[x] = (new_path_for(d, P.subject.get(x)), data, plain)
    if dry:
        shown = 0
        for x in P.order:
            if only and x not in only:
                continue
            if show is not None and shown >= show:
                break
            d = docs[x]
            path, data, plain = outputs[x]
            path = path if x in P.subject else getattr(d, "display_path", path)
            print(f"\n{'=' * 100}\n{os.path.relpath(path, tk.ROOT)}   [{P.reason.get(x)}]\n{'=' * 100}")
            print(f"From: {tk.fmt_addr(d.from_name, d.from_addr)}\nTo: {', '.join(tk.fmt_addr(*t) for t in d.to)}\nDate: {d.date.astimezone(tk.TZ):%a %Y-%m-%d %H:%M}")
            print(f"Subject: {P.subject.get(x, d.subject)}{'   (was: ' + d.subject + ')' if x in P.subject else ''}\n")
            print(plain)
            shown += 1
        print(f"\n-- dry run: {len(outputs)} files would change; nothing written")
        return
    apply_outputs(rid, P, docs, outputs, fields)


def check_output(raw, data, plain, d, new_subject):
    """Post-build invariants: headers byte-identical (bar Subject/MIME), attachments identical, body as intended."""
    of, _ = raw_header_fields(raw)
    nf, _ = raw_header_fields(data)
    keep = lambda fs: [(n, b) for n, b in fs if n not in MIME_HDRS and not (new_subject is not None and n == "subject")]
    if keep(of) != keep(nf):
        raise RuntimeError(f"{d.docid}: non-MIME headers changed during rebuild")
    m = email.message_from_bytes(data, policy=policy.default)
    b = m.get_body(("plain",)).get_content()
    if b.strip() != plain.strip():
        raise RuntimeError(f"{d.docid}: plain body mismatch after rebuild")
    atts = [(p.get_filename(), p.get_content_type(), p.get_payload(decode=True)) for p in m.walk()
            if not p.is_multipart() and p.get_content_disposition() == "attachment"]
    norm = lambda xs: [(fn, ct, (data_.replace(b"\r\n", b"\n") if ct.startswith("text/") else data_)) for fn, ct, data_ in xs]
    if norm(atts) != norm(d.attachments):
        raise RuntimeError(f"{d.docid}: attachments differ after rebuild")
    if new_subject is not None and re.sub(r"\s+", " ", str(m["Subject"])).strip() != new_subject:
        raise RuntimeError(f"{d.docid}: subject not applied")


def apply_outputs(rid, P, docs, outputs, fields):
    bdir = os.path.join(RW_DIR, "backup", rid)
    if os.path.exists(os.path.join(RW_DIR, f"{rid}.apply.json")):
        sys.exit(f"{rid} already applied — rollback first (thread_kit.py rewrite-rollback {rid})")
    os.makedirs(bdir, exist_ok=True)
    rec = {"rewrite_id": rid, "applied_at": datetime.now().isoformat(timespec="seconds"), "emails": [],
           "manifest_rows": {}, "loadfile_csv_rows": {}, "loadfile_dat_rows": {}}
    for x in P.order:
        d = docs[x]
        path, data, _ = outputs[x]
        shutil.copy2(d.path, os.path.join(bdir, os.path.basename(d.path)))
        with open(path, "wb") as f:
            f.write(data)
        if path != d.path:
            os.remove(d.path)
        rec["emails"].append({"docid": x, "reason": P.reason.get(x), "old_path": os.path.relpath(d.path, tk.ROOT),
                              "new_path": os.path.relpath(path, tk.ROOT), "sha_written": hashlib.sha1(data).hexdigest()})
    renamed = {x: outputs[x][0] for x in P.subject}
    if P.subject:
        update_tables(rec, P.subject, renamed)
    json.dump(rec, open(os.path.join(RW_DIR, f"{rid}.apply.json"), "w"), indent=2)
    print(f"applied {rid}: wrote {len(rec['emails'])} emails ({len(P.subject)} subject changes); backup in {os.path.relpath(bdir, tk.ROOT)}")


def update_tables(rec, subjects, paths):
    # manifest
    with open(tk.MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    si, di = hdr.index("subject_title"), hdr.index("document_id")
    for r in rows[1:]:
        if r[di] in subjects:
            rec["manifest_rows"][r[di]] = list(r)
            r[si] = subjects[r[di]]
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    open(tk.MANIFEST, "w", encoding="utf-8", newline="").write(buf.getvalue())
    # load file csv
    with open(LOADFILE_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    hdr = rows[0]
    si, fi, di = hdr.index("SUBJECT"), hdr.index("FILEPATH"), hdr.index("DOCID")
    for r in rows[1:]:
        if r[di] in subjects:
            rec["loadfile_csv_rows"][r[di]] = list(r)
            r[si] = subjects[r[di]]
            r[fi] = os.path.relpath(paths[r[di]], tk.CORPUS)
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    open(LOADFILE_CSV, "w", encoding="utf-8", newline="").write(buf.getvalue())
    # load file dat (þ-quoted, DC4-separated)
    raw = open(LOADFILE_DAT, encoding="utf-8", newline="").read()
    lines = raw.split("\n")
    hdr = lines[0].strip("þ").split(DAT_SEP)
    si, fi, di = hdr.index("SUBJECT"), hdr.index("FILEPATH"), hdr.index("DOCID")
    for n, ln in enumerate(lines[1:], 1):
        if not ln:
            continue
        cols = ln[1:-1].split(DAT_SEP)
        if cols[di] in subjects:
            rec["loadfile_dat_rows"][cols[di]] = ln
            cols[si] = subjects[cols[di]]
            cols[fi] = os.path.relpath(paths[cols[di]], tk.CORPUS)
            lines[n] = "þ" + DAT_SEP.join(cols) + "þ"
    open(LOADFILE_DAT, "w", encoding="utf-8", newline="").write("\n".join(lines))


def rollback(rid, force=False):
    recp = os.path.join(RW_DIR, f"{rid}.apply.json")
    rec = json.load(open(recp))
    bdir = os.path.join(RW_DIR, "backup", rid)
    for e in rec["emails"]:
        newp = os.path.join(tk.ROOT, e["new_path"])
        if os.path.exists(newp) and hashlib.sha1(open(newp, "rb").read()).hexdigest() != e["sha_written"] and not force:
            sys.exit(f"{e['new_path']} changed after {rid} was applied — refusing (use --force)")
    for e in rec["emails"]:
        newp, oldp = os.path.join(tk.ROOT, e["new_path"]), os.path.join(tk.ROOT, e["old_path"])
        if os.path.exists(newp):
            os.remove(newp)
        shutil.copy2(os.path.join(bdir, os.path.basename(oldp)), oldp)
    if rec["manifest_rows"]:
        with open(tk.MANIFEST, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        rows = [rec["manifest_rows"].get(r[0], r) if i else r for i, r in enumerate(rows)]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows(rows)
        open(tk.MANIFEST, "w", encoding="utf-8", newline="").write(buf.getvalue())
    if rec["loadfile_csv_rows"]:
        with open(LOADFILE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        rows = [rec["loadfile_csv_rows"].get(r[0], r) if i else r for i, r in enumerate(rows)]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\r\n").writerows(rows)
        open(LOADFILE_CSV, "w", encoding="utf-8", newline="").write(buf.getvalue())
    if rec["loadfile_dat_rows"]:
        raw = open(LOADFILE_DAT, encoding="utf-8", newline="").read()
        lines = raw.split("\n")
        for n, ln in enumerate(lines[1:], 1):
            if ln:
                did = ln[1:-1].split(DAT_SEP)[0]
                if did in rec["loadfile_dat_rows"]:
                    lines[n] = rec["loadfile_dat_rows"][did]
        open(LOADFILE_DAT, "w", encoding="utf-8", newline="").write("\n".join(lines))
    os.remove(recp)
    print(f"rolled back {rid}: restored {len(rec['emails'])} emails, {len(rec['manifest_rows'])} manifest rows, "
          f"{len(rec['loadfile_csv_rows'])} load-file rows")
