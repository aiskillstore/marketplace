# NPM Release Playbook

## Core Rules

1. 先定版本级别，再改版本号，不允许边发边想。
2. 先写 `CHANGELOG.md`，再 bump `package.json` / `package-lock.json`。
3. commit、tag、push、publish 顺序固定，不能乱。
4. `npm whoami` 失败时停止真实发布，只保留本地准备结果。
5. 发布失败时优先保住版本一致性，不要制造半发布状态。
6. 禁止自动 `checkout` / `switch` 到 `main`；当前 worktree 必须已经是用户确认的发布目标。
7. release commit 前运行 `../do-not-repeat-yourself/SKILL.md`，确认版本、CHANGELOG、package、tag 文案没有重复真相源漂移。

## Standard Flow

1. `git status --short`
2. `git branch --show-current`
3. `npm whoami`
4. 更新 `CHANGELOG.md`
5. `npm version patch|minor|major --no-git-tag-version`
6. 运行最小必要验证
7. 运行 `../do-not-repeat-yourself/SKILL.md`
8. `git add`
9. `git commit`
10. `git tag -a`
11. `git push origin "HEAD:<release-target-branch>"`
12. `git push origin vX.Y.Z`
13. `npm publish --dry-run`
14. `npm publish`
15. `npm view cc-devflow version`

## Failure Policy

- git push 失败：保留 commit 和 tag，记录远程失败原因
- npm publish dry-run 失败：禁止真实发布
- npm publish 失败：记录 registry 返回值，不回滚已创建的 commit/tag，避免掩盖真实状态
