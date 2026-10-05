# Pull Requests, Changelogs, Releases, and Pages

## Pull request structure

Use a title that summarizes the full branch diff, not only the last commit.

```markdown
## Summary

- What changed and why

## Important decisions

- Compatibility, architecture, security, or migration decisions

## Verification

- `command` — result

## Follow-up

- Remaining rollout, migration, or operational work
```

Omit empty sections. Mark unrun checks clearly. Use draft status when review, migration, or verification is incomplete; use ready-for-review only when the user requests it or repository workflow clearly establishes that convention.

Before creating a PR, search for an existing open PR for the same head branch. Update it rather than creating a duplicate.

## Changelogs

Follow the repository's existing format. When it uses Keep a Changelog:

- add user-visible changes under `Unreleased`;
- use Added, Changed, Deprecated, Removed, Fixed, or Security;
- keep entries focused on user impact;
- include verified issue links when available;
- preserve version comparison links.

Do not amend a published commit or create a changelog unprompted when repository policy does not require it.

## Releases

Preparing release notes does not authorize:

- version-file mutation;
- tagging;
- pushing a tag;
- creating a GitHub release;
- merging;
- deploying.

Perform only the actions the user requested. Verify the exact tag and remote state before publishing.

## GitHub Pages after a push

Inspect the Pages workflow trigger and the pushed ref:

```yaml
on:
  push:
    branches: [main]
```

This updates the public site only after a push to `main`. A feature-branch push should run validation but should not replace production documentation. Report “Pages will update after merge to main,” not “deployed.”

When the push triggers Pages:

1. identify the workflow run for the pushed SHA;
2. wait for build and deploy jobs;
3. report failure evidence or the published environment URL;
4. do not infer success from a successful local documentation build alone.
