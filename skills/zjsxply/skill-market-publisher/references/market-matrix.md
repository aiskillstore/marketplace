# Market Matrix

Use this matrix to decide whether the target market should be handled by wrapped live automation, by a prepared manual bundle, by seller onboarding, or by indexing only. Keep one-off submission evidence outside this skill.

## Wrapped Live Publishing

### ClawHub

- Mode: `auto-cli`
- Submission path: `clawhub skill publish <path> --version <semver>`
- Bulk path: `clawhub sync`
- Auth: CLI login
- Compatible unit: local skill directory
- Verification:
  - use CLI output and the authenticated destination workspace
- Notes:
  - Official CLI docs expose `skill publish <path>` and keep `publish <path>` as a legacy alias.
  - Good fit for direct skill-folder publishing from the workstation when the authenticated CLI is available.

### AgentSkill.sh

- Mode: `auto-http`
- Submission path: `POST https://agentskill.sh/api/skills/submit`
- Required fields: repository URL
- Auth: none
- Compatible unit: public repository or publish mirror
- Verification:
  - public author page `https://agentskill.sh/@<owner>`
  - public detail page `https://agentskill.sh/@<owner>/<skill-name>`
- Request shape:
  - `{"url":"https://github.com/owner/repo"}`
- Notes:
  - Public repo submission imports every discoverable `SKILL.md` in that repo.
  - Use a dedicated repo or publish mirror if the market submission must stay scoped to one skill.

### Skillz Directory

- Mode: `auto-http`
- Submission path: `POST https://www.skillz.directory/api/submit`
- Required fields:
  - skill name
  - author email
  - description
  - GitHub URL
  - category
- Optional fields:
  - tags
  - image URL
- Auth: none
- Compatible unit: public GitHub repository URL
- Verification:
  - `POST https://knowing-wren-258.convex.cloud/api/query`
  - detail page `https://www.skillz.directory/skills/<slug>`
- Current front-end behavior:
  - The public `/submit` page validates fields in the browser and posts JSON to `/api/submit`.
- Notes:
  - Categories are a fixed enum. Map domain-specific skills to the nearest supported category or `other`.
  - A `success: true` submit response is weaker evidence than a Convex query hit or public detail page.

### Skillstore

- Mode: `auto-http`
- Submission path: `POST https://skillstore.io/api/submit`
- Required fields:
  - `github_url`
- Optional fields:
  - `notes`
- Auth: none
- Compatible unit: public GitHub repo URL or folder `tree/<ref>/<path>` URL
- Verification:
  - `GET https://skillstore.io/api/submit?id=<submission_id>`
  - `https://skillstore.io/submissions/<submission_id>`
- Current behavior:
  - Anonymous submissions are accepted without prior login.
  - The backend exposes a public status API and status page.
- Notes:
  - Repo URLs and GitHub `tree/<ref>/<path>` URLs are accepted.
  - The status API may expose a workflow run URL before a public listing exists.
  - Folder URL submissions should be treated as best-effort scoping unless the status payload or final listing proves that the import stayed per-skill.

### agent-skills.md

- Mode: `auto-http`
- Submission path: `POST https://agent-skills.md/rpc/repos/submit`
- Required fields:
  - ORPC JSON envelope with a GitHub repo or folder URL
- Auth: none
- Compatible unit:
  - public GitHub repo URL
  - public GitHub pack or folder URL
- Verification:
  - public detail page `https://agent-skills.md/skills/<owner>/<repo>/<skill-name>`
- Notes:
  - The live submit flow accepts an ORPC JSON envelope rather than a classic form post.
  - Re-runs can return `alreadyExists`; treat public detail pages as the real success signal.
  - Pack-level submissions can import multiple skills from one repository scope.

### SkillsMD

- Mode: `auto-http`
- Submission path: `POST https://skillsmd.dev/api/submit`
- Required fields:
  - repo in `owner/repo` form
  - skill name
  - description
- Optional fields:
  - author email
- Auth: none
- Compatible unit: one skill name mapped onto a public GitHub repository
- Verification:
  - `https://skillsmd.dev/api/search?q=<skill-name>`
  - public registry after review
- Notes:
  - The live API returns `201` plus a submission ID when the item enters the review queue.
  - Fresh submissions can remain absent from public search until the review step completes.

### Bogen.ai

- Mode: `auto-http`
- Submission path: `POST https://www.bogen.ai/api/skills/submit`
- Required fields:
  - skill name
  - category
  - description
  - pasted `SKILL.md`
  - author name
  - author email
- Auth: none
- Compatible unit:
  - one pasted `SKILL.md` plus metadata
- Verification:
  - `https://www.bogen.ai/skills/`
- Notes:
  - Review-based directory.
  - A duplicate-name or pending-review `400` can mean the listing already exists in the queue.
  - Public listing is still required before claiming success.

### skillsrep.com

- Mode: `auto-http`
- Submission path: `POST https://skillsrep.com/submit`
- Required fields:
  - skill definition
  - GitHub repo
  - usage examples
  - version
- Optional fields:
  - tags
  - creator links
  - instruction and MCP fields
- Auth: none
- Compatible unit:
  - one skill definition plus repo metadata
- Verification:
  - `https://skillsrep.com/skill/<slug>`
  - `https://skillsrep.com/search?q=<query>`
- Notes:
  - Anonymous HTML form uses a server-side CSRF token.
  - Successful submits can redirect directly to a public detail page even when no success flash is visible.

### A2A Market

- Mode: `auto-http`
- Submission path: `POST https://api.a2amarket.live/v1/listings`
- Required fields:
  - listing name
  - description
  - price
  - category
  - seller wallet address
- Auth: seller wallet / operator input
- Compatible unit: sale listing for one skill
- Verification:
  - marketplace listing after creation
  - seller-facing listing lookup when available
- Notes:
  - This is a selling marketplace rather than a free directory.
  - It is useful when the user wants commercial distribution rather than only discovery.

## Verified Manual Submission Targets

### SkillNet

- Mode: `manual-web`
- Submission path:
  - website contribution flow at `http://skillnet.openkg.cn/`
  - official docs describe `Contribute -> Submit via URL / Upload Local Skill / Batch Upload Skills`
- Auth:
  - search and download are public
  - create and evaluate APIs require an API key
- Compatible unit:
  - skill folder URL
  - local skill folder upload
  - batch upload
- Verification:
  - `GET http://api-skillnet.openkg.cn/v1/search?q=<skill-name>`
  - `skillnet search "<skill-name>"`
- Notes:
  - Strong fit for `SKILL.md` ecosystems because the official project treats skills as first-class packages.

### AgentSkillsRepo

- Mode: `manual-web`
- Submission path: site submit modal on `https://agentskillsrepo.com/`
- Auth: public submit surface visible
- Compatible unit: GitHub repository URL containing `SKILL.md`
- Verification:
  - `https://agentskillsrepo.com/search?q=<query>`
  - public detail page after review
- Notes:
  - Official copy says all listed skills use the open `SKILL.md` ecosystem.

### skills.re

- Mode: `manual-web`
- Submission path: `https://skills.re/submit`
- Auth: public submit surface visible
- Compatible unit: repository URL
- Verification:
  - public author and skill pages after submit
  - public read APIs under `https://skills.re/api/rpc/`
- Current page behavior:
  - The page asks for a repository URL.
- Notes:
  - The page copy mentions a repository-root `skills/` folder.
  - Live preview and public read APIs can still accept some `root-pack` repositories, so verify the backend behavior before forcing a publish mirror.

## Auth-Gated Or Seller-Gated Targets

### Skills Directory (`skillsdirectory.com`)

- Mode: `manual-web`
- Submission path: `https://www.skillsdirectory.com/submit`
- Auth: GitHub sign-in required
- Compatible unit: GitHub repository URL
- Verification:
  - `GET https://skillsdirectory.com/api/registry?q=<query>`
  - `GET https://skillsdirectory.com/api/registry/<slug>`
  - public page `https://www.skillsdirectory.com/skills/<slug>`
- Notes:
  - Distinct platform from `skillsdir.dev`.
  - Good fit for post-submit public verification because the registry API is documented.

### mdskills.ai

- Mode: `manual-web`
- Submission path: `https://www.mdskills.ai/submit`
- Auth: login required
- Compatible unit: GitHub-backed skill submission
- Verification:
  - site search and public listing pages on `https://www.mdskills.ai/skills`
- Notes:
  - Public docs treat `SKILL.md` as a first-class ecosystem format.
  - Current submit path redirects to login before the real form appears.

### Skillery

- Mode: `manual-web`
- Submission path: `https://skillery.dev/submit`
- Auth: login required
- Compatible unit: GitHub-hosted skill or platform-native package
- Verification:
  - public listing at `https://skillery.dev/skills`
  - generated detail page `https://skillery.dev/skills/<slug>`
- Notes:
  - Public docs show install-side CLI support, but the platform's publish API is not public.

### SkillsZoo

- Mode: `manual-web`
- Submission path: `https://www.skillszoo.com/submit`
- Auth: login required
- Compatible unit: GitHub repository URL plus review metadata
- Verification:
  - public search on `https://www.skillszoo.com/search`
  - profile-side `My Submissions` for review state
- Notes:
  - Public form fields are visible, but the submit API is not documented as a stable integration surface.

### SkillHub

- Mode: `manual-web`
- Submission paths:
  - app workspace `https://www.skillhub.club/app/skills`
  - official CLI docs `https://www.skillhub.club/docs/cli`
- Auth: login required for management and publish
- Compatible unit:
  - local `SKILL.md`
  - zip upload
  - current-directory CLI publish
- Verification:
  - public directory `https://www.skillhub.club/skills`
  - public detail page `https://www.skillhub.club/skills/<slug>`
- Notes:
  - Official CLI documents `login`, `push`, and `publish`.
  - The market also advertises GitHub-based auto-indexing, so do not mix hosted publish and crawler discovery into one assumption.

### SkillHQ

- Mode: `manual-web`
- Submission paths:
  - seller page `https://skillhq.dev/become-seller`
  - official CLI commands `skillhq validate ./my-skill` and `skillhq publish ./my-skill --price <usd> --category <category>`
- Auth: seller onboarding and payout setup
- Compatible unit:
  - local skill directory with `SKILL.md` and `README.md`
- Verification:
  - expected public listing page after publish
  - official install flow once listed
- Notes:
  - Commercial marketplace with validation and revenue-share workflow.

### skillshop.sh

- Mode: `index-only`
- Listing path:
  - install the GitHub App into a GitHub org
  - publish a repository whose root contains `SKILL.md`
- Auth:
  - GitHub org permission to install the app
  - no normal submit form
- Compatible unit:
  - single-skill repository at repo root
- Verification:
  - `GET https://skillshop.sh/api/skills/<org>/<repo>`
  - `https://skillshop.sh/skills/<org>/<repo>`
- Notes:
  - This is a marketplace scan model, not a directory form submission model.
  - Selling requires payment metadata such as `price`, and paid listings require payout fields.

## Blocked, Partial, Or Legacy Targets

### Agent Skills Index

- Mode: `manual-web`
- Status: `blocked`
- Official paths:
  - docs: `https://agentskillsindex.com/en/docs/publishing`
  - submit page: `https://agentskillsindex.com/en/submit`
- Current documented intake:
  - manual submit with a GitHub repo URL
  - crawler discovery from a public GitHub repo tagged with `ai-skill`
- Recommendation:
  - do not claim live automation here
  - treat `ai-skill` topic plus later platform search as the only current fallback
  - latest recon still shows the public submit form, but the documented live submit path is not usable enough to wrap safely

### skillscatalog.ai

- Mode: `manual-web`
- Status: `partial`
- Official path: `https://skillscatalog.ai/submit`
- Notes:
  - Public submit exists, but anonymous behavior has been unstable enough that this skill should not claim wrapped automation.
  - Keep this target documented, but re-verify the browser flow before encoding new automation against it.

### Skills Directory (`skillsdir.dev`)

- Mode: `manual-web`
- Submission path: `https://www.skillsdir.dev/add`
- Current page behavior:
  - The site says to submit via GitHub or to use `skill publish` from the skill directory.
  - The page lists these requirements:
    - valid `SKILL.md`
    - at least one repository or documentation link
    - up to 3 verticals
    - concise summary
    - unique kebab-case ID
- Warning:
  - The advertised GitHub issue path has been unreliable enough that this remains a manual target only.

## Discovery Or Indexing Targets

### skills.sh

- Mode: `index-only`
- Notes:
  - Public discovery is tied to installability and ecosystem indexing rather than an explicit submission form in the current public docs.
  - Verification should use `npx skills find <query>` or the public search API:
    - `https://skills.sh/api/search?q=<query>&limit=10`

## Different Artifact Model

### skillsfor.ai

- Mode: `incompatible`
- Notes:
  - This registry operates on a different API-style artifact model.
  - Do not treat a plain `SKILL.md` folder as directly publishable here without a translation layer.

## Watchlist

These surfaces are relevant, but still need deeper validation before they should become wrapped live adapters:

- SkillNet upload endpoints beyond the official website flow
- AgentSkillsRepo submit backend
- Skillstore folder-scope semantics for tree URLs
- SkillHub publish automation semantics for noninteractive CLI use
- SkillHQ seller CLI semantics beyond the marketing page

## Source Pointers

- ClawHub CLI docs: `https://raw.githubusercontent.com/openclaw/clawhub/main/docs/cli.md`
- AgentSkill.sh submit page: `https://agentskill.sh/submit`
- Skillz Directory submit page: `https://www.skillz.directory/submit`
- Skillz Directory source repo: `https://github.com/keyman500/skills`
- Skillstore submit page: `https://skillstore.io/submit`
- Skillstore marketplace README: `https://raw.githubusercontent.com/aiskillstore/marketplace/main/README.md`
- Skillstore submission workflow: `https://raw.githubusercontent.com/aiskillstore/marketplace/main/.github/workflows/process-submission.yml`
- Agent Skills Index publishing docs: `https://agentskillsindex.com/en/docs/publishing`
- skills.re submit page: `https://skills.re/submit`
- Skills Directory add page: `https://www.skillsdir.dev/add`
- SkillNet official repository: `https://github.com/zjunlp/SkillNet`
- agent-skills.md submit page: `https://agent-skills.md/submit`
- SkillsMD registry: `https://skillsmd.dev/`
- AgentSkillsRepo home page: `https://agentskillsrepo.com/`
- Skills Directory submit page: `https://www.skillsdirectory.com/submit`
- Skills Directory registry API docs: `https://www.skillsdirectory.com/docs/registry-api`
- mdskills.ai submit page: `https://www.mdskills.ai/submit`
- Skillery submit page: `https://skillery.dev/submit`
- SkillsZoo submit page: `https://www.skillszoo.com/submit`
- SkillHub CLI docs: `https://www.skillhub.club/docs/cli`
- SkillHQ seller page: `https://skillhq.dev/become-seller`
- SkillShop agent manual: `https://skillshop.sh/agent.md`
- Bogen.ai submit page: `https://www.bogen.ai/skills/submit`
- skillsrep submit page: `https://skillsrep.com/submit`
