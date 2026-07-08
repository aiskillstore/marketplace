# npm-release Skill Changelog

## v1.1.0 - 2026-05-18

- add an npm-release checklist contract for registry identity, version parity, changelog, dry-run, tag, publish, and post-publish verification pause points

## v1.0.0 - 2026-04-10

- 为 `npm-release` 补齐 `version` frontmatter，纳入仓库维护类 skill 契约。
- 新增本地 `PLAYBOOK.md` 与 skill changelog，避免发布流程说明继续漂移成孤儿文件。
- 明确 `npm whoami` 失败属于发布阻断条件，要求在真实 `npm publish` 前先验证 registry 身份。
