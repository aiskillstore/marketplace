# File and record adapters

Owner: `dedupe`. Load when the `file` or `record` adapter is selected. Backlink: `SKILL.md` PD-003.

## File adapter

### Scope

Provide an explicit list of paths. Directory recursion, hidden files, mount crossings, archives, and generated outputs are outside scope unless named.

### Identity choices

Keep these distinct:

- path identity
- filesystem object identity using device and inode where available
- exact byte-content identity using SHA-256
- normalized text-content equality using an explicit encoding and text policy

Two paths with equal bytes are content duplicates, not necessarily safe deletion candidates. Ownership, permissions, links, backup status, and consumers can differ.

### Links

The inspector reports device, inode, size, byte hash, and symlink status for resolved files.

- Symlinks are unresolved by default.
- `follow_symlinks: true` is inspection authority only. It is not deletion authority.
- Equal device and inode values identify hard-linked directory entries on supporting filesystems.
- Never remove the last required name for a hard-linked object without explicit approval.

### Normalized files

Require `encoding` and a disclosed text normalization policy. Decode failures remain unresolved. Do not normalize binary formats, archives, office documents, images, audio, or video as text.

### Canonical policy

Possible selectors include preferred path, authoritative repository, retained metadata, first-seen, newest timestamp, or explicit choice. Time-based selection requires a runtime clock anchor and declared timestamp source.

### Mutation proof

Before deletion or movement, capture path, byte hash, size, link facts, canonical path, approved action, and reconstruction path. Afterward, verify retained bytes and all planned paths.

## Record adapter

### Schema

Record items must be objects. Declare:

- key fields and their order
- field types
- normalization per key field
- missing-field behavior
- null semantics
- non-key conflict policy
- canonical selector

### Exact key

Use canonical JSON for whole-record exact equality. Preserve distinctions among missing, null, empty string, zero, false, empty array, and empty object.

### Normalized key

Use a non-empty ordered `key_fields` array. The inspector normalizes string key values with the disclosed text policy and uses canonical JSON for other values.

A matching key identifies a group under the selected schema. It does not settle non-key values.

### Conflicts and merge

For each group, list every non-key field whose presence or value differs. Resolve each field with one of:

- keep canonical value
- fill only missing canonical value
- union values with stable order
- retain all values in a side record
- explicit source priority
- unresolved

Never use a generic "most complete" rule without naming scored fields, weights, and tie-breakers.

### Request examples

File exact inspection:

```json
{
  "adapter": "file",
  "mode": "exact",
  "items": ["/data/a.txt", "/data/b.txt"],
  "follow_symlinks": false
}
```

Record normalized inspection:

```json
{
  "adapter": "record",
  "mode": "normalized",
  "items": [
    { "id": 1, "email": " A@X.COM ", "name": "A" },
    { "id": 2, "email": "a@x.com", "name": "Alice" }
  ],
  "key_fields": ["email"],
  "normalization": {
    "casefold": true,
    "whitespace": "collapse"
  }
}
```

## Adapter checks

- Paths or records are bounded and indexed.
- Link and schema assumptions are explicit.
- Byte, path, object, and normalized identity are not conflated.
- Missing and null stay distinct unless the schema says otherwise.
- Non-key conflicts remain visible.
- Destructive work has exact authority and reconstruction proof.
