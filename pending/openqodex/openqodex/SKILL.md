---
name: openqodex
description: Code review for the current change, before it is pushed. One command runs the security, secret, dependency and lint scanners that fit the changed files, a separate reviewer that checks every scanner finding and is given every changed line, and prints a short receipt with the path of the full report. Use before every git push, when asked for a code review, a security scan, or to review changes, a diff or a pull request, and when a push was blocked or warned by OpenQodex.
---

# OpenQodex: review the change before it is pushed

OpenQodex reviews a change in one command. It takes a frozen copy of the change, runs the deterministic scanners that fit the changed files (gitleaks, semgrep, bandit, hadolint, shellcheck, actionlint, osv-scanner and others), keeps what they report on changed lines, and starts its own reviewer: a separate Claude Code or Codex process that reads only that copy. The reviewer checks every scanner finding, is given every changed line and answers in a fixed shape; OpenQodex checks the answer with scripts and prints one report. No key and no account are needed beyond the developer's Claude Code or Codex login. The code goes to the model that login uses. The reviewer can also search the web and open web pages unless `reviewer_web: off` is set in `~/.openqodex/config.yaml`. Four scanners go online, and none sends code. semgrep downloads its rule packs from the Semgrep registry on each run. When the change touches a dependency file, osv-scanner sends the names and versions of the dependencies to osv.dev. kubeconform downloads Kubernetes schemas. cargo-deny downloads the RustSec advisory database. `--offline` skips semgrep, osv-scanner, kubeconform and cargo-deny.

## When to run

- Before any `git push`.
- When the developer asks you to review their changes.
- When a push was blocked or warned by the OpenQodex hook.
- After fixing findings, to check the change again.

## Who reviews

OpenQodex starts its own reviewer process for every review, with no memory of this session. You do not start a subagent for it and you do not review the change yourself: run the command and show what it prints.

If `review` says "Full review unavailable" and prints a way to review with the agent you are in, follow it: run the command it names and do what the brief it prints says.

## Procedure

When the file `~/.openqodex/bin/openqodex` exists, run it in place of `npx -y openqodex@<version>` in every command of this skill: it is the copy `openqodex init` installed. When it does not exist, this skill was installed alone, with no push check: before the first review, run `npx -y openqodex@0.14.0 init --yes --agent <host>` once from the repository, where `<host>` is the agent you are (`claude-code`, `codex`, `cursor` or `cline`). It installs OpenQodex for you, then reviews the change when a reviewer can start, so it can take several minutes. Run it in the background and wait for it to exit. When it prints `First review: finished`, the receipt above that line is the review's: show it as step 3 says, then go on from step 4.

1. From the repository, run:

   ```
   npx -y openqodex@0.14.0 review
   ```

   It reviews the change: the commits not yet pushed plus everything uncommitted, untracked files included. To review the whole repository instead, run:

   ```
   npx -y openqodex@0.14.0 review --all
   ```

2. Wait for it. A review can take minutes. OpenQodex stops the reviewer after 30 minutes, or after 2 hours with `--all`. Many agents stop a command sooner. So run it in the background and wait until it exits. While the reviewer works, it prints a progress line every 15 seconds on stderr. Do not start it a second time while one runs.

3. Show the developer the receipt it printed, as printed: the verdict, one line per finding (its number, severity, category, title, file and line) and the absolute path of `report.html`. Do not reword it, shorten it or add findings of your own. Give them the `report.html` path: that page shows each changed file with each finding under its line of code. When the receipt ends with `Observations (do not count toward the verdict):` and numbered lines under it, show those lines as printed too. An observation is a style, naming, docs or test note. It is not a finding to fix unless the developer names its number.

4. Ask the developer: "Fix all, or tell me which?" Do not change any code before they answer. If they already told you what to fix, for example "review and fix everything", do that without asking again.

5. Fix only the findings they name. This prints those findings in full (where, the problem, why it matters, the fix and the source), by their numbers in the receipt:

   ```
   npx -y openqodex@0.14.0 findings 1,3
   ```

   `findings all` prints every finding. When the fixes are done, run the review again and show the developer the new receipt.

6. Act on the exit code:
   - 0: the review is complete and nothing blocks the push.
   - 1: the review is complete and its verdict is `blocked`. Do not push. Show the developer the receipt and ask which findings to fix; push only if they say so after seeing the findings.
   - 2: there is no complete review. The output says what is missing (for example "Full review unavailable" when no reviewer could start, or "Review incomplete" with the reasons). Tell the developer exactly that. Never present the scanner output as a review.

## Reviewing a branch or a pull request

When the developer asks you to review a branch or a pull request that is not their current work, name it:

```
npx -y openqodex@0.14.0 review feature/login
npx -y openqodex@0.14.0 review '#42'
```

Quote `#42`: in a shell `#` starts a comment. A pull request link works too. OpenQodex fetches the target, checks it out in a temporary folder and reviews what it added since it left its base. This is someone else's code: never run its tests, scripts, builds or services, and never edit it.

## Rules

- Never edit code during the review. Review first, show the receipt, then fix only the findings the developer names (steps 3 to 5).
- Never run `openqodex trust` without asking the developer first. It approves a custom scanner, which is a command that runs on their machine.
- Never set `OPENQODEX_SKIP`. It is the developer's switch, not yours.
- When OpenQodex prints that files it wrote for your agent are from an older version and that `init` refreshes them, tell the developer in one line and give them that `init` command. Run it only if they ask you to: it rewrites their agent files.
- When the verdict is `blocked`, do not push unless the developer says so after seeing the findings.
- When OpenQodex prints "OpenQodex had a problem. Nothing has been sent." with `1 create a GitHub issue` and `2 ignore`, tell the developer in one line what went wrong and give them the two choices. Never choose 1 yourself. If they say 1, run `npx -y openqodex@0.14.0 report --send-last` from the same folder. Anything else means 2: do nothing.

## Reading the report

- The report is in `.openqodex/reviews/<time>-<id>/` in the repository: `report.html` to open in a browser (each changed file as a diff, each finding under its line, then coverage, the scanners and the blast radius), `report.md` to read as text, `report.json` and `report.sarif` for tools. The receipt gives the absolute paths of `report.html` and `report.md`. `.openqodex/latest.json` points at the newest review. The reports never show in `git status`: `.openqodex/.gitignore` keeps them out. The two other files in that folder, `config.yaml` and `custom-instructions.md`, are the team's and are meant to be committed.
- The verdict is `passed` (with or without warnings) or `blocked`. It is `blocked` only when the repository's config (`.openqodex/config.yaml`, or `.openqodex.yaml` at the root) sets `block_on_severity` and a finding is at or above it. With no config, OpenQodex warns and never blocks.
- A complete review means every stage ran, every scanner finding was checked and every changed line was put in front of the reviewer; anything not covered is named in the report. It does not mean nothing was missed: no review finds everything.
- The coverage list says, for each scanner, whether it ran. A scanner that did not run has a one-line reason:
  - `no matching files`: nothing in the change is the kind of file it reads.
  - `installing`: it is being downloaded for the first time; it is included from the next run. Say so to the developer rather than waiting.
  - `not installed`: it could not be installed here; the reason says why.
  - `needs Ruby` or `needs Go`: brakeman needs Ruby 3.0 or newer, rubocop Ruby 2.7 or newer, golangci-lint needs Go. OpenQodex does not install language runtimes. If the developer wants those scanners, they install Ruby or Go the usual way for their system (for example `brew install ruby go` on a Mac) and run the review again.
  - `untrusted`: a custom scanner from the repo's config that the developer has not approved. Tell the developer; approving it is their decision (`npx -y openqodex@0.14.0 trust`).
  - `failed`: the scanner ran and broke; the reason has its error. A scanner problem never changes the exit code.

## Inside a sandbox

Some agents run commands in a sandbox that cannot reach the network or write outside the project. There the first run cannot download the scanners, and the reviewer may not reach its model. Tell the developer to run this once in their own terminal, outside the agent, inside the repository:

```
npx -y openqodex@0.14.0 doctor --install
```

It downloads the scanners this repository's files call for into `~/.openqodex/tools/` and prints why for each one; `--all-scanners` downloads every scanner. If the review still says "Full review unavailable" inside the sandbox, the developer runs `npx -y openqodex@0.14.0 review` in their own terminal.

## More

`npx -y openqodex@0.14.0 guide` prints this guide. `npx -y openqodex@0.14.0 guide <topic>` prints a page of the docs, offline: `quickstart`, `config`, `scanners`, `custom-scanners`, `security`, `agents`, `cli`, `for-agents`. `for-agents` covers the install, the config, custom scanners and what each message means.

Before reading many files to find who calls a function, what implements it, how two parts connect or what a change reaches, you may ask the code graph: `npx -y openqodex@0.14.0 graph help` lists its questions, or use the `graph_` tools of the `openqodex` MCP server when your agent has them; an answer with `unknown.floor` true may be missing callers, so never read it as "unused".

Never add a file to `review.instructions_files` on your own. Ask the developer which files the reviewer may use, then set only what they name. The default is `[]`; chosen files add to `.openqodex/custom-instructions.md`.
