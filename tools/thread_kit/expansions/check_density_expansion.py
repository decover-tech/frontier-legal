#!/usr/bin/env python3
"""Synchronize expansion metadata and check the new evidence chains offline.

Run after rendering THR-005, THR-006, THR-007. Labels remain blank pending
review; a signature footer does not determine privilege. Existing load-file
rows are preserved. This checker does not adjudicate pre-existing defects.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import thread_kit as tk

EXPECTED = {f'EMAIL-{n}' for n in range(1475, 1507)}


def sync_loadfiles(docs):
    csv_path = Path(tk.CORPUS) / 'Loadfile_Cascade_Timber.csv'
    dat_path = Path(tk.CORPUS) / 'Loadfile_Cascade_Timber.dat'
    with csv_path.open(newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        existing = list(reader)
    csv_ids = {r['DOCID'] for r in existing}
    dat_text = dat_path.read_text()
    sep = 'þ\x14þ'
    dat_lines = dat_text.splitlines()
    assert dat_lines[0][1:-1].split(sep) == fields
    dat_ids = {line[1:-1].split(sep)[0] for line in dat_lines[1:] if line}
    assert csv_ids == dat_ids, 'Existing load files disagree; refusing to append'
    assert len(csv_ids) == len(existing), 'Duplicate load-file IDs'
    rows = []
    for did in sorted(EXPECTED - csv_ids, key=tk.num):
        d = docs[did]
        dt = d.date.astimezone(tk.TZ)
        rows.append(dict(DOCID=did, CUSTODIAN=d.custodian.replace('_', ' '),
                         DATESENT=dt.strftime('%m/%d/%Y'), TIMESENT=dt.strftime('%H:%M:%S %Z'),
                         FROM=tk.fmt_addr(d.from_name, d.from_addr),
                         TO='; '.join(tk.fmt_addr(*a) for a in d.to),
                         CC='; '.join(tk.fmt_addr(*a) for a in d.cc), SUBJECT=d.subject,
                         TAG='', PRIVILEGED='', CONTAINS_PII='',
                         ATTACHMENTS='; '.join(a[0] for a in d.attachments),
                         MESSAGEID=d.msgid, FILEPATH=str(Path(d.path).relative_to(tk.CORPUS))))
    if rows:
        assert csv_path.read_bytes().endswith(b'\n') and dat_path.read_bytes().endswith(b'\n')
        buffer = io.StringIO(newline='')
        writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator='\r\n')
        writer.writerows(rows)
        with csv_path.open('a', newline='') as f:
            f.write(buffer.getvalue())
        with dat_path.open('a', newline='') as f:
            for row in rows:
                f.write('þ' + sep.join(row[k] for k in fields) + 'þ\n')
    print('Load-file rows appended:', len(rows))


def check(docs, baseline=None):
    assert EXPECTED <= docs.keys(), 'New messages missing'
    manifest, _ = tk.load_manifest()
    people = tk.build_people(docs)
    # Validate specs against the original corpus so used IDs are not collisions.
    original_docs = {k: v for k, v in docs.items() if k not in EXPECTED}
    original_manifest = {k: v for k, v in manifest.items() if k not in EXPECTED}
    for number in (5, 6, 7):
        spec = json.loads((HERE / f'THR-{number:03d}.json').read_text())
        _, issues = tk.validate(spec, original_docs, people, original_manifest)
        assert not [i for i in issues if i[0] in ('ERROR', 'WARN')], issues
    idx = tk.by_msgid(docs)
    assert len(idx) == len(docs), 'Duplicate Message-ID'
    attachment_copies = {}
    for did in EXPECTED:
        d = docs[did]
        assert d.irt in idx and d.date > idx[d.irt].date
        assert tk.coherent(d, idx[d.irt]), 'New subject/thread mismatch'
        assert all(ref in idx for ref in d.refs)
        assert manifest[did]['parent_id'] == idx[d.irt].docid
        assert int(manifest[did]['expected_attachment_count']) == len(d.attachments)
        assert 'X-Decover-' not in Path(d.path).read_text()
        for name, _, data in d.attachments:
            if name in attachment_copies:
                assert attachment_copies[name] == data, 'Changed forwarded attachment'
            attachment_copies[name] = data
    with (Path(tk.CORPUS) / 'Loadfile_Cascade_Timber.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == len(docs) == len(manifest) == 1486
    assert {r['DOCID'] for r in rows} == set(docs) == set(manifest)
    for r in rows:
        if r['DOCID'] in EXPECTED:
            d = docs[r['DOCID']]
            assert Path(tk.CORPUS, r['FILEPATH']).resolve() == Path(d.path).resolve()
            assert r['MESSAGEID'] == d.msgid and r['SUBJECT'] == d.subject
            assert not any(r[k] for k in ('TAG', 'PRIVILEGED', 'CONTAINS_PII'))
    dat_path = Path(tk.CORPUS) / 'Loadfile_Cascade_Timber.dat'
    lines = dat_path.read_text().splitlines()
    # DC4 does not split lines; both formats must contain exactly the same values.
    dat_rows = [ln[1:-1].split('þ\x14þ') for ln in lines if ln]
    assert len(dat_rows) == len(rows) + 1
    assert [list(r.values()) for r in rows] == dat_rows[1:]
    register = next(a[2].decode() for a in docs['EMAIL-1492'].attachments
                    if a[0] == 'Three_purchase_delivery_register_export_2023-08-16.txt')
    entries = [[c.strip() for c in line.split('|')] for line in register.splitlines()
               if line.startswith(('Cascade Pension Partners |', 'North Fork Energy Fund |', 'Blue River Capital |'))]
    assert len(entries) == 8
    allocations = [int(row[-1]) for row in entries]
    assert sum(allocations[:3]) == 1250000
    assert sum(allocations[3:5]) == 900000
    assert sum(allocations[5:]) == 1100000
    assert allocations[4] + allocations[6] == 560000
    assert sum(allocations[i] for i in (0, 3, 4, 5, 6)) == 2400000
    assert [row[4] for row in entries] == ['NW-03', 'NW-02', 'NW-01', 'NW-06', 'NW-07', 'NW-04', 'NW-07', 'NW-05']
    source_faces = dict(zip(['NW-01', 'NW-02', 'NW-03', 'NW-04', 'NW-05', 'NW-06', 'NW-07', 'NW-08'],
                            [590000, 520000, 620000, 580000, 550000, 640000, 560000, 490000]))
    from datetime import date
    issued = dict(zip(source_faces, ['2022-10-04', '2022-10-04', '2022-10-18', '2022-10-18',
                                    '2022-11-01', '2022-11-01', '2022-11-15', '2022-11-15']))
    parcel_allocated = {p: 0 for p in source_faces}
    contracts = json.loads((Path(tk.ROOT) / 'tools/doc_kit/library/CSC-CPA-BELLHAVEN.json').read_text())
    final_vars = {v['version']: v['vars'] for v in contracts['versions']}
    buyers = dict(zip(['Cascade Pension Partners', 'North Fork Energy Fund', 'Blue River Capital'],
                     ['CPP-final', 'NFEF-final', 'BRC-final']))
    for row in entries:
        buyer, agreement, delivered, certificate, parcel, face = row
        number = int(parcel[-2:])
        assert certificate == f'CSC-{parcel}-2022-{number:04d}'
        assert date.fromisoformat(delivered[:10]) >= date.fromisoformat(issued[parcel])
        assert agreement <= delivered[:10]
        parcel_allocated[parcel] += int(face)
    assert all(parcel_allocated[p] <= source_faces[p] for p in source_faces)
    for buyer, version in buyers.items():
        expected_face = int(final_vars[version]['face'].replace('$', '').replace(',', ''))
        assert sum(int(e[-1]) for e in entries if e[0] == buyer) == expected_face
    settlement = next(a[2].decode() for a in docs['EMAIL-1494'].attachments
                      if a[0] == 'Three_purchase_settlement_bridge_2023-08-18.txt')
    lines = [ln for ln in settlement.splitlines() if ln.startswith(('CPP |', 'North Fork |', 'Blue River |'))]
    totals = [Decimal(0)] * 5
    for ln in lines:
        cols = [c.strip() for c in ln.split('|')]
        face, price, cash, broker, admin, retained = map(Decimal, cols[1:])
        assert face * price == cash
        assert cash * Decimal('.06') == broker and cash * Decimal('.08') == admin
        assert cash - broker - admin == retained
        for i, value in enumerate((face, cash, broker, admin, retained)):
            totals[i] += value
    assert totals == list(map(Decimal, (3250000, 2932000, 175920, 234560, 2521520)))
    # Buyer/auditor transmissions suppress unrelated internal quoted chains.
    assert 'North Fork' not in docs['EMAIL-1495'].body
    assert 'Blue River' not in docs['EMAIL-1495'].body
    assert not tk.QUOTE_RE.search(docs['EMAIL-1495'].body)
    assert not tk.QUOTE_RE.search(docs['EMAIL-1505'].body)
    old_count = None
    if baseline:
        old = json.loads(Path(baseline).read_text())
        for path, digest in old.items():
            assert hashlib.sha256(Path(tk.ROOT, path).read_bytes()).hexdigest() == digest, path
        old_count = len(old)
        assert old_count == 1454
    baseline_idx = tk.by_msgid(original_docs)
    original_broken = sum(1 for d in original_docs.values() if d.irt and
                          (d.irt not in baseline_idx or not tk.coherent(d, baseline_idx[d.irt])))
    summary = dict(total_messages=len(docs), added_messages=len(EXPECTED),
                   unique_new_attachments=len(attachment_copies),
                   attachment_instances=sum(len(docs[k].attachments) for k in EXPECTED),
                   original_messages_byte_verified=old_count,
                   spec_errors=0, spec_warnings=0, indexes_match=True,
                   new_thread_mismatches=0, preexisting_thread_mismatches=original_broken,
                   labels='New documents unreviewed; label columns blank; existing benchmark snapshots unchanged')
    (HERE / 'validation.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sync-loadfiles', action='store_true')
    parser.add_argument('--baseline', help='Optional pre-expansion relative-path SHA256 snapshot')
    args = parser.parse_args()
    documents = tk.load_corpus()
    if args.sync_loadfiles:
        sync_loadfiles(documents)
    check(documents, args.baseline)
