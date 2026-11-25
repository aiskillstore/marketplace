# Import History Without Faking Evidence

For social imports, use native did identities (atproto_did is an alias; legacy
custom:atproto-did locators remain equivalent). Create with input.ifExists="return"
for safe retries: this attaches nothing to an existing contact. For handle changes,
call manage_identity add separately with input.ifExists="return"; an identity already
on that contact is a no-op, while another owner still conflicts. Seed links with
input.ifExists="return" to reuse them without changing their state.
Use ghostpaw-affinity batch [--chunk 500] with JSONL {tool,args}, or
{op:"event",kind:"interaction",input:{...}}. Per-line savepoints isolate failures;
--stop-on-error stops early. Exit 2 identifies malformed JSON; other failures exit 1.
Use externalRef {source:"bluesky",id:recordUri}, verbatim content and channel.
Participant contact locators may use identities, including did, instead of ids.
Read JSON flags from stdin with --input - or from @file for large payloads (E2BIG).
SQLite date-times without offsets mean UTC; microseconds truncate to milliseconds; raw timestamps remain in provenance.
Missing inbound-follow timestamps should use a known first_seen or be counted as skipped.
The synthetic scripts/examples/import_social_jsonl.mjs and import_dry_run.mjs
show the mapping and verify an idempotent retry and byte-identical text.

For archived messages with known timestamps, record actual evidence with externalRef:
{source, id} deduplicates retries across event families and commitments. Keep original
message text in content, use channel and parentRef/threadRef for context, and keep
summary short or let it derive from content. Content is limited to 1 MB UTF-8;
keep larger raw archives in the source system. Inspect events by external reference,
search scope "events", and use manage_event revise/delete to correct imports.
See the tools guide for field details. Existing 0.5.x databases upgrade in place.

Primary tools:
- `manage_contact`
- `manage_identity`
- `manage_relationship`
- `inspect_affinity_item`

Goal:
- Represent real pre-system relationship state without fabricating a timeline of events that never existed inside Affinity.

When to use:
- You are migrating from another CRM, notes system, or memory set.
- You already know a relationship exists and roughly how strong or active it is, but you do not want to reconstruct every past interaction.

When not to use:
- A new event just happened and should affect mechanics now.
- You are recording a specific conversation, milestone, transaction, or observation.

Step-by-step sequence:
1. Create or locate the relevant contacts first.
2. Add the strongest identities you know so the imported graph stays addressable later.
3. Use `manage_relationship` with `action: "seed_social_link"` to establish a relational link that already existed before the system.
4. Set only the fields you can justify: kind, rough rank, trust, cadence, state, and optional bond.
5. Inspect the result with `inspect_affinity_item` if you need to verify the exact post-import state.
6. From that point forward, switch to evidence tools for all new real-world activity.

Validation checks:
- The imported contact pair now has the expected relational link.
- The seeded state looks plausible when inspected.
- Later direct events continue progression from the seeded baseline rather than from zero.

Pitfalls:
- Do not backfill dozens of fake conversations just to reach a desired rank.
- Do not use import seeding for ordinary day-to-day relationship maintenance.
- Do not overstate confidence on rank or trust when the historical truth is actually vague.

Tips and tricks:
- Seed conservatively if you are unsure. It is safer to underclaim and let real future evidence move the link.
- Use bond text sparingly as a narrative reminder of why the imported state is what it is.
- Prefer one honest seed over many synthetic event reconstructions.

Tool calls to prefer:
- `manage_relationship` with `seed_social_link`
- `manage_contact` and `manage_identity` before seeding
- `inspect_affinity_item` for post-import verification

Related skills:
- `bootstrap-and-cold-start`
- `record-direct-evidence-well`