# Synthetic example

This repository intentionally does not ship a real or static business workbook. Generate a small synthetic example locally:

```bash
python scripts/generate_sample.py --output-dir generated-sample --write-xlsx
python scripts/sheet_to_report.py --inspect generated-sample/synthetic-business.xlsx
```

The generated workbook contains artificial channel, user, and business metrics. It is suitable for checking field inspection and discussing an analysis plan; it is not a benchmark dataset and carries no preset conclusion.

To exercise the full workflow, give the generated workbook and a business-review prompt to an AI tool that can read this Skill and execute local Python. The agent should build a new run directory and follow the contracts in `SKILL.md` and `references/`.