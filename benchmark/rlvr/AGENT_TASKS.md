# Cascade evidence-agent development tasks

These tasks use the workflow **find evidence → reconstruct events → resolve
conflicts → apply a supplied rule → submit a supported answer**. The numbering
below identifies this new agent-task sequence, separate from the existing
inventory pilot tasks and broader skill-family roadmap.

| Task | ID | Deliverable | Guide |
|---|---|---|---|
| 1 | `CTH-PRESERVATION-001` | Six preservation assessments at explicit checkpoints | [Preservation audit](preservation/README.md) |
| 2 | `CTH-CHRONOLOGY-001` | 14 supported milestones, their order and five disputed inferences | [Evidence chronology](chronology/README.md) |

Both tasks pin the same 1,486 Cascade Timber emails and provide bounded search,
read and submit tools with deterministic terminal rewards. They have separate
policies, schemas, oracles and runners. Offline controls and tests validate the
verifiers. Independent oracle review remains pending. A first
[five-model chronology pilot](chronology/FRONTIER_FIVE_2026-10-08_RUN2.md) is complete;
broader calibration and a live preservation evaluation remain pending.

[Clean-checkout validation](AGENT_TASKS_VALIDATION.json) records 89 passing tests,
all 149 model-episode transitions replayed offline, and the current code and
task hashes. No provider calls were made for that validation.
