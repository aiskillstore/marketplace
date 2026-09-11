# Contributing

Contributions that improve correctness, portability, chart selection, report clarity, or supported business scenarios are welcome.

## Before opening an issue

- Use synthetic or fully anonymized data.
- Remove names, phone numbers, emails, account identifiers, internal URLs, credentials, and confidential business figures.
- State the operating system, Python and Node versions, host AI tool, input file type, requested outputs, and the first failing command.
- For a visual defect, describe the affected page, office software, and whether information was clipped, changed, or missing.

Use the bug, feature, or use-case issue template so evidence and scope stay clear. Do not upload a real business workbook to a public issue.

## Pull requests

1. Keep analysis behavior separate from presentation-only changes.
2. Preserve source and metric contracts across HTML and PPT outputs.
3. Add or update focused tests for material logic changes.
4. Run the public checks below from the repository root.

```bash
python scripts/environment_check.py --target html
python scripts/generate_sample.py --output-dir generated-sample --write-xlsx
python scripts/sheet_to_report.py --inspect generated-sample/synthetic-business.xlsx
```

If the change affects PPT output, also run the relevant standard or SlideViber environment check and inspect the rendered deck in PowerPoint or WPS. Do not hand-edit a generated final file to hide an authoring defect.

By contributing, you agree that your contribution is licensed under the repository's MIT License.