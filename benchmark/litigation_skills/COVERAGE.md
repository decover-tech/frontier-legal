# Skill-family coverage

Checkpoint: 17 / 17 new episodes implemented; 17 independently approved. Two existing pilot aliases bring implemented family coverage to 19 / 19.

Control scores below validate the harness, not frontier-model performance. All new episodes are development-only and bounded initial skill episodes.

| Family | Skill | Package | Independent review | Positive control | Adversarial controls |
|---|---|---|---|---|---|
| CTH-LIT-01 | cold-start-interview | [Implemented](tasks/CTH-LIT-01/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-02 | customize | [Implemented](tasks/CTH-LIT-02/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-03 | matter-intake | [Implemented](tasks/CTH-LIT-03/task.json) | approved | 100% | 9/9 reduced score |
| CTH-LIT-04 | matter-workspace | [Implemented](tasks/CTH-LIT-04/task.json) | approved | 100% | 9/9 reduced score |
| CTH-LIT-05 | demand-received | [Implemented](tasks/CTH-LIT-05/task.json) | approved | 100% | 15/15 reduced score |
| CTH-LIT-06 | demand-intake | [Implemented](tasks/CTH-LIT-06/task.json) | approved | 100% | 7/7 reduced score |
| CTH-LIT-07 | demand-draft | [Implemented](tasks/CTH-LIT-07/task.json) | approved | 100% | 7/7 reduced score |
| CTH-LIT-08 | subpoena-triage | [Implemented](tasks/CTH-LIT-08/task.json) | approved | 100% | 16/16 reduced score |
| CTH-LIT-09 | legal-hold | Existing `CTH-PRESERVATION-001` | Legacy review pending | Existing tests | Existing controls |
| CTH-LIT-10 | chronology | Existing `CTH-CHRONOLOGY-001` | Legacy review pending | Existing tests | Existing controls |
| CTH-LIT-11 | claim-chart | [Implemented](tasks/CTH-LIT-11/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-12 | deposition-prep | [Implemented](tasks/CTH-LIT-12/task.json) | approved | 100% | 7/7 reduced score |
| CTH-LIT-13 | privilege-log-review | [Implemented](tasks/CTH-LIT-13/task.json) | approved | 100% | 10/10 reduced score |
| CTH-LIT-14 | brief-section-drafter | [Implemented](tasks/CTH-LIT-14/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-15 | matter-update | [Implemented](tasks/CTH-LIT-15/task.json) | approved | 100% | 10/10 reduced score |
| CTH-LIT-16 | matter-briefing | [Implemented](tasks/CTH-LIT-16/task.json) | approved | 100% | 9/9 reduced score |
| CTH-LIT-17 | portfolio-status | [Implemented](tasks/CTH-LIT-17/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-18 | oc-status | [Implemented](tasks/CTH-LIT-18/task.json) | approved | 100% | 8/8 reduced score |
| CTH-LIT-19 | matter-close | [Implemented](tasks/CTH-LIT-19/task.json) | approved | 100% | 9/9 reduced score |

The new-task reviews are independent agent source/oracle reviews, not licensed legal opinions. The two legacy pilots retain their original graders and need separate oracle review. Extraction has explicit OCR and missing-media limits; see `evidence/coverage.json`. No new model scores or held-out matter generalization are claimed.
