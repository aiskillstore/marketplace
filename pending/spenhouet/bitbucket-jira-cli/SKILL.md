---
name: bitbucket-jira-cli
description: Manage Bitbucket pull requests, repositories, and pipelines and Jira issues from the terminal with the bj CLI. bj mirrors the GitHub gh CLI, so gh pr/issue/repo commands map to bj pr/issue/repo, no MCP server or API wiring needed. Installs the bj CLI automatically if it is missing. Use when working with Bitbucket or Jira, opening or reviewing pull requests, managing Jira issues, running pipelines, or when a git branch name contains a Jira issue key like PROJ-42.
---

# bitbucket-jira-cli (`bj`)

`bj` is `gh` for Bitbucket and Jira. The command surface mirrors the GitHub CLI:
if you know `gh`, you know `bj`. It manages Bitbucket pull requests, repositories,
and pipelines, plus Jira issues, from one noun-first command tree.

If a command or flag is not covered here, run `bj <command> --help`; the flags
mirror `gh` and the help is authoritative.

## Install `bj` if it is missing

Before running any `bj` command, make sure the CLI is on `PATH`. If `command -v
bj` finds nothing, install it. This snippet picks whatever installer is already
available and prefers an isolated, self-updating install:

```bash
if ! command -v bj >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    uv tool install bitbucket-jira-cli          # isolated, self-updating (preferred)
  elif command -v pipx >/dev/null 2>&1; then
    pipx install bitbucket-jira-cli
  elif command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1; then
    pip install --user bitbucket-jira-cli
  else
    curl -LsSf uvx.sh/bitbucket-jira-cli/install.sh | sh   # installs uv, then bj
  fi
fi
```

On Windows PowerShell, install with:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://uvx.sh/bitbucket-jira-cli/install.ps1 | iex"
```

Then verify, and fix `PATH` if the install dir is not picked up yet:

```bash
command -v bj >/dev/null 2>&1 || export PATH="$HOME/.local/bin:$PATH"  # uv/pip user bin
bj --help >/dev/null    # confirms bj is installed and runnable
```

To run `bj` once without installing it (one-off commands, ephemeral CI), use
`uvx bitbucket-jira-cli <args>` in place of `bj <args>`. For repeated use in a
session, install it once with the snippet above so later `bj` calls just work.

## Setup

Authenticate once, like `gh auth login`:

```bash
bj auth login          # interactive; logs in Bitbucket and/or Jira
bj auth status         # show who you are logged in as
```

For CI or headless agents (no interactive prompt), pass tokens instead:

```bash
export BJ_BITBUCKET_TOKEN=...   # Bitbucket API token
export BJ_JIRA_TOKEN=...        # Jira API token
# or: bj auth login --bitbucket --with-token < token.txt
```

## Running non-interactively (agents, scripts, CI)

- Set `BJ_PROMPT_DISABLED=1` so `bj` never waits on a prompt; pass required
  values as flags or the command fails fast with a clear error. Piped output
  (non-TTY) already skips prompts.
- Set `NO_COLOR=1` to drop colors and the spinner (less noise in the transcript).
- Add `--json` for the full, raw API payload; shape it with `--jq '<expr>'`
  (requires the `jq` binary on `PATH`).
- Pass `--yes`/`-y` to accept confirmations (merge, close, stop).
- Exit codes: `0` success, `1` failure (includes "not logged in"), `2` usage
  error. Branch on these instead of parsing text.

## `gh` to `bj`

| `gh` | `bj` |
| --- | --- |
| `gh auth login` / `gh auth status` | `bj auth login` / `bj auth status` |
| `gh pr create` | `bj pr create` |
| `gh pr list` / `gh pr view` | `bj pr list` / `bj pr view` |
| `gh pr checkout` / `gh pr diff` | `bj pr checkout` / `bj pr diff` |
| `gh pr review` / `gh pr comment` | `bj pr review` / `bj pr comment` |
| `gh pr merge` / `gh pr close` | `bj pr merge` / `bj pr close` |
| `gh issue …` | `bj issue …` (Jira issues) |
| `gh repo clone` / `view` / `list` | `bj repo clone` / `view` / `list` |
| `gh run list` / `gh run view` | `bj pipeline list` / `bj pipeline view` |
| `gh api` | `bj api` |
| `gh browse` | `bj browse` |
| `gh release` | `bj release` (Jira versions) |
| `gh secret` / `gh variable` | `bj variable` (`--secured` for secrets) |
| `gh config` | `bj config` |
| `gh search` | `bj search` |
| `gh alias` | `bj alias` |
| `gh ssh-key` | `bj ssh-key` |
| `gh status` | `bj status` |
| `gh project` | `bj board` (Jira boards/sprints) |

## Differences from `gh`

- Two products behind one CLI: Bitbucket owns `pr`, `repo`, `pipeline`; Jira owns
  `issue`. Each backend has its own token (`BJ_BITBUCKET_TOKEN`, `BJ_JIRA_TOKEN`).
- `bj issue` targets Jira. Issue keys look like `PROJ-42`, not numbers.
- `bj pipeline` is Bitbucket Pipelines, the analog of `gh run`.
- `--json` emits the whole raw Bitbucket/Jira response. There is no `gh`-style
  field list; filter with `--jq` instead.
- `bj api` calls the Bitbucket or Jira REST API (`--backend bitbucket|jira`),
  not a GraphQL endpoint.
- A failed auth check exits `1` (a normal failure), where `gh` uses `4`.

## Branch-key automation

`bj` reads a Jira key from the current git branch (e.g. `feature/PROJ-42-thing`
gives `PROJ-42`) and uses it automatically:

- `bj pr create` fills the PR title from the ticket, links the PR to the issue,
  and transitions the ticket to In Progress.
- `bj pr merge` transitions the linked ticket to Done after a successful merge.

Preview the effect without writing anything using `--dry-run`; skip all Jira side
effects with `--no-jira`. If no key is found, `bj` acts like a plain Bitbucket
client.

## Common commands

```bash
# Pull requests (Bitbucket)
bj pr create --dry-run                 # preview title/link/transition
bj pr create --title "..." --yes       # non-interactive create
bj pr list --state open --json
bj pr view --json | jq '.title'
bj pr diff
bj pr review --approve                 # or --request-changes --body "..."
bj pr comment --body "..."             # add --file/--line for inline
bj pr merge --squash --delete-branch --yes

# Issues (Jira)
bj issue list --assignee me --json
bj issue view PROJ-42 --json
bj issue create --project PROJ --type Bug --summary "..."
bj issue edit PROJ-42 --field "Story Points=3"
bj issue transition PROJ-42 "In Review"
bj issue fields PROJ-42                 # list editable fields on the issue

# Repos and pipelines (Bitbucket)
bj repo clone WORKSPACE/REPO
bj pipeline list --json
bj pipeline run --branch main
```

## Safety

- Run `bj pr create` / `bj pr merge` with `--dry-run` first when unsure.
- `pr merge`, `pr close`, `issue close`, and `pipeline stop` change state. In an
  interactive session `bj` asks first; with `--yes` or when non-interactive it
  proceeds. Confirm intent with the user before passing `--yes` to these.
