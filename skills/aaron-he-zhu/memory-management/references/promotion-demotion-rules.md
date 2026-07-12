# Promotion and Demotion Rules

HOT promotion is an explicit user-authorized indexing decision, not an automatic consequence of score, veto, recency, frequency, or a hook.

## Promote to HOT

Promote only a current conclusion needed across sessions, such as an approved priority, active safety block, or high-value pointer. The entry:

- is three lines or fewer;
- records `last_updated` and the permission/decision reference;
- links to an accepted registry record or dated WARM artifact;
- contains no raw personal data, credential, or large dataset.

Auditors and registry owners do not receive an automatic HOT exception.

## Demote

- Review HOT entries older than 30 days; move the detail back to its WARM source and remove stale pointers after permission.
- Review WARM artifacts older than 90 days for COLD archival, subject to retention/legal hold.
- Preserve original path, content hash, and source links in archive metadata.
- Registry events/projections and live consent suppression never participate in HOT/WARM/COLD demotion.

## Supersede

For comparable non-canonical notes, mark the older note `superseded_by: <artifact/date>` and keep both until normal retention. If unit, window, denominator, source meaning, or authority differs, preserve both and open a conflict.

Registry facts change only through the owner event protocol with current revision. Working-memory consolidation may submit a proposal but may not edit the stream, projection, or generated human view.
