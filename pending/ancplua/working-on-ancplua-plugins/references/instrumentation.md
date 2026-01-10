# Publishing & Creating Plugins

> Based on [official Claude Code plugin docs](https://code.claude.com/docs/en/plugins)

## 1. Create Plugin Structure

Use the template or create manually:

```bash
# Option A: Copy template
cp -r tooling/templates/plugin-template plugins/<plugin-name>

# Option B: Create manually
mkdir -p plugins/<plugin-name>/.claude-plugin
mkdir -p plugins/<plugin-name>/{skills,commands,agents,hooks,scripts}
```

## 2. Create Manifests

### `plugins/<plugin-name>/.claude-plugin/plugin.json`

**Required fields:** `name`, `description`, `version`, `author`

```json
{
  "name": "<plugin-name>",
  "description": "Description of what the plugin does.",
  "version": "0.1.0",
  "author": {
    "name": "AncpLua",
    "url": "https://github.com/ANcpLua"
  },
  "repository": "https://github.com/ANcpLua/ancplua-claude-plugins",
  "license": "MIT"
}
```

> Note: `repository` and `license` are optional but recommended.

### `.claude-plugin/marketplace.json` (Repo Root)

Add your plugin to the monorepo marketplace:

```json
{
  "name": "<plugin-name>",
  "source": "./plugins/<plugin-name>",
  "description": "Short description.",
  "version": "0.1.0"
}
```

## 3. Create a Skill (Optional)

Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`:

```yaml
---
name: skill-name
description: What this skill does and when Claude should use it
---

# Skill: skill-name

Your skill instructions here...
```

Per [official docs](https://code.claude.com/docs/en/skills), only `name` and `description` are required in frontmatter.

## 4. Documentation & Validation

1. **README.md**: Add `plugins/<plugin-name>/README.md` explaining usage.
2. **CHANGELOG.md**: Add entry under `[Unreleased]` in repo root.
3. **Validate**:

```bash
# Full validation
./tooling/scripts/local-validate.sh

# Check marketplace sync
./tooling/scripts/sync-marketplace.sh
```

## Versioning & Release Checklist

- [ ] `version` in `plugin.json` matches `marketplace.json`
- [ ] CHANGELOG.md updated
- [ ] `local-validate.sh` passes
- [ ] `sync-marketplace.sh` passes
- [ ] README.md exists and is accurate
- [ ] Restart Claude Code after changes (required to load updates)

## Common Pitfalls

| Mistake | Solution |
|---------|----------|
| Invalid JSON | Run `jq . path/to/file.json` to verify syntax |
| Hardcoded paths | Use `${CLAUDE_PLUGIN_ROOT}` in hooks/MCP configs |
| Missing permissions | Run `chmod +x scripts/*.sh` |
| Changes not visible | Restart Claude Code |
| Version mismatch | Run `sync-marketplace.sh` to detect |
| Missing frontmatter | SKILL.md needs `name` and `description` in YAML |
