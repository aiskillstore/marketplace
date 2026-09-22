# Birdview 0.3.0

[中文](release-notes-0.3.0.zh.md)

Birdview now defaults to on-demand invocation and asks users to confirm the displayed map and change plan before implementation.

- Select Birdview using `/skills` or `$birdview` in Codex, or `/birdview` in Claude Code. Other hosts use their own skill selector or an explicit request.
- Automatic mode remains opt-in through `mode auto`. New projects default to `on-demand`; setup preserves existing auto, on-demand and off settings.
- In either active mode, the agent prepares and displays the map, affected files, constraints and verification plan, then waits for confirmation. Confirmation of the same plan is reused; material scope changes require renewed confirmation. Explicit task-specific waivers take precedence.
- Constraint discovery, reviewed rule graphs, source evidence, history and architecture integration now have typed contracts and rendering flows. Collection and applicability remain distinct from verified compliance.
- TypeScript sources, browser bundles, generated schemas and installation checks now cover the distributed implementation. Generated JavaScript remains included so skill users do not need to compile it.

Install the complete source bundle following the [installation guide](installation.md), then run `npm ci` and `node scripts/birdview.mjs doctor` in the skill directory. After upgrading, run `setup --project <project-root>` for configured projects to refresh managed instructions while preserving their mode. Use `mode on-demand` to switch an existing auto project to manual invocation. Start a fresh agent task to avoid cached instructions. Preserve local customizations. Distribution is through GitHub, not npm.

Release verification covers type checking, generated artifact consistency, unit tests, example validation, demo generation, Chromium browser suites, paired documentation and clean committed-source installation. The release procedure records actual results before publication.

Birdview shows agent-declared snapshots. The confirmation step is an agent instruction, not a filesystem lock or an approval button enforced by the HTML viewer. Real-session invocation and confirmation behavior across all supported agents has not been independently verified. No private DeepSeek source catalog or local preview is included in this release.
