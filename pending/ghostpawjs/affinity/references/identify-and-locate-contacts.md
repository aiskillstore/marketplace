# Identify And Locate Contacts

Handle identities normalize leading @ and case. Bluesky uses a domain handle,
X/Twitter uses 1–15 letters/digits/underscores, Mastodon uses user@host.tld.
Native did (alias atproto_did) validates did:<method>:<identifier>; legacy
custom:atproto-did locators find the same identity. Keep old handles as identities.
An owned identity makes contact creation fail atomically with conflict and
existingContactId. input.ifExists="return" returns the matching contact and
matchedIdentities without attaching any free identities. CLI: --if-exists return.
Name-only possible duplicates still warn. Search @handle is always literal.

Primary tools:
- `search_affinity`
- `inspect_affinity_item`
- `manage_identity`
- `manage_contact`

Goal:
- Resolve the right contact before mutating anything, using the strongest available locator.

When to use:
- A harness receives a name, email, phone number, URL, or ambiguous reference to a person or organization.
- You need to confirm whether a contact already exists before creating a new one.

When not to use:
- You already have one exact internal id from a prior successful tool result.
- You are reviewing a list surface rather than identifying one exact target.

Step-by-step sequence:
1. Start with `search_affinity` whenever the target might already exist.
2. If you have a strong natural key such as email, phone, or URL-like handle, use that query first rather than a vague display name.
3. If search returns one strong candidate, use `inspect_affinity_item` to confirm the profile before mutating.
4. If the target does not exist, create it with `manage_contact`.
5. Immediately add the best routing key with `manage_identity` so future lookup becomes exact rather than fuzzy.
6. If the system returns ambiguity, stop and clarify instead of guessing.

Validation checks:
- The inspected profile matches the intended person or organization.
- The best known routing identity is attached and, when appropriate, verified.
- Later searches by that identity return the same contact cleanly.

Pitfalls:
- Do not trust names alone when a natural key is available.
- Do not create a second contact just because search returned multiple plausible matches.
- Do not remove or revise identities casually; they are your best future locator surface.

Tips and tricks:
- Prefer exact identities over integer ids when the harness needs to survive across sessions or partial memory loss.
- After creating a contact from a vague mention, upgrade it with a real identity as soon as possible.
- If multiple weak matches appear, inspect before mutating.

Tool calls to prefer:
- `search_affinity` for candidate discovery
- `inspect_affinity_item` for exact confirmation
- `manage_identity` for routing-key upgrades
- `manage_contact` only after lookup fails honestly

Related skills:
- `bootstrap-and-cold-start`
- `reconcile-duplicates-and-merge-safely`