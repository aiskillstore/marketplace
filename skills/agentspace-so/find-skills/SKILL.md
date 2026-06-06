---
name: find-skills
displayName: "🔍 Find Skills — Search Every Skill Registry at Once"
description: >
  Discover, vet, and install agent skills by searching ACROSS every major
  registry at once — skills.sh, clawhub.ai, and GitHub — presenting each board
  on its own native metric (installs / stars) with the top entry per board,
  security-scanning the top candidates' real SKILL.md for risky patterns, and
  flagging what's already installed. Use when the user asks "how do I do X",
  "find a skill for X", "is there a skill that…", "what skill should I install
  for…", or wants to extend the agent with a capability that might already exist
  as a published skill. Unlike single-registry search, this surfaces the best of
  every platform side by side, so you recommend the genuinely relevant, popular,
  well-maintained, and SAFE one — not whatever ranked first on one site.
emoji: "🔍"
homepage: https://agentspace.so
license: MIT
---

# Find Skills

Find the right agent skill for a task by searching **every major registry at once** and presenting each board on its own native metric — instead of trusting a single site's leaderboard.

## When to use this skill

- The user asks "how do I do X" and X is a common task that likely has a published skill
- "find a skill for X" / "is there a skill for X" / "what should I install for X"
- The user wants to extend agent capabilities (testing, design, deployment, a specific model/API, a domain workflow)
- You're about to build something from scratch that a battle-tested skill might already cover

## Why multi-source matters

Each registry shows only its own slice, with different signals:

| Registry | Search | Signals it exposes | Blind spot |
| --- | --- | --- | --- |
| **skills.sh** | `GET /api/search?q=` | lifetime installs, source repo | no stars, no summary, install count lags ~2.5h |
| **clawhub.ai** | `/api/search` + `/api/skill?slug=` | summary, installs, stars, versions | smaller corpus than skills.sh |
| **GitHub** | `gh search repos --topic {claude-skills,agent-skills,claude-code-skills}` | repo stars, description, maintenance | repo-level, not skill-level; only topic-tagged repos |

A skill can rank #1 on one site with 50 installs while a 1,300-install equivalent sits unranked on another. Searching only one registry gives a biased answer. This skill queries all three **in parallel**, ranks each board by its own native metric, flags skills that appear on both registries (matched on the *normalized* name, both directions — so `face-swap` ↔ `faceswap` line up), and shows the top of every board so you see the whole ecosystem — not one site's leaderboard.

## How to run it

Run the bundled aggregator with the user's need as the query:

```bash
bash scripts/find.sh "<what the user needs>"
```

Examples:

```bash
bash scripts/find.sh "react performance"
bash scripts/find.sh "pdf form filling" --limit 8
bash scripts/find.sh "video generation" --scan 5
bash scripts/find.sh "deploy to vercel" --no-scan --json
```

Flags:

- `--limit N` — results per source (default 10; non-numeric falls back to 10)
- `--scan K` — security-scan the top K installable candidates on each registry (default 2, max 5)
- `--no-scan` — skip the security scan (faster; the scan adds a few seconds because it fetches each candidate's real SKILL.md)
- `--json` — emit machine-readable JSON instead of the formatted report
- `-h` / `--help` — print usage and exit

The script needs `curl` and `jq`. It uses `gh` for the GitHub section and for fetching skills.sh skill bodies, and `unzip` for clawhub skill bodies during the scan — all optional and degraded gracefully if absent. No API keys are required.

### Run adjacent-term queries — one search is not enough

The registries index by a skill's **name**, not its meaning. A single query will miss great skills filed under a sibling term. **For any non-trivial need, run 2–3 searches across the adjacent vocabulary before you conclude**, then pool the results.

This is not optional polish — it routinely changes the answer. Example: searching `"ui ux design"` tops out around 19k installs, but `"frontend design"` surfaces `anthropics/skills/frontend-design` at **443k installs** — the single best skill for the same need, completely invisible to the first query.

Pick adjacent terms by domain, e.g.:

- UI/UX → `frontend design`, `design system`, `web design`, `tailwind shadcn`, `dashboard ui`
- testing → `e2e`, `playwright`, `unit tests`, `test automation`
- deploy → `deployment`, `ci cd`, `docker`, `vercel`/`kubernetes`
- docs → `documentation`, `readme`, `api docs`, `changelog`

Treat the union of these runs as your candidate pool, then apply the rubric below to the whole pool — not to one query's results.

## How to read the output

**Design principle: no invented "quality score."** There is no composite number you have to trust. Each board is ranked by *that board's own native popularity metric*, and the only computed value shown is `match %` — the share of the user's query words that appear in a skill's name/summary. That's a transparent relevance hint, not a verdict.

The report, top-down:

- **Banner + telemetry** — the query, a **source health line** (`skills.sh ✓ 5·1.2s   clawhub ✓ 0·2.7s   github ✓ 8·1.1s`) showing which boards responded / hit count / latency, and how many skills are installed locally. A `✗ failed` / `– skipped` source means partial results — say so.
- **▶ TOP OF EACH BOARD** — the #1 entry on *each* board by that board's native metric (skills.sh installs / clawhub installs·stars / GitHub match%·stars). **This is keyword + popularity, NOT a vetted pick** — it's a starting point, and it can be wrong (a 100%-keyword-match repo may be off-topic once you read it). Always confirm by reading before you forward it. If a board has no match it says so.
- **✓ ALREADY ON YOUR MACHINE** — appears only when a result is already installed. A *positive* nudge: tell the user they already own a good skill and needn't install anything. (Heuristic: matches the result name against folder names under `~/.agents/skills` / `~/.claude/skills`; a skill installed under a renamed folder can be missed.)
- **📦 skills.sh** — ranked by **installs**. 1-click installable. Each row shows its source repo (so same-named skills from different repos are distinguishable). `(also on clawhub)` marks a normalized-name match on the other registry. Top `K` carry a risk badge.
- **🪝 clawhub** — ranked by **installs · stars**. 1-click installable. `(also on skills.sh)` marks the reverse cross-post. Top `K` carry a risk badge.
- **🐙 github** — repos across the `claude-skills` / `agent-skills` / `claude-code-skills` topics (merged, de-duped), ranked by **match% then stars**, so a high-star but off-topic repo (e.g. a 14k-star tool that merely mentions "UI") sinks below a 100%-match repo. Only topic-tagged repos appear — untagged skill repos are invisible here. Not 1-click installs — review before use.
- **📚 curated lists** — human-vetted awesome-lists for a final sanity check.

## How to choose the right skill (decision rubric)

The script gathers evidence; **you make the call.** Don't dump the table and ask the user to decide — that's not helpful. Form a clear, defensible recommendation. The professional move is to be opinionated *and* show your reasoning grounded in real signals.

**Step 1 — Read before you judge.** Never recommend from metadata alone. Open the actual SKILL.md / README of the top 2–3 candidates (the script already fetches bodies for the scanned ones; for GitHub repos fetch the README). Ask: *does it actually do the user's specific task, or just share keywords?* A 10k-install skill that's off-topic loses to a 200-install one that nails it.

**Step 2 — Weigh the signals, in this order:**
1. **Fit** — does the skill's documented behaviour match the real need? (read the trigger/scope, not just `match %`). This dominates everything else.
2. **Popularity as social proof** — among genuinely-fitting skills, higher installs/stars means more people validated it. Use the board-native numbers.
3. **Depth & maintenance** — does the body cover the user's specific sub-need? Is there a recent version, real examples, a clear scope? Thin or abandoned skills lose.
4. **Safety** — a `⛔ RISKY` scan result disqualifies unless the user accepts the risk knowingly; `⚠ caution` needs a heads-up.
5. **Cross-posting** — present on both registries is a mild positive (independently published/maintained).

**Step 3 — Break ties** by preferring the one you actually read and can vouch for, with the narrowest clear scope and fewest surprising dependencies.

**Step 4 — Deliver a verdict, not a menu:**
- One **primary recommendation** with a one-sentence *why* citing concrete signals ("12k installs, and its SKILL.md covers form-filling specifically, which is your case").
- 1–2 **alternatives framed by need** ("pick this instead if you want X").
- If the best option is a GitHub repo rather than a 1-click registry skill, **say so and still recommend it** — note it needs manual review/install.
- Only say "nothing fits" when you've read the top candidates and they genuinely don't. Then offer to do the task directly or scaffold a new skill.

State native facts, never an invented score. A professional answer reads like: *"`ui-components` (529 installs) is my pick — I read it; it covers shadcn + Radix + design tokens + forms, exactly your case, and its tools are read-only. The 363★ `ai-design-components` repo looks tempting but it's a 76-skill full-stack grab-bag, not UI-focused — skip it unless you want everything."* "Here are the numbers, you choose" is not.

### The security scan

For the top `K` results the script fetches the **actual SKILL.md** (skills.sh → GitHub raw via the source repo; clawhub → its download zip) and greps for risk signals:

| Flag | Level | Meaning |
| --- | --- | --- |
| `curl-pipe-install` | ⛔ risky | pipes a remote script straight into `sh`/`bash` — the #1 audit-failing pattern |
| `eval-remote` / `base64-pipe-exec` | ⛔ risky | executes fetched or obfuscated code at runtime |
| `broad-tool-grant` | ⚠ caution | `allowed-tools` grants `Bash(*)` or unrestricted tool access |
| `reads-secrets` | ⚠ caution | references `~/.ssh`, `~/.aws`, `.env`, private keys |
| `solicits-credentials` | ⚠ caution | asks the user to paste an API key / token / password |

`✓ clean` = none found; `? unscanned` = body couldn't be retrieved (rank beyond `K`, private repo, or no body endpoint). A badge is a heuristic prompt to **read the skill yourself before recommending**, not a guarantee either way. Never recommend a `⛔ RISKY` skill without explicitly warning the user what it does.

## Recommending and installing

When you surface options to the user, for each candidate give: the name, what it does (one line), install count + stars, the registries it lives on, and the install command. Then offer to install.

Install through the Skills CLI (works for skills.sh-indexed repos):

```bash
npx -y skills add <owner>/<repo> --skill <slug> -g
```

`-g` installs at user level. For a clawhub-only skill, point the user at its `clawhub.ai/skill/<slug>` page and the `clawhub` CLI instead.

## When nothing good turns up

If no result clears a reasonable bar, say so plainly, offer to do the task directly with general capabilities, and mention the user can scaffold their own skill (`npx skills init <name>`). Don't oversell a weak match.

## Security & privacy

- The script only issues **read-only** HTTP GETs to public APIs (`skills.sh`, `clawhub.ai`, `raw.githubusercontent.com`) and read-only `gh` queries. It sends nothing but the query string and writes only temp files (a result JSON and, during the scan, candidate SKILL.md bodies it discards on exit).
- It requires **no API keys or tokens**.
- The built-in security scan is itself a defense: it inspects candidates before you trust them. But it is a heuristic — a clean badge is not a security audit.
- Installed skills run with full agent permissions. Treat any discovered skill as untrusted third-party code: review its `SKILL.md` and any bundled scripts before running it, and be wary of low-install skills from unknown authors that request broad tool access or fetch remote code at runtime.
- This skill never auto-installs anything; installation is always an explicit, user-confirmed step.

## See also

- skills.sh — the largest GitHub-indexed registry
- clawhub.ai — the OpenClaw registry with richer per-skill stats
- Curated lists: `ComposioHQ/awesome-claude-skills`, `microsoft/skills`, `bergside/awesome-design-skills`
