# My Standard Plugin

A comprehensive Claude Code plugin for [domain/purpose]. This plugin provides agents, commands, and scripts for [primary use case].

## Overview

This plugin helps you:
- Primary benefit 1
- Primary benefit 2
- Primary benefit 3

## Features

### 🤖 Intelligent Agents

- **example-agent**: Deep analysis and specialized processing for task X

### ⚡ Commands

- `/my-standard-plugin:analyze [component]` - Analyze components and provide recommendations
- `/my-standard-plugin:fix [component]` - Automatically fix common issues

### 🛠️ Helper Scripts

- `scripts/helper.sh` - Utility functions for common operations

## Installation

### Manual Installation

1. Clone or download this plugin:
   ```bash
   git clone https://github.com/yourusername/my-standard-plugin.git
   ```

2. Symlink to Claude's plugin directory:
   ```bash
   ln -s /path/to/my-standard-plugin ~/.claude/plugins/my-standard-plugin
   ```

3. Restart Claude Code

### Marketplace Installation

```bash
claude plugin install my-standard-plugin
```

## Quick Start

### Analyze a Component

```bash
/my-standard-plugin:analyze authentication
```

This will analyze the authentication component and provide:
- Code quality assessment
- Identified issues
- Actionable recommendations

### Fix Issues Automatically

```bash
/my-standard-plugin:fix authentication
```

This will:
1. Identify fixable issues
2. Show proposed changes
3. Apply fixes with your approval
4. Verify changes

### Use the Agent for Deep Analysis

Simply ask Claude:
```
"Use the example-agent to perform a deep analysis of the authentication system"
```

The agent will:
- Gather context from your codebase
- Apply specialized expertise
- Provide detailed recommendations

## Usage Examples

### Example 1: Component Analysis

```bash
# Analyze a specific component
/my-standard-plugin:analyze user-profile

# Review the analysis report
# Follow recommended improvements
```

### Example 2: Automated Fixes

```bash
# Identify and fix issues
/my-standard-plugin:fix user-profile

# Review proposed changes
# Confirm to apply fixes
# Verify changes with tests
```

### Example 3: Agent-Assisted Work

Ask Claude:
```
"I need to refactor the authentication module. Can you use the example-agent to help?"
```

The agent will:
- Analyze current implementation
- Identify refactoring opportunities
- Suggest architectural improvements
- Help implement changes

## Configuration

(Optional) If your plugin supports configuration:

Create `.my-standard-plugin.config.json` in your project root:

```json
{
  "analysisDepth": "thorough",
  "autoFix": false,
  "reportFormat": "detailed"
}
```

## Requirements

- Claude Code v1.0.0 or higher
- Bash (for helper scripts)
- (List any other dependencies)

## Architecture

```
my-standard-plugin/
├── agents/           # Specialized agents for deep analysis
├── commands/         # User-invoked slash commands
├── scripts/          # Helper utilities
└── .claude-plugin/   # Plugin manifest
```

## Troubleshooting

### Plugin Not Loading

**Problem**: Plugin doesn't appear in Claude
**Solution**:
- Verify symlink is correct
- Check plugin.json syntax
- Restart Claude Code

### Commands Not Working

**Problem**: Commands return errors
**Solution**:
- Check command syntax
- Verify required arguments
- Review error messages

### Agent Not Invoking

**Problem**: Agent doesn't activate when expected
**Solution**:
- Be explicit: "Use the example-agent to..."
- Check agent description matches use case

## Development

### Adding New Commands

1. Create `commands/new-command.md`
2. Add YAML frontmatter with metadata
3. Document usage and implementation
4. Test thoroughly

### Modifying Agents

1. Edit agent markdown file
2. Update capabilities section
3. Test invocation scenarios
4. Update README.md

## Contributing

Contributions are welcome! Here's how to help:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Validate with `validate-plugin.py`

## Changelog

### v1.0.0 (Initial Release)
- Added example-agent for specialized analysis
- Added analyze command for component analysis
- Added fix command for automated repairs
- Added helper script utilities

## License

MIT License - see LICENSE file for details

Copyright (c) 2024 Your Name

## Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/yourusername/my-standard-plugin/issues)
- **Questions**: [GitHub Discussions](https://github.com/yourusername/my-standard-plugin/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/my-standard-plugin/wiki)

## Acknowledgments

- Thanks to the Claude Code team
- Inspired by [related projects]
- Contributors: [list contributors]

---

**Made with ❤️ for the Claude Code community**
