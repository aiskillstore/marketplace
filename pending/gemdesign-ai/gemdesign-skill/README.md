# gemdesign-skill

gemdesign-skill is a Skill designed for general-purpose AI agent platforms. With simple instructions to the agent, you can automatically generate high-fidelity, fully interactive UI prototype demos. For example, feed it a PRD requirements document and it will automatically design all prototype pages, preview them in real time in the browser, allow manual editing in the local GemDesign designer, and sync them to the GemDesign platform.

## Features

- Batch generate UI prototypes / design pages from a requirements document
- Conversational generation of a single page
- Modify existing GemDesign pages
- Local streaming real-time preview service (GemDesign designer, bundled in the CLI)

## Prerequisites

- [Node.js](https://nodejs.org/) (to run the local preview server)
- `@gemdesign-ai/cli` (the Skill automatically checks and installs it on first use)

```bash
npm install -g @gemdesign-ai/cli
gemdesign auth login --token <your_token>
```

To get a token: log in to https://design.gemcoder.com → Personal Center → MCP Token.

## Installation

This skill follows the [Agent Skills](https://agentskills.io) open standard and works across mainstream AI agent platforms. Copy the `gemdesign-skill` folder into your platform's skills directory:

- **Project skill**: `<project_path>/.agents/skills/gemdesign-skill`
- **Global skill**:
  - macOS/Linux: `~/.agents/skills/gemdesign-skill`
  - Windows: `%userprofile%\.agents\skills\gemdesign-skill`

For platform-specific directories (Claude Code, Codex, Cursor, TRAE, Qoder, OpenClaw, WorkBuddy, QClaw, Opencode, Hermes, etc.), see the root [README](../README.md).

The skill has no bundled runtime resources — the local preview server is provided by the `@gemdesign-ai/cli` package. The skill folder only contains `SKILL.md` and this README.


## Directory Structure

```
gemdesign-skill/
├── SKILL.md              # Core skill instructions
└── README.md             # This file
```

## License

MIT — see the root [LICENSE](../LICENSE).
