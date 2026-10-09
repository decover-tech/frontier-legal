"""Extraction, provenance, leakage and tamper tests; no paid model requests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.litigation_tasks.build_evidence import DOCX, extract, segments_to_text
from tools.litigation_tasks.evidence import BUNDLE_PATH, load_bundle, sha256

ROOT = Path(__file__).resolve().parents[3]


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle(ROOT)
        cls.documents = cls.bundle["documents"]

    def test_corpus_inventory_and_no_index_leakage(self):
        self.assertEqual(self.bundle["coverage"]["counts_by_kind"]["email"], 1486)
        self.assertEqual(len(self.documents), 2764)
        self.assertEqual(self.bundle["coverage"]["counts_by_kind"]["protocol"], 4)
        for source in self.bundle["manifest"]["source_files"]:
            self.assertTrue(source["path"].startswith(("definitions/", "data/contracts/", "data/emails/Custodians/", "data/emails/Exhibits/")))
            self.assertFalse(source["path"].endswith(".csv"))

    def test_public_documents_do_not_expose_paths_or_label_headers(self):
        for doc in self.documents.values():
            self.assertNotIn("source_path", doc)
            self.assertNotIn("original_filename", doc)
            self.assertNotIn("X-Decover-", doc["text"])
            self.assertNotIn("benchmark/hidden_gold", json.dumps(doc))

    def test_email_time_and_attachment_parentage(self):
        from datetime import datetime
        for key, doc in self.documents.items():
            if doc["kind"] == "email":
                self.assertIsNotNone(datetime.fromisoformat(doc["source_date"]).utcoffset())
                for child in doc["attachment_ids"]:
                    self.assertEqual(self.documents[child]["parent_email_id"], key)
            else:
                self.assertIsNone(doc["source_date"])
                if doc["kind"] in ("attachment", "inline_image"):
                    self.assertIn(key, self.documents[doc["parent_email_id"]]["attachment_ids"])

    def test_locator_spans_have_real_content(self):
        for doc in self.documents.values():
            previous = -1
            for loc in doc["locators"]:
                self.assertGreaterEqual(loc["start"], previous)
                self.assertTrue(doc["text"][loc["start"]:loc["end"]].strip())
                previous = loc["end"]

    def test_protocol_examples_are_private_but_original_is_preserved(self):
        full = self.bundle["manifest"]["full_protocol_extractions_evaluator_only"]
        self.assertEqual(len(full), 3)
        for key, original in full.items():
            public = self.documents[key]
            self.assertNotRegex(public["text"], r"EMAIL-\d+")
            self.assertNotIn("WORKED EXAMPLE", public["text"])
            self.assertIn("EMAIL-", original["text"])
            self.assertEqual(public["projection"]["original_text_sha256"], original["text_sha256"])
            self.assertTrue(self.bundle["manifest"]["provenance"][key]["projection_omissions"])
            original_paras = {l["locator"]: original["text"][l["start"]:l["end"]] for l in original["locators"]}
            for loc in public["locators"]:
                self.assertEqual(public["text"][loc["start"]:loc["end"]], original_paras[loc["locator"]])

    def test_scan_text_is_ocr_flagged_and_not_human_verified(self):
        scans = [d for d in self.documents.values() if d["extraction"]["ocr_attempted_pages"]]
        self.assertGreaterEqual(len(scans), 4)
        for doc in scans:
            self.assertEqual(doc["extraction"]["status"], "ocr_unverified")
            self.assertFalse(doc["extraction"]["ocr_human_verified"])
            self.assertTrue(doc["text"].strip())

    def test_unsupported_and_missing_ocr_are_not_empty_success(self):
        self.assertEqual(extract(b"unread bytes", "application/x-unhandled")["extraction"]["status"], "incomplete")
        from PIL import Image
        from io import BytesIO
        buffer = BytesIO(); Image.new("RGB", (10, 10), "white").save(buffer, format="PNG")
        with patch("tools.litigation_tasks.build_evidence.shutil.which", return_value=None):
            record = extract(buffer.getvalue(), "image/png")
        self.assertEqual(record["extraction"]["status"], "incomplete")
        self.assertTrue(record["extraction"]["failures"])

    def test_pdf_failed_parser_is_recorded(self):
        record = extract(b"%PDF fake", "application/pdf")
        self.assertEqual(record["extraction"]["status"], "incomplete")
        self.assertTrue(record["extraction"]["failures"])

    def test_text_extraction_is_deterministic_with_empty_lines(self):
        raw = b"first\r\n\r\nthird\n"
        self.assertEqual(extract(raw, "text/plain"), extract(raw, "text/plain"))
        record = extract(raw, "text/plain")
        self.assertEqual([x["line"] for x in record["locators"]], [1, 3])
        self.assertEqual(record["text"], "first\n\nthird")

    def test_docx_paragraph_projection_preserves_source_locator(self):
        record = extract((ROOT / "definitions/Subpoena_Enhanced.docx").read_bytes(), DOCX)
        loc = next(x for x in record["locators"] if x["locator"] == "document:paragraph:30")
        self.assertIn("7.", record["text"][loc["start"]:loc["end"]])
        self.assertIn("privilege log", record["text"][loc["start"]:loc["end"]])

    def test_tampered_extraction_is_rejected_even_without_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); bundle = root / BUNDLE_PATH; bundle.mkdir(parents=True)
            for name in ("manifest.json", "documents.jsonl", "coverage.json"):
                (bundle / name).write_bytes((ROOT / BUNDLE_PATH / name).read_bytes())
            with (bundle / "documents.jsonl").open("ab") as target:
                target.write(b" ")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                load_bundle(root, verify_sources=False)


if __name__ == "__main__":
    unittest.main()
