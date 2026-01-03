# AI Skillstore - Claude Code Plugin Marketplace

The official AI Skills marketplace for Claude Code. Discover, install, and manage AI agent skills to enhance your Claude Code experience.

## Quick Start

### Add this marketplace to Claude Code

```
/plugin marketplace add aiskillstore/marketplace
```

### Browse available plugins

```
/plugin
```
Then select the "Discover" tab.

### Install a plugin

```
/plugin install <plugin-name>@aiskillstore
```

For example:
```
/plugin install xlsx@aiskillstore
```

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
├── .claude-plugin/
│   └── marketplace.json      # Plugin catalog (Claude Code reads this)
├── plugins/                   # Approved plugins
│   └── <plugin-name>/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin manifest
│       ├── skills/
│       │   └── <skill-name>/
│       │       └── SKILL.md  # Skill definition
│       └── skill-report.json # Security audit + AI-generated content
├── pending/                   # Plugins awaiting review
├── schemas/                   # JSON validation schemas
└── .github/workflows/         # Automation workflows
```

## Available Plugins

Browse all available plugins at [skillstore.io](https://skillstore.io) or use the `/plugin` command in Claude Code to discover and install plugins directly.

## Links

- **Website**: [skillstore.io](https://skillstore.io)
- **Submit Skills**: [skillstore.io/submit](https://skillstore.io/submit)
- **Documentation**: [skillstore.io/docs](https://skillstore.io/docs)
- **GitHub**: [github.com/aiskillstore](https://github.com/aiskillstore)

## License

This marketplace catalog is licensed under MIT. Individual plugins may have their own licenses - check each plugin's LICENSE file.

---

**Made with care by the AI Skillstore team**
