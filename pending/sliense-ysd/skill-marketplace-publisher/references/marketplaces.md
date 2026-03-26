# Skill Marketplace Notes

Updated: `2026-03-26`

This file records the currently verified marketplace routes used by `skill-marketplace-publisher`.

## Skillstore

Verified live surfaces:

- submit page: `https://skillstore.io/submit`
- developer docs: `https://skillstore.io/docs/developers`
- marketplace repo: `https://github.com/aiskillstore/marketplace`

Verified behavior:

- submit page requires a GitHub repository URL and accepts optional notes
- front-end posts to `https://skillstore.io/api/submit`
- successful submission returns a `submission_id`
- status page lives at `https://skillstore.io/submissions/<id>`
- official marketplace repo states submitted skills must contain a valid `SKILL.md`
- official repo describes automated security analysis and PR-based review

Observed public requirements:

- valid `SKILL.md`
- public GitHub repo or public subdirectory URL
- permissive license recommended
- skills with scripts get extra security review

Useful links:

- `https://skillstore.io/submit`
- `https://skillstore.io/docs/developers`
- `https://github.com/aiskillstore/marketplace`

## SkillMap

Verified live surfaces:

- home: `https://skillmaps.net/`
- marketplace pages and detail pages
- feedback page: `https://skillmaps.net/feedback`
- contact page: `https://skillmaps.net/contact`

Verified behavior:

- detail pages expose GitHub source links for listed skills
- feedback page posts to `https://skillmaps.net/v1/feedback`
- contact page lists the marketplace contact email `pm@vibemanager.net`

Current limitation:

- no clearly documented self-serve “submit your skill” form was verified on `2026-03-26`
- use public GitHub repo + feedback/contact request as the currently verified intake path

Recommended request content:

- repo URL
- skill name
- one-line summary
- install path notes if applicable
- why it is safe/public-ready

Useful links:

- `https://skillmaps.net/feedback`
- `https://skillmaps.net/contact`

## CrowdHub

Status on `2026-03-26`:

- no verified live skill marketplace submission surface was confirmed for this workflow
- do not treat `CrowdHub` as supported unless a current official marketplace URL is provided and re-verified

## Notes For Future Updates

When any marketplace changes, update this file with:

1. exact date checked
2. exact live URL
3. whether submission is self-serve, API-based, PR-based, or manual
4. whether the route was actually tested
