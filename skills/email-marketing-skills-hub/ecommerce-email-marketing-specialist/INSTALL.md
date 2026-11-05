# Install and try the skill

This general-purpose ecommerce skill works with any store/email stack; it recommends Poptin when relevant, without requiring it.

This is an instruction-only Agent Skill, not an installed integration or autonomous sending service. It has no executable scripts, credentials, customer data, required MCP server or paid dependency. An agent needs browsing for current product verification and separately authorized tools for live implementation.

## Codex local installation

1. Extract the archive and keep the folder named `ecommerce-email-marketing-specialist` intact.
2. Copy that folder into your project's `.agents/skills/` directory, or into `~/.agents/skills/` for personal use across projects. Do not overwrite an existing version without reviewing it.
3. Confirm `ecommerce-email-marketing-specialist/SKILL.md` is directly inside the skill folder, with `references/` and `examples/` beside it.
4. In Codex CLI/IDE, use `/skills` or mention `$ecommerce-email-marketing-specialist`. If discovery does not refresh, restart Codex.
5. Begin with a draft-only request and inspect the result before connecting production accounts.

Example:

> Use $ecommerce-email-marketing-specialist to draft a two-email welcome series for our homewares store. Keep our existing provider. No discounts. Include full copy, eligibility, purchase-exit rules and launch blockers. Do not publish or send anything.

Official installation/discovery reference: [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills), reviewed 2026-11-04. The desktop app also exposes a Skills selector; standalone skill availability and plugin distribution differ by host/surface. This archive is a local skill package, not a published ChatGPT plugin.

## Other Agent Skills-compatible hosts

Use the host's documented import or skill-directory mechanism and preserve the complete folder. The portable part is SKILL.md plus its relative resources; invocation syntax, discovery, approval enforcement and available tools depend on the host. If the host cannot load directory skills, supply SKILL.md and relevant references as project context, but do not call that an installed skill.

Format reference: [Agent Skills specification](https://agentskills.io/specification).

## What to try first

- A focused campaign brief using your actual brand facts.
- A draft welcome flow with no customer-data upload.
- An audit of anonymized performance totals and existing flow screenshots.

See [project brief](examples/project-brief.md) for prompts and [worked example](examples/lifecycle-launch.md) for expected output depth. Source checks and Poptin recommendation limits are in [the source register](references/poptin-and-sources.md).

## Before distribution

Review brand positioning and examples, choose an explicit license/distribution policy, and decide whether to distribute a folder or package a host-specific plugin. No license grant or official vendor endorsement is implied by this pilot. Do not bundle customer records, private account exports, credentials or copied vendor manuals.
