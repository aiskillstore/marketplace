# sheet-to-report

[简体中文](README.zh-CN.md)

**Turn one business table into an evidence-led story with clear decisions and next actions.**

![sheet-to-report: from spreadsheet to evidence, charts, and actions](assets/brand/github-social-preview.png)

`sheet-to-report` is an Agent Skill for business reviews based on one well-structured Excel or CSV table. It helps an AI agent inspect the data, clarify metric definitions, identify material changes, connect conclusions to evidence, and produce an offline HTML report plus an optional editable presentation.

[Live demo](https://majichuan.github.io/sheet-to-report/) · [Quick start](QUICKSTART.md) · [FAQ](FAQ.en.md) · [Install](INSTALL.en.md)

**First run? [Follow the tutorial (Chinese)](https://majichuan.github.io/sheet-to-report/guide.html)**: download the fully synthetic 100,000-row practice workbook, choose direct analysis or plan-first, and follow the steps to HTML and optional PPT.


> v0.2 is Chinese-first. The full workflow has been accepted on several synthetic Chinese business scenarios; equivalent English-output acceptance is not yet complete.

## See it in action

The public demo uses a fully synthetic 100,000-row omnichannel workbook with 11 fields across 18 months. It contains no real company or personal data.

**[Open the complete public showcase](https://majichuan.github.io/sheet-to-report/)** · [Read the full HTML report](https://majichuan.github.io/sheet-to-report/report.html) · [Read the case walkthrough](DEMO.md)

The two images below show the same conclusion and numbers. The standard deck keeps the chart and text directly editable; the optional SlideViber pass changes the composition and visual hierarchy without dropping material information.

| Editable standard deck | Optional SlideViber refinement |
| --- | --- |
| ![Standard deck: a full-width editable chart shows that paid advertising return fell from the prior-year period](assets/screenshots/standard-ppt-chart.png) | ![SlideViber-refined deck: the business interpretation sits beside the same chart evidence](assets/screenshots/slideviber-ppt-chart.png) |

The online showcase compares four matching page pairs and provides both complete 23-slide demo decks: [download the editable standard PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-standard.pptx) or [download the SlideViber-refined PPTX](https://majichuan.github.io/sheet-to-report/downloads/sheet-to-report-demo-slideviber.pptx).

## Understand it in 30 seconds

- **For:** operations, sales, product, and business owners preparing weekly reviews, monthly reviews, campaign retrospectives, or management updates.
- **Bring:** one structured Excel or CSV table, the intended audience, and the question you want the report to answer.
- **Get:** an offline HTML report, an optional editable standard PPTX, and an optional SlideViber-refined deck.
- **Your role:** provide the data and goal and confirm material definitions. The agent checks, analyzes, builds the evidence trail, and produces the report.

## Why choose sheet-to-report

**Understand the change, follow the story, and know what to do next.**

- **Find the questions that matter.** It looks for material changes, opportunities, and risks around the reporting goal, then drills down only where the data supports it.
- **Keep conclusions traceable and bounded.** Key numbers retain their definitions and comparison scopes. When the data cannot support a claim, the report says so.
- **Turn separate findings into one reporting story.** Overall performance, important changes, supporting detail, business meaning, and next actions follow a deliberate sequence; charts and text reinforce the same point.
- **Make actions testable.** Recommendations identify the affected business object or process, the step to take, the signal to watch, and the condition for changing course.
- **Keep one source of truth across formats.** HTML, the editable standard deck, and the optional refined deck share the same analysis basis; visual refinement must not change the numbers, definitions, or decisions.

## Before you start

Use an AI tool that can read local files and run code. Prepare one structured Excel or CSV table plus the intended audience and reporting question. You do not need to write code or JSON; ask the agent to check the environment first.

HTML requires Python 3.10+ and the listed dependencies. Standard PPT export also needs Node.js 18+, `python-pptx`, and an available preview tool. SlideViber is installed separately. See [INSTALL.en.md](INSTALL.en.md). Remove or anonymize personal and sensitive data before uploading it. A skill listing by itself does not give the host platform a working model, file access, or artifact-generation runtime.

## From spreadsheet to report

| Stage | What the agent does | What you do | Visible result |
| --- | --- | --- | --- |
| 1. Set the scope | Checks the file, fields, time range, and runtime; proposes a short plan or starts analysis | State the goal and confirm material definitions when needed | A clear scope and any remaining questions |
| 2. Build the HTML report | Investigates business questions, verifies evidence, connects conclusions and actions, and checks the file | Review or request changes; stop here if HTML is enough | An openable HTML report and explicit check status |
| 3. Build a standard deck (optional) | Shows real theme samples when preview is available, then builds the selected full deck | Reply “create the PPT” and choose a theme | Theme previews, a full-deck reading path, and an editable PPTX |
| 4. Refine the deck (optional) | Checks SlideViber and recomposes the same approved analysis | Reply “create the refined deck” | A separate refined deck and preview; the standard deck remains |

The number of confirmations depends on real ambiguity, the selected start mode, existing preferences, and the host runtime. The agent should not repeat questions that have already been answered.

## Two ways to start

**Recommended for a first run: confirm a short analysis plan.**

> Use sheet-to-report to analyze this Excel file for a monthly review aimed at business leaders. Inspect the data first, then give me a short plan covering the recommended time range, the business questions worth answering, and any definitions I need to confirm. Wait for my confirmation before generating the HTML report. When it is complete, tell me how to continue to an editable PPT.

The plan should contain only the scope, priority questions, required confirmations, and expected output. You can then revise or approve it in normal business language.

**When the goal and definitions are already clear: analyze directly.**

> Use sheet-to-report to analyze this Excel file directly for a monthly review aimed at business leaders. Inspect the fields and time range first; ask only when an ambiguity could change the conclusion. Generate the HTML report first, then tell me how to continue to an editable PPT.

Both modes still pause for real ambiguities. Experimental business profiles may require a confirmed plan so that “direct” does not bypass a quality boundary.

## Continue after HTML

The agent should deliver an openable report, distinguish completed checks from unverified ones, and tell you that you can reply “create the PPT” if needed. With no existing preference, Clear Business is the first recommendation. Real rendered PPT pages should appear directly when the host supports preview; otherwise the limitation must be stated before theme selection, with a choice between a text-only direction or explicit authorization to use the recommendation.

After the standard deck, the agent should provide a full-deck reading path and a separate editable PPTX. You can reply “create the refined deck” to continue with SlideViber. SlideViber is optional and separately installed; the standard deck remains available, and chart editability may differ.

## Install

### Claude Code plugin

This repository is also packaged as a single-skill Claude Code plugin. The root `SKILL.md` remains the sole capability entrypoint; `.claude-plugin/plugin.json` only adds marketplace metadata, so the Claude distribution does not fork the analysis workflow.

Add the author-hosted marketplace and install the plugin from inside Claude Code:

```text
/plugin marketplace add majichuan/sheet-to-report
/plugin install sheet-to-report@majichuan-skills
```

This is a GitHub-hosted installation entry maintained by the author. It does not imply approval or inclusion in Anthropic's community directory.

To validate or preview a local clone:

```bash
claude plugin validate . --strict
claude --plugin-dir .
```

### Agent Skills installer

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

## Privacy, terms, and support

- [Privacy Policy](PRIVACY.md)
- [Terms of Use](TERMS.md)
- [Support](SUPPORT.md)
- [Security reporting](SECURITY.md)

## License

[MIT](LICENSE). Third-party and synthetic-data notices are in [NOTICE.md](NOTICE.md).
