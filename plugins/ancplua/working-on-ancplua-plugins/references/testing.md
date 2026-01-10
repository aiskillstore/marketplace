# Testing & Debugging

## Automated Validation

Run the full suite before pushing:

```bash
./tooling/scripts/local-validate.sh
```

This enforces:

| Check | Tool | What It Validates |
|-------|------|-------------------|
| Plugin manifests | `claude plugin validate` | JSON structure, required fields |
| Shell scripts | `shellcheck` | Bugs, quoting, safety |
| Markdown | `markdownlint` | Formatting, consistency |
| CI workflows | `actionlint` | GitHub Actions syntax |
| JSON syntax | `jq` | Valid JSON in all .json files |

## Marketplace Sync Check

Verify plugin.json versions match marketplace.json:

```bash
./tooling/scripts/sync-marketplace.sh
```

This detects:

- Plugins in filesystem but not in marketplace
- Plugins in marketplace but not in filesystem
- Version mismatches between plugin.json and marketplace.json

## Unit Testing

For logic-heavy plugins:

| Language | Command |
|----------|---------|
| JS/TS | `npm test` (Jest/Vitest) |
| Python | `pytest` |
| Go | `go test ./...` |

## Manual Verification & Debugging

If `local-validate.sh` passes but the plugin still fails:

### 1. Validate JSON Syntax

Parser errors are often silent. Check manually:

```bash
jq . .claude-plugin/plugin.json
jq . hooks/hooks.json
```

### 2. Check Permissions

Scripts must be executable:

```bash
find . -name "*.sh" -exec ls -l {} \;

# Fix if needed:
chmod +x path/to/script.sh
```

### 3. Verify No Hardcoded Paths

Ensure no absolute paths exist in configs:

```bash
grep -r "/Users/" .
grep -r "/home/" .

# Should return empty. Replace with ${CLAUDE_PLUGIN_ROOT}
```

### 4. Test Components Independently

- **MCP Servers**: Run the server command directly in terminal to see crash logs.
- **Hooks**: Execute the hook script manually to verify it runs without error.
- **Skills**: Check SKILL.md has valid YAML frontmatter with `name` and `description`.

### 5. Check Claude Code Logs

If plugin loads but behaves unexpectedly:

```bash
# macOS
tail -f ~/Library/Logs/Claude/claude-code.log

# Linux
tail -f ~/.local/share/claude-code/logs/claude-code.log
```

## Quick Debugging Checklist

- [ ] `local-validate.sh` passes
- [ ] `sync-marketplace.sh` passes
- [ ] All JSON files valid (`jq . file.json`)
- [ ] No hardcoded paths (`grep -r "/Users/"`)
- [ ] Scripts are executable (`chmod +x`)
- [ ] SKILL.md has `name` and `description` frontmatter
- [ ] Restarted Claude Code after changes
