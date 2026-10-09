"""Read-only, hash-checked evidence bundle. Never expose the provenance manifest to models.

``load_bundle(repository_root)`` returns a dict with ``documents`` (ID -> public
document), ``manifest`` (trusted provenance), ``coverage``, and ``bundle_sha256``.
Document ``locators`` are exact, half-open character spans of ``text``. Source
dates describe email sending only; attachment parent dates are availability
evidence, never assumed creation or execution dates.
"""
import hashlib
import json
from pathlib import Path

VERSION = "cascade-evidence/1.0.0"
BUNDLE_PATH = Path("benchmark/litigation_skills/evidence")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _checked_file(root, relative, digest):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence path escapes repository")
    raw = path.read_bytes()
    if sha256(raw) != digest:
        raise ValueError("Evidence hash mismatch: " + relative)
    return raw


def load_bundle(root, *, verify_sources=True):
    """Load the frozen extraction without requiring PDF/OCR dependencies.

    ``verify_sources=False`` is only for packaged execution where originals were
    checked before sealing. Extracted texts and coverage are always hash checked.
    The caller pins ``bundle_sha256`` in its task manifest.
    """
    root = Path(root).resolve()
    path = root / BUNDLE_PATH
    raw = (path / "manifest.json").read_bytes()
    manifest = json.loads(raw)
    if manifest["version"] != VERSION:
        raise ValueError("Unsupported evidence version")
    data = _checked_file(root, str(BUNDLE_PATH / "documents.jsonl"), manifest["documents_sha256"])
    coverage = json.loads(_checked_file(root, str(BUNDLE_PATH / "coverage.json"), manifest["coverage_sha256"]))
    if verify_sources:
        for item in manifest["source_files"]:
            _checked_file(root, item["path"], item["sha256"])
    documents = {}
    for line in data.splitlines():
        doc = json.loads(line)
        key = doc["document_id"]
        if key in documents or sha256(doc["text"].encode()) != doc["text_sha256"]:
            raise ValueError("Duplicate document or extracted text hash mismatch")
        for loc in doc["locators"]:
            if not 0 <= loc["start"] <= loc["end"] <= len(doc["text"]):
                raise ValueError("Invalid locator span")
        documents[key] = doc
    if len(documents) != manifest["document_count"]:
        raise ValueError("Document count mismatch")
    return {"documents": documents, "manifest": manifest, "coverage": coverage,
            "bundle_sha256": sha256(raw)}
