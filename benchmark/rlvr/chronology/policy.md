# Supplied chronology rules — Task 2, version 1.0.0

These are fictional benchmark rules for assembling an evidence chronology, not
legal conclusions or additional facts in the Cascade Timber matter.

T1 — Separate event time from report time. `event_start` and `event_end` bound the
event described by the requested milestone; `reported_on` is the date of the
originating report specified by that milestone. Prefer the contemporaneous report
to a later summary unless the milestone explicitly targets that summary. A later forwarded copy
is not another event. Use the date of the quoted original speaker, not the date of
the forward, when a dated quoted block clearly supplies the underlying statement.
Do not backdate a new confirmation to the event it later reports.

T2 — Preserve precision. Use sender-local ISO calendar dates. Set both bounds to
the same day for a supported day; use `interval` when only a range is supported.
For a past-tense event said to have occurred "this week," the week begins Monday
and the upper bound is the reporting day. Do not invent a particular day within
that range. A later restatement is a separate communication, not proof of a second
underlying event. Missing proof gets null dates in the resolution, never an
invented timeline event.

T3 — Attribute claims and distinguish states. `attributed_claim` records what a
speaker claimed, without treating it as independent proof. `instruction`,
`conditional_authorization`, `status_report`, `completed_action` and `assessment`
are distinct. A forecast, draft, plan, conditional permission or scheduling entry
does not prove execution. A completed narrow review does not resolve every issue.
The actor is the person making the recorded statement or performing the recorded
action, identified by email address; it is not necessarily the author of a later
forward containing that statement.

T4 — Resolve conflicts without erasing history. Retain both a claim and an
inconsistent or unverified follow-up. Repetition by the original speaker is not
independent corroboration. A lack of verification is not proof that the claim was
false. For conflicts about a specific checkpoint, use only original messages
available by that inclusive, timezone-aware cutoff. A later source may appear only
as a challenge rejected with `after_cutoff`.

T5 — Keep scope and completion separate. Distinguish Q4-H1/H2/H3 queue files from
the original Northwest parcels. Permission to submit is not a transmittal record;
submission is not certificate delivery. Correcting a document reference is not
reconciling acreage. A September remediation pilot does not establish performance
of historical quarterly controls. Calendar plans do not prove the work ran.

T6 — Evidence and ordering. Cite short verbatim decision-bearing passages that
were returned by `read`. Header dates, dated quoted headers and message context
may establish timing, but a subject line or document title alone cannot prove a
completed event. Include every independently needed support group. One original
fact repeated in multiple forwards is not multiple independent confirmations.
Order the requested milestones by event time. Where day-level ranges overlap,
only impose an order supported by the record (for example, dated same-day
instructions and the later status response). Otherwise either order is accepted.

Only original headers and decoded plain-text email bodies are evidence in this
task. Referenced attachments and authoring documents are unavailable. The rules
do not decide actual regulatory issuance, legal liability, eligibility, refunds,
or sanctions. A single outer Markdown JSON fence is accepted as transport syntax.
