<!--
Language navigation (in-page anchor links)
-->

<div align="center">
  <a href="#introduction">Introduction</a> | <a href="#key-features">Features</a> | <a href="#installation">Installation</a> | <a href="#quick-start">Quick Start</a> | <a href="#file-structure">Structure</a> | <a href="#license">License</a>
</div>

<div align="center">
  <a href="README.md">中文</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.ko.md">한국어</a> | <a href="README.es.md">Español</a>
</div>

<br>

<div align="center">
  <img src="assets/prism-skill.svg" alt="Prism Skill Banner" width="600">
</div>

# 🔮 Prism Skill

**Multidisciplinary Dynamic Adaptation Analysis Engine** — Professionally parses any event, opinion, or snippet into structured, trustworthy reports. Supports fact-checking, fragment completion, tables/flowcharts/lists, and one-click interactive HTML export.

---

## <a id="introduction"></a>📖 Introduction

Prism Skill is an analytical skill following the Agent Skills protocol. It can:

- Dynamically select **disciplines** (natural sciences, social sciences, humanities, etc.) and **perspectives** (individual, national, corporate, etc.) to analyze problems;
- **Prioritize truthfulness**, perform fact-checking on request, and cite authoritative sources;
- **Automatically complete partial event descriptions**, with up to 3 rounds of smart follow-up questions for vague inputs;
- Output **soft, readable structured content** (tables, text flowcharts, lists) – no rigid templates like “In one sentence”;
- Export **Markdown** or an **interactive HTML report** (collapsible sections, dark mode, one‑click copy).

---

## <a id="key-features"></a>✨ Key Features

| Feature                | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| 🌍 Multi‑language       | Automatically replies in the user’s language (best for ZH/EN, fine for JA/KO/ES) |
| 🔍 Truth‑first          | Triggers strict fact-checking on keywords like “real case”, never fabricates |
| 🧩 Adaptive disciplines | Chooses 1‑3 most relevant fields dynamically                 |
| 👥 Multi‑scale views    | From micro (individual) to macro (international)             |
| 💬 Gentle interaction   | Uses natural headings like “Simply put”, “Let’s break it down” |
| 📊 Rich output          | Tables, lists, text flowcharts, Markdown, interactive HTML   |
| ⚙️ CLI fallback         | Degrades to plain text/simple lists in pure‑text environments |
| 🛡️ Ethical boundaries   | No professional advice, no violence glorification, respects privacy, anti‑discrimination |

---

## <a id="installation"></a>📦 Installation

**Option 1: GitHub CLI (recommended)**

```bash
gh skill install sevenwoood/prism-skill prism-skill
```

**Option 2: Universal Skills CLI**

```bash
npx skills add sevenwoood/prism-skill --skill prism-skill
```

**Option 3: Manual**

```bash
git clone https://github.com/sevenwoood/prism-skill.git
# Copy the prism-skill folder to one of:
# - ~/.cursor/skills/
# - ~/.claude/skills/
# - ~/.codex/skills/
```

## <a id="quick-start"></a>🚀 Quick Start

**Example input**:

> “The Fed just raised interest rates. How does it affect ordinary people? I want real facts.”

**Example output (soft style)**:

```text
Simply put: A rate hike directly increases monthly payments for floating‑rate loans, while possibly slowing price rises.

Let’s break it down:
| Area | Impact |
|------|--------|
| Mortgage | +~¥140/month per ¥1M loan |
| Savings | Slightly higher interest |
| Jobs | Export‑related sectors may weaken |

So: The most direct effect is on loan costs; other aspects are minor.

If you’d like to dig deeper, we could talk about your specific loan situation, or how other countries are affected.
```

**Generate an HTML report**: After any analysis, type `output html` to get an interactive web page.

------

## <a id="file-structure"></a>📁 File Structure

```text
prism-skill/
├── SKILL.md                  # Core skill definition
├── README.md                 # Chinese documentation
├── README.en.md              # English documentation
├── README.ja.md              # Japanese documentation
├── README.ko.md              # Korean documentation
├── README.es.md              # Spanish documentation
├── references/               # Methodology and constraints
│   ├── analysis-framework.md
│   ├── source-priority.md
│   └── ethics-boundaries.md
├── examples/                 # Example dialogues
│   ├── economic-example.md
│   ├── health-example.md
│   └── social-example.md
└── assets/                   # Static resources
    └── prism-skill.svg       # Banner image
```

## <a id="license"></a>📄 License

MIT © 2026 Prism Skill Contributors

------

## ⚠️ Language Compatibility Notes

- **Best support**: Chinese, English (most accurate fact‑checking, smoothest output).
- **Other languages**: Japanese, Korean, Spanish work but deeper analysis may be slightly weaker.
- **Recommendation**: For critical analyses, ask the skill to “first analyze in English/Chinese, then translate to your language”.
- **Fact‑checking**: Different languages will prioritise authoritative sources in that language; for cross‑border events, specify the preferred region (e.g., “prefer Chinese official data”).

