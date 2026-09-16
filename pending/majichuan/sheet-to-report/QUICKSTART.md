# Quick start

## 1. Prepare the data

Use one well-structured Excel or CSV business table and state the question the review should answer. The current version processes one table per run.

## 2. Give it to an AI tool that can run local scripts

Make sure the host can read the supplied file and run local Python. For a first run, confirm a short plan before generation:

> Use sheet-to-report to analyze this Excel file for a monthly review aimed at business leaders. Inspect the data first, then give me a short plan covering the recommended time range, the business questions worth answering, and any definitions I need to confirm. Wait for my confirmation before generating the HTML report. When it is complete, tell me how to continue to an editable PPT.

When the goal and definitions are already clear, ask for direct analysis:

> Use sheet-to-report to analyze this Excel file directly for a monthly review aimed at business leaders. Inspect the fields and time range first; ask only when an ambiguity could change the conclusion. Generate the HTML report first, then tell me how to continue to an editable PPT.

You do not need to write code or JSON. Both modes still pause for ambiguities that could change the conclusion.

## 3. Choose the outputs you need

- Generate the offline HTML report first and review the conclusions, definitions, and evidence.
- Reply “create the PPT” when you need a presentation. Clear Business is the first recommendation with no existing preference; real rendered pages should appear directly when preview is available, and any preview limitation should be stated before theme selection.
- The standard result should include a full-deck reading path and a separate editable PPTX. Reply “create the refined deck” to continue with the optional, separately installed [SlideViber](https://github.com/tf71991/slideviber-skill). The HTML report and standard deck work without it.

[Live demo](https://majichuan.github.io/sheet-to-report/) · [FAQ](FAQ.en.md) · [Install](INSTALL.en.md) · [Back to overview](README.md)
