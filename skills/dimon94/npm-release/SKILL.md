---
name: npm-release
version: 1.1.0
description: Use when ready to publish a new version of cc-devflow npm package to npm registry, including version sync, changelog finalization, git tag creation, and publish verification.
skill_class: maintenance
route_family: maintenance
reads:
  - PLAYBOOK.md
  - CHANGELOG.md
  - references/git-commit-guidelines.md
  - ../do-not-repeat-yourself/SKILL.md
  - references/checklist-contract.md
---

# NPM Release Workflow

## Quick Start

1. Read `PLAYBOOK.md`, `CHANGELOG.md`, `references/git-commit-guidelines.md`, `../do-not-repeat-yourself/SKILL.md`, and `references/checklist-contract.md`.
2. Confirm the current worktree and branch are the user-approved release target.
3. Run `git status --short`, capture `release_target_branch="$(git branch --show-current)"`, inspect current version and recent commits, then run `npm whoami`.
4. Stop before real publish when git state, branch target, version conclusion, changelog, or npm auth is not proven.

`npm-release` 是内部维护 skill，不属于对外公开分发的五步 workflow。

## Release Law

Release is atomic: `package.json`, `package-lock.json`, `CHANGELOG.md`, release
commit, annotated tag, pushed branch, pushed tag, and npm registry version must
describe the same version.

Release skills must never auto-switch branches. If the current worktree is not
already the user-confirmed release target, stop and ask for the correct release
worktree/branch or create a separate release worktree without changing the main
checkout.

Release commits follow `references/git-commit-guidelines.md` and run `../do-not-repeat-yourself/SKILL.md` before staging.

## Stop Conditions

- Current branch is not the user-confirmed release target.
- Uncommitted changes exist before release preparation.
- Unpushed commits exist and the user has not approved releasing from this branch state.
- `npm whoami` fails for the publish registry.
- The release is pre-release/beta and no adaptation plan exists.

## Release Flow

1. Choose semver level:

| Type | Version Change | When |
| --- | --- | --- |
| `patch` | 2.4.3 -> 2.4.4 | Bug fixes, minor improvements |
| `minor` | 2.4.4 -> 2.5.0 | Backward-compatible features |
| `major` | 2.5.0 -> 3.0.0 | Breaking changes |

2. Update `CHANGELOG.md`, then update `package.json` and `package-lock.json`:

```bash
npm version <patch|minor|major> --no-git-tag-version
```

3. Verify:

```bash
npm run verify:publish
npm pack --dry-run
```

4. Commit:

```bash
git add CHANGELOG.md package.json package-lock.json

git commit -m "$(cat <<'EOF'
chore(release): bump version to X.Y.Z

问题:
- 公开包版本、CHANGELOG 和发布标签需要落到同一个可追溯节点。

变更:
- 更新 package version 和 CHANGELOG 到 X.Y.Z。
- 为 npm publish 准备 release commit。

原因:
- release commit 把版本标记和说明绑定，避免 tag 指向不可解释的历史。

验证:
- npm run verify:publish
- npm pack --dry-run

风险:
- 中：版本、tag、registry 三者必须保持一致；失败时按本 skill 的恢复流程处理。
EOF
)"
```

5. Tag:

```bash
git tag -a vX.Y.Z -m "$(cat <<'EOF'
Release vX.Y.Z - <brief title>

Main changes:
- Change 1
- Change 2

Full changelog: https://github.com/Dimon94/cc-devflow/blob/main/CHANGELOG.md
EOF
)"
```

6. Verify commit and tag:

```bash
git log --oneline -1
git show vX.Y.Z
```

7. Push and publish:

```bash
git push origin "HEAD:${release_target_branch}"
git push origin vX.Y.Z
npm publish --dry-run
npm publish
npm view cc-devflow version
npx --yes cc-devflow@X.Y.Z --help
```

## Failure Policy

- `git push` failure: keep local commit/tag, capture the remote error, and retry the exact branch/tag push when network/auth recovers.
- `npm publish --dry-run` failure: do not publish.
- `npm publish` failure: capture registry output; do not delete local commit/tag to hide the failed release state.
- Published critical bug within npm's allowed unpublish window:

```bash
npm unpublish cc-devflow@X.Y.Z
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z
git revert HEAD
```

After npm's unpublish window, publish a new patch instead.

## Exit Criteria

- `package.json`, `package-lock.json`, `CHANGELOG.md`, release commit, tag, and npm registry version match.
- Release commit and annotated tag point to the final changelog.
- Branch and tag push succeeded, or the remote blocker is captured.
- `npm publish` succeeded, or the registry blocker is captured after dry-run prevented real publish.
- Post-publish smoke used `npm view` and `npx --yes cc-devflow@X.Y.Z --help`.
