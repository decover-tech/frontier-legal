# Cascade evidence bundle

This is a frozen extraction of the permitted Cascade Timber sources, not a gold-answer collection. The model-facing runtime may expose `documents.jsonl` records through bounded search/read tools. **Keep `manifest.json` private:** it contains filesystem provenance and full original protocol paragraphs, including worked answers intentionally omitted from public protocol projections.

The bundle includes 1,486 emails, 331 MIME attachments, 884 inline images, 21 standalone contracts, 38 standalone exhibits and four protocols (2,764 records). Duplicate payloads retain separate family/provenance records. IDs preserve `EMAIL-###`; attachment IDs include the parent and MIME walk index; other asset IDs are opaque hashes. Filenames and source paths are not document metadata. Names naturally written inside a source are retained as evidence.

## Loading and pinning

```python
from tools.litigation_tasks.evidence import load_bundle
bundle = load_bundle(repository_root)
documents = bundle["documents"]
# Pin bundle["bundle_sha256"] in a task, and never expose bundle["manifest"].
```

The loader checks all original asset hashes, the exact extraction file, coverage file and per-document text hashes. `verify_sources=False` skips original-file checks only for a sealed runtime whose package was validated previously; extraction hashes remain mandatory. The loader does not enforce task cutoffs. The runtime must enforce them before search/read. For an attachment, derive availability from its parent email; do not interpret a null attachment `source_date` as unrestricted availability or as a creation date. Standalone asset dates require explicit task authorization; no date is invented from filenames or filesystem timestamps.

`locators` contain exact half-open character spans into document `text`, plus original paragraph, PDF page, text line, spreadsheet sheet/row or slide identifiers. Email headers shown are Date/From/To/Cc/Subject only. Hidden `X-Decover-*` headers fail the build. Filesystem CSV indexes, authoring notes, hidden labels, evaluator gold and repository documentation are outside the source allowlist.

## Text and OCR coverage

Unique PDF payloads cover 115 pages: 81 had native text, and 34 required OCR. All 34 OCR pages produced candidate text; none is certified accurate. OCR uses Poppler at 200 dpi and Tesseract English PSM 6. Exact versions, source SHA256, output SHA256 and extraction-script SHA256 are pinned in the manifest. No extraction exceptions occurred in this build. Eighty-one inline-image records had no detected text and remain discoverable with `no_text_detected` status.

`complete_text` means the selected text representation was extracted without a parser failure. It does **not** certify visual completeness. PDF signatures, stamps, annotations, layout and native-page images are not validated by text extraction. DOCX table paragraphs/comments/footnotes/revision deletions are extracted, but media and pagination are not interpreted. Spreadsheet formulas are preserved without recalculation; charts/images are not interpreted. Slides and notes supply text, but their figures and spatial relationships are not interpreted. Empty extraction never establishes absence of evidence.

Four standalone executed scans (KW-01, KW-02, Blue River and Cascade Pension Partners) were rendered and visually inspected across all 16 pages by the extraction-building agent. This was a source-layout check, not an independent audit of each OCR character. OCR remains explicitly unverified, including mixed native/scanned application attachments.

## Protocol projections

The summons instrument is fully retained as `DOC-568de2fba6d1c11aff9a`. It has seven requests, while the original PDF attached to EMAIL-023 has four and the responsiveness protocol organizes five categories. These are distinct source versions; the extraction does not reconcile or silently replace one with another.

The following public protocol records contain manually selected rule paragraphs only. Their locators remain original DOCX paragraph numbers. Removed case-specific examples, answer labels, example headings and branding are recorded by locator/reason/hash in the trusted manifest. The complete faithful text is separately preserved there. Intentional omissions are not extraction failures.

| Protocol | Public document ID |
|---|---|
| Attorney-client privilege | `DOC-0b1783352879f6609582` |
| Work product | `DOC-6b28a758f72225ef6f71` |
| Responsiveness | `DOC-df2dc8ac4b6020584cb5` |

The original protocol language is supplied benchmark policy, not independently researched legal authority. Task policies must state how conflicts, cutoff availability and missing rule prerequisites are handled.

## Rebuilding and validation

```sh
python3 -m tools.litigation_tasks.build_evidence
python3 -m unittest tools.litigation_tasks.tests.test_evidence -v
```

Rebuilding needs `pypdf`, `openpyxl`, Pillow, `pdftoppm` and `tesseract`; reading the sealed extraction needs only Python's standard library. Output ordering is deterministic, without timestamps or absolute local paths. Different extraction-library/OCR versions may produce different outputs: regenerate a new pin and review the changes rather than silently accepting them. Tests cover source counts, temporal provenance, locator spans, protocol leakage, malformed PDFs, absent OCR, unsupported types and hash tampering.
