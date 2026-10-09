# CTH-LIT-08 — IRS instrument triage and production reconciliation

Skill family: `subpoena-triage`. Development episode, within the Cascade Timber
matter only. Historical cutoff: September 6, 2023, 23:59:59 Pacific.

The episode requires the agent to reconcile an original attached instrument with
the supplied enhanced instrument, distinguish agency/counsel reports from planned
events, follow the extension and rolling-production chain, and produce a supported
internal triage artifact. The original attached PDF and enhanced DOCX differ in
both title and scope. The task's policy states which version governs this exercise
without pretending the corpus proves historical amendment or service of the DOCX.

The agent must reconstruct the timeline and examine actual attachments. It cannot
pass merely by extracting email subject dates, repeating the latest due date, or
asserting that a receipt means the examination is complete. Missing service proof,
procedural authorities, and production-completeness evidence remain explicit gaps.

`benchmark/hidden_gold/litigation_skills/research/CTH-LIT-08.json` is authoring material with source text, locators, SHA256 hashes,
attachment extraction coverage and candidate findings. It is deliberately excluded
from model inputs. `policy.md` is public. Runtime package and evaluator oracle are
separate artifacts; no authoring answers should be bundled into observations.

The reference skill's live research, global configuration, sending and calendar
operations are adapted into local draft artifacts under the benchmark policy.
No live legal workflow is executed.
