# Release Checklist

Use this before tagging a public release.

## Repository Hygiene

- No real PDFs, receipts, licenses, invoices, IDs, or screenshots with personal data.
- No generated files under `output/`, `outputs/`, `uploads/`, or `tmp/`.
- No `.env`, API keys, tokens, cookies, or credentials.
- `README.md` has current install and usage instructions.
- `CHANGELOG.md` has a release entry.
- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md` exist.

## Skill Compatibility

- Directory name matches `SKILL.md` frontmatter `name`.
- `name` uses lowercase letters, numbers, and hyphens.
- `description` explains what the skill does and when to use it.
- `SKILL.md` remains concise enough for agent context.
- Optional resources are referenced clearly from `SKILL.md`.
- No hosted service, API key, or provider-specific dependency is required.

## Validation

```bash
python scripts/validate_skill.py .
python -m py_compile scripts/pdf_guardrails.py scripts/validate_skill.py
```

Optional:

```bash
uv run --with pymupdf --with pillow python scripts/pdf_guardrails.py safe-sample.pdf --out /tmp/prettify-pdf-check
```

## GitHub Release

1. Update `CHANGELOG.md`.
2. Confirm validation passes.
3. Tag the release:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. Create a GitHub release with:
   - What changed.
   - Install command.
   - Compatibility note.
   - Privacy warning not to upload real documents to public issues.

## Discovery

To make the repo easier to find:

- Add GitHub topics: `agent-skills`, `skill-md`, `pdf`, `pdf-tools`, `document-ai`, `codex`, `claude-code`, `local-first`, `privacy`.
- Use a concise repo description: `Agent Skill for prettifying PDFs without breaking IDs, barcodes, dates, amounts, or source meaning.`
- Pin a demo issue or discussion with synthetic before/after examples.
- Submit to directory listings using [publishing-directories.md](publishing-directories.md).
