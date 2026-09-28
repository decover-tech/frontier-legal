#!/usr/bin/env python3
"""thread_kit — expand an existing Cascade Timber email into a long, consistent thread.

The thread-expander agent writes the *story* (a JSON spec: who replies to whom, when, and
what they say). This tool does everything mechanical and checkable:

  context  <DOCID>          dossier for writing a thread off an anchor email
  validate <spec.json>      consistency checks (chronology, reply logic, knowledge cutoffs,
                            participants, figures, privilege) — no files written
  render   <spec.json>      validate, then write .eml files + manifest rows + report
           [--dry-run]      print the rendered messages instead of writing
  rollback <THREAD_ID>      delete a rendered thread's files and manifest rows
  scan                      corpus-wide thread statistics (longest chains, broken links)
  logos [--apply]           retrofit signature logos into generated docs (seed stays locked)
  people                    sender directory (org, mail client, signature, active window)

Quoting, signatures, headers, Message-IDs, References chains, logos, and file placement are
produced here so they always match the corpus conventions (see
documentation/Cascade_Timber_EML_Dataset_Plan.md, "Threading & signature spec").
"""
import argparse
import csv
import email
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from email import policy
from email.message import EmailMessage
from email.utils import format_datetime, getaddresses, parseaddr, parsedate_to_datetime
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.environ.get("THREAD_KIT_ROOT") or os.path.join(os.path.dirname(__file__), "..", ".."))
CORPUS = os.path.join(ROOT, "data", "emails")
CUSTODIANS = os.path.join(CORPUS, "Custodians")
MANIFEST = os.path.join(ROOT, "DOCUMENT_MANIFEST.csv")
WORKDIR = os.path.join(ROOT, "Logs", "threads")
RULES = json.load(open(os.path.join(os.path.dirname(__file__), "rules.json")))
TZ = ZoneInfo("America/Los_Angeles")
SEED_MAX = 250

ORGS = {
    "cascadetimber.com": "Cascade Timber Holdings, Inc.",
    "alderpointpartners.com": "Alder Point Partners",
    "bellhavenadvisory.com": "Bellhaven Advisory",
    "llassociates.com": "L&L Associates",
    "greenacresurvey.com": "GreenAcre Land Survey Co.",
    "mosslane-cpa.com": "Moss & Lane LLP",
    "larsentaxadvisory.com": "Larsen Tax Advisory",
    "whitakerforensic.com": "Whitaker Forensic Accounting",
    "irs.gov": "Internal Revenue Service",
    "northstar-comms.com": "Northstar Communications",
    "bluerivercap.com": "Blue River Capital",
    "cppension.org": "Cascade Pension Partners",
    "willamettefh.com": "Willamette Family Holdings",
    "northforkef.com": "North Fork Energy Fund",
}
QUOTE_RE = re.compile(r"^(-----Original Message-----|---------- Forwarded message -+|On .+ wrote:\s*$)", re.M)


# ---------------------------------------------------------------- corpus loading

def num(docid):
    return int(docid.split("-")[1])


def fmt_addr(name, addr):
    return f"{name} <{addr}>" if name else addr


class Doc:
    def __init__(self, path):
        with open(path, "rb") as f:
            m = email.message_from_binary_file(f, policy=policy.default)
        self.path = path
        self.docid = str(m["X-Decover-DocID"])
        self.custodian = os.path.basename(os.path.dirname(path))
        self.msgid = str(m["Message-ID"] or "").strip()
        self.irt = str(m["In-Reply-To"] or "").strip()
        self.refs = str(m["References"] or "").split()
        self.from_name, self.from_addr = parseaddr(str(m["From"]))
        self.from_addr = self.from_addr.lower()
        self.to = [(n, a.lower()) for n, a in getaddresses([str(m["To"] or "")]) if a]
        self.cc = [(n, a.lower()) for n, a in getaddresses([str(m["Cc"] or "")]) if a]
        self.date = parsedate_to_datetime(str(m["Date"]))
        self.subject = re.sub(r"\s+", " ", str(m["Subject"] or "")).strip()
        body = m.get_body(("plain",))
        self.body = body.get_content() if body else ""
        self.attachments = []
        self.logo = None
        for part in m.walk():
            if part.is_multipart():
                continue
            disp = part.get_content_disposition()
            if disp == "attachment":
                self.attachments.append((part.get_filename(), part.get_content_type(), part.get_payload(decode=True)))
            elif disp == "inline" and part.get_content_type().startswith("image/"):
                self.logo = part.get_payload(decode=True)

    @property
    def participants(self):
        return {self.from_addr} | {a for _, a in self.to} | {a for _, a in self.cc}

    @property
    def new_text(self):
        """The message's own text, above any quoted history."""
        m = QUOTE_RE.search(self.body)
        return (self.body[: m.start()] if m else self.body).rstrip()


def load_corpus():
    docs = {}
    for p in sorted(glob.glob(os.path.join(CUSTODIANS, "*", "*.eml"))):
        d = Doc(p)
        docs.setdefault(d.docid, d)
    return docs


def load_manifest():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["document_id"]: r for r in rows}, (rows[0].keys() if rows else [])


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")[:90]


def base_subject(s):
    return re.sub(r"^\s*((re|fw|fwd)\s*:\s*)+", "", s, flags=re.I).strip()


# ---------------------------------------------------------------- people directory

def client_for(addr):
    return "outlook" if addr.split("@")[-1] in RULES["outlook_domains"] else "gmail"


def extract_signature(doc):
    lines = doc.new_text.splitlines()
    name = doc.from_name or ""
    first = name.split()[0] if name else None
    for i in range(len(lines) - 1, max(-1, len(lines) - 25), -1):
        ln = lines[i].strip()
        if name and (ln.startswith(name) or (first and ln.startswith(first + " ") and len(ln) < 60)):
            sig = "\n".join(lines[i:]).strip()
            dom = doc.from_addr.split("@")[-1]
            # reject signatures carrying another org's block (a known defect in generated batches)
            for d, org in ORGS.items():
                if d != dom and org in sig:
                    return None
            return sig
    return None


def build_people(docs):
    people = {}
    by_sender = defaultdict(list)
    for d in docs.values():
        by_sender[d.from_addr].append(d)
    folders = set(os.listdir(CUSTODIANS))
    for addr, ds in by_sender.items():
        ds.sort(key=lambda d: num(d.docid))
        name = Counter(d.from_name for d in ds).most_common(1)[0][0]
        sig = None
        for d in ds:  # seed first, then generated; skip alias variants (e.g. "Kane" for Whitfield)
            if d.from_name != name:
                continue
            sig = extract_signature(d)
            if sig:
                break
        if not sig and "@" in addr and addr.split("@")[0] in ("hr", "facilities", "it-notifications"):
            sig = f"{name}\n{ORGS.get(addr.split('@')[-1], '')}".strip()
        folder = name.replace(" ", "_") if name.replace(" ", "_") in folders else None
        dates = sorted(d.date for d in ds)
        people[addr] = {
            "name": name, "address": addr, "org": ORGS.get(addr.split("@")[-1], addr.split("@")[-1]),
            "client": client_for(addr), "logo": addr.split("@")[-1] in RULES["logo_domains"],
            "signature": sig, "custodian_folder": folder,
            "first_sent": dates[0].date().isoformat(), "last_sent": dates[-1].date().isoformat(),
            "sent_count": len(ds),
        }
    overrides = os.path.join(os.path.dirname(__file__), "people_overrides.json")
    if os.path.exists(overrides):
        for addr, patch in json.load(open(overrides)).items():
            if not addr.startswith("_"):
                people.setdefault(addr, {"address": addr, "sent_count": 0, "first_sent": None, "last_sent": None,
                                         "client": client_for(addr), "logo": False, "custodian_folder": None,
                                         "org": ORGS.get(addr.split("@")[-1], "")}).update(patch)
    # recipients who never send (keep for address validation)
    for d in docs.values():
        for n, a in d.to + d.cc:
            if a not in people:
                folder = n.replace(" ", "_") if n and n.replace(" ", "_") in folders else None
                people[a] = {"name": n, "address": a, "org": ORGS.get(a.split("@")[-1], a.split("@")[-1]),
                             "client": client_for(a), "logo": False, "signature": None,
                             "custodian_folder": folder, "first_sent": None, "last_sent": None, "sent_count": 0}
    return people


LOGO_DIR = os.path.join(os.path.dirname(__file__), "logos")
CONTACT_RE = re.compile(r"^(?:.*\|\s*)?([\w.+-]+)@([\w.-]+)$")
_logo_cache = {}


def logo_for(domain):
    fn = RULES["logo_domains"].get(domain)
    if fn and fn not in _logo_cache:
        _logo_cache[fn] = open(os.path.join(LOGO_DIR, fn), "rb").read()
    return _logo_cache.get(fn)


def html_with_logos(plain):
    """HTML alternative of a plain body with an org logo after every matching signature
    contact line (quoted layers included). Returns (html, [png bytes in cid order]) or (None, [])."""
    import html as H
    out, imgs, depth = [], [], 0
    style = "margin:0 0 0 .8ex;border-left:1px solid #ccc;padding-left:1ex"
    for line in plain.rstrip("\n").split("\n"):
        m = re.match(r"^((?:> ?)*)(.*)$", line)
        d = m.group(1).count(">")
        content = m.group(2)
        while depth < d:
            out.append(f'<blockquote style="{style}">'); depth += 1
        while depth > d:
            out.append("</blockquote>"); depth -= 1
        out.append((H.escape(content) or "&nbsp;") + "<br>")
        c = CONTACT_RE.match(content.strip())
        if c and not re.match(r"^(From|To|Cc|Sent|Date):", content.strip()) and \
                c.group(1).lower() not in RULES["logo_excluded_mailboxes"]:
            png = logo_for(c.group(2).lower())
            if png:
                n = len(imgs) + 1
                imgs.append(png)
                org = ORGS.get(c.group(2).lower(), "")
                out.append(f'<img src="cid:{{CID{n}}}" alt="{H.escape(org)}" style="margin:4px 0"><br>')
    out += ["</blockquote>"] * depth
    if not imgs:
        return None, []
    body = "\n".join(out)
    return ('<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>'
            '<body><div style="font-family:Calibri,Arial,sans-serif;font-size:11pt">\n' + body + "\n</div></body></html>"), imgs


# ---------------------------------------------------------------- thread graph

def by_msgid(docs):
    return {d.msgid: d for d in docs.values() if d.msgid}


def children_map(docs):
    idx = by_msgid(docs)
    kids = defaultdict(list)
    for d in docs.values():
        if d.irt in idx:
            kids[idx[d.irt].docid].append(d.docid)
    return kids


def ancestors(doc, idx):
    chain, seen, cur = [], set(), doc
    while cur.irt in idx and cur.irt not in seen:
        seen.add(cur.irt)
        cur = idx[cur.irt]
        chain.append(cur)
    return list(reversed(chain))


def coherent(child, parent):
    return base_subject(child.subject).lower() == base_subject(parent.subject).lower()


# ---------------------------------------------------------------- date formatting

def outlook_sent(dt):
    return dt.strftime("%A, %B ") + str(dt.day) + dt.strftime(", %Y ") + dt.strftime("%I:%M %p").lstrip("0")


def gmail_date(dt):
    return dt.strftime("%a, %b ") + str(dt.day) + dt.strftime(", %Y at ") + dt.strftime("%I:%M %p").lstrip("0")


def parse_local(s):
    dt = datetime.fromisoformat(s)
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt


# ---------------------------------------------------------------- spec handling

class Msg:
    """A message (existing corpus doc or spec-defined) in a uniform shape for quoting."""

    def __init__(self, docid, msgid, from_name, from_addr, to, cc, date, subject, body, refs, attachments):
        self.docid, self.msgid = docid, msgid
        self.from_name, self.from_addr = from_name, from_addr
        self.to, self.cc, self.date, self.subject = to, cc, date, subject
        self.body, self.refs, self.attachments = body, refs, attachments

    @property
    def participants(self):
        return {self.from_addr} | {a for _, a in self.to} | {a for _, a in self.cc}

    @classmethod
    def from_doc(cls, d):
        return cls(d.docid, d.msgid, d.from_name, d.from_addr, d.to, d.cc, d.date.astimezone(TZ),
                   d.subject, d.body, d.refs, d.attachments)


def next_docid(docs, manifest):
    used = [num(k) for k in list(docs) + list(manifest)]
    for rec in glob.glob(os.path.join(WORKDIR, "*.render.json")):
        used += [num(x) for x in json.load(open(rec))["docids"]]
    return max(used) + 1


def resolve_person(addr, people, spec):
    addr = addr.lower()
    for p in spec.get("new_people", []):
        if p["address"].lower() == addr:
            base = {"client": client_for(addr), "logo": False, "custodian_folder": None,
                    "org": ORGS.get(addr.split("@")[-1], addr.split("@")[-1])}
            base.update(p)
            base["address"] = addr
            return base
    return people.get(addr)


def as_list(v):
    if v is None:
        return []
    return [v] if isinstance(v, str) else list(v)


def quote_block(parent, client, kind):
    to = "; ".join(fmt_addr(n, a) for n, a in parent.to)
    cc = "; ".join(fmt_addr(n, a) for n, a in parent.cc)
    if client == "outlook":
        hdr = ["-----Original Message-----", f"From: {fmt_addr(parent.from_name, parent.from_addr)}",
               f"Sent: {outlook_sent(parent.date)}", f"To: {to}"]
        if cc:
            hdr.append(f"Cc: {cc}")
        hdr.append(f"Subject: {parent.subject}")
        return "\n".join(hdr) + "\n\n" + parent.body.rstrip()
    if kind == "forward":
        hdr = ["---------- Forwarded message ----------", f"From: {fmt_addr(parent.from_name, parent.from_addr)}",
               f"Date: {gmail_date(parent.date)}", f"Subject: {parent.subject}", f"To: {', '.join(fmt_addr(n, a) for n, a in parent.to)}"]
        if cc:
            hdr.append(f"Cc: {', '.join(fmt_addr(n, a) for n, a in parent.cc)}")
        return "\n".join(hdr) + "\n\n" + parent.body.rstrip()
    lead = f"On {gmail_date(parent.date)} {fmt_addr(parent.from_name, parent.from_addr)} wrote:"
    quoted = "\n".join(("> " + ln) if ln.strip() else ">" for ln in parent.body.rstrip().splitlines())
    return lead + "\n\n" + quoted


def subject_for(parent_subject, client, kind, override=None):
    if override:
        return override
    # Mail clients don't double a reply prefix, but do stack FW: on top of RE: ("FW: RE: x").
    if kind == "forward":
        return ("FW: " if client == "outlook" else "Fwd: ") + parent_subject
    if re.match(r"^\s*re\s*:", parent_subject, re.I):
        return parent_subject
    return ("RE: " if client == "outlook" else "Re: ") + parent_subject


def build(spec, docs, people, manifest):
    """Resolve the spec into rendered message dicts. Returns (messages, issues)."""
    issues = []
    err = lambda k, m: issues.append(("ERROR", k, m))
    warn = lambda k, m: issues.append(("WARN", k, m))

    anchor_id = spec.get("anchor")
    if anchor_id not in docs:
        err("-", f"anchor {anchor_id} not found in corpus")
        return [], issues
    idx_new = {}
    out = []
    start = spec.get("start_docid") or next_docid(docs, manifest)
    n = start
    thread_id = spec.get("thread_id") or "THR-UNNAMED"

    for i, m in enumerate(spec.get("messages", [])):
        key = m.get("key") or f"m{i + 1}"
        if key in idx_new:
            err(key, "duplicate key")
            continue
        kind = m.get("kind", "reply")
        if kind not in ("reply", "reply_all", "forward"):
            err(key, f"kind must be reply|reply_all|forward, got {kind!r}")
            continue
        pref = m.get("parent") or anchor_id
        if pref in idx_new:
            parent = idx_new[pref]["_msg"]
        elif pref in docs:
            parent = Msg.from_doc(docs[pref])
        else:
            err(key, f"parent {pref!r} is neither an earlier spec key nor a corpus DocID")
            continue

        sender = resolve_person(m.get("from", ""), people, spec)
        if not sender:
            err(key, f"unknown sender {m.get('from')!r} (declare in new_people if intentional)")
            continue
        recips = {}
        for field in ("to", "cc"):
            lst = []
            for a in as_list(m.get(field)):
                p = resolve_person(a, people, spec)
                if not p:
                    err(key, f"unknown {field} address {a!r}")
                    continue
                lst.append((p["name"], p["address"]))
            recips[field] = lst
        if not recips["to"]:
            err(key, "message has no To recipients")

        try:
            dt = parse_local(m["date"])
        except Exception:
            err(key, f"bad date {m.get('date')!r} (use YYYY-MM-DDTHH:MM, Pacific local time)")
            continue

        client = sender["client"]
        subject = subject_for(parent.subject, client, kind, m.get("subject"))
        body = (m.get("body") or "").strip()
        banner = RULES["banners"].get(m.get("banner")) if m.get("banner") else None
        if m.get("banner") and not banner:
            err(key, f"banner must be one of {list(RULES['banners'])}")
        parts = []
        if banner:
            parts.append(banner)
        if body:
            parts.append(body)
        if m.get("signature", True):
            if sender.get("signature"):
                parts.append(sender["signature"])
            else:
                warn(key, f"no corpus signature for {sender['address']}; add one via new_people/signature")
        new_text = "\n\n".join(parts)
        full = new_text + "\n\n" + quote_block(parent, client, kind) + "\n" if m.get("quote", True) else new_text + "\n"

        atts = []
        if kind == "forward" and m.get("keep_attachments", True):
            atts += list(parent.attachments)
        for a in m.get("attachments", []):
            if "from_doc" in a:
                src = docs.get(a["from_doc"])
                found = [x for x in (src.attachments if src else []) if not a.get("filename") or x[0] == a["filename"]]
                if not found:
                    err(key, f"attachment source {a} not found")
                atts += found
            else:
                fn, content = a.get("filename"), a.get("content", "")
                ctype = "text/csv" if fn.lower().endswith(".csv") else "text/plain"
                atts.append((fn, ctype, content.encode("utf-8")))

        docid = f"EMAIL-{n}"
        n += 1
        if docid in docs or docid in manifest:
            err(key, f"{docid} is already used in the corpus/manifest — pick another start_docid")
        dom = sender["address"].split("@")[-1]
        msgid = f"<email-{num(docid)}.{dt.strftime('%Y%m%d%H%M')}@{dom}>"
        refs = (parent.refs or []) + [parent.msgid]
        msg = Msg(docid, msgid, sender["name"], sender["address"], recips["to"], recips["cc"], dt,
                  subject, full, refs, atts)
        custodian = m.get("custodian") or sender.get("custodian_folder") or next(
            (people.get(a, {}).get("custodian_folder") for _, a in recips["to"] + recips["cc"]
             if people.get(a, {}).get("custodian_folder")), None)
        if not custodian or not os.path.isdir(os.path.join(CUSTODIANS, custodian)):
            err(key, f"no custodian folder for this message (set 'custodian'; got {custodian!r})")
        rec = {"key": key, "kind": kind, "parent_ref": pref, "parent": parent, "sender": sender,
               "body": body, "new_text": new_text, "banner": m.get("banner"), "custodian": custodian,
               "duplicates": as_list(m.get("duplicates")), "arc": m.get("arc", spec.get("arc", "")),
               "event_id": m.get("event_id", spec.get("event_id", "")),
               "role": m.get("role", f"thread expansion ({thread_id})"), "short_ok": m.get("short_ok", False),
               "_msg": msg, "spec": m}
        idx_new[key] = rec
        out.append(rec)
    for r in out:  # duplicates consume DocIDs after the main run
        r["dup_ids"] = []
        for _ in r["duplicates"]:
            r["dup_ids"].append(f"EMAIL-{n}")
            n += 1
    return out, issues


# ---------------------------------------------------------------- validation

def in_period(pattern_list, text, dt):
    hits = []
    for r in pattern_list:
        if re.search(r["pattern"], text, re.I) and dt.date() < datetime.fromisoformat(r["not_before"]).date():
            hits.append(r)
    return hits


def validate(spec, docs, people, manifest):
    msgs, issues = build(spec, docs, people, manifest)
    err = lambda k, m: issues.append(("ERROR", k, m))
    warn = lambda k, m: issues.append(("WARN", k, m))
    info = lambda k, m: issues.append(("INFO", k, m))
    if not spec.get("thread_id"):
        err("-", "spec needs a thread_id (e.g. THR-004)")
    if not spec.get("bible_refs"):
        warn("-", "spec should cite bible_refs (§ + tag) for the facts it relies on")
    short = 0
    for r in msgs:
        m, p, k = r["_msg"], r["parent"], r["key"]
        # chronology
        if m.date <= p.date + timedelta(minutes=1):
            err(k, f"date {m.date:%Y-%m-%d %H:%M} is not after parent {p.docid or r['parent_ref']} ({p.date:%Y-%m-%d %H:%M})")
        gap = m.date - p.date
        if gap > timedelta(days=21):
            warn(k, f"{gap.days}-day gap to parent — long threads usually move in hours/days; justify or split")
        if m.date.year > 2023 or m.date < datetime(2021, 11, 1, tzinfo=TZ):
            err(k, "date outside the matter window (Nov 2021 – Dec 2023)")
        if m.date.weekday() >= 5:
            warn(k, "sent on a weekend — fine if intentional (e.g. deadline crunch)")
        if not (6 <= m.date.hour < 21):
            warn(k, f"sent at {m.date:%H:%M} — outside normal hours")
        # reply logic
        if r["kind"] in ("reply", "reply_all", "forward") and m.from_addr not in p.participants:
            err(k, f"{m.from_addr} was not on the parent message, so can't {'forward' if r['kind'] == 'forward' else 'reply to'} it")
        rcpt = {a for _, a in m.to + m.cc}
        if r["kind"] in ("reply", "reply_all") and m.from_addr != p.from_addr and p.from_addr not in rcpt:
            err(k, f"reply does not go back to the parent's sender {p.from_addr}")
        if r["kind"] == "reply_all":
            dropped = p.participants - rcpt - {m.from_addr}
            if dropped:
                info(k, f"reply-all drops {sorted(dropped)} — make sure the story means it")
        if r["kind"] == "forward":
            added = rcpt - p.participants
            if added:
                info(k, f"forward brings in new readers {sorted(added)}")
        # body sanity
        body = r["body"]
        if QUOTE_RE.search(body):
            err(k, "body contains quoted-history markers — write only the new text; the tool renders quoting")
        if m.from_addr in body.lower() or (r["sender"].get("signature") and r["sender"]["signature"].split("\n")[0] in body.split("\n")[-3:]):
            err(k, "body appears to include a signature — the tool appends it")
        words = len(re.findall(r"\w+", body))
        if not body and r["kind"] != "forward":
            err(k, "empty body on a reply")
        if 0 < words < 25 and not r["short_ok"]:
            short += 1
        for t in RULES["tidy_admissions"]:
            if t.lower() in body.lower():
                warn(k, f"'{t}' reads as a too-tidy admission — known corpus weakness; rephrase unless seed-anchored")
        # knowledge cutoffs
        att_text = " ".join(a[2].decode("utf-8", "ignore") for a in m.attachments
                            if a[1].startswith("text/") and r["kind"] != "forward")
        text = f"{m.subject}\n{body}\n{att_text}"
        for h in in_period(RULES["terms"], text, m.date):
            err(k, f"knowledge cutoff: /{h['pattern']}/ not allowed before {h['not_before']} ({h['anchor']})")
        for h in RULES["never"]:
            if re.search(h["pattern"], text, re.I):
                err(k, f"banned by design: /{h['pattern']}/ — {h['reason']}")
        for a in m.participants:
            for pr in RULES["participants"]:
                if re.search(pr["address_pattern"], a) and m.date.date() < datetime.fromisoformat(pr["not_before"]).date():
                    err(k, f"{a} cannot appear before {pr['not_before']} ({pr['anchor']})")
        for s in RULES["senders"]:
            if m.from_addr == s["address"] and m.date.date() > datetime.fromisoformat(s["not_after"]).date():
                err(k, f"{s['address']} cannot send after {s['not_after']} — {s['reason']}")
            elif s["address"] in rcpt and m.date.date() > datetime.fromisoformat(s["not_after"]).date():
                warn(k, f"{s['address']} is a recipient after {s['not_after']} — {s['reason']}")
        # facts
        for fig in re.findall(r"\$\s?\d[\d,.]*\s?[KMB]?\b", body):
            f = fig.replace(" ", "")
            if f not in RULES["known_figures"]:
                warn(k, f"figure {f} is not in the bible money ledger — confirm it reconciles (bible §2/§3)")
        for pid in set(re.findall(r"\b[A-Z]{2}-\d{2}\b", body)):
            if pid not in RULES["known_parcels"] and not pid.startswith("RM"):
                warn(k, f"parcel id {pid} is not a bible parcel (NW-01..08, KW-01/02, RM-* decoys)")
        # privilege
        if r["banner"]:
            outside = [a for a in m.participants if any(a.endswith(d) for d in RULES["outside_parties"])]
            if outside:
                warn(k, f"privilege banner with outside parties {outside} — likely vitiated; intended? ({RULES['privilege_note']})")
        if r["custodian"] and r["custodian"] not in {people.get(a, {}).get("custodian_folder") for a in m.participants}:
            warn(k, f"custodian {r['custodian']} is not a participant — collected from a non-party mailbox?")
    if msgs:
        if short > 0.4 * len(msgs):
            warn("-", f"{short}/{len(msgs)} messages under 25 words — corpus is already criticized for short, convenient replies")
        depth = max(len(chain_of(r, msgs)) for r in msgs)
        if len(msgs) < 5:
            warn("-", f"only {len(msgs)} new messages — the goal is long chains (8–20)")
        info("-", f"{len(msgs)} new messages; deepest chain from anchor = {depth + 1} messages (incl. anchor + existing ancestors not counted)")
    return msgs, issues


def chain_of(r, msgs):
    keys = {x["key"]: x for x in msgs}
    c = [r]
    while c[-1]["parent_ref"] in keys:
        c.append(keys[c[-1]["parent_ref"]])
    return c


# ---------------------------------------------------------------- rendering

def build_mime(headers, plain, attachments):
    """headers: list of (name, value) in order (no Content-*/MIME-Version)."""
    em = EmailMessage(policy=policy.default)
    for k, v in headers:
        em[k] = v
    em.set_content(plain, charset="utf-8", cte="quoted-printable")
    html, imgs = html_with_logos(plain)
    if html:
        tag = os.urandom(4).hex().upper() + "." + os.urandom(4).hex().upper()
        cids = [f"image{n:03d}.png@01D{tag}" for n in range(1, len(imgs) + 1)]
        for n, cid in enumerate(cids, 1):
            html = html.replace(f"{{CID{n}}}", cid)
        em.add_alternative(html, subtype="html", charset="utf-8", cte="quoted-printable")
        hpart = em.get_payload()[1]
        for n, (png, cid) in enumerate(zip(imgs, cids), 1):
            hpart.add_related(png, "image", "png", cid=f"<{cid}>", filename=f"image{n:03d}.png", disposition="inline")
    for fn, ctype, data in attachments:
        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            em.add_attachment(data.decode("utf-8", "ignore"), subtype=subtype, filename=fn)
        else:
            em.add_attachment(data, maintype=maintype, subtype=subtype, filename=fn)
    return em.as_bytes(policy=policy.default.clone(linesep="\n"))


def to_eml(m):
    h = [("From", fmt_addr(m.from_name, m.from_addr)), ("To", ", ".join(fmt_addr(n, a) for n, a in m.to))]
    if m.cc:
        h.append(("Cc", ", ".join(fmt_addr(n, a) for n, a in m.cc)))
    h += [("Subject", m.subject), ("Message-ID", m.msgid), ("Date", format_datetime(m.date))]
    if m.refs:
        h += [("In-Reply-To", m.refs[-1]), ("References", " ".join(m.refs))]
    h.append(("X-Decover-DocID", m.docid))
    return build_mime(h, m.body, m.attachments)


def retrofit_logos(docs, apply):
    """Rebuild generated docs (DocID > 250) so Outlook-org signatures carry logos. Headers and
    plain text are preserved verbatim; old inline images are replaced; true attachments kept."""
    changed = 0
    for d in sorted(docs.values(), key=lambda d: num(d.docid)):
        if num(d.docid) <= SEED_MAX:
            continue
        html, imgs = html_with_logos(d.body)
        if not html and not d.logo:
            continue
        with open(d.path, "rb") as f:
            m = email.message_from_binary_file(f, policy=policy.default)
        hdrs = [(k, v) for k, v in m.items() if not k.lower().startswith("content-") and k.lower() != "mime-version"]
        data = build_mime(hdrs, d.body, d.attachments)
        changed += 1
        if apply:
            with open(d.path, "wb") as f:
                f.write(data)
    print(f"{'rewrote' if apply else 'would rewrite'} {changed} generated docs (seed EMAIL-001–{SEED_MAX:03d} untouched)")


def manifest_row(r, docid, custodian, family, parent_docid, role):
    m = r["_msg"]
    return {
        "document_id": docid, "family_id": family, "parent_id": parent_docid,
        "datetime": m.date.strftime("%m/%d/%Y %H:%M:%S %z"),
        "sender_author": fmt_addr(m.from_name, m.from_addr),
        "recipients": "; ".join(fmt_addr(n, a) for n, a in m.to + m.cc),
        "custodian": custodian.replace("_", " "), "document_type": "email",
        "subject_title": m.subject, "arc": r["arc"], "event_id": r["event_id"],
        "intended_evidentiary_role": role, "expected_attachment_count": str(len(m.attachments)),
        "status": "thread-expansion",
    }


def render(spec, docs, people, manifest, fields, dry):
    msgs, issues = validate(spec, docs, people, manifest)
    report_issues(issues)
    if any(i[0] == "ERROR" for i in issues):
        sys.exit("render aborted: fix ERRORs first")
    anchor = spec["anchor"]
    family = manifest.get(anchor, {}).get("family_id") or anchor
    files, rows = [], []
    for r in msgs:
        m = r["_msg"]
        parent_docid = r["parent"].docid
        copies = [(m.docid, r["custodian"], r["role"])] + [
            (did, c, f"custodial duplicate of {m.docid}") for did, c in zip(r["dup_ids"], r["duplicates"])]
        for did, cust, role in copies:
            m.docid = did
            data = to_eml(m)
            path = os.path.join(CUSTODIANS, cust, f"{did}_{slug(m.subject)}.eml")
            if dry:
                print(f"\n{'=' * 100}\n{os.path.relpath(path, ROOT)}\n{'=' * 100}")
                print(f"From: {fmt_addr(m.from_name, m.from_addr)}\nTo: {m.to}\nCc: {m.cc}\nDate: {format_datetime(m.date)}\nSubject: {m.subject}\n")
                print(m.body)
            else:
                if os.path.exists(path):
                    sys.exit(f"refusing to overwrite {path}")
                with open(path, "wb") as f:
                    f.write(data)
                files.append(os.path.relpath(path, ROOT))
            rows.append(manifest_row(r, did, cust, family, parent_docid, role))
        m.docid = copies[0][0]
    if dry:
        return
    with open(MANIFEST, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        for row in rows:
            w.writerow(row)
    os.makedirs(WORKDIR, exist_ok=True)
    tid = spec["thread_id"]
    json.dump({"thread_id": tid, "anchor": anchor, "docids": [r["document_id"] for r in rows], "files": files,
               "rendered_at": datetime.now().isoformat(timespec="seconds")},
              open(os.path.join(WORKDIR, f"{tid}.render.json"), "w"), indent=2)
    write_report(spec, msgs, rows, issues)
    print(f"\nrendered {len(rows)} docs ({rows[0]['document_id']}–{rows[-1]['document_id']}); report: Logs/threads/{tid}_REPORT.md")


def write_report(spec, msgs, rows, issues):
    tid = spec["thread_id"]
    L = [f"# {tid} — thread expansion report", "",
         f"Anchor: {spec['anchor']}  |  Arc: {spec.get('arc', '')}  |  Event: {spec.get('event_id', '')}",
         f"Bible refs: {', '.join(spec.get('bible_refs', []))}", "", spec.get("rationale", ""), "",
         "| DocID | Parent | Kind | Date (PT) | From | # recipients | Subject | Custodian |", "|---|---|---|---|---|---|---|---|"]
    byid = {r["_msg"].docid: r for r in msgs}
    for row in rows:
        r = byid.get(row["document_id"])
        kind = r["kind"] if r else "dup"
        L.append(f"| {row['document_id']} | {row['parent_id']} | {kind} | {row['datetime']} | {row['sender_author'].split(' <')[0]} | "
                 f"{row['recipients'].count('<')} | {row['subject_title']} | {row['custodian']} |")
    L += ["", "## Validation (at render time)", ""]
    L += [f"- {lvl} [{k}] {m}" for lvl, k, m in issues if lvl != "ERROR"] or ["- clean"]
    L += ["", "## Continuity checks run", "",
          "- Chronology: every message after its parent; backward-only In-Reply-To/References.",
          f"- Knowledge cutoffs: {len(RULES['terms'])} dated term rules + {len(RULES['participants'])} participant windows + sender departures.",
          "- Seed EMAIL-001–250 untouched (expansion only adds children).", ""]
    open(os.path.join(WORKDIR, f"{tid}_REPORT.md"), "w").write("\n".join(L))


def report_issues(issues):
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    for lvl, k, m in sorted(issues, key=lambda i: order[i[0]]):
        print(f"{lvl:5} [{k}] {m}")
    c = Counter(i[0] for i in issues)
    print(f"-- {c['ERROR']} errors, {c['WARN']} warnings, {c['INFO']} info")


def rollback(tid, fields):
    recp = os.path.join(WORKDIR, f"{tid}.render.json")
    rec = json.load(open(recp))
    for f in rec["files"]:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            os.remove(p)
    ids = set(rec["docids"])
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if not (r["document_id"] in ids and r["status"] == "thread-expansion")]
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    os.remove(recp)
    print(f"rolled back {tid}: removed {len(rec['files'])} files and {len(ids)} manifest rows")


# ---------------------------------------------------------------- context / scan

def cutoffs_at(dt):
    banned = [r for r in RULES["terms"] if dt.date() < datetime.fromisoformat(r["not_before"]).date()]
    soon = [r for r in RULES["terms"] if dt.date() <= datetime.fromisoformat(r["not_before"]).date() < (dt + timedelta(days=45)).date()]
    return banned, soon


def context(docid, docs, people, manifest, window):
    if docid not in docs:
        sys.exit(f"{docid} not in corpus")
    d = docs[docid]
    idx = by_msgid(docs)
    kids = children_map(docs)
    P = print
    P(f"# Context for {docid}  (seed={'yes — LOCKED, expand only by adding replies' if num(docid) <= SEED_MAX else 'no'})\n")
    P(f"File: {os.path.relpath(d.path, ROOT)}")
    row = manifest.get(docid, {})
    P(f"Manifest: arc={row.get('arc')} event={row.get('event_id')} family={row.get('family_id')} role={row.get('intended_evidentiary_role')}")
    P(f"Date: {d.date.astimezone(TZ):%a %Y-%m-%d %H:%M %Z}   From: {fmt_addr(d.from_name, d.from_addr)}")
    P(f"To: {', '.join(fmt_addr(*x) for x in d.to)}   Cc: {', '.join(fmt_addr(*x) for x in d.cc)}")
    P(f"Subject: {d.subject}   Attachments: {[a[0] for a in d.attachments]}\n")
    P("## Body\n" + d.body.rstrip() + "\n")
    anc = ancestors(d, idx)
    P("## Existing thread")
    if d.irt and d.irt not in idx:
        P(f"- In-Reply-To {d.irt} points outside the corpus")
    for a in anc:
        P(f"- ancestor {a.docid} {a.date.astimezone(TZ):%Y-%m-%d %H:%M} {a.from_name}: {a.subject}")
    if anc and not coherent(d, anc[-1]):
        P(f"  ! header link looks broken: parent subject differs ('{anc[-1].subject}') — don't build on that link")

    def walk(x, depth):
        for c in sorted(kids.get(x, []), key=lambda c: docs[c].date):
            cd = docs[c]
            P(f"{'  ' * depth}- child {c} {cd.date.astimezone(TZ):%Y-%m-%d %H:%M} {cd.from_name}: {cd.subject}"
              + ("" if coherent(cd, docs[x]) else "  ! broken link (subject differs)"))
            walk(c, depth + 1)
    walk(docid, 0)
    if not anc and not kids.get(docid):
        P("- standalone (no ancestors or replies in corpus)")
    P("\n## Participants")
    for a in sorted(d.participants):
        p = people.get(a, {})
        P(f"- {p.get('name')} <{a}> | {p.get('org')} | client={p.get('client')} | logo={p.get('logo')} | "
          f"custodian={p.get('custodian_folder')} | sends {p.get('first_sent')}..{p.get('last_sent')} ({p.get('sent_count')})")
        for s in RULES["senders"]:
            if s["address"] == a:
                P(f"    ! {s['reason']} (no sending after {s['not_after']})")
    banned, soon = cutoffs_at(d.date)
    P(f"\n## Knowledge cutoffs as of {d.date.date()} — NOT yet knowable")
    for r in banned:
        P(f"- until {r['not_before']}: /{r['pattern']}/  ({r['anchor']})")
    if soon:
        P("\n## Becomes knowable within 45 days (a long thread may cross these — check each message's own date)")
        for r in soon:
            P(f"- {r['not_before']}: /{r['pattern']}/")
    for pr in RULES["participants"]:
        if d.date.date() < datetime.fromisoformat(pr["not_before"]).date():
            P(f"- participant {pr['address_pattern']} not before {pr['not_before']}")
    lo, hi = d.date - timedelta(days=window), d.date + timedelta(days=window)
    P(f"\n## Corpus neighbors (±{window}d, shared participant or same arc)")
    arc = row.get("arc")
    near = []
    for x in docs.values():
        if x.docid == docid or not (lo <= x.date <= hi):
            continue
        same_arc = arc and manifest.get(x.docid, {}).get("arc") == arc
        if x.participants & d.participants or same_arc:
            near.append(x)
    for x in sorted(near, key=lambda x: x.date)[:60]:
        P(f"- {x.docid} {x.date.astimezone(TZ):%Y-%m-%d %H:%M} [{manifest.get(x.docid, {}).get('arc', '?')}] "
          f"{x.from_name} → {', '.join(n or a for n, a in x.to)[:60]}: {x.subject}")
    unrendered = [r for k, r in manifest.items() if k not in docs and r.get("arc") == arc and r["datetime"]
                  and lo.replace(tzinfo=None) <= datetime.strptime(r["datetime"][:19], "%m/%d/%Y %H:%M:%S") <= hi.replace(tzinfo=None)]
    if unrendered:
        P(f"\n## Planned but not yet rendered (manifest, same arc, ±{window}d) — don't pre-empt these")
        for r in unrendered[:30]:
            P(f"- {r['document_id']} {r['datetime'][:16]} {r['sender_author'].split(' <')[0]}: {r['subject_title']}")
    P(f"\nNext free DocID: EMAIL-{next_docid(docs, manifest)}")


def scan(docs):
    idx = by_msgid(docs)
    broken = sum(1 for d in docs.values() if d.irt and (d.irt not in idx or not coherent(d, idx[d.irt])))
    dangling = sum(1 for d in docs.values() if d.irt and d.irt not in idx)

    def depth(d):
        n, cur, seen = 1, d, set()
        while cur.irt in idx and coherent(cur, idx[cur.irt]) and cur.irt not in seen:
            seen.add(cur.irt)
            cur = idx[cur.irt]
            n += 1
        return n
    parents = {idx[d.irt].docid for d in docs.values() if d.irt in idx}
    leaves = [d for d in docs.values() if d.docid not in parents]
    dist = Counter(depth(d) for d in leaves)
    print(f"docs: {len(docs)}  with In-Reply-To: {sum(1 for d in docs.values() if d.irt)}  "
          f"broken links (subject mismatch or dangling): {broken}  dangling: {dangling}")
    print("coherent chain length (leaves):", dict(sorted(dist.items())))
    for d in sorted(leaves, key=depth, reverse=True)[:10]:
        print(f"  {depth(d):3}  {d.docid}  {d.subject}")


# ---------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("context"); c.add_argument("docid"); c.add_argument("--window", type=int, default=21)
    v = sub.add_parser("validate"); v.add_argument("spec")
    r = sub.add_parser("render"); r.add_argument("spec"); r.add_argument("--dry-run", action="store_true")
    rb = sub.add_parser("rollback"); rb.add_argument("thread_id")
    sub.add_parser("scan")
    lg = sub.add_parser("logos", help="retrofit signature logos into generated docs (DocID > 250)")
    lg.add_argument("--apply", action="store_true")
    pp = sub.add_parser("people"); pp.add_argument("address", nargs="?")
    a = ap.parse_args()

    docs = load_corpus()
    manifest, fields = load_manifest()
    if a.cmd == "scan":
        return scan(docs)
    if a.cmd == "logos":
        return retrofit_logos(docs, a.apply)
    if a.cmd == "rollback":
        return rollback(a.thread_id, fields)
    people = build_people(docs)
    if a.cmd == "people":
        sel = [people[a.address.lower()]] if a.address else sorted(people.values(), key=lambda p: -p["sent_count"])
        return print(json.dumps(sel, indent=1))
    if a.cmd == "context":
        return context(a.docid.upper(), docs, people, manifest, a.window)
    spec = json.load(open(a.spec))
    if a.cmd == "validate":
        _, issues = validate(spec, docs, people, manifest)
        report_issues(issues)
        sys.exit(1 if any(i[0] == "ERROR" for i in issues) else 0)
    if a.cmd == "render":
        render(spec, docs, people, manifest, fields, a.dry_run)


if __name__ == "__main__":
    main()
