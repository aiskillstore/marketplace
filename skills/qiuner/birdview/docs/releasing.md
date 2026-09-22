# Release Checklist

[中文](releasing.zh.md)

1. Review the diff and choose the release version. Keep `package.json`, the root package entry in `package-lock.json`, README version badges and release notes consistent.
2. Run `npm ci`, `npm run typecheck`, `npm run check:build`, `npm test`, `npm run validate:examples` and `node scripts/check-docs.mjs`. Review translated documentation before updating its confirmation record.
3. Run `npm run build:demo` and inspect the generated diff. Open the demo in both languages; check architecture, changes, comparison, guide and inspector within one screen on desktop and mobile. Install Chromium with `npx playwright install chromium`, then run `npm run test:browser` (viewer, guide, constraints, viewport and website); record any skipped checks.
4. Include `LICENSE` and `THIRD_PARTY_NOTICES` in distributions. Check that screenshots, examples and attachments contain no private data. Preserve third-party notices in generated HTML when distributing it separately.
5. Write release notes covering changes, installation, verification and known limitations. Birdview shows agent-declared activity; it does not independently observe edits or enforce the pre-edit workflow.
6. After explicit authorization, commit the reviewed changes, create the version tag and publish the GitHub release. Run `npm run check:install` against the committed release candidate before tagging. Check the tag and downloadable contents. GitHub release preparation does not enable npm publication: the package remains `private`.

GitHub offers bilingual bug and feature forms. The default PR template is English; use the Chinese companion when preferred. These platform templates are not executable skill instructions.
