---
name: agent-checkpoint
description: 'An undo button for AI agent work: save the project before a risky change, see exactly what changed, roll back in one command. Use when: Save a checkpoint before a refactor, codemod, dependency upgrade or migration; See exactly which files an agent added, changed or deleted; Roll back the whole project or a single file, and undo the roll back.'
license: MIT
metadata:
  author: Nex AI
  version: '1.2'
  agensi-slug: agent-checkpoint
compatibility: 'Works with any agent that can run Python 3.8+: Claude Code, Codex, Cursor, Windsurf, Cowork. The automatic hook is for Claude Code.'
---

# Agent Checkpoint

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/agent-checkpoint). Scripts, extension source, and templates from the original package are not in this folder.

### What it does

One script, `checkpoint.py`, that gives any project an undo button for agent work:

```bash
checkpoint.py save -m "before the payments refactor"
checkpoint.py diff --patch
checkpoint.py restore 1 --dry-run
checkpoint.py restore 1
```

### Why next to git and /rewind

- Claude Code's `/rewind` tracks edits made with Claude's file tools. It does not track files changed by **Bash commands** (`rm`, `mv`, `sed -i`, generators, `npm install`, formatters), by background **subagents**, or by other tools.
- Asking an agent to commit or stash before every risky step pollutes history, and `stash`/`checkout`/`reset` are exactly the commands that lose uncommitted work when they go wrong.

### Safe by design

- **Inside git**: checkpoints are commits under `refs/checkpoints/`, built with a private index. Your branch, HEAD, staging area and stash are never touched, and checkpoints are never pushed.
- **Outside git**: deduplicated content-addressed copies in `.agent-checkpoints/`.
- **Every restore is undoable**: it checkpoints the current state first.
- **Never loses what it did not save**: files that are ignored, too large, or inside nested repositories and submodules are left alone.
- **Byte-exact**: line endings, modes and symlinks come back as saved.
- Optional **Claude Code hook** that checkpoints before Bash commands that can change files and before subagents start, merged into your existing settings with a backup.

Python 3.8+, standard library only. 79 automated tests, including regressions for every issue found in a pre-release review.

Built by Nex AI, nex-ai.be

## When to use

- Save a checkpoint before a refactor, codemod, dependency upgrade or migration
- See exactly which files an agent added, changed or deleted
- Roll back the whole project or a single file, and undo the roll back
- Recover from changes Claude Code's /rewind does not track (Bash commands, subagents, other tools)
- Checkpoint automatically before risky Bash commands with a Claude Code hook

## Known limitations

Not a backup: checkpoints live on the same disk. Submodule and nested repository contents, ignored files and files over the size limit (default 50 MB) are not captured. Byte-exact line endings need git 2.40 or newer. Recreating symlinks on Windows needs Developer Mode or admin rights.

## Example

**Request**

Refactor the payments module to support a second provider. Save a checkpoint first so we can go back if it gets messy.

**Result**

## Checkpoint saved, refactor done, and an easy way back

Before touching anything:

```
$ checkpoint.py save -m "before the payments refactor"
Checkpoint 1 saved (git): before the payments refactor
```

After the refactor, here is exactly what changed:

```
$ checkpoint.py diff
Since checkpoint 1 (before the payments refactor): 4 modified, 1 added, 2 deleted
  M  src/index.ts
  D  src/orders/draft.ts
  D  src/orders/routes.ts
  M  src/orders/service.ts
  A  src/payments/providers/index.ts
  M  src/payments/refunds.ts
  M  src/payments/stripe.ts
```

The two deletions in `src/orders/` were not part of the plan (a codemod I ran matched too broadly), so I rolled those back only:

```
$ checkpoint.py restore 1 --path src/orders/draft.ts --path src/orders/routes.ts
Restored checkpoint 1 (before the payments refactor) (src/orders/draft.ts, src/orders/routes.ts): 2 added
  A  src/orders/draft.ts
  A  src/orders/routes.ts

The state before this restore is saved as checkpoint 2. Undo with: checkpoint.py restore 2
Your branch, HEAD and staging area were not touched; 'git status' shows the restored files as changes.
```

### If you want to drop the whole refactor

`checkpoint.py restore 1` puts the project back exactly as it was, and `restore 2` would bring the refactor back.

## Questions

### Is this a backup?

No. Checkpoints live on the same disk as the project. It undoes bad edits; it does not survive a dead drive.

### Will it mess with my git history?

No. It never changes HEAD, branches, the staging area or the stash. Checkpoints are refs under refs/checkpoints/ that git push does not send.

### Does it store my .env?

No. Ignored files are never captured, restored or deleted.

### Does the hook slow Claude down?

Read-only commands exit in under 0.1 s. A git checkpoint of a 5,000-file project takes about 0.1 s; outside git the hook gives up after 20,000 files or 8 seconds instead of stalling.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
