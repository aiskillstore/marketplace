---
name: website-ci-gate
description: "Add a squirrelscan CI check using the squirrel CLI in Claude Code, GitHub Copilot, Codex, Cursor, and other coding agents for GitHub Actions, GitLab, and preview deploys. It picks thresholds from a baseline run of squirrelscan audit rules, fails builds on a score threshold, error findings, or new findings, and handles the exit codes correctly. Use when asked \"add squirrelscan to GitHub Actions\", \"fail CI on website audit errors\", or \"gate preview deploys on audit scores\"."
license: See LICENSE file in repository root
compatibility: Requires the squirrel CLI installed and accessible in PATH, or the hosted squirrelscan MCP server connected
metadata:
  author: squirrelscan
  version: "0.1.3"
allowed-tools: Bash(squirrel:*) Read Edit Grep Glob
---

# Website CI Gate

Add a squirrelscan check to CI so a pull request, a preview deploy or a release fails when the site gets worse: a score below a threshold, an error-severity finding, or findings that are new since the last audit.

This skill writes pipeline config and picks thresholds from a real baseline. It does not fix findings; use `audit-website` for that.

## Before the first audit

Run `squirrel --version`. If it fails, install the CLI from [squirrelscan.com/download](https://squirrelscan.com/download) (the `squirrelscan` skill has `references/install.md`). Then run `squirrel auth status`:

- **Signed out, or `--offline`**: the audit runs on this machine, is free, and nothing is published.
- **Signed in**: the audit is billed in credits (50 plus 2 per audited page, plus 1 per distinct external link the cloud verifies), adds the site to the user's dashboard, can turn on recurring audits and publishes an unlisted report. Tell the user the cost (`squirrel credits`) and get a yes. Offer `--offline` or `--no-publish`. For a site the user does not own, add `--ephemeral`: nothing is added to the dashboard, scheduled or published.

Every flag below is checked against the squirrel CLI docs (https://docs.squirrelscan.com/cli/audit). Rule docs: `https://docs.squirrelscan.com/rules/{category}/{rule_id}`.

CI runners are signed out unless `SQUIRRELSCAN_API_KEY` is set. A signed-out audit runs deterministic rules for free; an audit signed in with an org API key pays no audit or page charge, checks external links from the runner for free, and bills only cloud renders (2 credits per rendered page; `--http` renders nothing). Keep the key in the CI secret store, never in the repo.

## Step 1: find the baseline

Run once locally and read the scores:

```bash
squirrel audit https://staging.example.com --level quick --format json -o baseline.json
```

Choose thresholds the site passes today. A gate that is red on day one gets turned off. Tighten later.

## Step 2: pick the gate

`--fail-on` thresholds are absolute, not a comparison with an earlier audit. Quote each expression: the shell reads bare `<` and `>` as redirection.

```bash
squirrel audit "$URL" --level quick --format json -o report.json \
  --fail-on 'score<85' --fail-on 'score:perf<70' --fail-on 'severity>=error'
```

| Expression | Trips when |
|------------|-----------|
| `score<N` | overall health score is below N |
| `score:<category><N` | a category score is below N, for example `score:perf<80` |
| `severity>=error` or `errors>0` | any error-severity finding |
| `warnings>0` | any warning-severity finding (also counts a security rule that timed out) |

To fail only on findings that are **new** since the last audit, use a cloud audit of the website: `squirrel ci <url> --website <id> --fail-on-new error` (needs an org API key with `audits:read` and `audits:write` scopes in `SQUIRRELSCAN_API_KEY`; the first audit of a website exits 0 with no baseline).

Narrow what runs with `--rule-include` (for example `security,links`) and silence a rule that does not apply with `--rule-exclude` or a waived `[[ignore]]` in `squirrel.toml`. A narrowed run is partial and its score is not comparable to a full audit's.

## Step 3: exit codes

| Code | Meaning | Pipeline |
|------|---------|----------|
| `0` | Ran, every threshold passed | pass |
| `2` | A threshold tripped | fail the job |
| `1` | Operational error: bad flags, a crash, a site that answered with an error | fail, and read the message |
| `3` | The page was blocked by a WAF or bot manager: nothing was audited | fail or alert, never pass |
| `4` | The start URL redirected to another site | fail: fix the URL |
| `5` | The start URL could not be reached | fail: the preview may not be up yet |

A step that only treats `2` as failure will pass on `3`, `4` and `5`. Let the job fail on any non-zero exit.

## Step 4: write the workflow (show the diff first)

Prefer the official action on GitHub:

```yaml
name: Site audit
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: squirrelscan/audit-action@v1
        with:
          url: https://staging.example.com
          fail-on: "score<85,severity>=error"
          token: ${{ secrets.SQUIRRELSCAN_API_KEY }}   # optional
```

Without the action:

```yaml
      - run: |
          curl -fsSL --connect-timeout 10 --max-time 120 https://install.squirrelscan.com | bash
          echo "$HOME/.local/bin" >> "$GITHUB_PATH"
      - run: squirrel audit "$URL" --level quick --fail-on 'score<85' --fail-on 'severity>=error'
        env:
          URL: https://staging.example.com
          SQUIRRELSCAN_API_KEY: ${{ secrets.SQUIRRELSCAN_API_KEY }}
```

GitLab: the same two commands in `script:` with `SQUIRRELSCAN_API_KEY` as a masked variable. Preview deploys (Vercel, Netlify, Cloudflare Pages): audit the preview URL the platform gives the job (for example `github.event.deployment_status.environment_url` on a `deployment_status` trigger), after the deploy is ready. For a deploy-time audit of the deployed URL, `--refresh` avoids a cached crawl.

Do not edit existing workflow files without showing the user the diff, and do not add secrets yourself: tell the user which secret to create.

## Stop condition

Stop when the job is green on the current main, and the user has seen it go red on a deliberate regression (ask before pushing a throwaway branch). Document the thresholds and why in the repo, next to the workflow.

## Hand off

Fixing what the gate finds: `audit-website`, or the topic skills (`security-audit`, `seo-audit`, `performance-audit`, `accessibility-audit`).
