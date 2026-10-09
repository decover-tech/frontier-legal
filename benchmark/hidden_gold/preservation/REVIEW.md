# Evaluator authoring review — CTH-PRESERVATION-001

**Contains answers. Do not expose this directory to the agent.** This is public repository development material, not secret held-out data. Independent reviewer sign-off remains pending.

Source files are unchanged. The seven rules are authored benchmark policy, not additional facts or external legal authority. The expected assessment applies that explicit policy to the passages below.

## C01

Were technical mailbox deletion safeguards documented before the formal hold? Identify the earliest documented activation and retain its scope.

Cutoff: `2023-06-13T23:59:59-07:00`.

Expected fields:

```json
{
  "status": "documented_complete",
  "scope": "draft_list_only",
  "effective_date": "2023-05-26",
  "known_by": "2023-05-26",
  "responsible": "dosei@cascadetimber.com",
  "next_action": "monitor_stated_scope"
}
```

Required rules: R1, R3, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-206](<../../../data/emails/Custodians/Wendy_Park/EMAIL-206_Mailbox preservation _ prep.eml>), [EMAIL-207](<../../../data/emails/Custodians/Wendy_Park/EMAIL-207_RE_ Mailbox preservation _ prep.eml>): “I've suspended automated mailbox deletion for the exec team and the people on John's draft custodian list.”

Challenges and the required reason:

- `notice_not_first_control`: EMAIL-024. Accepted clause: “This is a legal hold notice. Preserve all documents, communications, and records related to the Coastal Solar Credit Program, Alder Point Partners, and Bellhaven Advisory.”

## C02

Was completion of Nina Alvarez's mailbox export documented by this checkpoint? Reconcile pending work, instructions, generic export updates, departure and later confirmation.

Cutoff: `2023-07-07T23:59:59-07:00`.

Expected fields:

```json
{
  "status": "confirmation_gap",
  "scope": "named_mailbox",
  "effective_date": null,
  "known_by": null,
  "responsible": "wpark@cascadetimber.com",
  "next_action": "obtain_named_export_confirmation"
}
```

Required rules: R1, R2, R5, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-059](<../../../data/emails/Custodians/Dan_Osei/EMAIL-059_RE_ Document collection _ technical scope.eml>), [EMAIL-1063](<../../../data/emails/Custodians/Wendy_Park/EMAIL-1063_Collection_scope_note.eml>): “Nina Alvarez's mailbox is flagged pending” OR “Nina Alvarez's mailbox is next in line because of her end-of-June departure”
- [EMAIL-062](<../../../data/emails/Custodians/John_Ellery/EMAIL-062_RE_ Legal hold _ departing employee mailbox.eml>): “please coordinate with Alder Point to preserve and export her mailbox before deprovisioning.”
- [EMAIL-061](<../../../data/emails/Custodians/John_Ellery/EMAIL-061_RE_ Legal hold _ departing employee mailbox.eml>), [EMAIL-062](<../../../data/emails/Custodians/John_Ellery/EMAIL-062_RE_ Legal hold _ departing employee mailbox.eml>), [EMAIL-082](<../../../data/emails/Custodians/Jay_Whitfield/EMAIL-082_Automatic Reply_ Out of Office _ Last Day June 30.eml>): “my last day at Alder Point Partners is June 30.” OR “Nina Alvarez (Alder Point) is departing June 30.”

Challenges and the required reason:

- `after_cutoff`: EMAIL-1096. Accepted clause: “her mailbox was exported before her last day”
- `generic_not_specific`: EMAIL-1055, EMAIL-1060, EMAIL-1061, EMAIL-1062, EMAIL-1064, EMAIL-1067, EMAIL-1068, EMAIL-1070, EMAIL-1085, EMAIL-1090, EMAIL-1097, EMAIL-1102, EMAIL-1104, EMAIL-1118, EMAIL-1119, EMAIL-1122, EMAIL-1124, EMAIL-1130, EMAIL-1136. Accepted clause: “Collection update: mailbox exports underway per the custodian list, with hold status confirmed per mailbox. Export manifest to follow.”
- `instruction_not_completion`: EMAIL-062. Accepted clause: “please coordinate with Alder Point to preserve and export her mailbox before deprovisioning.”

## C03

Reassess Nina's export and permitted access at this later checkpoint. Identify the supported event-time bound and earliest qualifying confirmation; reconcile the earlier pending status.

Cutoff: `2023-07-26T23:59:59-07:00`.

Expected fields:

```json
{
  "status": "documented_complete",
  "scope": "named_mailbox",
  "effective_date": "before:2023-06-30",
  "known_by": "2023-07-11",
  "responsible": "jellery@cascadetimber.com",
  "next_action": "retain_export_route_access_to_legal"
}
```

Required rules: R1, R2, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-1096](<../../../data/emails/Custodians/Craig_Sato/EMAIL-1096_Mailbox_export_Nina_Alvarez.eml>): “her mailbox was exported before her last day”
- [EMAIL-1155](<../../../data/emails/Custodians/Alan_Brooks/EMAIL-1155_Nina_mailbox_admin_record_cross_company.eml>): “Any Alder request for access to her mailbox or folders, including from Tom or Priya, comes to me first.”
- [EMAIL-061](<../../../data/emails/Custodians/John_Ellery/EMAIL-061_RE_ Legal hold _ departing employee mailbox.eml>), [EMAIL-062](<../../../data/emails/Custodians/John_Ellery/EMAIL-062_RE_ Legal hold _ departing employee mailbox.eml>), [EMAIL-082](<../../../data/emails/Custodians/Jay_Whitfield/EMAIL-082_Automatic Reply_ Out of Office _ Last Day June 30.eml>): “my last day at Alder Point Partners is June 30.” OR “Nina Alvarez (Alder Point) is departing June 30.”

Challenges and the required reason:

- `superseded_status`: EMAIL-059, EMAIL-1063. Accepted clause: “Nina Alvarez's mailbox is flagged pending” OR “Nina Alvarez's mailbox is next in line because of her end-of-June departure”

## C04

What Alder hold-notice receipt is actually documented? Identify who acknowledged and distinguish that fact from group-wide implementation.

Cutoff: `2023-06-14T23:59:59-07:00`.

Expected fields:

```json
{
  "status": "documented_complete",
  "scope": "acknowledging_person_only",
  "effective_date": "2023-06-14",
  "known_by": "2023-06-14",
  "responsible": "pshah@alderpointpartners.com",
  "next_action": "verify_remaining_acknowledgments"
}
```

Required rules: R1, R3, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-025](<../../../data/emails/Custodians/Priya_Shah/EMAIL-025_Legal hold _ please confirm.eml>): “Confirming receipt of the legal hold notice.”

Challenges and the required reason:

- `receipt_not_implementation`: EMAIL-060. Accepted clause: “auto-delete has been disabled for all mailboxes under hold, and a litigation-hold flag has been applied in the email system.”

## C05

Do the records establish preservation on Bellhaven's own systems? Reconcile its inquiry, Cascade's technical controls and the later IT scope clarification.

Cutoff: `2023-11-10T23:59:59-08:00`.

Expected fields:

```json
{
  "status": "confirmation_gap",
  "scope": "external_native_systems",
  "effective_date": null,
  "known_by": null,
  "responsible": "jellery@cascadetimber.com",
  "next_action": "request_direct_external_confirmation"
}
```

Required rules: R1, R4, R5, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-070](<../../../data/emails/Custodians/Derek_Holt/EMAIL-070_RE_ Coastal Solar _ placements paused.eml>): “should we be doing anything on our end to preserve our own files, or just wait to hear from their counsel?”
- [EMAIL-1066](<../../../data/emails/Custodians/Sarah_Nguyen/EMAIL-1066_Third_party_hold_gap_note_Bellhaven_070_link.eml>): “Nothing on Bellhaven's own systems is covered by anything IT has done”

Challenges and the required reason:

- `different_system_scope`: EMAIL-060. Accepted clause: “auto-delete has been disabled for all mailboxes under hold, and a litigation-hold flag has been applied in the email system.”

## C06

Assess the claim: Nina's June 30 account disablement proves her mailbox was deleted that day. Distinguish operational account state from data loss.

Cutoff: `2023-07-26T23:59:59-07:00`.

Expected fields:

```json
{
  "status": "contradicted",
  "scope": "named_mailbox",
  "effective_date": "2023-06-30",
  "known_by": "2023-07-11",
  "responsible": "jellery@cascadetimber.com",
  "next_action": "maintain_hold_no_deletion_inference"
}
```

Required rules: R1, R5, R6, R7.

Support groups (one qualifying read quotation per group; all independent groups required):

- [EMAIL-1096](<../../../data/emails/Custodians/Craig_Sato/EMAIL-1096_Mailbox_export_Nina_Alvarez.eml>): “the account was disabled on June 30 but not deleted.”

Challenges and the required reason:

- `disabled_not_deleted`: EMAIL-1096. Accepted clause: “the account was disabled on June 30 but not deleted.”

## Reviewer checks

- Verify earliest qualifying evidence and event-date precision; distinguish hindsight from contemporaneous knowledge.
- Check that each status follows the supplied policy rather than a legal conclusion.
- Check for equivalent passages in the pinned collection that the accepted groups should include.
- Confirm that subject-only or generic boilerplate cannot establish named export completion or native third-party controls.
- Re-run the tests and oracle search/read/submit control after any revision; version and re-pin changed policy/oracle assets.
