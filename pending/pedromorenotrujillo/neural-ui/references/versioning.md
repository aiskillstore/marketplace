# Version maintenance

This installed skill is a snapshot for 2.0.1. Before applying it to another version, inspect the actual package exports, declarations and changelog; do not claim coverage for an untested release.

Maintainers regenerate API references from the installed npm tarball's declarations using the Neural AI repository's api:generate command. api:check compares exports, full declaration hashes, input/output aliases, domain declarations, public tokens and style hashes with the reviewed snapshot. Any change requires review; regeneration alone does not certify compatibility.

For a new release, maintainers update the exact package pin and lockfile, capture npm integrity and the matching source commit, review changes to the upstream support policy, regenerate, and run structural/import checks, negative tests, strict Angular builds and browser scenarios. Review the short authored references only where behavioral contracts changed. The generated API catalog does not require hand-editing every component.

Keep supported version metadata, examples and evidence consistent. Older versions are mentioned only in migration or historical evidence, never as active install targets. Keep Native imports excluded. Remove stale generated entrypoint files when an entrypoint disappears; do not retain an obsolete reference as a compatibility alias.

Agent specifications can change independently of Neural. Recheck [Codex skill locations](https://developers.openai.com/codex/skills/), [Claude Code skills](https://code.claude.com/docs/en/skills) and [Agent Skills format](https://agentskills.io/specification) when changing packaging. Portable frontmatter, relative references and complete directory copying avoid unnecessary per-agent forks.

After deterministic checks, run the separate agent evaluation prompts in the repository's tests/agent-scenarios.md with actual Codex and Claude Code sessions. Record agent versions, output, compilation and interaction results. Never mark these evaluations passed just because structural validation succeeded.
