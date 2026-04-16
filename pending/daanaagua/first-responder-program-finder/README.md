# first-responder-program-finder

Installable Codex skill for navigating the public website at [https://firstresponderhomeprograms.com/](https://firstresponderhomeprograms.com/).

This skill teaches an agent how to:

- use the free homepage finder
- inspect state pages and program detail pages
- distinguish verified results, under-review signals, and deeper-opportunity teasers
- guide a signed-in or paid user into the private Decision Pack workspace
- explain what the site can and cannot claim

## Scope

Use this skill for website UI navigation and interpretation.

Do **not** use it as the main path when the task is:

- editing the site codebase
- querying internal JSON artifacts directly
- calling worker APIs directly
- modifying billing, auth, or database logic

## Files

- `SKILL.md` — installable skill definition
- `references/free-finder-and-state-pages.md` — free layer navigation
- `references/paid-decision-pack-workspace.md` — paid layer and workspace navigation

