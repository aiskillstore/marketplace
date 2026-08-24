---
name: tag-release
description: Use when asked to tag or cut a patch, minor, or major release. Tags the remote default branch in the repo's convention, pushes, and watches the release to green.
user-invocable: true
---

# Tag a release

Tag the current `origin` default-branch HEAD in the repository's established
version format and tag kind. Inspect the release convention, compute the next
version, verify the exact target, push the tag, and watch the release to green.

The request authorizes creating and pushing the tag and running the repository's
established release workflow. Ask only when a required value cannot be derived
or the repository state makes the release ambiguous.

## 1. Sync to the origin default branch first

The tag must point at what is actually on the remote, not whatever your local
checkout happens to be at.

```sh
git remote get-url origin
git ls-remote --symref origin HEAD
git fetch origin --tags --prune
```

- Resolve the GitHub `owner/repository` from the `origin` URL. Pass that value
  explicitly with `--repo` or `-R` to every `gh` command so `GH_REPO`, another
  remote, or a configured default cannot redirect release operations.
- Resolve the default branch from the remote's symbolic `HEAD`, not from a local
  branch or a potentially stale `origin/HEAD`. Record its full ref name.
- Leave the working tree and local branches untouched. A dirty or diverged
  checkout does not affect a tag created directly from the fetched remote-tracking
  ref.
- Record `git rev-parse origin/<default-branch>` as the candidate release commit.
  Do not cut a release from a red default branch. If the repository gates
  releases on CI, verify the checks are green on that exact commit.

## 2. Read the prior release and the repo's convention

Never invent a format. Look at what the repo already does:

```sh
gh release list -R <owner/repository>    # if releases are forge Release objects
git ls-remote --tags --refs origin 'refs/tags/<relevant-prefix>*'
```

Choose the relevant package or release namespace before selecting the latest
version. A repository may contain unrelated product tags, package tags, or legacy
formats that sort ahead of the series being released. Treat the remote tag refs
as authoritative. Local tags may be stale or local-only even after `git fetch
--tags --prune`. Fetch and inspect matching tag objects only after identifying
the relevant remote series.

From the latest release, read:

- **Version format**: a leading `v` or not, any component or package prefix (a
  monorepo may tag `pkg-name/v1.2.3`), and any pre-release or build suffix.
- **Tag kind**: lightweight, annotated, or signed. Check with
  `git cat-file -t <tag>` (a `tag` object means annotated/signed, a `commit` means
  lightweight) and `git verify-tag <tag>` for signing.
- **Release mechanism**: whether a release is just a pushed tag (a pipeline picks
  it up), or an explicit forge Release created with `gh release create`.

If there is no prior release, there is nothing to bump from: use the repo's
documented starting version, or ask which to use.

## 3. Compute the next version

Compute a semantic bump from the latest tag in the relevant series, preserving
its leading `v` and any package prefix:

- **patch**: `x.y.(z+1)`
- **minor**: `x.(y+1).0`
- **major**: `(x+1).0.0`

Follow the repository's established transition from prerelease to stable tags.
If history does not establish whether to advance, retain, or drop a prerelease
suffix, ask the user.

Record the computed tag, candidate commit SHA, tag kind, and release mechanism.

## 4. Create the tag, matching convention

Immediately before tagging, re-fetch and confirm nothing moved:

```sh
git ls-remote --symref origin HEAD
git fetch origin --tags --prune
git rev-parse origin/<default-branch>
git ls-remote --tags --refs origin 'refs/tags/<relevant-prefix>*'
gh api 'repos/<owner>/<repository>/commits/<release-sha>/check-runs'
gh api 'repos/<owner>/<repository>/commits/<release-sha>/status'
```

The default branch, its SHA, and the latest relevant tag must be unchanged, the
proposed tag must not exist, and required checks on the release SHA must be
green. If anything moved, recompute the release and repeat this check. If a
required check is pending or failing, stop.

Then tag the fetched remote HEAD explicitly, matching the kind of the prior tags:

```sh
# lightweight (prior tags are lightweight):
git tag <version> origin/<default-branch>

# annotated (prior tags are annotated):
git tag -a <version> origin/<default-branch> -m "<version>"
```

A global `tag.gpgsign = true` silently turns even a lightweight or annotated tag
into a signed one. If the repo's existing tags are unsigned, pass `--no-sign` so
the new tag matches. If they are signed, sign it.

## 5. Push, then watch the release to green

```sh
git push origin <version>
```

If the convention includes a forge release, create it only after pushing the
verified local tag. Use `gh release create <version> --verify-tag ...`, matching
how prior releases set their title, notes, and assets, and pass
`--repo <owner/repository>`. Then verify the outcome:

```sh
git ls-remote origin 'refs/tags/<version>' 'refs/tags/<version>^{}'
gh run watch <run-id> -R <owner/repository> --exit-status --interval 20
gh release view <version> -R <owner/repository>
```

For an annotated or signed tag, compare the peeled `^{}` result with the
release commit SHA. For a lightweight tag, compare the direct tag result.
Do not call it done until the remote tag resolves to the release commit, the
release pipeline is green, and the expected release artifacts exist.

## 6. Report

State the version you cut, the commit SHA it points at, how it was tagged
(lightweight / annotated / signed), and the release or pipeline result.
