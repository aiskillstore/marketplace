# Agent Skill Trust Check

Static pre-install trust check for agent skills, `SKILL.md` files, and skill marketplace listings.

Agent skill marketplaces are useful, but installing a skill is still a trust decision. This repo provides a small local scanner and a portable `SKILL.md` review guide for checking public skill text before it gets installed.

## Run With npm

```bash
npx --yes agent-skill-trust-check@latest ./SKILL.md --json
```

## Run From Source

```bash
git clone https://github.com/TateLyman/agent-skill-trust-check.git
cd agent-skill-trust-check
npm run check
node bin/agent-skill-trust-check.js ./SKILL.md
```

Run against a public GitHub/raw/Gist URL from the checkout:

```bash
node bin/agent-skill-trust-check.js https://raw.githubusercontent.com/owner/repo/main/SKILL.md --json
```

Run the marketplace-safe stdin wrapper:

```bash
node bin/agent-skill-trust-check-stdin.js < ./SKILL.md
```

## What It Checks

- Shell/process execution.
- Destructive command patterns.
- Secret or credential access.
- Wallet/payment/signing behavior.
- Remote network/webhook output.
- Persistence/background behavior.
- Prompt-boundary language.
- Missing provenance signals such as license, tests, permissions, versioning, source, and uninstall notes.

## Output

The CLI returns:

- `verdict`
- `risk_score`
- `findings`
- `positives`
- `missing_signals`
- `patch_order`

The stdin wrapper always returns compact JSON and does not read local files, fetch URLs, or spawn subprocesses. It is the safer entry point for agent-skill marketplaces that call tools with stdin/stdout contracts.

## Marketplace Review

For a paid marketplace-grade pass, use:

https://orkai.ai/skills/agent-skill-trust-check

For private review work:

https://tateprograms.com/payments.html

For creator marketplace submission copy, see:

`marketplace/agensi-listing.md`

Additional marketplace-ready skill files:

- `marketplace/paperclip-skill.md` for Paperclip Skills publish flow.
- `marketplace/skillshop-skill.md` for SkillShop private-repo listings.

## Boundary

This scanner is a static text pass. It does not execute the target skill and it does not replace sandboxing, code review, dependency review, or runtime monitoring.

## License

MIT
