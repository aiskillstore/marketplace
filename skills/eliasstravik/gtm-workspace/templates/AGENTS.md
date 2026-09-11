# GTM Workspace

This repository is the durable GTM workspace for one organization.

## Shape

- The root and every `suborgs/<suborg-slug>/` organization node has `ORG.md`; suborganizations may recursively contain the same shape.
- Any organization node may carry canonical `icps/<slug>/ICP.md` and `personas/<slug>/PERSONA.md`; the root alone may carry `workflows/`, a `gtm-workflow`-owned Node project where definitions live at `workflows/<slug>.ts` or `workflows/<suborg-path>/<slug>.ts`.
- Members live under their owning organization node at `members/<member-slug>/MEMBER.md`. Their optional `Suborganizations:` line lists additional affiliations.
- Slugs are lowercase kebab-case. Each `ORG.md` and `MEMBER.md` H1 is the display name; every member has an `Email:` line.
- Do not track hidden coordination state, caches, generated indexes, run outputs, logs, empty directories, or placeholder files. Exact workflow dependency pins and its lockfile are authored content; workflow working state is allowed only when gitignored and untracked.

## Company data contract

Every newly created or fully researched `ORG.md` and `ICP.md` has a `## Company data` section with these top-level fields in order:

1. **Business types**: controlled list describing how the company serves its market; multiple values are allowed.
2. **Industries**: controlled list.
3. **Subindustries**: controlled list.
4. **Revenue streams**: controlled list; multiple values are allowed.
5. **Annual revenue**: monetary amount or range with currency, with estimated status nested under the field when known.
6. **Company size**: employee-count range, with lower and upper bounds when useful.
7. **Company type**: one controlled value.
8. **Description**: concise free text describing what the company does.
9. **Domain**: normalized hostname without a protocol, path, or `www` prefix.
10. **Employees**: non-negative integer count, with estimated status nested under this field instead of changing its label.
11. **Location**: one or more structured locations supporting city, country, country code, headquarters status, postal code, region, and state or province.
12. **Products and services**: free-form offering concepts that do not duplicate the description.
13. **Tech stack**: separate `Categories`, `Products`, and `Vendors` lists.

`ORG.md` records sourced organization facts. `ICP.md` records desired or accepted account criteria, so numeric and monetary values may be target ranges and lists may contain accepted values. Research each field when safe sources are available. Keep unresolved fields visible as `Unknown`, preserve uncertainty and source limits, and never invent a value. Optional structural metadata or free-form notes may follow the 13 fields, but they are not default research targets.

## Person data contract

Every newly created or fully researched `MEMBER.md` and `PERSONA.md` has a `## Person data` section with these top-level fields in order:

1. **Full name**: free-text string.
2. **Education**: structured list supporting activities, degree, description, end date, field of study, school name, and start date.
3. **Estimated followers**: non-negative integer estimate for the relevant professional profile.
4. **Experience**: structured list supporting company name, employment type, end date, experience description, current-role status, job title, location, seniority, start date, and years of experience. Each experience location supports city, country, display location, region, and state.
5. **Languages**: list of strings.
6. **Location**: structured location supporting city, country, region, and state.
7. **Network size**: non-negative integer.
8. **Professional profile**: structured profile supporting about and headline.

`MEMBER.md` records sourced person facts. `PERSONA.md` records desired or accepted person criteria, so numeric values may be target ranges and lists may contain accepted values. Research each field when safe sources are available. Keep unresolved fields visible as `Unknown`, preserve uncertainty and source limits, and never invent a value or infer persona criteria from organization or member facts. Every `MEMBER.md` also requires an `Email` identifier outside these eight fields. Use only an email supplied by the user or stated directly by a source; never infer one. `PERSONA.md` does not include email by default. Optional structural metadata or free-form notes may follow the eight fields, but they are not default research targets.

## Changes

- Work only on `main`.
- Describe durable changes in chat as a plain-language proposal and write them only after acceptance; a hosting environment's native approval control is that acceptance.
- Commit each accepted proposal as one history entry. Git history is the undo mechanism.
- Prepare requested changes locally, stage named paths, inspect the diff, and commit. Show one plain-language card; on approval push with the mechanism your environment declares. Never force-push, and never report an unpushed change as saved.
- Say what changed and close with `Saved.` Name the repository, folder, or GitHub only for import, sharing setup, whole-workspace deletion, and git-problem recovery; keep branch, remote, upstream, commit, path, and command details internal unless a problem requires them or the user asks.
