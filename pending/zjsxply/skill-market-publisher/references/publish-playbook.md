# Publish Playbook

Use this playbook to map one local skill into the right submission path for each market.

## 1. Start With One Release Unit

- The release unit is one directory that contains `SKILL.md`.
- If the source repository contains many skills, decide whether the target market accepts:
  - one repository containing many skills
  - one repository or folder per skill
  - one uploaded `SKILL.md` file or zip archive
- If a market wants a different repository layout, create a publish mirror instead of restructuring the source repo.

## 2. Classify The Intake Model

Use one of these intake models before building automation:

- Repository URL intake
  - Market asks for a public GitHub repository or folder URL.
  - Typical inputs: repo URL, optional branch or folder URL, optional description or email.
  - Good fit for directory sites and registries.
  - Accepted folder URLs do not guarantee single-skill scope. Some backends still ingest the full repository pack.
- Local skill directory intake
  - Market CLI publishes from the current local skill directory.
  - Typical inputs: local path, version, category, authenticated CLI session.
- Raw `SKILL.md` intake
  - Market asks for pasted `SKILL.md` content plus metadata fields.
  - Good fit for niche review-based directories.
- Upload intake
  - Market asks for `SKILL.md`, `.zip`, or a local skill package.
  - Verify whether the uploaded file must include only the skill or a full project bundle.
- Seller platform intake
  - Market expects pricing, payout, payment, or wallet information in addition to skill metadata.
- GitHub App or crawler intake
  - Market does not expose a normal submit form.
  - Listing happens after repository tagging, GitHub App installation, or passive indexing.

## 3. Match The Repo Layout

The bundled CLI classifies the current layout as:

- `single-skill-repo`
- `root-pack`
- `skills-subdir-pack`
- `nested-skill-dir`
- `standalone-skill-dir`

Use these rules:

- Repository-intake directories often accept `single-skill-repo` and `root-pack`.
- Markets that parse `skills/` at repo root usually prefer `skills-subdir-pack`.
- Treat submit-page copy about layout as a hint, not a guarantee. Confirm the real preview or submit behavior before creating a publish mirror.
- Local CLI publish flows generally work from any local skill directory, but only if the CLI uses the current working directory or accepts a path argument.
- GitHub App or repo-indexing markets are sensitive to repo scope. If you only want one listing, publish from a repo that contains only that skill.

## 4. Fill Only Explicit Market Fields

Do not guess market-only fields.

- Versioned CLI markets: set an explicit semantic version.
- Review queues: provide author email only if the official form asks for it.
- Seller markets: provide price, payout, wallet, or payment product fields only when required.
- GitHub URL markets: use a stable repo or folder URL and a stable branch.
- Fixed category enums: map domain-specific skills to the closest supported category or `other`; do not invent unsupported labels.

## 5. Verify Scope Semantics

- Use a repository URL when the market explicitly imports every `SKILL.md` it can discover from a repo.
- Use a folder `tree/<ref>/<path>` URL or raw `SKILL.md` content when the market can truly submit one skill at a time.
- Do not assume a folder URL stayed folder-scoped just because the API accepted it.
- Confirm scope from the submit response, status API, or resulting public pages.

## 6. Use A Safe Submission Order

For every market:

1. `inspect`
2. `plan`
3. `bundle`
4. dry-run or manual review
5. live submit or publish
6. public verification

Do not probe a live market with fake data only to learn validation rules.

## 7. Respect Auth Boundaries

Common auth patterns:

- Anonymous HTTP submit
  - Safe to automate if the endpoint is public and stable.
- Logged-in web submit
  - Document the flow, but do not hardcode fragile private browser requests.
- Logged-in CLI publish
  - Only wrap the CLI if the command shape is official and stable.
- GitHub App install
  - Treat as an onboarding flow, not a standard submit form.
- Seller dashboard
  - Expect payment, payout, or compliance setup before the first publish.

## 8. Prepare A Listing Brief

Before or during submit, prepare a compact listing brief that contains:

- the one-line value proposition
- the canonical repo URL and `SKILL.md` URL
- the exact submit scope URL
- one sample task or test prompt
- the expected outcome or verification target
- any visible file inventory or important bundled resources
- the strongest trust signal the market exposes, such as audit result, status page, or workflow URL

This mirrors the most useful public directory pages and makes both manual review and post-submit verification faster.

## 9. Separate Reusable Guidance From Run Logs

Keep this skill reusable.

- Update the skill when the workflow, official endpoint, or verification method changes.
- Do not store sample submission IDs, sample PRs, sample slugs, or sample account pages here.
- Store temporary evidence in a bundle output directory or task notes outside the skill folder.
