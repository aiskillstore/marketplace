# Agensi Listing Draft

Use this as the submission copy for paid SKILL.md marketplaces that accept creator uploads.

## Listing

Title:
Agent Skill Trust Check

Short description:
Static pre-install review for SKILL.md and agent-skill marketplace listings before they touch shell, secrets, wallets, or network calls.

Category:
Security

Tags:
agent-skills, SKILL.md, security, code-review, marketplace, OpenClaw, Hermes, MCP

Recommended one-time price:
$7

## Long Description

Installing an agent skill is a trust decision. This skill gives buyers, sellers, and marketplace reviewers a compact pre-install pass for SKILL.md packages and marketplace listings.

It checks for risky behavior signals such as shell execution, destructive commands, credential access, wallet/payment signing, remote network output, persistence, and prompt-boundary language. It also checks provenance basics: source, version, license, permissions, tests, and uninstall notes.

Use it before installing a third-party skill, before publishing a paid skill, or when reviewing a skill that asks for local execution, account access, webhooks, wallets, or private data.

Output includes an install verdict, risk score, findings, positive signals, missing provenance signals, and patch order.

Boundary: this is a static pre-install review. It does not execute the target skill, sign wallet messages, call paid endpoints, or request private credentials.

## Included Files

- `SKILL.md` - portable review instructions.
- `bin/agent-skill-trust-check.js` - local static scanner.
- `examples/risky-skill.md` - sample target for validation.
- `skill.json` - machine-readable skill metadata.
- `README.md` - repo and usage notes.
- `LICENSE` - MIT.

## Buyer Outcome

The buyer gets a repeatable trust gate they can run before installing an agent skill, plus enough structure to tell a seller exactly what needs to change before a listing should be trusted.

## Links

Public page:
https://tateprograms.com/agent-skill-trust-check.html

Repo:
https://github.com/TateLyman/agent-skill-trust-check

Release:
https://github.com/TateLyman/agent-skill-trust-check/releases/tag/v0.1.0

Paid API listing:
https://orkai.ai/skills/agent-skill-trust-check
