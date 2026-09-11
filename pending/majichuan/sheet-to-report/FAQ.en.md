# FAQ

## Can I use it without writing code?

Yes. Give one well-structured Excel or CSV table and a reporting goal to an AI tool that can access local files and run scripts. The agent runs the commands and asks only when a date, metric definition, or business object could change the conclusion.

## What is the minimum setup?

- **HTML only:** Python 3.10+ and the base packages in `requirements.txt`.
- **Editable standard PPTX:** Node.js 18+ and `python-pptx` are also required.
- **Refined PPTX:** install SlideViber separately only if you want that optional step.

Run from the skill directory:

```bash
python scripts/environment_check.py --target html
```

See [INSTALL.en.md](INSTALL.en.md) for the full setup.

## Why does the agent ask questions?

Direct analysis resolves high-confidence fields automatically. The agent must ask when multiple date columns, ratio denominators, customer/order grain, or incomplete periods could change the answer. It should explain the business impact instead of asking you to fill technical configuration.

## What if the workbook has several sheets?

The current version analyzes one structured table per run. Select one sheet first. Multi-sheet joins, multi-row headers, and merged cells are outside the current scope.

## What if HTML succeeds but PPT export fails?

Keep the HTML and run the environment check for the next output. A standard-deck failure must not invalidate the HTML; a refinement failure must not overwrite the accepted HTML or standard deck.

## Is SlideViber required?

No. It is an optional visual refinement step. HTML and the editable standard deck remain independently usable.

## Does a model account, API, permission, or quota error mean the skill is broken?

Not necessarily. The host platform may have failed before the model ran the skill. Confirm that the host model works, then check whether the skill actually started reading the file.

## What should I include in a bug report?

Include the failed stage, the exact error text, operating system and AI host, and whether HTML or a standard deck was already produced. Remove or replace private business and personal data before posting publicly.
