# Marketing Mindset

> **The marketing OS for AI agents — think like a marketer first, get tactics as the output.** Not another bag of CRO/SEO/copywriting tricks. This is how a 15-year B2B marketer *decides*, so an agent gives a real opinion instead of a template.

[![Use in Claude Code](https://img.shields.io/badge/Use%20in-Claude%20Code-orange)](SKILL.md)
[![Add to Cursor](https://img.shields.io/badge/Add%20to-Cursor-blue)](.cursorrules)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-6e40c9)](AGENTS.md)
[![ChatGPT](https://img.shields.io/badge/ChatGPT-SKILL.lite.md-10a37f)](SKILL.lite.md)
[![Grok](https://img.shields.io/badge/Grok-SKILL.md-111111)](SKILL.md)

![GitHub Repo stars](https://img.shields.io/github/stars/axelfreeman/marketing-mindset?style=social)
![views](https://komarev.com/ghpvc/?username=axelfreeman&repo=marketing-mindset&label=views&style=flat-square&color=2563eb)

---

### The gap this fills

Every other "marketing skill" for AI agents hands over tactics. Nobody packages **how a marketer thinks**. When an agent needs to decide *should I do X to get Y*, *where do I get my first customer*, or *is this idea worth it*, tactics don't answer. This skill does.

### See it work

[examples/demo-transcript.md](examples/demo-transcript.md) — one request in ("SaaS for finance, 0 customers"), a sharp 3-month plan out.

### The problem

Founders and solo operators can generate code, not content. "How do I do marketing" is genuinely unclear to them. They need an agent that gives honest, non-generic marketing judgment — not a template.

### The fix

Five principles and a decision framework, distilled from 15 years of hands-on B2B internet marketing:

1. **Don't learn marketing from stale sources** — skip the first Google results and cached LLM doctrine
2. **Three-month horizon** — no 2-year cycles; be useful within 3 months
3. **The user has the right to make the first move** — don't block bold or hacky first steps
4. **Every hypothesis must be testable fast** — any teammate can run the test
5. **Marketing runs ahead of the product** — ship the landing page before the build

Plus: competitors as the source of truth, three keys to the human, and the client stages (first client by hand and free → 2–10 by copying competitors).

### The metaphors (share these)

- 🍔 **The McDonald's Burger** — photograph the product better than it is
- 🧬 **Think like a cancer cell** — when nothing else applies, multiply
- 🚫 **The stop-list** — why Product Hunt is lying to you

### Who it's for

- **AI agents** (Claude Code, Cursor, ChatGPT — any agent that reads SKILL.md)
- **Founders & solo operators** selling a service that can't be touched but is needed right now
- **Indie hackers & solopreneurs** shipping a SaaS alone
- **Freelancers** (dev, design, writing) hunting for client #1
- **Developers** who can ship code but freeze on "how do I get customers"
- **Agency owners & fractional CMOs** — encode your judgment so juniors stop producing generic work
- **Course creators & info-product sellers** — the "can't be touched, needed now" market
- **Product managers** validating an idea before writing code
- **Prompt engineers** studying how to give an AI a personality with hard boundaries
- **VC, investors & venture scouts** — stress-test marketing claims in due diligence
- **Open-source maintainers** — grow adoption of a project
- **Startup accelerators & incubators** — a repeatable framework for portfolio companies
- **SDRs & sales engineers** — own their own outreach and positioning

### Tested on

Verified to load correctly on these models before release — each adapter matches the target's native syntax:

| Model | File to use |
|---|---|
| **Claude Code** | `SKILL.md` → `.claude/skills/marketing-mindset/` |
| **Cursor** | `.cursorrules` |
| **Codex** | `AGENTS.md` + `SKILL.md` |
| **ChatGPT (Custom GPT)** | paste `SKILL.lite.md` as instructions |
| **Grok / xAI** | `SKILL.md` (system prompt) |
| **Qwen (qwen3)** | `SKILL.lite.md` |
| **DeepSeek (V3 / Flash)** | `SKILL.lite.md` |
| **Llama (Meta)** | `SKILL.md` |
| **Mistral** | `SKILL.md` |
| **Gemini** | `SKILL.md` |
| **Hermes (Nous)** | `SKILL.md` |

### What you actually get

Working through this skill ends in concrete deliverables — a competitor analysis, three outbound angles, and sharper positioning (see the [demo](examples/demo-transcript.md)). The mindset is the input; the tactics are the output.

### Install

```bash
npx skills add axelfreeman/marketing-mindset
```

**Low-context or weaker models?** Use the compact [`SKILL.lite.md`](SKILL.lite.md) — the same mindset compressed to the essentials.

### The first-client gate

```bash
python scripts/first-client-gate.py
```

One honest question before you start: do you have your first client yet? If the answer isn't "me," the skill waits.

### Spread the word

If it works, star it and share it. The network effect compounds.

### Keywords

marketing mindset, marketing operator mindset, how a marketer thinks, marketing skills for AI agents, growth marketing, first customers, B2B lead generation, positioning, launch, copywriting, cold outreach, SaaS marketing

### A note on "growth hacks" and "embellishing"

"Growth hacks", "embellish", and "frame case studies" mean marketing positioning and copywriting — presenting the product's value in its best, boldest light — not fraud, fabricated testimonials, or deceiving users. Bold marketing, always legal.

### Author

Written by Axel Freeman, a B2B marketer with 15 years of validated experience across B2B SaaS. Not a content farm — the operator's own method.

### License

MIT
