# Using prettify-pdf With Claude And OpenClaw

This skill is a plain `SKILL.md` folder. It works anywhere the agent can load Agent Skills-style directories.

## Claude Code

Install globally for your user:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.claude/skills/prettify-pdf"
```

Restart Claude Code or start a new session, then ask:

```text
Use $prettify-pdf to redesign this receipt PDF. Preserve all IDs, dates, times, amounts, labels, barcode, and seal exactly.
```

Project-scoped install:

```bash
mkdir -p .claude/skills
git clone https://github.com/sethupavan12/prettify-pdf .claude/skills/prettify-pdf
```

Claude Code skills are loaded from personal `~/.claude/skills/<skill-name>/SKILL.md` or project `.claude/skills/<skill-name>/SKILL.md` folders.

## Claude.ai

Claude.ai supports uploaded custom skills. Package this repository as a zip, then upload it in the Claude skill settings UI.

```bash
git clone https://github.com/sethupavan12/prettify-pdf
zip -r prettify-pdf.zip prettify-pdf \
  -x "prettify-pdf/.git/*" \
  -x "prettify-pdf/output/*" \
  -x "prettify-pdf/tmp/*" \
  -x "prettify-pdf/uploads/*" \
  -x "prettify-pdf/outputs/*"
```

After enabling the skill, prompt Claude with:

```text
Use prettify-pdf on this uploaded PDF. Highlight the important information, but preserve source values and barcode/QR/seal assets exactly.
```

## OpenClaw

OpenClaw uses AgentSkills-compatible folders containing `SKILL.md`.

Install for all OpenClaw agents:

```bash
mkdir -p "$HOME/.openclaw/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.openclaw/skills/prettify-pdf"
openclaw skills list
```

Install for one workspace:

```bash
mkdir -p skills
git clone https://github.com/sethupavan12/prettify-pdf skills/prettify-pdf
openclaw skills list
```

Start a new session or restart the gateway if the skill does not appear:

```bash
openclaw gateway restart
```

Test:

```bash
openclaw agent --message "Use prettify-pdf to QA this redesigned receipt against the original PDF. Check IDs, timestamps, totals, labels, barcode visibility, and clipped text."
```

## OpenCode

OpenCode-compatible skill loaders commonly use `.opencode/skill/<name>/SKILL.md`.

```bash
mkdir -p .opencode/skill
git clone https://github.com/sethupavan12/prettify-pdf .opencode/skill/prettify-pdf
```

Then ask your OpenCode session:

```text
Use prettify-pdf to make this PDF clearer while preserving all exact source values and machine-readable assets.
```

## Optional Helper Dependencies

The skill works as instructions without dependencies. The optional local helper needs Python plus PyMuPDF and Pillow:

```bash
uv run --with pymupdf --with pillow python scripts/pdf_guardrails.py input.pdf --out /tmp/prettify-pdf-check
```

Use the helper when you want extracted text, rendered source pages, and embedded image assets for stricter QA.
