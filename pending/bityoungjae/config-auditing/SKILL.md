---
name: config-auditing
description: "Neovim configuration audit knowledge base. Use when: reviewing config files for issues, checking deprecated APIs, optimizing settings, or performing health checks. Provides checklists, best practices, and version-specific deprecated API detection patterns."
allowed-tools: Read, Bash, Grep, Glob
---

# Neovim Configuration Auditing Skill

Systematic configuration analysis for identifying issues, optimizations, and deprecated API usage in Neovim setups.

## Supporting Documents

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [audit-checklist.md](audit-checklist.md) | Structured audit categories with detection patterns | Systematic config review |
| [best-practices.md](best-practices.md) | lazy.nvim patterns, vim.opt usage, keymap conventions | Optimization suggestions |
| [deprecated-apis.md](deprecated-apis.md) | Version-specific deprecated APIs with grep patterns | Compatibility checks |

## Quick Validation Commands

Run these headless commands for rapid assessment:

```bash
# Get Neovim version
nvim --version | head -1

# Get config path
nvim --headless -c "lua print(vim.fn.stdpath('config'))" -c "qa" 2>&1

# Count Lua files in config
find ~/.config/nvim -name "*.lua" 2>/dev/null | wc -l

# Count plugins (lazy.nvim)
ls ~/.local/share/nvim/lazy 2>/dev/null | wc -l

# Check for deprecated vim.api.nvim_buf_set_option usage
grep -rn "nvim_buf_set_option\|nvim_win_set_option" ~/.config/nvim --include="*.lua" 2>/dev/null | head -10

# Check startup time
nvim --startuptime /tmp/nvim-startup.log +q && tail -5 /tmp/nvim-startup.log

# Validate Lua syntax in config
nvim --headless -c "lua dofile(vim.fn.stdpath('config')..'/init.lua')" -c "qa" 2>&1

# Check for error on startup
nvim --headless -c "qa" 2>&1 | head -20
```

## Scoring Criteria

Assign grades based on issue severity and count:

| Grade | Criteria | Description |
|-------|----------|-------------|
| **A** | 0 Critical, 0-2 Warnings | Excellent - Production ready |
| **B** | 0 Critical, 3-5 Warnings | Good - Minor improvements possible |
| **C** | 0 Critical, 6+ Warnings OR 1 Critical | Acceptable - Needs attention |
| **D** | 2-3 Critical issues | Poor - Significant problems |
| **F** | 4+ Critical issues | Failing - Requires immediate fixes |

### Issue Severity Definitions

**Critical**: Security risks, breaking deprecated APIs (removed in current version), runtime errors
**Warning**: Performance issues, deprecated APIs (still working), code style violations
**Suggestion**: Optional improvements, modern alternatives, organization tips

## Audit Workflow

1. **Gather Environment Info**
   - Neovim version (determines which deprecated APIs apply)
   - Plugin manager type (lazy.nvim, packer.nvim, etc.)
   - Config structure (single file vs modular)

2. **Run Category Audits**
   - Follow [audit-checklist.md](audit-checklist.md) categories in order
   - Use grep patterns to detect issues programmatically
   - Note severity for each finding

3. **Check Version Compatibility**
   - Reference [deprecated-apis.md](deprecated-apis.md) for user's Neovim version
   - Flag APIs deprecated OR removed in their version

4. **Apply Best Practices**
   - Compare against [best-practices.md](best-practices.md)
   - Suggest optimizations where applicable

5. **Calculate Grade**
   - Count Critical/Warning/Suggestion issues
   - Apply scoring criteria above
   - Provide overall health assessment

## Output Template

```xml
<audit_report>
## Summary
- **Grade**: [A-F]
- **Neovim Version**: [detected version]
- **Config Location**: [path]
- **Plugin Count**: [count]

## Critical Issues
[List each critical issue with file:line and fix]

## Warnings
[List each warning with file:line and recommendation]

## Suggestions
[List optional improvements]

## Statistics
| Metric | Value |
|--------|-------|
| Total Lua files | X |
| Total lines | Y |
| Plugins | Z |
| Startup time | Nms |
| Deprecated APIs | N |
</audit_report>
```
