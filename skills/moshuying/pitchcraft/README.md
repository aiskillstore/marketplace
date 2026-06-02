# pitchcraft （汇报.Skill）

**Languages:** [English](README.md) · [简体中文](README.zh-CN.md)

![License: Apache License 2.0](https://img.shields.io/badge/License-apache2.0-blue.svg)

A Claude Agent Skill for structured persuasion—**your work deserves to be seen.**

Writing good code is a skill. Getting leaders to understand what you shipped, trust your judgment, and act on your recommendations is a bigger one.

Most people only practice the first.

pitchcraft is a **structured persuasion framework** for project kickoffs, status updates, wrap-ups, investor pitches, and solution selling. It is not a writing template—it helps you translate what you built into language your audience understands, trusts, and acts on.

**Influence is not innate—it can be structured.**

---

## Why this project exists

In the AI era, execution is commoditized; persuasion compounds. AI can write code, but explaining _why now_, _why us_, and _why this matters_ to decision-makers still needs you—AI can make you better at it.

pitchcraft turns that from a gift into a **repeatable workflow**:

> One persuasion structure + scenario templates + AI-driven material intake + pre-submit checklist.

## How it differs from “AI weekly report” tools

|           | Generic AI reports           | pitchcraft                                                           |
| --------- | ---------------------------- | -------------------------------------------------------------------- |
| Scenarios | Weekly/monthly activity logs | Kickoff, status, wrap-up, pitch, solution selling                    |
| Goal      | Record work                  | Persuade and secure support                                          |
| AI role   | Fill-in-the-blank            | Ask what’s missing, who’s in the room, what they care about          |
| Core idea | “What we did”                | “Why they should care”                                               |
| Memory    | None                         | Leader context, business positioning, format prefs (when configured) |

---

## Star History

<a href="https://www.star-history.com/?repos=moshuying%2Fpitchcraft&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=moshuying/pitchcraft&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=moshuying/pitchcraft&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=moshuying/pitchcraft&type=date&legend=top-left" />
 </picture>
</a>

## Framework: 5-part persuasion structure

Every scenario shares the same backbone; section emphasis changes:

```
Hook → Context → Proposal → Evidence → Ask
```

| Scenario         | Hook focus              | Evidence focus      | Ask                     |
| ---------------- | ----------------------- | ------------------- | ----------------------- |
| Project kickoff  | Pain / opportunity      | Why us (moat)       | Resources, approval     |
| Status update    | Headline takeaway       | Key metrics         | Decisions, coordination |
| Wrap-up / annual | Goal attainment         | Quantified outcomes | Next phase or handoff   |
| Investor pitch   | Market space            | Moat + traction     | Investment, partnership |
| Solution selling | Customer pain alignment | Cases + data        | Deal, next steps        |

---

## Install

### npm / npx

```bash
# Global (~/.claude/skills/pitchcraft/)
npm install -g pitchcraft
```

Also works with the [Vercel skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add moshuying/pitchcraft -a claude-code -a cursor -y
```

Publish: `npm publish` (scoped: set `"name": "@moshuying/pitchcraft"` if `pitchcraft` is taken on npm).

### Claude Code

```
/plugin marketplace add moshuying/pitchcraft
/plugin install pitchcraft
```

Or tell your agent:

```
Install pitchcraft for me: https://github.com/moshuying/pitchcraft
```

Restart, then use a trigger phrase below. The plugin installs the English `SKILL.md` by default. For Chinese, copy `SKILL.zh-CN.md` over `SKILL.md` (see **Localization**).

### SkillsMP / GitHub discovery

[SkillsMP](https://skillsmp.com) auto-indexes repos with a root `SKILL.md` and valid frontmatter (`name`, `description`). This repo keeps root `SKILL.md` in sync with `.claude/skills/pitchcraft/SKILL.md` for crawlers and the Claude Code plugin.

On GitHub: **Settings → General → Topics** → add `claude-skills` or `claude-code-skill` (daily sync).

### Cursor / Codex / other AI tools

| Tool                 | How                                                                      |
| -------------------- | ------------------------------------------------------------------------ |
| Cursor               | Paste `prompts/universal.md` (or `universal.zh-CN.md`) into Rules for AI |
| Codex CLI            | Same content as system instructions                                      |
| ChatGPT / Claude web | Paste the prompt file into the chat                                      |

### Trigger phrases

**English**

- **status update** / **briefing** — cross-level update, 15 minutes to set the tone
- **project kickoff** — persuade leadership to approve and fund
- **milestone review** — sync progress, keep investment
- **wrap-up** / **retrospective** — goals, outcomes, assets
- **pitch** / **fundraising** — investors or partners
- **solution selling** — customer decision-makers

**中文（使用 `SKILL.zh-CN.md` 或 `universal.zh-CN.md` 时）**

- **汇报** / **简报** · **立项汇报** · **阶段汇报** · **结项总结** · **路演** · **方案推销**

---

## How it helps

pitchcraft is not a magic wand. The workflow:

1. **Pick a scenario** — kickoff, status, wrap-up, pitch, or solution selling
2. **Intake materials** — AI checks completeness and asks for gaps
3. **Understand the audience** — role, familiarity, concerns shape the draft
4. **Draft to structure** — 5-part framework, stay on message
5. **Run the checklist** — sourced metrics? risks with judgment?

You focus on substance; structure and checks are handled by the framework and AI.

---

## Localization

| File                                       | Language                 |
| ------------------------------------------ | ------------------------ |
| `README.md`                                | English (default)        |
| `README.zh-CN.md`                          | 简体中文                 |
| `prompts/universal.md`                     | English                  |
| `prompts/universal.zh-CN.md`               | 简体中文                 |
| `.claude/skills/pitchcraft/SKILL.md`       | English (plugin default) |
| `.claude/skills/pitchcraft/SKILL.zh-CN.md` | 简体中文                 |

---

## Repository layout

```
pitchcraft/
├── SKILL.md                      # Root skill (SkillsMP / lazy-load index)
├── package.json                  # npm install → .claude/skills/pitchcraft/
├── scripts/install.js
├── .claude/
│   └── skills/pitchcraft/
│       ├── SKILL.md              # English (plugin install source)
│       └── SKILL.zh-CN.md
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── commands/
│   ├── pitchcraft.md
│   └── pitchcraft.zh-CN.md
├── prompts/
│   ├── universal.md
│   └── universal.zh-CN.md
├── README.md
├── README.zh-CN.md
├── LICENSE
└── .gitignore
```

---

## Further reading

Ideas drawn from:

- Malcolm Gladwell — _Blink_: first impressions; the first 10 seconds of a briefing matter.
- Malcolm Gladwell — _The Tipping Point_: how ideas spread; persuasion lowers acceptance friction.
- Chip Heath & Dan Heath — _Made to Stick_: SUCCESs (Simple, Unexpected, Concrete, Credible, Emotional, Stories).
- Robert Cialdini — _Influence_: reciprocity, commitment, social proof, liking, authority, scarcity.
- Nancy Duarte — _Resonate_: tension between “what is” and “what could be.”
- Barbara Minto — _The Pyramid Principle_: conclusion first, MECE, hierarchy.
- Anne-Laure Le Cunff — _Tiny Experiments_: decisions and progress under uncertainty.

---

## What it is / isn’t

### Not

- ❌ “AI writes my weekly status” — activity logs are out of scope
- ❌ A repeat of _The Pyramid Principle_ — concrete, executable templates, not principles only
- ❌ Flattery or scripts — the goal is accurate understanding of your work

### Is

- ✅ Structured persuasion for “limited time, specific audience, clear ask”
- ✅ One framework, five scenario instances—learn kickoff, reuse for pitches
- ✅ Checklists so you don’t skip metrics, risks, or audience fit
- ✅ In the AI era, make execution visible, credible, and amplified

---

## Status

**v1.0** — core framework, 5 scenario templates, workflow, checklist, cross-platform install, EN + zh-CN

**Planned:** Japanese / Korean; web writing assistant; more scenarios (incident review, tech review, OKR alignment)

---

## License

[Apache 2.0](LICENSE).

---

## Author

Created by [@jiujiangliu](https://github.com/moshuying). Refined through real executive and stakeholder briefings.
