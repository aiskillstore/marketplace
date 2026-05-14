# prettify-pdf

[![skills.sh](https://skills.sh/b/sethupavan12/prettify-pdf)](https://skills.sh/sethupavan12/prettify-pdf)

Make PDFs easier to read without breaking the facts that make them official.

`prettify-pdf` is an open, provider-neutral Agent Skill for redesigning and QAing PDFs that contain high-stakes information: receipts, invoices, appointments, tickets, government forms, reports, resumes, statements, and anything with IDs, dates, amounts, barcodes, QR codes, seals, stamps, or signatures.

The skill is intentionally local and model-agnostic. It does not require an API key, hosted service, server, or specific LLM provider.

## Why It Exists

Most "make this PDF prettier" workflows fail in the worst possible place: they make the document look nicer while quietly changing a receipt number, clipping a timestamp, relabeling a name, dropping a barcode, or hiding a required action.

This skill teaches an agent to treat the original PDF as evidence, then redesign around reader clarity with a strict visual verification gate.

## Install

Clone the repo into a skills directory supported by your agent.

For Codex-style local skills:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/sethupavan12/prettify-pdf "${CODEX_HOME:-$HOME/.codex}/skills/prettify-pdf"
```

For Claude Code-style personal skills:

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.claude/skills/prettify-pdf"
```

For project-scoped skills, copy or vendor this folder into your project skill directory, for example `.claude/skills/prettify-pdf/`.

OpenClaw shared skill:

```bash
mkdir -p "$HOME/.openclaw/skills"
git clone https://github.com/sethupavan12/prettify-pdf "$HOME/.openclaw/skills/prettify-pdf"
openclaw skills list
```

Directory / package-manager installs:

```bash
npx skills add sethupavan12/prettify-pdf
```

More platform-specific commands are in [docs/usage-claude-openclaw.md](docs/usage-claude-openclaw.md).

## Use

Ask your agent to use the skill on a PDF:

```text
Use $prettify-pdf to redesign this payment receipt. Keep all IDs, amounts, dates, timestamps, barcode, and seal exactly intact.
```

```text
Use $prettify-pdf to make this appointment confirmation easier to read. Highlight the date, time, location, applicant, reference number, and required documents.
```

```text
Use $prettify-pdf to QA this redesigned invoice against the original PDF. Find any changed IDs, totals, dates, payment terms, missing logo, missing barcode, or layout collisions.
```

More examples are in [examples/prompts.md](examples/prompts.md).

## Directory Links

- GitHub: [sethupavan12/prettify-pdf](https://github.com/sethupavan12/prettify-pdf)
- skills.sh install: `npx skills add sethupavan12/prettify-pdf`
- Directory publishing notes: [docs/publishing-directories.md](docs/publishing-directories.md)

## What The Skill Enforces

- Preserve source values exactly: IDs, timestamps, dates, names, amounts, totals, addresses, notes, and line items.
- Preserve source labels and meaning. Ambiguous adjacent text must not be relabeled into a guessed relationship or role.
- Preserve machine-readable and official assets: QR codes, barcodes, seals, stamps, signatures, and logos.
- Render the final PDF to images before delivery.
- Compare source and final renders visually, because text extraction can pass while the page is still visually wrong.
- Treat clipping, collisions, missing assets, altered punctuation, or changed label meaning as blocking failures.

## Repository Layout

```text
prettify-pdf/
├── SKILL.md
├── references/
│   └── quality-checklist.md
├── scripts/
│   ├── pdf_guardrails.py
│   └── validate_skill.py
├── examples/
│   └── prompts.md
├── docs/
│   ├── agent-compatibility.md
│   ├── launch-plan.md
│   ├── publishing-directories.md
│   ├── quality-gates.md
│   ├── release-checklist.md
│   └── usage-claude-openclaw.md
├── evals/
│   └── evals.json
└── agents/
    └── default.yaml
```

`SKILL.md` is the only required skill file. Everything else supports open-source use, validation, examples, and repeatable QA.

## Optional Local Guardrail Helper

The helper extracts source evidence for sensitive PDF redesigns:

```bash
python scripts/pdf_guardrails.py ~/Downloads/example.pdf --out /tmp/prettify-pdf-check
```

It writes:

- `extracted-text.txt`
- `manifest.json`
- rendered page images
- extracted embedded images such as barcodes, QR codes, seals, logos, stamps, and signatures

Install optional helper dependencies:

```bash
python -m pip install pymupdf pillow
```

Or run without modifying your environment:

```bash
uv run --with pymupdf --with pillow python scripts/pdf_guardrails.py ~/Downloads/example.pdf --out /tmp/prettify-pdf-check
```

## Validate

Run the release checks:

```bash
python scripts/validate_skill.py .
python -m py_compile scripts/pdf_guardrails.py scripts/validate_skill.py
```

If you have the local Codex skill validator available, this also passes:

```bash
python /path/to/quick_validate.py .
```

## Contributing

Contributions are welcome, especially better validation heuristics, examples, eval cases, and agent compatibility notes. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

For launch positioning, repository topics, and announcement copy, see [docs/launch-plan.md](docs/launch-plan.md).
For directory submission steps, see [docs/publishing-directories.md](docs/publishing-directories.md).

## Security And Privacy

Do not commit real receipts, IDs, licenses, invoices, or other private PDFs. Keep generated outputs under ignored folders such as `output/`, `outputs/`, `uploads/`, or `tmp/`.

Report issues privately using [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
