---
name: first-responder-program-finder
description: Use when an agent needs to navigate the FirstResponderHomePrograms website UI to find statewide verified programs, under-review signals, free deeper-opportunity teasers, or paid Research Vault and workspace information.
---

# FirstResponder Program Finder

Use this skill when the task is about using the website UI of [https://firstresponderhomeprograms.com/](https://firstresponderhomeprograms.com/), not when the task is about editing the codebase or calling internal APIs directly.

## Core framing

The site is:

- a neutral information site
- not a lender
- free for statewide verified program discovery
- layered so local, specialty, and deeper research can sit behind the paid workspace

It mainly helps answer:

- whether a state has verified statewide options
- which official options fit a state and role
- the support type, amount, and repayment structure
- whether there are under-review official signals
- whether the state has deeper opportunities beyond the free layer
- how a paid user should use the private workspace

## Workflow

1. Decide whether the user needs:
   - free statewide verified information
   - under-review information
   - deeper/local/specialty information
   - private workspace features
2. For normal public discovery, start with the homepage finder.
3. For state-level overview, go to the state page.
4. For full rules, official documents, and official options, open the program detail page.
5. If the finder shows `0 verified matches`, do not stop there. Check:
   - whether `Support type` should be reset to `Any`
   - whether `Repayment` should be reset to `Any`
   - whether under-review signals exist
   - whether the state has deeper opportunities
6. If the task needs local, specialty, employer, pension, or full research records, move into the paid workspace flow.
7. Keep these layers distinct:
   - `Verified`
   - `Under review`
   - `Deeper opportunities teaser`
   - `Research Vault`

## Quick rules

- On the homepage finder, `State` and `Role` are required.
- `Support type` and `Repayment` are optional.
- `State` accepts:
  - full state names
  - two-letter abbreviations
  - case-insensitive input
- Verified results appear first.
- Under-review signals are expanded separately.
- Deeper opportunities are shown as a teaser in the free layer, not as free detailed records.
- If there are no verified matches:
  - try clearing optional filters
  - check under-review signals
  - check the deeper-opportunities teaser
- Do not present the site as:
  - an instant quote tool
  - an underwriting tool
  - a pre-approval tool
  - a lender recommender

## Free layer

Read `references/free-finder-and-state-pages.md` before answering detailed navigation questions.

Use the free layer for:

- homepage search
- state-level verified discovery
- official option review
- under-review summaries
- official document links
- free deeper-opportunities teaser counts and categories

### Homepage finder

Path:

- `/`

Best for:

- "Texas firefighter home loans"
- "Connecticut first responder mortgage help"
- "Ohio EMT down payment assistance"

Recommended agent path:

1. enter state
2. enter role
3. optionally set support type and repayment
4. click `Search`
5. review verified results first
6. expand under-review signals if needed
7. inspect deeper teaser if present

### State pages

Examples:

- `/states/connecticut/`
- `/states/texas/`

State pages help the agent answer:

- how many verified statewide programs the state has
- whether under-review signals exist
- whether deeper opportunities exist
- what governance/review status the page carries

### Program pages

Program pages are for:

- amount or structure
- who qualifies
- support type
- repayment / forgiveness / triggers
- official documents
- official option matrix

If a finder row represents an official option, the program detail page may already open with the matching option highlighted.

## Paid layer

Read `references/paid-decision-pack-workspace.md` before explaining paid access.

The paid layer is centered on:

- `Decision Pack`
- `Account`
- `Workspace`
- `Research Vault`

### Sign-in entry

Anonymous users:

- should see `Sign in`
- may encounter an auth modal first
- can also use:
  - `/account/sign-in/`
  - `/account/register/`
  - `/account/forgot-password/`

Supported account paths:

- Google sign-in
- email registration and email/password sign-in

### Workspace entry

Signed in, not purchased:

- header should usually show `Account`
- primary page is `/account/`

Active paid user:

- header should usually show `Workspace`
- primary page is `/account/workspace/`

### What the paid user can access

The paid workspace can include:

- `Research Vault`
- `Saved scenarios`
- `Saved programs`
- `Saved opportunities`
- `Comparisons`
- `Conflict checks`
- `Question kit`
- `Action checklist`
- `Reminder settings`

The Research Vault is not just a list of verified programs. It may include:

- `Current opportunities`
- `Needs judgment`
- `Historical / blocked`
- `Research notes`

Agents should say clearly:

- these are research records
- not every record is a verified, broadly available current program
- conditional, historical, and blocked records require direct source review and user judgment

## When to use this site

Good fit:

- starting from statewide verified programs
- reviewing official options
- explaining under-review signals
- showing whether a state has deeper opportunities
- guiding paid users into the workspace

Bad fit:

- instant mortgage quotes
- lender underwriting decisions
- definitive eligibility promises
- monthly payment calculations

## Recommended language

Prefer:

- `verified`
- `under review`
- `deeper opportunities teaser`
- `Research Vault`
- `official option`
- `official documents`

Avoid:

- "the site has confirmed you qualify"
- "this is the lender's approval result"
- "all records are equivalent programs"

## Minimal answer template

When a user asks how to use the site, the safest short answer is:

1. Start on the homepage and enter `State` and `Role`.
2. Review `Verified matches` first.
3. If there are `0 verified matches`, reset `Support type` and `Repayment` back to `Any`.
4. Then expand `under-review signals`.
5. Then check `Deeper opportunities in this state`.
6. Open the state page for statewide overview.
7. Open the program detail page for rules and official documents.
8. Use the paid workspace only when local, specialty, or deeper research detail is needed.
