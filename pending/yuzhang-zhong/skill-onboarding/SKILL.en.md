---
name: skill-onboarding
description: After a user first uses a skill, actually run it once and hand back a "usage card" that surfaces the capabilities buried in its docs. **Pairs with skill-creator**: right after creating or editing a skill with it, run this flow to verify the first run and produce a card, closing the "build → run → card → feedback" loop. Tool skills are the priority — one underlying tool is often split across a dozen skills (and the user can't tell which to use), or the reverse: a single skill hides dozens of commands and the user only remembers the most convenient one. This merges them into one card and diffs the tool's own inventory against local skills to find capabilities the user never knew existed. Triggers: first use of a skill, just finished using one, just created or edited a skill with skill-creator, or "what else can this skill do", "how do I use X", "what am I missing", "what else can this tool do", "what commands don't I know about". Behavior is configurable (language, auto-trigger, card length, exclusion list). Not for skill quality scoring.
version: 3.4.0
agent_created: true
license: MIT
metadata:
  tags: "onboarding, capability discovery, CLI companion, skill usage"
  category: "productivity"
---

# skill-onboarding

<p align="center">
  <strong>However well a skill is written, you only ever use the first two lines.</strong>
</p>

<p align="center">
  <a href="SKILL.md" title="简体中文">🇨🇳 简体中文</a> ·
  <strong title="English">🇬🇧 English</strong>
</p>

## Why this exists

Skills load progressively: only `name` and `description` enter context at session start.
So **a user only ever uses the 1–2 most obvious features**, and the rest of the document may as well not exist.

This skill does one thing: after a user first genuinely uses a skill, **run it once, read it once, hand back one card.**

## Pairs with skill-creator

The two skills are only complete **used together**:

```
skill-creator     →  create / edit a skill
skill-onboarding  →  verify the first run, hand back one usage card
```

The loop is **build → run → card → feedback**. Whatever the card exposes (missing dependency,
docs disagreeing with the implementation, an ability that was never written down clearly)
is exactly what to fix in the skill next round.

With `pair_with_skill_creator` on (the default): after using skill-creator to create or edit a skill,
**run this flow right away** — don't stop at "built".

Division of labour: create / edit / delete → skill-creator; run once + verify + write the card → this skill;
quality scoring → neither.

## Three steps

1. **Pick the target** — one skill, or a CLI tool family?
2. **Probe** — read the whole thing + run read-only probes
3. **Write the card** — five sections, readable in one sitting

---

### 1 · Pick the target

**A group of skills that is really one thing** → **one card for the whole family**. Two signals:

- They share one underlying tool or service (different names, same interface underneath)
- They cross-reference each other, or one carries a "sub-skill routing" table (one skill hands work off to several others)

The test isn't "the names look alike" — it's **"the user can't tell which one to use"**.

**The reverse case counts too**: one skill holding dozens of commands or hundreds of options. The user still only ever uses the one path that's most convenient. A card for an overloaded single skill has exactly the same shape as a family card — the second section still groups by what the user would say.

Skills may live in several different skills directories. Search all of them. **Skills installed from the official marketplace count too** — anything outside `~/.workbuddy/skills` still belongs in scope.

Check whether it has already been onboarded:

```
python "<skill_dir>/scripts/onboarding_state.py" check <id>
```

`NEW` → run the full flow. `SEEN` → only re-send when the user explicitly asks.

### 2 · Probe

**Read**: read SKILL.md in full, and **glance at the filenames under `references/`** — advanced capabilities usually live only there, with the main file saying nothing beyond "see xxx".

**Run**: pick the cheapest side-effect-free path. It must be a real call.

| Type | Probe |
|---|---|
| CLI tool | `--help` for the subcommand list → `doctor` / `status` / `whoami` for availability |
| Ships scripts | `--help` / dry-run / feed it minimal fake data |
| Generates artifacts | Write to a temp dir, delete afterwards |
| **No scripts / relies on an external service** | Check whether its declared prerequisites are present: is the tool on PATH, is the connection established. Run any self-check command it ships |
| Write-only (send mail, order, deploy) | Don't run it; verify up to a fully-constructed request |

**Within a set of scripts, prefer the ones that retrieve or query; avoid the ones that generate or call external services** — those need keys, cost money, and may mutate outside state.

**`--help` and the argument tables are the capability inventory — run them all if you can.** For CLI tools, `--help` on every major domain; for script-based skills, `--help` on every main script.
A user's blind spot is never "what is this tool called" — it's "there are fifteen more subcommands / fifteen more flags?".

**Three things that get misread as "the script is broken"**:

- `--help` reports a path error → usually the script **has no argument parsing** and treated `--help` as input. Run it with no args, or follow the usage format it prints itself.
- Output says "not found: `./xxx`" → the script **hardcodes a relative path** and must run from the skill directory. Nothing is actually missing.
- It returns structured JSON (even on error) → that's this skill's output protocol. Read the JSON, not the traceback.

**When it really fails, pick one of four causes and pick correctly**: missing dependency / **environment problem** / the command itself is broken / it simply never implemented `--help`.
Environment problems (shell, paths, wrapper) must read "environment issue, worked around" — **never "the skill is broken"**.

### 3 · Write the card

```
<✅ Working ｜ ⚠️ Partially working, reason ｜ ❌ Could not verify, reason>
<One line: what it is, what it's good at, what it isn't>

What you can do
    action      what you get
    action      what you get

What most people miss
    phrase      why it's worth knowing
    phrase      why it's worth knowing

If you remember one thing
    the shortest phrase
```

**Pick the second heading by nature**: `What you can do` for tools; `When it comes into play` for methods and guidelines.

**A family of skills gets a family card**: the second section becomes a "what do you want to do" list, grouped by what the user would actually say, **not by command or module name**:

```
What you can do
    Chat, groups        send, search history, create groups, escalate
    Set brand tone      brand
    Logos and banners   built into design
    Decks and pitches   built into design, with charts
```

(That shows the grouping shape only — don't copy it verbatim. Real cases live in `examples/`.)

**Rules**

- **No paths, no filenames, no provenance.** Users want capability, not location.
- **Write like a person.** Short sentences, concrete, spoken. Avoid "it's worth noting", "essentially", "this means that", "it comes as no surprise". No decorative emoji either, but keep the status marks ✅ / ⚠️ / ❌ since they carry information.
- Every capability needs a **copy-pasteable phrase**. If you can't write one, it's still a feature description.
- **Sections are a ceiling, not a quota.** If there's only one or two things to do, write one or two. The "what most people miss" section can be absent entirely. Padding is fabrication.
- Readable in one sitting: single skill ≤40 lines, family card ≤60.
- For family cards, the "what most people miss" section should lead with **diff findings**: what the tool supports vs what's installed locally. The gap is what the user never knew about.
- Any problem found must become an actionable next step, not just a complaint.
- **Choose the number in the first paragraph for maximum "look how little you've used".** Command count, capability-domain count, ready-made category count — whichever lands hardest ("50 commands", "hundreds of ready-made categories"). That sentence is the most valuable one on the card.
- **The first entry under "what most people miss" should be the one that changes your whole approach** — not an obscure flag, but something that routes you down a different path (classify before acting, narrow before sorting, background instead of waiting).

**Archive**

```
write   → ~/.workbuddy/skill-onboarding/cards/<id>.md
mark    → python "<skill_dir>/scripts/onboarding_state.py" mark <id>
```

## Configuration

Set once, applies from then on. Stored at `~/.workbuddy/skill-onboarding/config.json` (defaults used if absent).

```
python "<skill_dir>/scripts/onboarding_state.py" config                # show
python "<skill_dir>/scripts/onboarding_state.py" config set <key> <value>
python "<skill_dir>/scripts/onboarding_state.py" config reset          # back to defaults
```

| Key | Default | Effect |
|---|---|---|
| `language` | `zh` | Card language: `zh` / `en` / `auto` (follow the user) |
| `auto_trigger` | `true` | Offer a card automatically after a first run |
| `max_lines` | `40` | Line cap for a standard card |
| `family_max_lines` | `60` | Line cap for a family card |
| `exclude` | `[]` | Skills never to onboard (`check` returns `SKIP`) |
| `pair_with_skill_creator` | `true` | Run a first-run verification after creating / editing a skill |

Hard to break: invalid values are rejected up front, and `config reset` always brings you back.

## Safety

- **Read-only first**: no deleting files, no sending messages, no writing to production data, no placing orders, no changing config.
- IM write operations are limited to conversations of ≤3 people. Large groups are read-only, always.
- Anything that can only be verified by really touching a third party: verify up to a constructed request, and note "not actually run".
- Use fake data for verification. Never pull in real business data.

## Don't

- Write the card after reading only the description → step 2 skipped.
- Write "verified working" with zero tool calls → fabricated conclusion.
- Produce one card per skill in the same family → fragments the picture; the user still can't see the whole.
- Output scorecards / compliance checks / improvement advice → that's skill-tester's job.
- Recite the SKILL.md directory structure → that's a table of contents, not usage.

## Environment notes

- The scripts are pure Python standard library — `python` / `python3` just works. If it isn't on PATH,
  use the absolute path to your own interpreter.
- **Set the working directory via a `cwd` option, not by relying on `cd`** — in some restricted shells
  `cd` silently does nothing and the script still runs from the original directory. Plenty of skill
  scripts hardcode relative paths like `./references/...`.
- Some CLIs ship a `sh` wrapper depending on `dirname` / `sed`. On a shell with a broken toolchain it
  dies with `Cannot find module '...\node_modules\...'` (note the truncated path — the wrapper failed
  to resolve its own directory). Call the real entry point directly to bypass it —
  **this is an environment problem, not a broken skill**.

## Example

`example.md` — one standard card plus one CLI tool card. Match that density.
`examples/` — three real cards: a coding assistant, a PDF tool (50 commands), a stock screener (6 entry points). They cover the three typical shapes; use them as reference when writing.
