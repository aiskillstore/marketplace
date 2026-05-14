# Contributing

Thanks for helping improve `prettify-pdf`.

This repository is a pure Agent Skill. Keep contributions focused on skill instructions, local helper scripts, validation, examples, and documentation.

## Principles

- Preserve source truth over visual polish.
- Keep the skill provider-neutral. Do not require a specific LLM, API key, hosted service, or server.
- Treat real PDFs as sensitive. Do not commit private receipts, IDs, invoices, licenses, bank references, or screenshots containing personal data.
- Prefer deterministic local checks where possible.
- Keep `SKILL.md` concise. Move detailed guidance into `references/` or `docs/`.

## Local Checks

Run these before opening a pull request:

```bash
python scripts/validate_skill.py .
python -m py_compile scripts/pdf_guardrails.py scripts/validate_skill.py
```

If you have optional dependencies installed, smoke-test the helper:

```bash
python -m pip install pymupdf pillow
python scripts/pdf_guardrails.py path/to/safe-sample.pdf --out /tmp/prettify-pdf-check
```

Use only public, synthetic, or redacted PDFs for examples and tests.

## Pull Request Checklist

- `SKILL.md` still has valid YAML frontmatter.
- The skill directory remains self-contained.
- No generated outputs, private PDFs, or screenshots are committed.
- New behavior is covered in `evals/evals.json` or `examples/prompts.md` when useful.
- Documentation mentions any new optional dependency.
- `scripts/validate_skill.py .` passes.

## Good First Contributions

- Add public-safe eval prompts for new PDF types.
- Improve barcode, QR code, seal, or stamp detection in `scripts/pdf_guardrails.py`.
- Add examples for different agents.
- Improve visual QA guidance for multi-page documents.
- Add synthetic fixtures that contain no personal or official data.
