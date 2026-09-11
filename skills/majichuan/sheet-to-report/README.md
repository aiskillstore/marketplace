# sheet-to-report

[简体中文](README.zh-CN.md)

**Turn one structured business table into an evidence-traceable report that is ready to read, discuss, and present.**

![sheet-to-report: from spreadsheet to evidence, charts, and actions](assets/brand/github-social-preview.png)

`sheet-to-report` is an Agent Skill for business reviews based on one well-structured Excel or CSV table. It helps an AI agent inspect the data, clarify metric definitions, identify material changes, connect conclusions to evidence, and produce an offline HTML report plus an optional editable presentation.

> **First use:** give the file to an AI tool that can read local files and run Python, then ask it to use `sheet-to-report` for a monthly business review and generate the HTML first. You do not need to write code or JSON; the agent asks only when an ambiguity could change the conclusion.

[Live demo](https://majichuan.github.io/sheet-to-report/) · [Quick start](QUICKSTART.md) · [FAQ](FAQ.en.md) · [Install](INSTALL.en.md)

> v0.2 is Chinese-first. The full workflow has been accepted on several synthetic Chinese business scenarios; equivalent English-output acceptance is not yet complete.

## See it in action

The public demo uses a fully synthetic 100,000-row omnichannel workbook with 11 fields across 18 months. It contains no real company or personal data.

**[Open the complete public showcase](https://majichuan.github.io/sheet-to-report/)** · [Read the full HTML report](https://majichuan.github.io/sheet-to-report/report.html) · [Read the case walkthrough](DEMO.md)

The two images below show the same conclusion and numbers. The standard deck keeps the chart and text directly editable; the optional SlideViber pass changes the composition and visual hierarchy without dropping material information.

| Editable standard deck | Optional SlideViber refinement |
| --- | --- |
| ![Standard deck: a full-width editable chart shows that paid advertising return fell from the prior-year period](assets/screenshots/standard-ppt-chart.png) | ![SlideViber-refined deck: the business interpretation sits beside the same chart evidence](assets/screenshots/slideviber-ppt-chart.png) |

The online showcase compares four matching page pairs and provides both complete 23-slide demo decks: [download the editable standard PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-standard.pptx) or [download the SlideViber-refined PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-slideviber.pptx).

## Outputs

| Output | Purpose |
| --- | --- |
| **Offline HTML report** | Read the overall picture, key judgments, evidence-linked charts, limitations, and next actions in one navigable file. |
| **Editable standard PPTX** | Present the same analysis as a structured business story with section guidance, source notes, and editable charts and text. |
| **SlideViber-refined PPTX (optional)** | Recompose the approved content for stronger visual communication while preserving the standard deck and all material information. |

## What makes it useful

- **Analysis before layout.** It starts from the business question and semantic contract instead of filling a fixed report template.
- **Evidence you can trace.** Metrics keep their definitions, periods, filters, and source relationships; unsupported claims are narrowed or rejected.
- **Charts chosen for the conclusion.** The skill matches chart form to the comparison, trend, distribution, relationship, or process that needs to be explained.
- **Actions with owners and checks.** Recommendations specify the actual object or role, the action, the validation signal, and the boundary.
- **One source of truth across formats.** HTML, the standard deck, and the optional refined deck share the same analysis model and numeric evidence.

## Install

An Agent Skills-compatible installer can add it directly from GitHub:

```bash
npx skills add https://github.com/majichuan/sheet-to-report --skill sheet-to-report
```

View the public listing and install count on [skills.sh](https://skills.sh/majichuan/sheet-to-report/sheet-to-report).

You can also download a release ZIP or copy the repository into the skill directory supported by your AI tool. Keep `SKILL.md`, `references/`, `scripts/`, and `assets/` together.

Check the local runtime from the skill directory:

```bash
python --version
python scripts/environment_check.py --target html
```

See [INSTALL.en.md](INSTALL.en.md) for standard PPT and optional SlideViber requirements.

For file, environment, metric-definition, or host-model errors, see the [FAQ](FAQ.en.md). Outputs are staged, so a later PPT or refinement failure should not remove an already accepted HTML report or standard deck.

## Try it with synthetic data

```bash
python scripts/generate_sample.py --output-dir generated-sample --write-xlsx
python scripts/sheet_to_report.py --inspect generated-sample/synthetic-business.xlsx
```

Then give the spreadsheet to an AI tool that can read local files and run Python, for example:

> Use sheet-to-report to analyze this spreadsheet for a monthly business review. Confirm any metric definition that could change the conclusion, then generate the HTML report. If I request a PPT, show two real theme sample pages before building the full deck.

The agent performs the analysis and report-authoring workflow described in `SKILL.md`; the CLI inspection command alone does not generate the finished narrative.

## Requirements and boundaries

- Python 3.10+ for analysis and HTML workflow.
- Node.js 18+ and `python-pptx` 1.0+ for the current standard PPT workflow.
- [SlideViber](https://github.com/tf71991/slideviber-skill) is optional, installed separately, and governed by its own license.
- One structured Excel or CSV table per run. Multi-table joins, database connections, and scheduled background execution are outside v0.2.
- The host AI tool must be able to access the supplied file and execute local scripts. Compatibility differs by tool and operating system.
- Do not use this skill for medical, investment, credit, employee-rating, or other high-stakes decisions.

Before reporting a bug, remove or replace private business data. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Third-party and synthetic-data notices are in [NOTICE.md](NOTICE.md).
