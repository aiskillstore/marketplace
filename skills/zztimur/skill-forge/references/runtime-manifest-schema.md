# Runtime Manifest Schema

Every canonical Skill Forge runtime archive contains
`skill-forge/runtime-manifest.json`. The manifest binds the archive's regular
runtime members to one committed Git source identity. It proves internal
archive integrity; local Git provenance is a separate verification result.

## Version 1

The canonical schema identifier is `skill-forge.runtime-manifest.v1`.
Objects use exact keys and file records are sorted by UTF-8 path bytes.
Canonical JSON is the UTF-8 encoding of Python-equivalent
`json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
separators=(",", ":"))`: no BOM or trailing newline, no insignificant
whitespace, object keys in Unicode code-point order, and non-ASCII characters
encoded literally rather than as `\u` escapes. The v1 schema contains no
floating-point values. The structural example below abbreviates the `files`
array; a real manifest contains the complete selector expansion.

```json
{
  "schema": "skill-forge.runtime-manifest.v1",
  "package": {"name": "skill-forge", "root": "skill-forge"},
  "source": {
    "object_format": "sha1",
    "commit": "<full object id>",
    "tree": "<full object id>"
  },
  "selection": {
    "policy": "skill-forge.runtime-paths.v1",
    "selectors": [
      "SKILL.md",
      "README.md",
      "LICENSE",
      "agents",
      "references",
      "scripts/inspect_skill_package.py",
      "scripts/package_skill.py",
      "scripts/portable_zip_paths.py",
      "scripts/run_self_tests.py",
      "scripts/runtime_manifest.py",
      "scripts/validate_audit_contract.py"
    ]
  },
  "canonical_zip": "skill-forge.zip.v1",
  "hash_algorithm": "sha256",
  "manifest": {
    "path": "runtime-manifest.json",
    "self_hash_policy": "excluded"
  },
  "files": [
    {
      "path": "SKILL.md",
      "size": 1234,
      "sha256": "<64 lowercase hexadecimal characters>",
      "git_mode": "100644"
    }
  ]
}
```

`selection` is an exact, versioned allowlist. File selectors name one committed
regular file; directory selectors include every committed regular descendant.
Every selector must match, and the manifest must use the authoritative list
shown above without additions, omissions, or reordering. This makes runtime
completeness part of the proof and keeps source verification within bounded,
fixed Git command lines.

`files` lists every regular archive member selected by that policy below
`skill-forge/`, except the generated manifest itself, and no others. Paths are
canonical, portable POSIX-relative UTF-8 identities.
`git_mode` is `100644` or `100755`. A file's size and SHA-256 cover its exact
committed blob bytes. Verification is bounded to 5,000 files, 25 MiB per file,
and 100 MiB total runtime bytes.

## Canonical ZIP Policy

`skill-forge.zip.v1` requires:

- only regular file members, with no explicit directory entries;
- member order sorted by UTF-8 path bytes;
- stored members with no compression;
- timestamp `1980-01-01 00:00:00` for every member;
- Unix regular-file metadata derived from `git_mode`;
- the UTF-8 filename flag exactly when a member name is non-ASCII;
- no member extra fields or comments and no archive comment;
- no self-extracting prefix or trailing bytes outside the final ZIP end record;
- an exact member set matching the manifest plus the manifest itself; and
- exact full-archive bytes equal to reconstruction by the v1 canonical writer.

The last rule covers local headers and archive layout as well as the active
central directory. It rejects hidden gaps, obsolete directory structures, and
local-only metadata that a central-directory-only parser would not expose.
Runtime member metadata and declared sizes are validated before payload reads.

These rules make two builds from the same committed revision byte-for-byte
reproducible. A plain `git archive` ZIP is not canonical even when its file
contents happen to match.

## Evidence Boundary

Manifest verification establishes that the ZIP is canonical and internally
self-consistent. It does not by itself prove that the declared commit exists or
that Git produced the bytes. Source proof separately resolves the embedded
commit and tree in a caller-selected local Git repository, reads the selected
Git blobs, and reproduces the manifest. Git replacement refs are disabled and
inherited repository-selection/configuration variables are sanitized so local
aliases cannot substitute a different object graph. Reports keep
`archive_integrity`, `source_proof`, and their shared manifest-digest binding
distinct. Both proof results expose the same manifest SHA-256; archive integrity
additionally exposes the canonical archive SHA-256.

The caller is responsible for establishing why that local repository is
trusted. Source proof demonstrates consistency with its selected local Git
object graph; it does not prove a remote origin, branch or tag reachability,
signer identity, tag authenticity, authorship, or release authorization. It is
also separate from independent Skill Forge inspection and official host
validation.

Source proof is `Pass` when Git reproduces the manifest, `Fail` when resolved
Git evidence contradicts it, and `Not Assessed` when Git or the requested
history is unavailable. If source proof was explicitly requested, anything
other than `Pass` fails the package-verification command even though archive
integrity remains a separate result.

Archive-only verification leaves source proof Not Assessed:

```bash
python3 -S scripts/package_skill.py verify /path/to/skill-forge.zip --json
```

Supply the caller-selected source repository to require local source proof and
the manifest-digest binding:

```bash
python3 -S scripts/package_skill.py verify /path/to/skill-forge.zip \
  --json --source-repo /path/to/skill-forge-source
```
