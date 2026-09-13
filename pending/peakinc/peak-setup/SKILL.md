---
name: peak-setup
description: Move a repository's GitHub Actions jobs to Peak runners. Use when the user asks to set up Peak, speed up CI, switch runners to Peak, or run `peak init`. Runs the Peak CLI in agent mode, relays the sign-in link, and returns the pull request link.
license: MIT
metadata:
  author: Peak
  homepage: https://peak.inc
  docs: https://docs.peak.inc/quickstart
---

# Set up Peak in a repository

Peak runs GitHub Actions jobs on bare-metal microVMs. The only change to a repository is the `runs-on` line of each job. The Peak CLI makes that change, opens a pull request, and never edits anything else.

## Before you start

Check these. Stop and tell the user if one fails.

- The folder is a git repository with a GitHub remote named `origin`.
- Node 22.13 or newer is installed. Run `node --version`.
- The user is an owner of the GitHub organization. Personal accounts do not work yet.

## Steps

1. Run this in the repository folder:

   ```
   npx -y @peakinc/init@latest --yes --json --no-browser
   ```

2. Read stdout one line at a time. Each line is one JSON object with an `event` field.

3. When you see `{"event":"authorization_required","url":...,"user_code":...}`, show the user the `url` and the `user_code`. Say: "Open this link and approve the sign in." Then keep reading. The command waits up to 10 minutes.

4. When you see `{"event":"pull_request","url":...}`, give the user that link. Say what changed: the number of jobs from the `plan` event, and the files from the `applied` events.

5. When you see `{"event":"done"}`, stop. Do not merge the pull request. The user merges it.

## If the command stops early

Read the exit code.

| Code | Meaning | What to do |
| --- | --- | --- |
| 0 | Done | Report the pull request link. |
| 2 | Stopped | The user or a timeout stopped it. Ask the user if they want to run it again. |
| 3 | Blocked | A check failed. The `check` event with `"ok":false` has a `fix` field. Show the user the `text` and the `fix`. If a `links` event came, show those links too. |
| 4 | Failed | Show the user the `error` event's `message`. |

Common blocks and their fixes:

- `The Peak GitHub App cannot see owner/repo.` Show the `github_app` link from the `links` event. The user adds the repository to the App there, then adds it in Peak Settings.
- `GitHub is not connected to Peak.` Show the `peak_settings` link. An organization owner connects GitHub there.

## Hard jobs

The `plan` event lists jobs the CLI could not move under `manual`, with a `reason`. Matrix jobs with macOS or Windows legs, `runs-on` expressions, and runner label lists land here. For these, run the Peak agent instead:

```
npx -y @peakinc/wizard@latest --yes --json --no-browser
```

It does everything `init` does. For the hard jobs it sends only those workflow files to Peak over a secure connection. Peak decides per job and edits only the `runs-on` line and the matrix values. The events are the same, plus `translate_skipped` for each job Peak left as it was, with the reason.

## Manual fallback

If neither command can run, change one line per job in `.github/workflows/*.yml`:

```yaml
runs-on: ubuntu-latest     # before
runs-on: peak-ubuntu-24.04-4   # after
```

Open a pull request with that change. Leave everything else in the file as it is.

## Rules

- Never print, log, or store a token. The CLI never prints one either.
- Never edit workflow files by hand when the CLI can make the change.
- Never merge the pull request. The user merges it.
- Never remove the old CI. The user removes it after the first green run on Peak.
- If `PEAK_TOKEN` is set in the environment, the CLI uses it and skips the sign in. Do not ask for it. Do not echo it.
- To undo a run: `npx -y @peakinc/init@latest --undo`. It deletes the branch the CLI made and nothing else.

## Events you may see

`check`, `step`, `progress`, `free_minutes`, `authorization_required`, `waiting`, `authenticated`, `links`, `detected`, `plan`, `diff`, `applied`, `committed`, `pull_request`, `run`, `done`, `error`. The wizard adds `ci_detected`, `plan_requested`, `translate_skipped`.

Every question the CLI could ask has a flag. With `--yes` there are no questions. Without `--yes`, a `question` event arrives with `id`, `text`, `choices` and `default`; answer on stdin with `{"answer":"<id>","value":"<choice>"}`.
