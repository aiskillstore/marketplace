# Quick start

## 1. Prepare the data

Use one well-structured Excel or CSV business table and state the question the review should answer. The current version processes one table per run.

## 2. Give it to an AI tool that can run local scripts

Make sure the host can read the supplied file and run local Python. A first prompt can be:

> Use sheet-to-report to analyze this spreadsheet for a monthly business review. Confirm any metric definition that could change the conclusion, then generate the HTML report. If I request a PPT, show two real theme sample pages before building the full deck.

You do not need to write code or JSON. The agent asks only when an ambiguity could change the conclusion.

## 3. Choose the outputs you need

- Generate the offline HTML report first and review the conclusions, definitions, and evidence.
- Generate the editable standard PPTX when you need a presentation.
- Optionally install [SlideViber](https://github.com/tf71991/slideviber-skill) for a refined deck. The HTML report and standard deck work without it.

[Live demo](https://majichuan.github.io/sheet-to-report/) · [FAQ](FAQ.en.md) · [Install](INSTALL.en.md) · [Back to overview](README.md)
