# Installation and usage

For a quick diagnosis, start with the [FAQ](FAQ.en.md). This page keeps the full setup and environment boundaries.

[简体中文](INSTALL.md)

The skill has three output levels. Install only what the requested level needs.

| Target | Required runtime |
| --- | --- |
| HTML report | Python 3.10+ with the packages in `requirements.txt`; a host AI tool that can read the workbook and run local scripts |
| Editable standard PPTX | HTML requirements plus Node.js 18+ and `python-pptx` 1.0+ |
| Optional SlideViber refinement | Standard-PPT requirements plus a separate SlideViber installation and its current dependencies |

PowerPoint or WPS is used to view and edit finished decks. It does not replace the analysis runtime.

## Install the skill

After the repository is published, use an Agent Skills-compatible installer:

```bash
npx skills add https://github.com/majichuan/sheet-to-report
```

Alternatively, download the release ZIP or copy the repository into the skill directory supported by your AI tool. Keep the directory structure intact and run commands from the installed skill root.

Install Python dependencies into the Python environment used by the host tool:

```bash
python --version
python -m pip install -r requirements.txt
python scripts/environment_check.py --target html
```

A passing environment check verifies declared package versions for the chosen target. It does not verify fonts, browser startup, Office rendering, or native editability.

## Start an analysis

Give the AI tool one structured Excel or CSV file and a business goal. For example:

> Use sheet-to-report to create a monthly business review for an operations lead. Inspect the fields first, confirm any definition that could change the conclusion, then generate an evidence-linked HTML report with key judgments, charts, limitations, and next actions.

The agent may inspect the input with:

```bash
python scripts/sheet_to_report.py --inspect "path/to/data.xlsx"
```

Choose either direct analysis or a confirmed analysis plan. Direct analysis still asks about ambiguous metrics, denominators, periods, or sensitive fields; it does not guess definitions. Content-operations and project-operations profiles currently require a confirmed plan.

The finished narrative is authored by the host agent under `SKILL.md` and `references/html-analysis.md`. Running the legacy `--request ... --output ...` command by itself is not equivalent to the current AI-driven workflow.

## Create the standard PPTX

Run the target-specific check first:

```bash
python scripts/environment_check.py --target standard
```

The standard deck uses the accepted report model and chapter projection. It is written with public `python-pptx` dependencies and does not require a Codex-private presentation library.

Theme behavior is consistent across hosts:

- An explicitly requested or previously accepted theme wins.
- If no theme is specified and the user has not delegated the choice, show candidate directions with a real cover page and chart page for each direction.
- If the user explicitly delegates the decision, use the `clean` / clear-business default.
- The full chapter deck currently accepts the verified `clean`, `corporate`, and `warm` configurations. An unverified full-deck theme must fail clearly rather than being advertised as supported.

After export, render and inspect the complete deck in PowerPoint or WPS. Fix authoring logic when text is clipped, objects overlap, or information is missing; do not hand-edit a final file to hide a generator defect.

## Optional SlideViber refinement

The standard PPTX is already a complete deliverable. If the user wants a more presentation-led composition, install [SlideViber](https://github.com/tf71991/slideviber-skill) separately and follow its current license and dependency instructions.

Check the target with the actual SlideViber directory:

```bash
python scripts/environment_check.py --target slideviber --slideviber-dir "path/to/slideviber"
```

The refined deck must inherit the accepted theme and the same evidence. Save it as a separate file. Do not remove body content, numbers, caveats, or source notes to make a page look cleaner. Complex SVG elements may require SlideViber's Chromium raster fallback; disclose any loss of native editability.

## Synthetic local check

```bash
python scripts/generate_sample.py --output-dir generated-sample --write-xlsx
python scripts/sheet_to_report.py --inspect generated-sample/synthetic-business.xlsx
```

This confirms sample generation and field inspection. It does not replace a host-agent analysis or a rendered PPT review.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Python or a package is missing | Confirm the exact interpreter used by the host tool, then install `requirements.txt` into that environment. |
| HTML passes but PPT fails | Run the `standard` or `slideviber` check; verify the actual Python, Node, fonts, and rendering application. |
| The skill changed during a run | Keep the old run directory and start a new run with the upgraded skill instead of editing stored fingerprints. |
| A conclusion is not supported | Confirm the definition or narrow the conclusion; do not manufacture evidence. |
| A page clips or drops information | Preserve the failed candidate, fix the authoring or layout layer, and export again. |
| Office substitutes fonts or objects | Record the application version and affected page, then check the actual font and object type. |

The bundled scripts do not call an external model API, but the host AI platform may read the supplied workbook. Review its data policy and remove personal or confidential fields before use.
