# Gauntlet

<img src="assets/gauntlet-icon-512.png" width="160" alt="Gauntlet: an armored fist with a check mark inside a shield">

An agent skill for adversarial review and root-cause repair of code, designs, APIs, infrastructure, and agent workflows. It directs the agent to look for counterexamples, substantiate findings, and re-attack repairs before declaring completion.

Reviews are read-only unless you authorize fixes. Gauntlet works with sub-agents or separate solo review passes; neither reviewer agreement nor a green test suite is treated as proof that all defects are absent.

## Install

From the project where you want to use Gauntlet:

```sh
npx skills add aakashH242/gauntlet --skill gauntlet
```

For user-wide installation instead:

```sh
npx skills add aakashH242/gauntlet --skill gauntlet --global
```

Choose one scope. The [Skills CLI](https://github.com/vercel-labs/skills) uses Node.js/npm and network access to install from GitHub. It detects installed agents and can prompt for a selection. To target a specific host:

```sh
# Codex
npx skills add aakashH242/gauntlet --skill gauntlet --agent codex

# Claude Code
npx skills add aakashH242/gauntlet --skill gauntlet --agent claude-code
```

For manual installation, copy this directory to your host's skill location and keep the supporting directories alongside `SKILL.md`:

| Host | Project location | User-wide location |
| --- | --- | --- |
| Codex | `.agents/skills/gauntlet/` | `~/.agents/skills/gauntlet/` |
| Claude Code | `.claude/skills/gauntlet/` | `~/.claude/skills/gauntlet/` |

Gauntlet follows the [Agent Skills format](https://agentskills.io/specification). `agents/openai.yaml` is optional display and invocation metadata for OpenAI hosts; the review instructions and tracker are shared across hosts.

## Use

Review only:

> Use Gauntlet to adversarially review this change. Focus on tenant isolation and retry safety. Do not modify files. Separate confirmed defects from unresolved hypotheses.

Review and repair:

> Use Gauntlet to review and fix this change at the root cause. Preserve unrelated work. Use sub-agents when available, otherwise perform separate solo passes. Do not deploy.

To select the skill explicitly, use `$gauntlet` in Codex or `/gauntlet` in Claude Code. Other hosts may provide a skill selector or use the natural-language requests above.

The workflow is **map → attack → substantiate → trace cause → repair → verify → re-attack**. The agent selects relevant review lenses, records findings and evidence, and works within a finite budget. Changes invalidate affected evidence; a round that changes the target cannot count as a clean re-attack. See [SKILL.md](SKILL.md) for the complete protocol and stopping rules.

## Optional tracker

The agent can track work using a host tool, a [Markdown ledger](templates/run.md), or the included Python helper. Without writable storage, it must label conversation-only tracking as non-persistent.

The helper requires Python 3.10+ with `sqlite3`, uses only the standard library, and needs no API key or network access:

```sh
python3 /path/to/installed/gauntlet/scripts/gauntlet.py --help
```

It stores tasks, findings, checks, revisions, and rounds in a SQLite ledger and validates recorded completion gates. It does not execute tests, spawn agents, authenticate approvals, or prove that supplied evidence is true. Keep ledgers in a private directory and out of version control. See [tracker instructions](references/tracker.md) for initialization and event examples.

The portable format and installer support multiple hosts. Agent behavior has not yet been evaluated across hosts or models; see the [evaluation guide](evals/README.md).

## License

[MIT license](LICENSE).
