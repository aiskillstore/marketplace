---
name: brewpage-publish-safe
description: "Publish approved content to BrewPage and update the exact published item. This Skillstore edition stores anonymous owner credentials in private application state. Supports HTML, Markdown, JSON, files and verified website archives."
allowed-tools: Bash(bash ${CLAUDE_SKILL_DIR}/scripts/brewpage-run.sh *)
license: MIT
---

# BrewPage Publish Safe

Publish or update only when the user explicitly requests that write and identifies the content or exact target. Installing or invoking the skill, preparing a draft, and asking for instructions are insufficient. Resolve missing access choices before a write. A local-only request makes no BrewPage request.

Use the bundled REST runner for this edition. It calls the official BrewPage API, automatically retains anonymous owner proof and private management links in the OS user's protected application state, and reports the reader link and storage result. Keep proof out of commands, transcripts and content. Use the regular BrewPage skill or MCP when the user explicitly needs connected account ownership or delivery of a private receipt.

Use `bash ${CLAUDE_SKILL_DIR}/scripts/brewpage-run.sh` with the installed skill path and the relevant literal arguments from the [usage guide](README.md). Run one bundled command at a time. Keep selected content and paths as argument values. Never generate shell code from them.

Review the selected content for credentials before publication. For a site, review its JSON archive manifest before authorizing flagged files. A `CONFIRM` result is pending, with no upload. Re-run with its digest only after the user approves that exact manifest. For an update, use the original workspace and exact saved reader link. A failed update never authorizes a new publication.

After `OWNER TOKEN SAVED` or `OWNER TOKEN REUSED`, report the confirmed reader URL and whether ownership was saved or reused. If the publication succeeded and recovery was saved, report both and use `owner-recover` in the same workspace. An uncertain create stays pending until its pending receipt is recovered or a verified first-party outcome is recorded through [protected reconciliation](README.md#resolve-an-uncertain-create). A new create needs separate authorization after recovery.
