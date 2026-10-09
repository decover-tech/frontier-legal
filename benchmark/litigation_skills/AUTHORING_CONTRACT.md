# Executable task-package contract v1

Authoring documentation only; never model input. Shared runtime is owned by the master agent. Source evidence is packaged independently. Do not edit other authors' task directories.

Each author owns `benchmark/litigation_skills/tasks/CTH-LIT-XX/{task.json,policy.md,output_schema.json,fixtures.json}`; `benchmark/hidden_gold/litigation_skills/CTH-LIT-XX.json`; `tools/litigation_tasks/tests/test_task_XX.py`. Keep research/dossiers in `benchmark/hidden_gold/litigation_skills/research/CTH-LIT-XX.json`, not public policy. The runtime exposes only explicitly selected public fields and assets, never research/oracles/filesystem.

## Public task

`task.json` fields:

- `task_id`, `skill`, `title`, `version` (`1.0.0`), `split` (`development`), `cutoff` (ISO8601 with timezone), `instruction`, `availability` (`ready`, `partial`, or `missing-trigger`). Availability describes source/workflow readiness, not code completeness.
- `dependencies`: array of CTH-LIT IDs; standalone fixture always supplied even when chained mode is possible.
- `findings`: array of `{id, question, answer_schema, counterevidence_required}`. Prefer 4–7 substantial findings spanning discovery, time/scope reconstruction, conflict and rule application. Use task-specific named answer fields and public alternatives/types; do not expose correct values or answer document IDs. Include meaningful uncertainty labels.
- `artifact_schemas`: mapping of allowed relative output path (e.g. `intake/matter.json`) to a bounded JSON schema. Distinct deliverables for each skill. Artifacts are simulated local JSON work products and may also be rendered as readable Markdown/CSV; never perform real-world sending/config/calendar operations. Structure consequential factual/assertive fields so they can be verified; do not grade arbitrary long prose by keyword matching.
- `limits`: `{max_steps:120, max_observation_chars:220000, search_page_size:8, read_page_chars:6000}` (adjust only with rationale).
- `state_invariants`: optional public statements describing immutable history/unknown approvals, permitted paths etc.
- Runtime/build will add pinned `bundle_manifest_sha256`, `policy_sha256`, `schema_sha256`, `fixtures_sha256`, `oracle_sha256` after all assets are ready. Do not hardcode temporary hashes.

`policy.md` is supplied benchmark policy, source-grounded where applying corpus protocols. Clearly separate the evaluation's formatting/state rules from supplied legal protocols. Exclude worked examples that reveal case-specific determinations. Do not import law from memory/internet. Never claim prior legal review of author-produced rules.

`fixtures.json`: `{"artifacts": {"allowed/path.json": <source-grounded initial JSON>}, "provenance": [{"artifact_path":..., "description":..., "sources":[citations]}]}`. Empty artifacts allowed. Fixture status is explicitly a task-provided draft, not a new historical source. Missing approvals/preferences/authority remain null/unknown. For state tasks, initial history/protected fields must be preserved. All fixture paths must appear in artifact_schemas.

## Agent tools and answer

Shared runtime provides search(query,offset), read(document_id,locator/offset), list_artifacts, read_artifact(path), write_artifact(path,content), submit(answer). Paths restricted to this task's declared artifacts; writes change isolated in-memory/workspace artifacts only. Required artifact contents are evaluated at submission. No filesystem/shell/network access for task agents.

Terminal action: `{"tool":"submit","answer":{"findings":{"F01":{"answer":<task-specific JSON object>,"support":[citation],"counter":[citation]}}}}`.

Citation shape: `{"document_id":"EMAIL-... or packaged asset ID","locator":"...","quote":"verbatim source passage"}`. Read before citing. Exact passage provenance is checked, with whitespace normalization. Locator must be an actual evidence segment. Minimum 20 non-whitespace characters; quote complete relevant clauses. Up to 8 support and 6 counter citations. Body paragraphs/pages/tables are separately locatable; email header alone cannot prove the body proposition. Runtime will accept multiple independently reviewed equivalent proof spans. Original reference skills may be read as specifications, not used as source evidence.

Use `tools.litigation_tasks.schema.output_schema(task)` to generate output_schema.json (master will implement). This builds the common finding/citation structure around your distinct answer schemas. Schemas support object/properties/required/additionalProperties, arrays/items/uniqueItems/minItems/maxItems, string/enum, integer/minimum, boolean/null, and anyOf. Do not encode expected answers by making public enums singleton where alternatives are meaningful.

## Evaluator-only oracle

`CTH-LIT-XX.json` fields:

- `task_id`, `author_review_status` (`author_checked`), `independent_review_status` initially `pending`, `findings` mapping each finding ID to:
  - `accepted_answers`: list of equivalent complete answer objects. Keep genuine equivalent encodings/interpretations; don't accept unsupported conclusions. Individual answer fields earn partial accuracy, using the best coherent accepted alternative.
  - `support_groups` and `counter_groups`: list of proof obligations; each is `{id, description, alternatives:[{document_id,locator,quote}]}`. A group is satisfied by any valid cited passage covering an accepted support span. These spans must be independently reviewed for entailment, and alternate source passages/quoted-thread equivalents should be included where valid. No preference for one arbitrary phrase if another passage supports the same proposition. Root can resolve evidence aliases to packaged IDs/locators; use `{source_path, attachment_name, quote}` temporarily for non-email assets and flag them for resolution. Exact quotes should be minimal complete supporting clauses, not arbitrary labels.
  - `notes` describing why each proof is sufficient and how conflicting evidence changes the answer. Cases with missing trigger/authority must qualify claims as not established by available record, accounting for extraction gaps.
- `artifact_checks`: list of `{path,pointer,kind,...}`. Supported kinds: `equals` with `value`, `equals_finding` with `finding` and `answer_pointer`, `preserve` comparing initial fixture value at the same pointer, `append_only` requiring initial array prefix plus `min_new` count. Use JSON pointers; root pointer is empty string. Every consequential artifact field must be schema-constrained and checked (or derived from a graded finding). Do not use an ungraded prose blob as a “brief”. Add explicit draft/not-sent/unknown authority checks where relevant.
- `control_artifacts`: a complete set of correct final artifacts (evaluator only), one for each declared path. Must satisfy checks and cited findings. Root's control runner will read relevant source spans, write these artifacts, and submit the first accepted answer with oracle proofs.
- `negative_controls`: list of meaningful mutations `{name,kind,...}`. Kinds: `answer_field` (`finding`,`pointer`,`value`), `drop_counter` (`finding`), `fabricate_quote` (`finding`), `artifact_field` (`path`,`pointer`,`value`), `unread_citations`, `post_cutoff_citation` (explicit later proof if applicable). Each mutation must reduce reward or trigger failure. Required: fabricated quote, incorrect conclusion/unknown overclaim, and at least one task-specific conflict/state adversary.

Reward contract: evidence-backed answer accuracy and proof coverage form 80%; artifact correctness forms 20% when artifacts are present (otherwise findings100%). A finding earns no credit without its required supporting proof. Counterevidence obligations reduce scores when omitted. Valid but irrelevant citations reduce evidence precision. Exact accepted answer fields are not sufficient without provenance. Rule application is encoded in substantive answer fields, not an arbitrary rule-ID match. No intermediate gold feedback; terminal diagnostic components only.

## Tests and independent review

Task test should load `LitigationEnvironment('CTH-LIT-XX', root=ROOT)` and invoke generic `exercise_controls(task_id, root=ROOT)`; the latter returns positive and named negative results. Root will provide API. Add a unique adversarial case when generic oracle controls don't cover it. Author control success is not independent review. A different agent reviews actual sources/proofs/counterevidence and records accepted alternatives, issues/fixes, reviewer identity and limitations in `benchmark/litigation_skills/reviews/CTH-LIT-XX.json`; root validates the review links. Do not assert all skill modes are complete: these are bounded initial episodes.
