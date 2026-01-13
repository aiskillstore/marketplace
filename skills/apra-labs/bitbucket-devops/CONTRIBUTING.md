# Contributing to Claude Bitbucket DevOps Skill

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

Found a bug? Please create an issue on GitHub with:

1. **Clear title** describing the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs **actual behavior**
4. **Environment details**:
   - Claude Code version
   - bitbucket-mcp version
   - Operating system
5. **Logs or screenshots** if applicable

### Suggesting Features

Have an idea? Create a GitHub Discussion or Issue with:

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How would it work?
3. **Alternatives considered** - What else did you think about?
4. **Examples** - Show how users would interact with it

### Pull Requests

We welcome pull requests! Here's the process:

#### 1. Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/claude-bitbucket-devops-skill.git
cd claude-bitbucket-devops-skill
```

#### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

#### 3. Make Changes

**For skill functionality changes:**
- Edit `SKILL.md` - The main skill logic
- Update `README.md` - User-facing documentation
- Add examples in `QUICK_REFERENCE.md`

**Guidelines:**
- Keep the skill description concise in the YAML frontmatter
- Include clear examples for each feature
- Add error handling for edge cases
- Test with real Bitbucket pipelines

#### 4. Test Your Changes

**Manual testing:**

1. Install the modified skill in your local Claude Code:
   ```bash
   # Windows
   copy SKILL.md %USERPROFILE%\.claude\skills\bitbucket-devops\

   # macOS/Linux
   cp SKILL.md ~/.claude/skills/bitbucket-devops/
   ```

2. Restart VSCode/Claude Code

3. Test the new functionality:
   - Ask questions that should trigger your feature
   - Verify it works as expected
   - Check error cases

4. Test with different scenarios:
   - Different repositories
   - Various pipeline states
   - Edge cases (no pipelines, very old pipelines, etc.)

#### 5. Commit and Push

```bash
git add .
git commit -m "feat: add support for pipeline comparison"
# Use conventional commits: feat|fix|docs|style|refactor|test|chore

git push origin feature/your-feature-name
```

#### 6. Create Pull Request

1. Go to GitHub and create a Pull Request
2. Fill out the PR template
3. Link related issues
4. Wait for review

## Coding Guidelines

### Skill.md Structure

```markdown
---
name: bitbucket-devops
description: Brief, keyword-rich description
allowed-tools: Bash, Read, Write, Grep, Glob
---

# Title

## Usage Patterns

### Pattern Name

**User Request Examples:**
- Example 1
- Example 2

**Steps:**
1. Clear step-by-step process
2. Include MCP tool calls
3. Show expected output

**Example Output:**
```text
Formatted example
```
```

### Best Practices

1. **Be specific**: Include exact MCP tool names and parameters
2. **Show examples**: Use real-world scenarios
3. **Handle errors**: Include common error cases and solutions
4. **Keep it simple**: Focus on user experience, not implementation
5. **Test thoroughly**: Verify all examples work

## Testing

### What to Test

- [ ] Skill activates for relevant queries
- [ ] MCP tools are called correctly
- [ ] Error handling works
- [ ] Log files are created properly
- [ ] Works across different repositories
- [ ] Edge cases are handled

### Test Checklist

Before submitting a PR:

- [ ] Tested with successful pipeline
- [ ] Tested with failed pipeline
- [ ] Tested with running pipeline
- [ ] Tested with non-existent pipeline
- [ ] Tested log slicing for large logs
- [ ] Tested across 2+ different repos
- [ ] Verified no credentials are exposed
- [ ] Updated documentation

## Documentation

Update these files when adding features:

- `SKILL.md` - Main skill logic and instructions
- `README.md` - User-facing documentation
- `QUICK_REFERENCE.md` - Quick command reference
- `CONTRIBUTING.md` (this file) - If process changes

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Other unprofessional conduct

## Attribution

All contributors will be recognized in the project. By contributing, you agree:

1. Your contributions are your own work
2. You grant Apra Labs rights to use your contribution under CC BY 4.0
3. You agree to be listed in contributors

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/Apra-Labs/claude-bitbucket-devops-skill/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/Apra-Labs/claude-bitbucket-devops-skill/issues)
- **Security issues**: Email security@apralabs.com (if applicable)

## Development Setup

### Prerequisites

- Claude Code VSCode extension
- Node.js 16+ (for bitbucket-mcp)
- Bitbucket account with app password
- Git

### Local Setup

1. Clone both repositories:
   ```bash
   git clone https://github.com/MatanYemini/bitbucket-mcp.git
   git clone https://github.com/Apra-Labs/claude-bitbucket-devops-skill.git
   ```

2. Setup bitbucket-mcp:
   ```bash
   cd bitbucket-mcp
   npm install
   npm run build
   ```

3. Configure VSCode settings (see README.md)

4. Install skill locally:
   ```bash
   # Link to skills directory
   # Windows:
   mklink /D %USERPROFILE%\.claude\skills\bitbucket-devops claude-bitbucket-devops-skill

   # macOS/Linux:
   ln -s $(pwd)/claude-bitbucket-devops-skill ~/.claude/skills/bitbucket-devops
   ```

5. Restart VSCode

### Making Changes

1. Edit `SKILL.md` in your cloned repo
2. Changes are automatically reflected (symlinked)
3. Restart VSCode to reload the skill
4. Test your changes

## Release Process

Maintainers will:

1. Review and merge PRs
2. Update version in README
3. Create GitHub release
4. Update changelog

## License

By contributing, you agree your contributions will be licensed under CC BY 4.0.

---

Thank you for contributing! 🎉
