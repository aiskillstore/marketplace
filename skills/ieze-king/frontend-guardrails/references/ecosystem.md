# Ecosystem — compose, don't reinvent

This skill is opinionated *policy*. It deliberately does not re-implement work that mature tools, MCP servers, or companion skills already do well. When a task touches one of the areas below, prefer detecting and using the existing solution over writing your own version. Recommend installing what's missing rather than substituting prose for a real tool.

## Referencing third-party work responsibly
This skill **recommends, it does not warrant.** Anything it points at runs in the user's project, so:
- Only reference reputable, verifiable sources — official Anthropic skills, verified-publisher or high-adoption community tools — never an obscure or unmaintained one.
- Never silently auto-install or auto-adopt. Surface the recommendation and let a human review and approve it.
- Do not pretend to be a security scanner. Route security judgments to the dedicated tools below rather than asserting something is "safe."
- When this is published, ship a standard open-source LICENSE with a no-warranty clause; recommendations are suggestions the adopter is responsible for vetting.

## Behavioral discipline (principle 16)
The built-in `/code-review` skill (Claude Code) audits a diff for correctness bugs, unnecessary complexity, and scope creep — the exact failure modes principle 16 targets. Run it before declaring any non-trivial task done. This skill keeps only a thin behavioral summary so it stands alone when that companion isn't present.

## Visual design quality & scaffolding (principles 3, 5)
The official `frontend-design` skill produces distinctive, production-grade UI and design-token-driven layouts. Use it for creative direction and scaffolding; this skill governs consistency and discipline around whatever it generates.

## UI quality gate / audit (principles 3, 5, 10, 11)
The `ui-ux-pro-max` skill audits already-built UI against a broad rule set covering accessibility, performance, spacing, color systems, and visual hierarchy — things ESLint can't see. Run it as an end-of-session quality gate, not a generator. Install via the Claude Code marketplace: `/plugin install ui-ux-pro-max@ui-ux-pro-max`.

## Accessibility (principle 11)
- A dedicated WCAG audit skill/agent scans for missing alt text, heading order, contrast, ARIA, and keyboard issues.
- In the linter: `eslint-plugin-jsx-a11y` (or the framework equivalent) catches a11y problems at write time.
Prefer these over manual prose review for anything beyond the basics in `references/accessibility.md`.

## Current, version-accurate APIs & docs (principles 9, 16)
The Context7 MCP pulls up-to-date, version-specific library documentation into context, which directly prevents hallucinated or outdated APIs. Recommended as the default companion MCP for this skill (and a natural thing to bundle if this is shipped as a plugin).

## Linting & formatting (principles 1, 2, 3, 13, 16)
ESLint / Biome / Oxlint plus Prettier (or a multi-provider setup like Ultracite) enforce consistency, catch many correctness bugs, and remove debug artifacts deterministically. The skill's job is to ensure these run and are respected — not to restate their rules.

## Performance & SEO auditing (principles 10, 14)
Lighthouse / web-vitals tooling measures Core Web Vitals, performance budgets, and SEO/meta coverage objectively. Prefer real measurement over guessing.

## Design system & tokens (principle 3)
A design-system-engineer agent (tokens, primitives, Storybook) can establish the token system this skill then enforces consistent use of.

## Visual verification (principle 16)
Claude Preview / Claude in Chrome can open the built UI, walk its states, and screenshot it — turning "I think it works" into "I saw it work." Use to verify rendering and interaction.

## Testing (principle 16)
Use the project's existing framework (Vitest, Jest, Playwright, Testing Library, Cypress) rather than introducing a new one. Match the project's conventions.

## Code review & supply-chain security (principles 9, 16)
The skill should not judge safety itself — it routes to tools built for it:
- **CodeRabbit** — AI code review on pull requests; flags bugs, vulnerabilities, and risky patterns before merge. A strong final gate on anything that lands, generated or referenced.
- **Dependency / supply-chain scanning** — `npm audit` (built in) for known CVEs; **Socket** for malicious-package and supply-chain detection; **Snyk** for deeper vulnerability and license scanning; **Dependabot** for ongoing automated alerts and update PRs.
- Run a dependency scan whenever a package is added, and treat a failed audit as a blocker, not a warning to ignore.

## Vetting referenced skills / MCPs
Before recommending a skill, plugin, or MCP server:
- Prefer official or verified-publisher sources; for community ones, check adoption (stars/installs), recent maintenance, and an open license.
- MCP servers can execute code and access data — review the permissions they request and prefer audited, reputable ones. Never recommend one that asks for more access than the task needs.
- Leave the final adopt/decline decision to the human.


## How to apply this file
1. Identify which area the current task touches.
2. Check whether the project already has the relevant tool/skill installed and use it.
3. If it's absent and would clearly help, recommend installing it (with the exact command if known) rather than hand-rolling a weaker substitute.
4. Fall back to this skill's inline guidance only when no suitable tool is available.
