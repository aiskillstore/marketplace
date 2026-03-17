# Compatibility Notes

## Role Division

This skill handles **decision logic**. Other skills handle **file operations and Obsidian syntax**.

| Responsibility | This skill | Other skills |
|---|---|---|
| Classify a note as project/area/resource/archive | YES | no |
| Decide where a note should go | YES | no |
| Create, read, write .md files | delegate | obsidian-markdown, obsidian-cli |
| Format Obsidian wikilinks, callouts, embeds | delegate | obsidian-markdown |
| Execute vault file moves | with permission | obsidian-cli |
| Generate dataview queries | no | obsidian-bases, obsidian-markdown |
| PARA review reports (content) | YES | no |
| PARA frontmatter additions | YES | no |

When both this skill and another Obsidian skill are active, this skill provides the **what and where**, the other provides the **how**.

---

## Installed Obsidian Skills in This Vault

### obsidian-markdown
- Creates and edits Obsidian-flavored markdown
- Handles wikilinks, callouts, embeds, properties syntax
- **This skill should delegate** file creation and markdown formatting to obsidian-markdown

### obsidian-cli
- Reads, creates, searches notes via CLI
- Executes file moves and vault operations
- **This skill should delegate** actual file system operations to obsidian-cli when available

### obsidian-bases
- Creates and edits `.base` files (database-style views)
- **No conflict** — PARA skill doesn't touch `.base` files

### json-canvas
- Creates `.canvas` files
- **No conflict** — PARA skill doesn't touch `.canvas` files

---

## Frontmatter Conflict Rules

1. Never remove fields written by other skills
2. Never rename existing tags that don't use `para/` prefix
3. If a note has `type:` or `category:` or similar fields from another convention, leave them alone — add `para_type:` separately
4. If `tags` already exists as a list, append to it; never replace it
5. If `status` already exists with a non-PARA value, add `para_status:` as a separate field rather than overwriting

---

## File Operation Safety Protocol

Before any file move or rename:
1. Check if the note is linked from other notes via `[[filename]]` wikilinks
2. Obsidian auto-updates wikilinks on moves IF you use obsidian-cli or the Obsidian app itself
3. Do NOT use raw shell `mv` commands for moves — use obsidian-cli to preserve link integrity
4. If obsidian-cli is unavailable, warn the user that links may break and ask for confirmation

---

## Vault-Specific Conventions for This Vault

Detected structure:
- `1_Projects/` — Projects (numbered prefix convention)
- `2_Areas/` — Areas
- `3_Resources/` — Resources
- `4_Archives/` — Archive
- `attachments/` — Media files (never classify or move these)
- `zVaultCode/` — Vault config/code (never touch)
- `.obsidian/` — Obsidian config (never touch)

Do not create new top-level folders without asking the user first. If an Inbox folder is needed, suggest `0_Inbox/` to maintain the numerical prefix convention.

---

## When Multiple Skills Are Called

If the user's request needs both this skill and obsidian-markdown or obsidian-cli, this skill should:
1. Complete classification and routing decision first
2. Clearly indicate "I'll now delegate file creation to [other skill]" or "Please run the obsidian-cli command to move this file"
3. Provide the exact target path and frontmatter to apply

Never silently assume another skill ran. State handoffs explicitly.
