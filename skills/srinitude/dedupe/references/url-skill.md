# URL and skill adapters

Owner: `dedupe`. Load when the `url` or `skill` adapter is selected. Backlink: `SKILL.md` PD-004.

## URL adapter

### Component policy

Declare how each component is treated:

- scheme
- host and internationalized host form
- explicit and default port
- path, slash policy, dot segments, percent encoding, and case
- query pair order, blank values, repeated keys, and dropped names
- fragment

The deterministic inspector lowercases scheme and host and can remove default HTTP or HTTPS ports. It preserves path meaning. Query sorting, fragment stripping, and parameter removal happen only when declared in `url_policy`.

### Tracking parameters

Name every parameter allowed for removal. Do not apply an assumed global tracking list. A query parameter can change resource identity.

### Redirects

Redirect resolution requires network authority. Record:

- runtime clock anchor
- request method and redirect limit
- each status and location
- final URL
- cache or freshness policy
- failures and loops

A redirect observed now is not permanent identity. Keep literal, normalized, and resolved URL classes separate.

### Security

Reject URLs containing user information. Do not leak credentials, signed query values, tokens, or private hosts into reports. Prefer source indices and hashed keys.

## Skill adapter

### Scope and provenance

Each item is one skill directory containing `SKILL.md`. Record:

- path and source class, such as bundled, hub, external, or user-local
- frontmatter name and version
- host creation and compatibility provenance when present
- packet file count and SHA-256
- bundled manifest, hub lock, and usage-sidecar facts when available

Do not trust one provenance store when another governing store disagrees. A frontmatter and sidecar mismatch is unresolved until reconciled at the canonical owner.

### Exact packet identity

Hash relative paths and bytes for `SKILL.md` plus recognized support directories:

- `references/`
- `templates/`
- `scripts/`
- `assets/`
- `examples/`
- `evals/`

Ignore runtime `__pycache__` directories and `.pyc` files. Reject packet symlinks. Equal packet hashes prove packet equality only. They do not decide which installation source or path should remain.

### Name conflicts

The same skill name with different packet hashes is an identity conflict, not an exact duplicate. Preserve both until source ownership, version, compatibility, and canonical path are resolved.

Different names with similar procedures are overlap candidates. Compare triggers, boundaries, invariants, commands, references, and evaluation behavior. Use the broader canonical owner only when meaning and quality are preserved.

### Normalized and semantic review

Normalization can ignore line endings or non-semantic Markdown whitespace only under an explicit policy. A semantic overlap review must remain a candidate review and cannot authorize deletion.

Load `simplify-skill` when the requested outcome is simplifying one skill's rules. `dedupe` owns cross-item identity, canonical mapping, and mutation safety; it does not take over internal simplification.

### Canonical policy

Use documented source precedence and ownership. Consider:

- supported host source class
- current compatibility review
- complete support packet
- canonical author and version
- active references from cron jobs, profiles, or skills
- user direction

Never pick the newest version or modification time without checking compatibility and runtime time.

### Mutation gate

Before removing or merging a skill:

1. Read every governing provenance store.
2. Search references by skill name and path.
3. Select the canonical owner and absorption target.
4. Preserve or rewrite dependents.
5. Use supported skill lifecycle tools.
6. Re-read the installed packet and active registry.
7. Run native checks and the required post-mutation evaluation process.

Do not recursively clean the whole skill tree.

## Request examples

URL normalized inspection:

```json
{
  "adapter": "url",
  "mode": "normalized",
  "items": ["HTTPS://Example.COM:443/a?b=2&a=1#top"],
  "url_policy": {
    "strip_fragment": true,
    "sort_query": true,
    "drop_query_params": []
  }
}
```

Skill exact inspection:

```json
{
  "adapter": "skill",
  "mode": "exact",
  "items": ["/skills/one", "/skills/two"]
}
```

## Adapter checks

- URL transformations are component-specific and disclosed.
- Redirects use explicit network and time authority.
- Skill packets preserve relative paths and source provenance.
- Same-name packet differences remain conflicts.
- Cross-skill semantic overlap never becomes silent deletion.
