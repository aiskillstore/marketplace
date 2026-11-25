---
name: affinity
description: "Search and maintain local contacts, identities, relationships, events, commitments, and recurring dates. Use when recording relationship evidence or reviewing a social CRM."
license: "MIT"
compatibility: "The release binary needs no runtime. MCP stdio or ghostpaw-affinity CLI."
---

# affinity

Affinity is a local relationship model and social CRM. Search before creating contacts. Inspect before revising or merging. Record direct evidence honestly, keep identities and structural ties distinct from social links, and ask for clarification when a target is ambiguous. Review commitments and recurring dates regularly. Derived scores guide attention and do not prove relationship quality.

## Running inside sandboxed agent harnesses

Inside a Codex CLI `--sandbox workspace-write` session, the database and its
parent directory must be inside a writable root, including SQLite's `-wal` and
`-shm` side files. A default DB under `~/.ghostpaw` outside those roots can fail
with `SQLITE_CANTOPEN` or `EPERM` (often exit 70; directory creation failures
may exit 2), even when normal shell permissions allow access. Put the DB inside the workspace with `--db ./state/affinity.db`,
or set `GHOSTPAW_AFFINITY_DB="$PWD/state/affinity.db"` for CLI/MCP use.

To use an external DB directory, add it when starting the OpenAI Codex CLI
(replace `<dir-with-db>` with its absolute path):

```sh
codex exec --sandbox workspace-write --add-dir <dir-with-db> "Run the GhostPaw CLI"
```

Alternatively, set `sandbox_workspace_write.writable_roots` in
`~/.codex/config.toml` before starting the session:

```toml
[sandbox_workspace_write]
writable_roots = ["/absolute/dir-with-db"]
```

## What goes where

| Store | Use for |
| --- | --- |
| souls | Agent identity and voice. |
| codex | Beliefs with uncertainty and provenance: things that might be wrong or change. |
| affinity | People, organizations, agents, and their relationships. |
| questlog | Tasks and deadlines. |
| grimoire | Procedures and how-tos. |
| Plain memory/files | Stable operational facts. |

For boundary cases, keep identity in souls, a revisable claim about someone in codex linked to their affinity record, actionable work in questlog, and reusable steps in grimoire; leave stable setup details in plain memory/files.


## Calling tools

MCP: connect to ghostpaw-affinity, then call a tool by name with its JSON arguments.

CLI: `ghostpaw-affinity call <tool> '<JSON object>'` or `ghostpaw-affinity <tool> --parameter value` (without a global install: `npx -y @ghostpaw/affinity <tool> ...`).

Inspect schemas with `ghostpaw-affinity describe <tool>`. Use `--db <path>` to select a database.

## search_affinity

Search contacts by name, identity, attributes, link roles, bonds and event text. All whitespace tokens must match. Dormant and lost contacts are excluded by default; use includeDormant and includeLost to include them.

Use when:

Not for:

Read-only.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| scope | string | no | contacts, events, all. Search scope; defaults to contacts. |
| query | string | yes | Free-text or natural-key query. |
| kind | string | no | human, agent, group, company, team, pet, service, other. Optional contact kind filter. |
| lifecycleState | string | no | active, dormant, merged, lost. Optional lifecycle state filter. |
| attribute | string / array | no |  |
| tag | string / array | no |  |
| includeLost | boolean | no | Include lost contacts (search excludes them by default). |
| includeOwner | boolean | no | Whether owner contacts are included. |
| includeDormant | boolean | no | Whether dormant contacts are included. |
| limit | integer | no | Optional result limit. |
| offset | integer | no | Optional result offset. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |

```sh
ghostpaw-affinity search "Jana"
```

## review_affinity

Review one affinity surface such as contacts, journals, link queues, commitments, dates, graph state, or merge history.

Use when:

Not for:

Read-only.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| ref | object | no |  |
| includeContent | boolean | no | Deprecated alias for --with-content; includes verbatim event content. |
| channel | string | no | Filter events by channel. |
| view | string | yes | contacts.list, contacts.duplicates, events.timeline, events.thread, events.contact_journal, events.link_timeline, events.moments, commitments.open, links.owner, links.observed, links.progression_readiness, links.radar, dates.upcoming, graph.chart, merges.history, merges.dismissed. Which review surface to return. |
| now | integer / string | no | Optional current timestamp for overdue calculations. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| contact | object | no | Optional target contact locator. |
| link | object | no | Optional target link locator. |
| contactIds | array | no | Optional contact-id subset. |
| kind | string | no | Optional contact kind or link kind filter, depending on the view. |
| lifecycleState | string | no | active, dormant, merged, lost. Optional contact lifecycle-state filter. |
| linkState | string | no | active, dormant, strained, broken, archived. Optional link state filter. |
| attribute | string / array | no |  |
| tag | string / array | no |  |
| includeLost | boolean | no | Include lost contacts (search excludes them by default). |
| includeOwner | boolean | no | Whether owner contacts are included. |
| includeDormant | boolean | no | Whether dormant rows are included. |
| includeArchived | boolean | no | Whether archived links are included. |
| includeStructural | boolean | no | Include structural ties as marked chart edges. |
| includeObserved | boolean | no | Whether observed links are included. |
| eventTypes | array | no | Optional event-type filter. |
| momentKind | string | no | breakthrough, rupture, reconciliation, milestone, turning_point. Optional moment kind filter. |
| commitmentType | string | no | promise, agreement. Optional commitment type filter. |
| recurrenceKind | string | no | birthday, anniversary, renewal, memorial, custom_yearly. Optional recurrence-kind filter. |
| horizonDays | integer | no | Optional horizon-days filter. |
| exactOnly | boolean | no | Whether duplicate review is exact-only. |
| minScore | number | no | Optional duplicate minimum score (default 0.5; use 0 for all candidates). |
| includeDismissed | boolean | no | Whether dismissed pairs are included in duplicate review (marked with dismissed flag). |
| since | integer / string | no | Optional lower timestamp bound. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| until | integer / string | no | Optional upper timestamp bound. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| limit | integer | no | Optional result limit, 1..10000 (default 50); use offset for paging. |
| offset | integer | no | Optional result offset. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| refSource | string | no | External reference source. |
| refId | string | no | External reference id. |
| withContent | boolean | no | Include verbatim event content. |
| ref.source | string | yes | External source; trimmed and lowercased. |
| ref.id | string | yes | Non-empty external id. |
| contact.contactId | integer | no | Exact contact id. |
| contact.identity | object | no | Contact identity locator. |
| link.linkId | integer | no | Exact link id. |
| link.endpoints | object | no | Endpoint-based link locator. |

```sh
ghostpaw-affinity review events.contact_journal --with-content --channel bluesky --contact '{"contactId":2}'
```

## inspect_affinity_item

Inspect one exact affinity item such as the owner profile, a contact profile, or one link detail.

Use when:

Not for:

Read-only.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| kind | string | yes | event, owner_profile, contact_profile, link. What to inspect. |
| eventId | integer | no | Exact event id. |
| ref | object | no |  |
| contact | object | no | Target contact. Required when kind=contact_profile. Provide contactId or identity. |
| link | object | no | Target link. Required when kind=link. Provide linkId or endpoints. |
| topLinksLimit | integer | no | Optional top-links cap. |
| recentEventsLimit | integer | no | Optional recent-events cap. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| refSource | string | no | External reference source. |
| refId | string | no | External reference id. |
| ref.source | string | yes | External source; trimmed and lowercased. |
| ref.id | string | yes | Non-empty external id. |
| contact.contactId | integer | no | Exact contact id. |
| contact.identity | object | no | Contact identity locator. |
| link.linkId | integer | no | Exact link id. |
| link.endpoints | object | no | Endpoint-based link locator. |

```sh
ghostpaw-affinity show contact_profile --contact '{"contactId":2}'
```

## manage_contact

Create, revise, export or permanently delete a contact (confirm: true required; owner cannot be deleted). Export without contact exports the whole database. Lifecycle lost is soft delete. ALWAYS search_affinity first before creating — duplicates corrupt the graph.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | create, revise, migrate_kind, set_lifecycle, export, delete. Operation to perform. |
| input | object | no | New contact payload. Required when action=create. |
| kind | string | no | human, agent, group, company, team, pet, service, other. Replacement contact kind for migrate_kind. Owner must remain human or agent. Audited without bond mechanics. |
| confirm | boolean | no | Required true for permanent deletion. |
| contact | object | no | Target contact. Required when action=revise or set_lifecycle. Provide contactId or identity. |
| patch | object | no | Allowed contact patch. Required when action=revise. |
| lifecycleState | string | no | active, dormant, merged, lost. Target lifecycle state. Required when action=set_lifecycle. |
| options | object | no | Optional lifecycle metadata. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| input.identities | array | no | Optional identities to attach. An identity owned by another live contact causes a conflict, or returns that contact when ifExists=return. |
| input.ifExists | string | no | Identity collision policy; return attaches nothing. |
| input.doNotContact | boolean | no | Block outbound engagement unless explicitly overridden. |
| input.name | string | yes | Contact name. |
| input.kind | string | yes | Contact kind. |
| input.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| input.bootstrapOwner | boolean | no | Whether this contact should be the owner. |
| contact.contactId | integer | no | Exact contact id. |
| contact.identity | object | no | Contact identity locator. |
| patch.name | string | no | Optional replacement name. |
| patch.doNotContact | boolean | no | Block outbound engagement unless explicitly overridden. |
| options.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |

```sh
ghostpaw-affinity contact create '{"name":"Fox","kind":"human","bootstrapOwner":true}'
```

## merge_contacts

Merge one loser contact into one winner contact using explicit contact locators.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| winner | object | yes | Winner contact. Provide contactId or identity. |
| loser | object | yes | Loser contact. Provide contactId or identity. |
| reasonSummary | string | no | Optional merge reason. |
| now | integer / string | no | Optional merge timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| winner.contactId | integer | no | Exact contact id. |
| winner.identity | object | no | Contact identity locator. |
| loser.contactId | integer | no | Exact contact id. |
| loser.identity | object | no | Contact identity locator. |

```sh
ghostpaw-affinity contact merge --winner '{"contactId":2}' --loser '{"contactId":8}' --reason-summary "same person"
```

## manage_duplicate_dismissal

Dismiss or un-dismiss a duplicate candidate pair so it does not resurface in review_affinity contacts.duplicates.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | dismiss, undismiss. Action to perform. |
| left | object | yes | Left contact. Provide contactId or identity. |
| right | object | yes | Right contact. Provide contactId or identity. |
| reason | any | no | Optional reason for the dismissal. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| left.contactId | integer | no | Exact contact id. |
| left.identity | object | no | Contact identity locator. |
| right.contactId | integer | no | Exact contact id. |
| right.identity | object | no | Contact identity locator. |

```sh
ghostpaw-affinity duplicate dismiss --left '{"contactId":5}' --right '{"contactId":10}' --reason '"different people"'
```

## manage_identity

Add, revise, verify, or remove one routing identity on a contact. Use this for emails, phone numbers, social handles, and URLs — anything that could locate a person. Do not use manage_attribute for these.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | add, revise, verify, remove. Operation to perform. |
| contact | object | no | Target contact. Required when action=add. Provide contactId or identity. |
| input | object | no | New identity payload. Required when action=add. |
| identityId | integer | no | Identity id. Required when action=revise, verify, or remove. |
| patch | object | no | Identity patch. Required when action=revise. |
| verifiedAt | integer / string | no | Verification timestamp. Optional for action=verify. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| removedAt | integer / string | no | Removal timestamp. Optional for action=remove. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| contact.contactId | integer | no | Exact contact id. |
| contact.identity | object | no | Contact identity locator. |
| input.ifExists | string | no | Return an existing identity on this contact without changes. |
| input.type | string | yes | Identity type: did, atproto_did, email, phone, url, website, handle, x, twitter, linkedin, github, mastodon, bluesky, telegram, whatsapp, signal, matrix, discord, slack, instagram, facebook, youtube, tiktok, address, other, account_id, alias, or custom:<name> (lowercase a-z, 0-9, underscore or hyphen). |
| input.value | string | yes | Identity value. |
| input.label | string | no | Optional label. |
| input.verified | boolean | no | Whether the identity starts verified. |
| input.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| patch.type | string | no | Optional identity type: did, atproto_did, email, phone, url, website, handle, x, twitter, linkedin, github, mastodon, bluesky, telegram, whatsapp, signal, matrix, discord, slack, instagram, facebook, youtube, tiktok, address, other, account_id, alias, or custom:<name> (lowercase a-z, 0-9, underscore or hyphen). |
| patch.value | string | no | Optional identity value. |
| patch.label | string | no | Optional label. |

```sh
ghostpaw-affinity identity add --contact '{"contactId":2}' --input '{"type":"email","value":"jana@x.de"}'
```

## manage_relationship

Seed social links, revise bond and state, and manage structural ties. Seed a link as soon as a relationship is mentioned — do not wait for repeated evidence.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | revise, seed_social_link, revise_bond, override_state, set_structural_tie, remove_structural_tie. Operation to perform. |
| from | object | no | Source contact. Required when action=seed_social_link or set_structural_tie. Provide contactId or identity. |
| to | object | no | Target contact. Required when action=seed_social_link or set_structural_tie. Provide contactId or identity. |
| kind | string | no | Link kind. Required for seed_social_link and set_structural_tie. Can be passed here or inside input. For seed_social_link: personal, family, professional, romantic, care, service, observed, other_relational. For set_structural_tie: works_at, manages, member_of, married_to, partner_of, parent_of, child_of, sibling_of, friend_of, client_of, vendor_of, reports_to, belongs_to, other_structural. |
| role | string | no | Optional role for seed_social_link or set_structural_tie. Can be passed here or inside input. |
| patch | object | no | Replacement link fields; cadenceDays null unpins. |
| input | object | no | Full payload for seed_social_link or set_structural_tie. Alternative to top-level kind/role. |
| link | object | no | Target link. Required when action=revise_bond, override_state, or remove_structural_tie. Provide linkId or endpoints. |
| bond | any | no | Bond text. Required when action=revise_bond. Null to clear. |
| state | string | no | active, dormant, strained, broken, archived. Link state. Required when action=override_state. |
| options | object | no | Optional metadata. |
| removedAt | integer / string | no | Removal timestamp. Optional for action=remove_structural_tie. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| from.contactId | integer | no | Exact contact id. |
| from.identity | object | no | Contact identity locator. |
| to.contactId | integer | no | Exact contact id. |
| to.identity | object | no | Contact identity locator. |
| patch.rank | integer | no | Non-negative relationship rank. |
| patch.affinity | number | no | Affinity from 0 inclusive to 1 exclusive. |
| patch.trust | number | no | Trust from 0 to 1. |
| patch.cadenceDays | oneOf | no | Positive days pins cadence; null on revise restores derivation. |
| patch.bond | oneOf | no | Bond text; null clears. |
| patch.state | string | no | Relationship state. |
| input.rank | integer | no | Non-negative relationship rank. |
| input.affinity | number | no | Affinity from 0 inclusive to 1 exclusive. |
| input.trust | number | no | Trust from 0 to 1. |
| input.cadenceDays | oneOf | no | Positive days pins cadence; null on revise restores derivation. |
| input.bond | oneOf | no | Bond text; null clears. |
| input.state | string | no | Relationship state. |
| input.kind | string | no | Link kind. |
| input.role | string | no | Optional role. |
| input.ifExists | string | no | Existing link behavior. |
| input.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| link.linkId | integer | no | Exact link id. |
| link.endpoints | object | no | Endpoint-based link locator. |
| options.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |

```sh
ghostpaw-affinity relationship tie --from '{"contactId":2}' --to '{"contactId":3}' --kind works_at --role Founder
```

## record_event

Record one social event such as an interaction, observation, milestone, or transaction. For interactions, milestones, and transactions the owner contact is auto-injected into participants if missing. Observations may omit the owner when recording third-party evidence.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| kind | string | yes | interaction, observation, milestone, transaction. Event kind. |
| input | object | yes | Event payload. Always required. Interaction events also require `type`. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| input.type | string | no | Interaction subtype. Required when kind=interaction, omit otherwise. |
| input.overrideDoNotContact | boolean | no | Explicitly override a contact doNotContact block for this event. |
| input.affectsBond | boolean | no | Whether evidence affects the relationship; defaults false for like/follow/repost labels and observations with significance <=2; explicit true opts in. |
| input.content | string | no | Verbatim text, including empty text; at most 1 MB UTF-8. Summary may be omitted when content is supplied. |
| input.externalRef | object | no |  |
| input.channel | string | no | Free-text channel, trimmed and lowercased, at most 40 characters. |
| input.parentRef | object | no |  |
| input.parentEventId | integer | no | Parent event id. |
| input.threadRef | object | no |  |
| input.momentKind | string | no | Optional moment kind. |
| input.occurredOn | string | no | Calendar day. |
| input.provenance | oneOf | no |  |
| input.occurredAt | oneOf | yes | When the event occurred, Unix timestamp in milliseconds. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| input.summary | string | no | Event summary. Must be non-empty. |
| input.significance | integer | yes | Event significance from 1 to 10. |
| input.participants | array | yes | Participant list. Must be non-empty and include the owner contact. |
| input.now | oneOf | no | Optional timestamp override. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |

```sh
ghostpaw-affinity event record --kind interaction --input '{"type":"conversation","occurredAt":"today","summary":"Call re pilot","significance":6,"participants":[{"contactId":2,"role":"recipient","directionality":"mutual"}]}'
```

## manage_commitment

Record or resolve one commitment such as a promise or agreement. The owner contact is auto-injected into participants if missing.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | record, resolve. Operation to perform. |
| input | object | no | Commitment payload. Required when action=record. |
| commitmentEventId | integer | no | Commitment event id. Required when action=resolve. |
| resolution | string | no | kept, cancelled, broken. How the commitment was resolved. Required when action=resolve. |
| options | object | no | Optional metadata. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| input.commitmentType | string | yes | Promise or agreement. |
| input.overrideDoNotContact | boolean | no | Explicitly override a contact doNotContact block for this event. |
| input.affectsBond | boolean | no | Whether evidence affects the relationship; defaults false for like/follow/repost labels and observations with significance <=2; explicit true opts in. |
| input.content | string | no | Verbatim text, including empty text; at most 1 MB UTF-8. Summary may be omitted when content is supplied. |
| input.externalRef | object | no |  |
| input.channel | string | no | Free-text channel, trimmed and lowercased, at most 40 characters. |
| input.parentRef | object | no |  |
| input.parentEventId | integer | no | Parent event id. |
| input.threadRef | object | no |  |
| input.momentKind | string | no | Optional moment kind. |
| input.occurredOn | string | no | Calendar day. |
| input.provenance | oneOf | no |  |
| input.occurredAt | oneOf | yes | When the commitment was made, Unix timestamp in milliseconds. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| input.summary | string | no | Commitment summary. Must be non-empty. |
| input.significance | integer | yes | Commitment significance from 1 to 10. |
| input.dueAt | oneOf | no | Optional due timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| input.dueOn | string | no | Due calendar day. |
| input.participants | array | yes | Participant list. Must be non-empty and include the owner contact. |
| input.now | oneOf | no | Optional timestamp override. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| options.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| options.resolvingEvent | object | no |  |

```sh
ghostpaw-affinity commitment record --input '{"commitmentType":"promise","occurredAt":"today","dueAt":"+3d","summary":"Send proposal","significance":6,"participants":[{"contactId":2,"role":"recipient"}]}'
```

## manage_date_anchor

Add, revise, or remove recurring date anchors on contacts or links. Use this for birthdays, anniversaries, and yearly events — not manage_attribute.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | add, revise, remove. Operation to perform. |
| input | object | no | Date anchor payload. Required when action=add. |
| anchorEventId | integer | no | Anchor event id. Required when action=revise or remove. |
| patch | object | no | Anchor patch. Required when action=revise. |
| options | object | no | Optional metadata. |
| removedAt | integer / string | no | Removal timestamp. Optional for action=remove. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| input.target | object | yes | Date-anchor target. |
| input.recurrenceKind | string | yes | Recurrence kind. |
| input.anchorMonth | integer | yes | Anchor month, 1–12. |
| input.anchorDay | integer | yes | Anchor day, 1–31 (validated per month). |
| input.summary | string | yes | Summary. Must be non-empty. |
| input.significance | integer | yes | Significance from 1 to 10. |
| input.now | oneOf | no | Optional timestamp override. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| input.force | boolean | no | Whether to bypass duplicate checks. |
| patch.recurrenceKind | string | no | Optional recurrence kind. |
| patch.anchorMonth | integer | no | Optional month, 1–12. |
| patch.anchorDay | integer | no | Optional day, 1–31. |
| patch.summary | string | no | Optional summary. |
| patch.significance | integer | no | Optional significance, 1–10. |
| options.now | oneOf | no | Optional timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| options.force | boolean | no | Whether duplicate checks should be bypassed. |

```sh
ghostpaw-affinity date add --input '{"target":{"kind":"contact","contact":{"contactId":2}},"recurrenceKind":"birthday","anchorMonth":11,"anchorDay":3,"summary":"Jana bday","significance":4}'
```

## manage_attribute

Set, unset, or replace custom metadata attributes on contacts, links and events. For emails, phones, handles, and URLs use manage_identity instead — those are routing keys, not attributes.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | set, unset, replace. Operation to perform. |
| target | object | no | Attribute target. Always required. |
| name | string | no | Attribute name. Required when action=set or unset. |
| value | any | no | Attribute value. Required when action=set. Null for presence/tag semantics. |
| entries | array | no | Key-value map to replace all attributes. Required when action=replace. |
| removedAt | integer / string | no | Removal timestamp. Optional for action=unset. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| target.kind | string | yes | Target kind. |
| target.eventId | integer | no | Target event id; provide eventId or ref. |
| target.ref | object | no |  |
| target.contact | object | no | Contact locator. Required when kind=contact. Provide contactId or identity. |
| target.link | object | no | Link locator. Required when kind=link. Provide linkId or endpoints. |
| entries.name | string | yes | Attribute name. |
| entries.value | oneOf | no | Attribute value, or null for presence/tag semantics. |

```sh
ghostpaw-affinity attribute set --target '{"kind":"contact","contact":{"contactId":2}}' --name pipeline_stage --value '"proposal"'
```

## manage_event

Revise or delete one event by eventId or external reference. Delete requires confirm=true and recomputes affected relationships.

Use when:

Not for:

Writes: writes_state.

| Parameter | Type | Required | Values / description |
| --- | --- | --- | --- |
| action | string | yes | revise, delete. Action. |
| eventId | integer | no | Event id; provide eventId or ref. |
| ref | object | no |  |
| confirm | boolean | no | Must be true to delete. |
| patch | object | no | Fields to revise; externalRef may only be added when absent. |
| tz | string | no | IANA time zone for due days and local calendar calculations; defaults to TZ or the process local zone. |
| refSource | string | no | External reference source. |
| refId | string | no | External reference id. |
| ref.source | string | yes | External source; trimmed and lowercased. |
| ref.id | string | yes | Non-empty external id. |
| patch.summary | string | no | Short non-empty label. |
| patch.content | string | no | Verbatim content, at most 1 MB UTF-8. |
| patch.occurredAt | oneOf | no | Event timestamp. Accepts epoch milliseconds integer, ISO 8601 date-time with Z/offset, YYYY-MM-DD, DD.MM.YYYY, today, tomorrow, yesterday, +3d or -2d. UTC midnight for dates; dueAt uses UTC end of day. |
| patch.significance | integer | no | Significance 1..10. |
| patch.channel | string | no | Channel, at most 40 characters. |
| patch.type | string | no | Type within the same event kind. |
| patch.externalRef | object | no |  |

```sh
ghostpaw-affinity event revise --event-id 1 --patch '{"summary":"Corrected"}'
```

## Workflow guides

- `ghostpaw-affinity skill bootstrap-and-cold-start`: Establish a clean Affinity baseline with one owner, one verified identity, and the minimum structure needed for later evidence and review work.
- `ghostpaw-affinity skill operate-agent-relationships`: Coach multiple agent contacts with explicit commitments, verified outcomes, and fixed relationship rhythms.
- `ghostpaw-affinity skill identify-and-locate-contacts`: Find the right contact reliably, prefer stable natural keys when possible, and avoid creating duplicates through weak lookup discipline.
- `ghostpaw-affinity skill import-history-without-faking-evidence`: Import pre-existing relationship state honestly, using seeded links for known history instead of inventing fake journal evidence.
- `ghostpaw-affinity skill model-structure-orgs-and-households`: Model factual structure such as employment, membership, hierarchy, and household ties without confusing it with live relational mechanics.
- `ghostpaw-affinity skill record-direct-evidence-well`: Record direct owner-facing social evidence in a way that produces truthful mechanics, good moments, and useful future review surfaces.
- `ghostpaw-affinity skill record-observations-and-referrals`: Capture third-party and referral truth without overclaiming intimacy, directness, or trust that the operator did not actually earn.
- `ghostpaw-affinity skill capture-transactions-and-commercial-events`: Capture commercially meaningful interactions as transactions so operational and service relationships accumulate the right evidence shape.
- `ghostpaw-affinity skill manage-promises-and-agreements`: Track obligations explicitly from creation to resolution so open commitments remain actionable and trust consequences stay honest.
- `ghostpaw-affinity skill manage-recurring-dates-and-reminders`: Use date anchors for recurring salience so important birthdays, anniversaries, renewals, and memorials feed review surfaces cleanly.
- `ghostpaw-affinity skill review-radar-progression-and-graph`: Use the review surfaces to prioritize maintenance, understand progression readiness, and read the shape of the relationship graph without guessing from raw rows.
- `ghostpaw-affinity skill reconcile-duplicates-and-merge-safely`: Review duplicate candidates carefully and merge only after the identity, history, and structural consequences are understood.
- `ghostpaw-affinity skill tools`: Tool parameters, nested fields, and examples.

## Principles

- Honor evidence before narrative.
- Clarify before you act.
- Keep truths in their proper layer.
- Read derived signals with judgment.
- Protect relationship integrity over time.
- Follow the operational protocol.
