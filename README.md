# AI Skillstore - Agent Skills Marketplace

The official AI Skills marketplace for Claude Code and Codex. Discover, install, and manage AI agent skills following the [Agent Skills specification](https://agentskills.io/specification).

## Quick Start

### Claude Code Installation

#### Method 1: Quick Install (Recommended)

Copy this prompt and paste it into Claude Code:

```
Download all files from https://github.com/aiskillstore/marketplace/tree/main/skills/<skill-name> and save to ~/.claude/skills/
```

Claude Code will automatically fetch and install the skill files.

#### Method 2: Manual Install

1. Download the skill ZIP from [skillstore.io](https://skillstore.io)
2. Extract to your preferred scope directory:
   - **Project scope**: `.claude/skills/<skill-name>/` (current project only)
   - **User scope**: `~/.claude/skills/<skill-name>/` (all projects)
3. Each skill folder must contain a `SKILL.md` file

### Codex Installation

#### Method 1: Use $skill-installer (Recommended)

Run this command inside Codex:

```
$skill-installer install https://github.com/aiskillstore/marketplace/tree/main/skills/<skill-name>
```

#### Method 2: Manual Install

1. Download the skill ZIP from [skillstore.io](https://skillstore.io)
2. Extract to your preferred scope directory:
   - **Repo scope**: `.codex/skills/<skill-name>/` (current project)
   - **User scope**: `~/.codex/skills/<skill-name>/` (your account)
   - **System scope**: `/etc/codex/skills/<skill-name>/` (all users)
3. Restart Codex to load new skills

## For Skill Developers

### Submit Your Skill

1. Visit [skillstore.io/submit](https://skillstore.io/submit)
2. Enter your GitHub repository URL containing a `SKILL.md` file
3. Wait for automated security analysis
4. Admin reviews and approves your submission
5. Your skill becomes available in the marketplace

### Skill Requirements

Your repository should contain:

- `SKILL.md` - The skill definition file (required)
- Supporting files referenced by the skill (optional)
- `LICENSE` - License file (recommended)

### Security Analysis

All submitted skills undergo automated security analysis that checks for:

- Dangerous code patterns (eval, exec, system commands)
- File system access outside project scope
- Network requests to external hosts
- Obfuscated or minified code
- Credential/secret handling

Skills that fail security checks will not be published.

## Repository Structure

```
.
├── skills/                    # Approved skills
│   └── <skill-name>/
│       ├── SKILL.md           # Skill definition (required)
│       ├── scripts/           # Optional executable scripts
│       ├── references/        # Optional additional docs
│       └── assets/            # Optional static resources
├── pending/                   # Skills awaiting review
├── schemas/                   # JSON validation schemas
└── .github/workflows/         # Automation workflows
```

## Available Skills

Browse all available skills at [skillstore.io](https://skillstore.io).

## Links

- **Website**: [skillstore.io](https://skillstore.io)
- **Submit Skills**: [skillstore.io/submit](https://skillstore.io/submit)
- **Documentation**: [skillstore.io/docs](https://skillstore.io/docs)
- **Agent Skills Spec**: [agentskills.io/specification](https://agentskills.io/specification)
- **GitHub**: [github.com/aiskillstore](https://github.com/aiskillstore)

## License

This marketplace catalog is licensed under MIT. Individual skills may have their own licenses - check each skill's LICENSE file.

---

**Made with care by the AI Skillstore team**
