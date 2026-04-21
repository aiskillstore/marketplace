# Verification Playbook

Use this playbook after every submission attempt.

## Verification Ladder

Prefer stronger evidence over weaker evidence:

1. Public status API or public status page
2. Public detail page for the exact skill
3. Public search or registry API that returns the skill
4. Official CLI search or install path that resolves the skill
5. Generic site search or category listing
6. Negative result plus a known review queue or login gate

Do not treat a successful submit response alone as proof that a skill is publicly visible.

## Response Semantics

Interpret submit responses before deciding what to verify next:

- `alreadyExists` or `updated`: the market recognized an existing listing or repo import; verify the public detail pages.
- `processing`, `workflow_run_url`, or `submission received`: the intake pipeline accepted the request; the listing may still be private or pending review.
- `201 created` with a submission ID: treat this as queue admission unless the market also exposes a public detail page immediately.
- duplicate-name or pending-review errors: often a listing identity collision, not a transport or payload failure.
- HTTP 200 plus a redirect to `/skill/<slug>`: usually stronger than a flash message, because it proves a public detail page exists.

## Reusable Checks By Market

### AgentSkill.sh

- Best signal: public author or skill page.
- Check:
  - `https://agentskill.sh/@<owner>/<skill-name>`
  - creator pages under `https://agentskill.sh/@<owner>`
- Interpretation:
  - success payload with `updated` means the repo was re-imported, not newly created
  - public page exists: listed
  - submit API accepted but no page yet: re-check import scope and indexing delay

### Skillstore

- Best signal: public status API plus public status page.
- Check:
  - `GET https://skillstore.io/api/submit?id=<submission_id>`
  - `https://skillstore.io/submissions/<submission_id>`
- Stronger public evidence:
  - linked marketplace PR in the status payload or status page
- Interpretation:
  - `processing` plus `workflow_run_url`: accepted into the intake pipeline
  - `estimated_skills` greater than `1` after a folder URL: treat the submit as pack-scoped until the final listing proves otherwise
  - `approved`: accepted into the processing pipeline
  - public PR present: intake finished and marketplace change was generated

### Skillz Directory

- Best signal: public Convex query plus public detail page.
- Check:
  - `POST https://knowing-wren-258.convex.cloud/api/query`
  - payload: `{"path":"skills:list","args":{"search":"<skill-name>"}}`
  - detail page: `https://www.skillz.directory/skills/<slug>`
- Interpretation:
  - bare `{"success":true}` submit response is only transport success
  - query hit plus live detail page: public
  - empty query result after submit response: likely pending review or blocked before publish

### SkillNet

- Best signal: public search API or official CLI search.
- Check:
  - `GET http://api-skillnet.openkg.cn/v1/search?q=<skill-name>`
  - `skillnet search "<skill-name>"`
- Optional quality check:
  - `skillnet evaluate <path-or-url>` for a local or published skill
- Interpretation:
  - search hit: indexed
  - no hit: not indexed yet or contribution not accepted

### skills.sh

- Best signal: public search API or official install/search tooling.
- Check:
  - `https://skills.sh/api/search?q=<query>&limit=10`
  - `npx -y skills find <query>`
- Interpretation:
  - hit returned: indexed
  - no hit: not indexed or not installable through this ecosystem

### Skills Directory (`skillsdirectory.com`)

- Best signal: public registry API.
- Check:
  - `GET https://skillsdirectory.com/api/registry?q=<query>`
  - detail: `GET https://skillsdirectory.com/api/registry/<slug>`
  - public page: `https://www.skillsdirectory.com/skills/<slug>`
- Interpretation:
  - registry hit: public
  - no hit after submit: pending review or rejected

### agent-skills.md

- Best signal: public detail page after repo intake.
- Check:
  - `https://agent-skills.md/skills/<owner>/<repo>/<skill-name>`
- Interpretation:
  - `skillsAdded` or `alreadyExists` in the submit response only describes intake behavior
  - public detail page exists: listed
  - repo accepted but no public page: still importing or rejected

### SkillsMD

- Best signal: public registry search after review.
- Check:
  - `https://skillsmd.dev/api/search?q=<skill-name>`
  - homepage registry search when it is public
- Interpretation:
  - `201` plus a submission ID means queued for review
  - search hit or public registry entry: live
  - empty search after a fresh `201`: still pending review

### skills.re

- Best signal: public author and skill APIs plus SSR detail pages.
- Check:
  - `POST https://skills.re/api/rpc/skills/getAuthorByHandle`
  - `POST https://skills.re/api/rpc/skills/getByPath`
  - `https://skills.re/author/<handle>`
  - `https://skills.re/skill/<handle>/<repo>/<skill-slug>`
- Interpretation:
  - author API hit plus skill API hit: public
  - root-pack repo accepted by preview or submit APIs can still be valid even if submit-page copy mentions a repo-root `skills/` directory
  - no public record after submit: pending review, blocked, or surface changed

### AgentSkillsRepo

- Best signal: site search and generated detail page.
- Check:
  - `https://agentskillsrepo.com/search?q=<query>`
  - public detail page if the market generated one
- Interpretation:
  - search hit: listed
  - no hit: still pending review or not accepted

### SkillHub

- Best signal: public skills listing plus detail page.
- Check:
  - `https://www.skillhub.club/skills`
  - expected detail page such as `https://www.skillhub.club/skills/<slug>`
- Optional operator check:
  - authenticated CLI output after `skillhub publish`
- Interpretation:
  - public detail page: listed
  - CLI success but no public page yet: likely pending propagation or publish not completed

### skillshop.sh

- Best signal: public skill detail API.
- Check:
  - `GET https://skillshop.sh/api/skills/<org>/<repo>`
  - optional page: `https://skillshop.sh/skills/<org>/<repo>`
- Interpretation:
  - payload exists and `purchasable` is true: listed and buyable
  - no payload: repo has not been indexed or seller setup is incomplete

### SkillHQ

- Best signal: public sales page and install path.
- Check:
  - expected public page under `https://skillhq.dev/s/<slug>` if the platform issues one
  - official install flow described by SkillHQ docs
- Interpretation:
  - validated locally is not enough; wait for the public listing

### Bogen.ai

- Best signal: public skills directory listing after review.
- Check:
  - `https://www.bogen.ai/skills/`
- Interpretation:
  - duplicate-name or pending-review `400` means the listing name is already in the review or publish pipeline
  - submit success page alone means only that the form was accepted
  - public listing is required before claiming success

### skillsrep.com

- Best signal: final redirect URL or public detail page.
- Check:
  - final redirect target after submit, typically `https://skillsrep.com/skill/<slug>`
  - `https://skillsrep.com/search?q=<query>`
- Interpretation:
  - redirect to a public detail page: public
  - missing success flash with a public detail page still counts as success
  - submit response without a redirect or public page: pending review or changed form behavior

### Skills Directory (`skillsdir.dev`), mdskills.ai, Skillery, SkillsZoo, Agent Skills Index, skillscatalog.ai

- Best signal: public listing or search result on the official site.
- Use official review queues, detail pages, or search pages if available.
- If the site is login-gated or the documented endpoint is broken, classify the outcome as:
  - `pending review`
  - `login required`
  - `blocked by current platform behavior`
  - `surface changed, needs recon`

## Negative Results

A negative result is only meaningful when you also record the strongest surface you checked.

- Good: "site search, public detail page, and status API all show nothing"
- Weak: "the submit request returned 200"

When a market uses manual review, negative public search results usually mean `pending` rather than `failed`.
