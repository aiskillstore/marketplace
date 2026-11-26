# Website CI gate skill for Claude Code, GitHub Copilot, Codex and Cursor

`website-ci-gate` is an Agent Skills `SKILL.md` from squirrelscan that adds a website audit check to CI: a GitHub Actions website audit and preview deploy gate for coding agents. It uses the squirrel CLI in Claude Code, GitHub Copilot, Codex, Cursor and other agents to fail builds on a score threshold, error findings or new findings. It writes pipeline config and picks thresholds from a real baseline. It does not fix findings.

## What it does

- Runs a baseline audit first and chooses thresholds the site passes today, since a gate that is red on day one gets turned off.
- Writes `--fail-on` gates: `score<N`, `score:<category><N`, `severity>=error`, `errors>0` and `warnings>0`, quoted so the shell does not read `<` as redirection.
- Fails only on new findings with `squirrel ci <url> --website <id> --fail-on-new error`, using an org API key.
- Handles exit codes: `2` is a tripped threshold, and `3`, `4` and `5` (blocked, redirected, unreachable) mean nothing was audited, so the job must fail on any non-zero exit.
- Writes a GitHub Actions workflow with the official action or the plain CLI, plus the GitLab equivalent.
- Audits preview deploys (Vercel, Netlify, Cloudflare Pages) after the deploy is ready.
- Shows you the diff before editing a workflow file, and tells you which secret to create instead of adding it.
- Keeps `SQUIRRELSCAN_API_KEY` in the CI secret store, never in the repo.

## Questions it answers

- Add squirrelscan to GitHub Actions
- Fail CI on website audit errors
- Gate preview deploys on audit scores
- How do I fail a build when my site's score drops?
- What score threshold should I start with?
- What do squirrel exit codes 2, 3, 4 and 5 mean in CI?
- How do I fail only on new findings?
- How do I audit a preview deployment URL in a pull request?

## Install

With any Agent Skills tool (Claude Code, GitHub Copilot, Codex, Cursor, Gemini CLI, Amp and others):

```bash
npx skills add squirrelscan/skills --skill website-ci-gate
```

- **Claude Code plugin** (installs all the skills plus the hosted squirrelscan MCP server):

  ```
  /plugin marketplace add squirrelscan/skills
  ```

  ```
  /plugin install squirrelscan@squirrelscan
  ```

- **Codex**: `npx skills add` lands the skill in `.agents/skills/`. To add the MCP server too, configure it in `~/.codex/config.toml` ([Codex docs](https://docs.squirrelscan.com/developers/agents/codex)).
- **GitHub Copilot**: `npx skills add squirrelscan/skills --skill website-ci-gate -a github-copilot` (project `.agents/skills/`, or `~/.copilot/skills/` with `-g`). Add the hosted MCP server too, see the [GitHub Copilot docs](https://docs.squirrelscan.com/developers/agents/copilot).
- **Cursor**: use the Cursor plugin in this repo, or the [one-click MCP link](cursor://anysphere.cursor-deeplink/mcp/install?name=squirrelscan&config=eyJ1cmwiOiJodHRwczovL21jcC5zcXVpcnJlbHNjYW4uY29tL21jcCJ9) plus the skill.
- **Gemini CLI, Amp and other Agent Skills tools**: `npx skills add` plus the MCP server ([docs](https://docs.squirrelscan.com/developers/agents)).

**Requirements:** the squirrel CLI installed and in PATH ([squirrelscan.com/download](https://squirrelscan.com/download), check with `squirrel --version`), or the hosted squirrelscan MCP server connected (`https://mcp.squirrelscan.com/mcp`).

Install the CLI on macOS or Linux:

```bash
curl -fsSL https://install.squirrelscan.com | bash
```

## Use it in Claude Code, GitHub Copilot, Codex or Cursor

```text
Add squirrelscan to GitHub Actions for https://staging.example.com
```

```text
Fail CI on website audit errors and score drops below 85
```

```text
Gate preview deploys on audit scores
```

The agent runs a baseline, proposes thresholds, shows you the workflow diff and tells you which secret to create, then checks the job is green on main.

## How it works

1. Run a baseline locally with `squirrel audit` at `--level quick` and read the scores.
2. Pick the gate: absolute `--fail-on` thresholds, or `squirrel ci` with `--fail-on-new` for new findings.
3. Handle exit codes so `3`, `4` and `5` fail the job.
4. Write the workflow with the official action or the plain CLI, after showing you the diff.
5. Stop when the job is green on main and you have seen it go red on a deliberate regression. Document the thresholds next to the workflow.

## Related skills

- [`audit-website`](../audit-website/): fixing what the gate finds.
- [`security-audit`](../security-audit/): fixes for security findings.
- [`seo-audit`](../seo-audit/): fixes for SEO findings.
- [`performance-audit`](../performance-audit/): fixes for performance findings.

## Links

- [squirrelscan.com](https://squirrelscan.com)
- [docs.squirrelscan.com](https://docs.squirrelscan.com)
- [Repo README](../../README.md)
- [`SKILL.md`](./SKILL.md) for this skill
- MIT licensed
