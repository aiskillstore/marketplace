# Bootstrap And Cold Start

Primary tools:
- `manage_contact`
- `manage_identity`
- `inspect_affinity_item`
- `review_affinity`

Goal:
- Establish one clean owner record, make it reachable, and verify the system is ready for later relationship work.

When to use:
- The database is new or logically empty.
- A harness needs to initialize its own operator profile before doing anything else.

When not to use:
- The owner already exists and you only need to update profile fields.
- You are importing historical relationships; use the import-focused skill after bootstrap.

Step-by-step sequence:
1. Assume the schema is already initialized and the database is live before using any tool.
2. Use `manage_contact` with `action: "create"` and `bootstrapOwner: true` exactly once for the operator, BEFORE recording any events. Use kind `agent` for bots and non-human operators, kind `human` for people. CLI: `contact create --bootstrap-owner`. Creation results expose top-level `id` (CLI JSON: `jq .id`); the tool field is `input.bootstrapOwner`.
3. Immediately attach at least one routing identity with `manage_identity` so future lookups can use a stable natural key.
4. Use `inspect_affinity_item` with `kind: "owner_profile"` to confirm that the owner profile exists and reads back cleanly.
5. Use `review_affinity` with `view: "contacts.list"` to confirm that the portfolio is still minimal and no duplicate owner-like records were created during setup.

Validation checks:
- The owner profile loads successfully.
- The owner has at least one live identity.
- The contact list shows exactly the records you expect at this early stage.

Pitfalls:
- Do not create a non-owner placeholder and plan to convert it later if the harness can bootstrap the real owner immediately.
- Do not skip identity attachment, or later natural-key lookup will be weaker and duplicate-prone.
- Do not seed relationships before the owner exists if later evidence is meant to be owner-facing.

Tips and tricks:
- Prefer an identity that is stable across sessions, such as a primary email or canonical profile URL.
- Keep the first dataset tiny. Bootstrap is for a trustworthy base, not a full import.
- If setup feels ambiguous, inspect first and add less rather than more.

Tool calls to prefer:
- `manage_contact` for owner creation
- `manage_identity` for first routing key
- `inspect_affinity_item` for confirmation
- `review_affinity` for early portfolio sanity checks

Related skills:
- `identify-and-locate-contacts`
- `import-history-without-faking-evidence`