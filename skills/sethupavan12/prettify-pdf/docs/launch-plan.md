# Launch Plan

This project is easiest to explain when the promise is concrete:

> Make PDFs beautiful without breaking the facts.

## Positioning

Short description:

```text
Agent Skill for prettifying PDFs without breaking IDs, dates, amounts, barcodes, QR codes, seals, signatures, or source meaning.
```

Longer pitch:

```text
prettify-pdf is a local-first Agent Skill that helps AI agents redesign receipts, invoices, appointments, tickets, forms, resumes, and reports while preserving high-stakes source data. It adds a strict visual QA gate so text extraction passing is not enough: the final PDF must render cleanly, preserve machine-readable assets, and match the original facts.
```

## GitHub Topics

Add these repository topics:

- `agent-skills`
- `skill-md`
- `pdf`
- `pdf-tools`
- `document-ai`
- `local-first`
- `privacy`
- `codex`
- `claude-code`
- `openclaw`
- `opencode`
- `llm-tools`

## Launch Assets

Use synthetic files only.

Create:

- A fake receipt before/after.
- A fake appointment confirmation before/after.
- A screenshot showing the visual audit catching a clipped timestamp or changed barcode.
- A short GIF or video: original PDF -> redesigned PDF -> source/final audit.

## README Hooks

Lead with failure avoidance:

- "Pretty PDFs are easy. Pretty PDFs that still scan, verify, and preserve every ID are harder."
- "Text extraction can pass while the rendered PDF is visually wrong."
- "For receipts, invoices, government forms, and appointment confirmations where a wrong digit matters."

## Announcement Draft

```text
I open-sourced prettify-pdf, a provider-neutral Agent Skill for redesigning PDFs without breaking critical data.

It focuses on receipts, invoices, appointments, forms, tickets, resumes, and reports where IDs, timestamps, totals, barcodes, QR codes, seals, and labels must survive exactly.

The key idea: the agent must render and visually audit the final PDF against the original. Text extraction passing is not enough.

Repo: https://github.com/sethupavan12/prettify-pdf
```

## Where To Share

- GitHub README and pinned repo.
- skills.sh: ask users to install with `npx skills add sethupavan12/prettify-pdf`.
- agentskill.sh: submit `https://github.com/sethupavan12/prettify-pdf` at `https://agentskill.sh/submit`.
- ClawHub/OpenClaw: publish with `clawhub skill publish . --slug prettify-pdf --name "Prettify PDF" --version 0.1.0`.
- Skillstore, SkillUse, mdskills.ai, skillsdir.dev, and OmniSkill: use the repository URL and the metadata in `docs/publishing-directories.md`.
- Hacker News "Show HN" with a synthetic before/after.
- Reddit communities that allow tools: `r/LocalLLaMA`, `r/selfhosted`, `r/pdf`, `r/opensource`, `r/ClaudeAI`, `r/AI_Agents`.
- X/LinkedIn thread with the visual failure story and fixed result.
- Agent-skill marketplaces or directories as they become available.

## Maintainer Loop

For the first week after launch:

- Respond quickly to issues.
- Ask users for synthetic examples, not private PDFs.
- Turn repeated bugs into eval prompts.
- Add small releases with changelog entries.
- Keep the repo focused on a pure skill, not a hosted app.
