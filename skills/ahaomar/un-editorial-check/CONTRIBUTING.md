# Contributing

Node.js 18 or later is required. Keep runtime dependencies at zero. Add a failing regression before changing rule, profile, CLI or compatibility behaviour, then run `npm test` and `npm run check:syntax`.

Before release, also run `npm run check:portability`, parse all maintained JSON, run `npm pack --dry-run`, exercise the direct and installed CLIs with `--self-scan --quiet`, and run `git diff --check`. No lockfile is needed because the package has no dependencies. Record institutional source checks and limitations in `MAINTAINING.md` and the rule catalogue.

## Skill portability

The repository-root `SKILL.md` is the canonical public definition. Do not submit copied `SKILL.md` files for individual hosts or recursive symbolic links. Keep its frontmatter to `name`, `description`, `license`, `compatibility` and string-valued `metadata`; keep the name equal to the package and directory identity.

A new host or changed host adapter requires official-documentation verification, an exact source URL and verification date in `COMPATIBILITY.md`, a fixture or portability test, and matching updates to the README matrix. State clearly whether support is native host discovery, `npx skills` installation, or a rules/manual adapter. Optional metadata such as `agents/openai.yaml` must not duplicate or override the canonical workflow.

Do not include private content, credentials, machine-specific configuration, generated tarballs or installed skill copies in fixtures or commits. Follow `CODE_OF_CONDUCT.md`; report security issues through `SECURITY.md`.
