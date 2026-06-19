# 🪶 Quill - Style Distiller

> Distill writing styles from articles or author names, and generate executable, reusable writing Skills.

Quill is a "meta-skill" for style distillation. Feed it an article, an author's name, or a collection of texts, and it will automatically analyze the writing style characteristics, generating a reusable "Writing Style Skill Card." From then on, every piece you write can be rewritten in that target style with one command.

**In one sentence**: Turn "writing style" into an executable, tunable, fusible writing engine.

---

## ✨ Core Features

| Feature                          | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| 🧪 **Single-Style Distillation**  | Extract 6 dimensional features: vocabulary, syntax, rhetoric, narrative perspective, rhythm, and timeline structure |
| 🎨 **Style Blending**             | Blend multiple authors' styles with per-dimension ratio control (e.g., "70% Borges + 30% Kafka") |
| 🔴 **De-AI Audit**                | Automatically filter templated expressions to make text feel more "human-written" |
| 🎛️ **Style Intensity**            | Three adjustable levels: Light / Medium / Deep rewrite       |
| ⏳ **Narrative Structure Toggle** | Enable/disable timeline structures (flashback, interlude, multi-thread, etc.) anytime |
| 🔄 **Incremental Updates**        | Append new articles to recalibrate and upgrade existing Skills |
| 📝 **Revision Notes**             | Dimension-level modification summaries after each rewrite, showing exactly what changed and why |

---

## 🚀 Installation

### Method 1: GitHub CLI (Recommended)

```bash
gh skill install sevenwoood/quill
```



### Method 2: Universal Skills CLI

```bash
npx skills add sevenwoood/quill --skill quill
```



### Method 3: Manual Installation

```bash
git clone https://github.com/sevenwoood/quill.git
```



Copy the `quill` folder to one of the following directories:

- `~/.cursor/skills/`
- `~/.claude/skills/`
- `~/.codex/skills/`

------

## 📖 Quick Start

### Scenario 1: Imitating a Well-Known Author

**You type**:

```text
Imitate Borges
```



**You receive**:

- A complete "Borges Writing Style Skill Card"
- Including vocabulary preferences, syntactic rhythm, rhetorical density, narrative perspective, and more

**Then**:

```text
Apply this style to rewrite: The weather was nice today. I walked down the street, saw a beggar, and felt sorry for him.
```



**You receive**:

- A stylistically rewritten piece
- Accompanied by Revision Notes, showing specific changes across vocabulary, syntax, rhetoric, and more

------

### Scenario 2: Feeding Your Own Articles

**You type**:

```text
(Paste 3 of your own short prose pieces)
```



**The system automatically**:

1. Detects stylistic consistency
2. If conflicts are found (e.g., early vs. late style differences), generates a Style Diagnosis Report
3. Asks for your preferences (period selection, processing method, etc.)
4. Generates a custom Skill Card

**You receive**: Your very own personal writing style engine.

------

### Scenario 3: Style Blending

**You type**:

```text
Blend Borges + Kafka
```



**The system automatically**:

1. Distills each author's style separately
2. Generates a Style Blending Ratio Confirmation table
3. You confirm per-dimension ratios (e.g., Vocabulary A70% B30%, Syntax 50/50)
4. Generates a blended Skill Card

**You receive**: A unique "Borges × Kafka" hybrid writing style, all your own.

------

## 🧭 Full Workflow

```text
Step 1: Launch
Type "Start" or directly feed articles/author names
    ↓
Step 2: Feed & Confirm
Choose intent: Single / Blend / Compare / Not sure
    ↓
Step 3: Diagnosis (if conflicts detected)
Read the Style Diagnosis Report and make your choice
    ↓
Step 4: Skill Generated
Receive "✅ [Style Name] Writing Style Skill successfully generated!"
    ↓
Step 5: Apply Rewrite
Type "Apply this style to rewrite: [content]"
    ↓
Step 6: Fine-Tune (optional)
Anytime, type "Style intensity: Light",
"Enable narrative structure",
"Adjust blend ratio: Vocabulary A70% B30%"
```



------

## ⚙️ Hot-Swap Commands

Type these commands anytime during the conversation to adjust in real-time:

| You Type                                   | Effect                                                   |
| :----------------------------------------- | :------------------------------------------------------- |
| `Enable narrative structure`               | Enable timeline structures (flashback, interlude, etc.)  |
| `Disable narrative structure`              | Disable timeline structures                              |
| `Style intensity: Light`                   | Fine-tune vocabulary only, keep original framework       |
| `Style intensity: Medium`                  | Full rewrite, preserve original meaning (default)        |
| `Style intensity: Deep`                    | Complete rewrite, original as "inspiration seed"         |
| `Adjust blend ratio: Vocabulary A70% B30%` | Fine-tune blend proportions                              |
| `Update Skill: [new article]`              | Append new material to recalibrate and upgrade the Skill |

------

## 🧩 Use Cases

- **Literary Creation**: Experiment with different authors' styles to find your own voice
- **Writing Practice**: Deconstruct master styles and learn vocabulary, syntax, and rhythm
- **Content Polishing**: Make writing feel more "human" and remove AI template traces
- **Style Experimentation**: Blend multiple author styles to create entirely new genres
- **Brand Copywriting**: Unify tone and voice across multiple pieces

------

## 🛡️ Ethics & Disclaimer

This Skill imitates writing style only and does not reproduce original expression. Please respect the spirit of originality and avoid impersonation or plagiarism.

> All rewritten content is marked as "Rewritten in [Style Name] style" and noted as "This is a simulated style, not original work by the named author."

------

## 📁 Project Structure

```text
quill/
├── SKILL.md                    # Core skill definition file
├── README.md                   # Project documentation (Chinese)
├── README.en.md                # Project documentation (English)
├── assets/
│   ├── banner_quill.png        # Banner image
│   └── logo_quill.png          # Logo icon
├── references/                 # Backend rule documents (black box)
│   ├── distillation-dimensions.md
│   ├── diagnosis-rules.md
│   ├── de-ai-audit-rules.md
│   └── ethics-statement.md
└── examples/
    ├── example-single-style.md
    ├── example-style-blending.md
    ├── example-rewrite.md
    └── example-update-skill.md
```



------

## 📄 License

MIT License

------

## 🙋 Feedback & Contributions

Issues and PRs are welcome.

------

**Get Started**: Launch Quill in your AI conversation by typing "Start".