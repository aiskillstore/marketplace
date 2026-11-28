# Technical audit: from finding to verified fix

> Part of the visdenda-agent skill. Back to https://visdenda.com/skills/visdenda-agent/SKILL.md.
> Read this when the task matches: Explain the finding, fix the page, re-check the rule, then decide what else changes.

## Read the latest run, not the whole history

`diagnose_site` ranks failing rules from the latest completed run by page count and links
each rule to a P0/P1 search update when the rule came from one. `get_audit_findings` gives
the per-page findings with status, severity, detail and `evidenceKey`.

Use `warn` and `fail` differently:

- `fail` is a conclusion that the page violates the rule.
- `warn` is a signal worth review; it does not mean the same as fail.
- `na` means the rule could not be evaluated on that page. It is not a pass.

## Explain before editing

Call `explain_finding` for the rule title, category, stored detail, documentation link and
verification guidance. Quote the `evidenceKey` when you report the finding; it is how a human
can replay the evidence. Do not invent a cause beyond the stored detail.

## Fix in the right layer

- Page-level markup/content → edit the page.
- Template-wide issue → change the template, not one page.
- Crawl/index directive issue → check `get_page_report` and a live `audit_url` before changing robots,
  canonical or hreflang.
- If the site is not verified, stop and ask the user to verify ownership.

## Verify the rule

After the change, run `audit_url` with both `url` and `siteId`: it evaluates the applicable
rules on that page and diffs against the latest completed run (fixed / regressed / still
failing). Then call `verify_fix` with the site and `findingStateId`, plus an idempotency key.
A pass resolves the finding as fix-applied; anything else records the verdict and leaves it open.

`verify_fix` is a rule recheck. It is not a traffic experiment. For traffic effects, use the
28-day GSC window and say the result is not yet conclusive.

## Close the loop

- `get_finding_lifecycle` for backlog age and resolutions.
- `compare_audit_runs` for what changed across two full runs.
- `get_project_status` for the next action and current run state.
- A full `run_audit` commits finding state; use it when the change is broad, not for every
  single-page edit.
