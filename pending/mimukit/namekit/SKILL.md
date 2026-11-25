---
name: namekit
description: >-
  Name a project to a naming convention you already use, then prove the name is free on the domain, npm, and GitHub before you commit to it. Use when the user says "name this project", "what should I call this", "give me project name ideas", "come up with a name for X", "is <name> taken", "check if this name is available", or "/namekit".
license: MIT
disable-model-invocation: true
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch, WebFetch
metadata:
  internal: false
---

# namekit

Name a project against a **convention** rather than a blank page, and hand back only names that are actually free. Two explicit **modes**:

- **`generate`.** Turn a project description into a ranked shortlist of names built to the user's naming convention, then probe the two or three the user picks against the domain, npm, and GitHub namespaces and crown one.
- **`check`.** Take names the user already has and report whether each one is free. No generation.

## When this fires

An ask that supplies a description gets `generate`. An ask that supplies names gets `check`. When the user supplies both, run `check` on their names first, then offer `generate`, because a name they already like outranks anything you invent.

## The probes (both modes)

Three namespaces, three commands. Each one is a public HTTP contract, so it is safe to pin.

```sh
# domain registration: status, final URL, content type (read the rule below)
curl -s -o /dev/null -w '%{http_code} %{url_effective} %{content_type}' -L --max-time 10 https://rdap.org/domain/<name>.com

# npm package: 404 = free
curl -s -o /dev/null -w '%{http_code}' --max-time 10 https://registry.npmjs.org/<name>

# GitHub org or user handle: exit 0 = taken; "HTTP 404" on stderr = free
gh api /users/<name> --silent
```

**A domain 404 is a verdict only when a registry answered it.** rdap.org redirects to the registry's own RDAP server, so a 404 means "not registered" only when the final URL is off rdap.org and the content type is `application/rdap+json`. A 404 that stays on rdap.org means the TLD has no RDAP service (`.de` and `.io` returned this for registered names), and a `text/html` 404 means the registry endpoint failed (`.ai` returned this for `google.ai`). Report both as unknown (checked 2026-11-16).

**Read only the listed answers as verdicts.** A domain or npm status other than 200 or 404 (a 429, a 5xx, `000` on a timeout) is **unknown**. For `gh api`, only exit 0 means taken, and only a nonzero exit whose stderr says `HTTP 404` means free. Any other failure is unknown: `gh help exit-codes` lists 1 for any failure, 2 for a cancel, and 4 for missing authentication, and none of those proves the handle is free. Retry an unknown probe once. A name with an unknown result after the retry is neither removed nor crowned as free; report the namespace as unknown and name the reason.

Check `.com` plus whichever second TLD the project's surface implies (`.dev` for a developer tool, `.ai` for a model product, the country TLD for a local audience). Skip a namespace the project will never occupy: a CLI-only tool does not need an npm name, and an internal tool needs no domain.

**Probe two or three names at a time.** RDAP answers a small batch and returns 429 to a burst, and a 429 is not a verdict. A bulk sweep of dozens of names throws away its own domain results.

**Report each result as that probe's own claim.** A 404 from RDAP means the domain is not registered. It does not mean the domain is for sale, is affordable, or is free of a trademark. Say "not registered", and let the user find out the price.

**Degrade rather than block.** With no shell, no network, or no `gh`, say which probes were skipped and hand back the ranked shortlist on the four rubric criteria alone.

---

## Mode: `generate`

### 1. Restate, then interview

Reflect the project description back in one sentence before asking anything.

Then interview. Six items make the pool; ask only the ones the description leaves open, and check each item against the description rather than skipping the round because it reads complete ("AI growth platform for SMBs" still names no audience, tone, or surface), cap the round at five questions, and ask them in a single batch:

1. **What it does.** The domain and the outcome.
2. **Who it is for, and what language they read.** A Bangla-reading audience opens roots an English-only audience closes.
3. **Tone.** Plain, technical, or playful.
4. **Words to include or avoid.** A founder usually has one of each.
5. **Where the name gets typed.** Domain, package name, CLI command, org handle. This sets the length tolerance and decides which probes run.
6. **How permanent it is.** A throwaway internal tool and a product you will defend for a decade deserve different effort.

**Done when** every unanswered pool item has an answer or an explicit "does not matter", and the restatement stands uncorrected.

### 2. Resolve the convention

Work down this ladder and stop at the first rung that answers:

1. **Stated.** The user names the convention outright ("suffix everything with `aloy`").
2. **Derived from examples.** The user cites their own names ("like `codealoy`, `growaloy`, `saasaloy`"), and the shared tail is the convention.
3. **Read from their repos, on request.** Only when the user points at them: `gh repo list <owner> --limit 100 --json name`. Sample the projects, not the forks, because a fork's name is somebody else's convention.
4. **Ask.** Offer suffix, prefix, portmanteau, or none.

**Read the convention fresh every run.** Never store it or fall back to a house default such as `kit`; a stored convention goes stale when the user changes their mind, while names already shipped stay current.

**State the resolved convention in the output.**

**Done when** the convention is written down as an affix plus its position, or the user has chosen to work without one.

### 3. Mine roots and build candidates

Draw roots from **four separate sources**:

- **The domain noun.** What the thing is about: `code`, `saas`, `ledger`.
- **The outcome verb.** What it does for someone: `grow`, `ship`, `learn`.
- **The user or their material.** Who holds it: `dev`, `shop`, `desk`.
- **The metaphor, or a non-English root** when the interview named a non-English audience.

A non-English root passes **one gate**: a single Latin transliteration dominates in common use. When a root has two spellings people both write, drop it rather than scoring it down.

Join each root to the affix with the [seam rule](#the-seam-rule), score it against the [rubric](#the-rubric), then cut. Generate **25 or more raw candidates**, and rank the best **12** into the shortlist. The width is deliberate: the user probes two or three names per batch, so the list has to feed several batches before it needs regenerating.

**Done when** the ranked 12 draw roots from at least three of the four sources, and each carries a one-line rationale plus its rubric verdict.

### 4. Show the shortlist, then probe what the user picks

**Print the ranked 12 before you probe anything.** The names come first, in a table of name, root and source, seam case, and rubric verdict, with no availability column yet.

Then ask the user to pick **two or three names** to probe. Use `AskUserQuestion` when it is available, and a plain one-line ask when it is not. **Probe only the names the user picks.** An unpicked name stays unprobed, however good its rubric score.

Run [the probes](#the-probes-both-modes) over the picks. **Any hit removes that name.** Availability is a verdict here, not a score.

**One exception: a namespace the user already owns passes, and reads *yours*.** Resolve their owner from the git remote when a repo exists (`gh repo view --json owner`), from the repos that sourced the convention otherwise, and by asking once when neither answers.

**When a batch returns nothing free**, report each pick with the probe that killed it, reprint the candidates still unprobed, and ask for the next batch of two or three. Repeat the loop until one name is free or the user stops it. Never auto-select the next batch, because the pick is the user's.

**Regenerate only when the list runs out.** Once every one of the 12 is probed and taken, run [Mine roots and build candidates](#3-mine-roots-and-build-candidates) again with the taken roots excluded, and show the new list the same way. **Two generation passes is the cap.**

**Done when** at least one probed name is free in every probed namespace, or the user stops the loop, and every probed name carries a free, taken, or unknown result for every probe that ran.

### 5. Crown, then search once

Crown the free name that ranks highest on the rubric. Then run **one** web search, on that name alone, for the existing product or live trademark the registries miss. Fetch the top hit when the search result is ambiguous about what the thing is.

A hit re-crowns the next free name and states the conflict in a line, and the new crown gets its own search before you report it. Repeat until a crowned name survives its search. When no free runner-up is left, say so and send the user back to the pick loop. Search only the crowned name.

**Done when** the final crowned name has been searched and survives, or no free name is left to crown.

### 6. Hand off

_Write every hand-off in this skill in the procedural register: one instruction per sentence, active voice, present tense, no metaphor._

Print the probed names as a ranked table before the three beats:

| Name | Root (source) | Seam | Rubric | `.com` | npm | GitHub |
|------|---------------|------|--------|--------|-----|--------|
| `growaloy` | grow (outcome verb) | hard join | 4/4 | free | free | free |

**What changed.** Report the resolved convention, the crowned name and the one-sentence reason, how many batches the user probed, and whether a second generation pass ran. Name each probed name the registries took, with the probe that killed it. List the candidates that stayed unprobed, so the user can come back to them.

**Where it landed.** namekit writes no file by default. Write `docs/names/NNNN-names-<slug>-YYYY-MM-DD.md` only when the user asks, where `<slug>` is the project's short kebab-case name and the date is the file's creation date. To get the serial `NNNN`, take the highest leading four-digit serial in `docs/names/` across this worktree, every other worktree that `git worktree list` names, and `origin/<default branch>` (`git ls-tree --name-only origin/<base> docs/names/` after `git fetch origin <base>`), and add one; start at `0001` when there is none. Scan all three, because parallel worktrees otherwise take the same serial. Skip a source that fails, such as no remote, and without git list the directory only. The serial is per directory and never reused. Keep the whole name stable on a later edit. Follow the host repository's own artifact convention when it documents one. With no filesystem, print the document as a codeblock and give the filename.

**Next.** Crown one move. The name is chosen and nothing owns it yet, so the move is to claim the namespaces the project actually needs, in the order the interview's typed-surface answer implies. Name **repokit** to set a new repo's About panel and topics when it is installed, otherwise `gh repo create`. When the name came out of an idea session, name **ideakit** as the runner-up so the decision lands back in that idea's log. namekit never registers a domain, publishes a package, or creates an org.

### The seam rule

Three cases cover every convention.

- **Hard join.** The root's tail and the affix's head do not collide, so concatenate. `code` + `aloy` → `codealoy`. Prefix form: `open` + `forge` → `openforge`.
- **Elision.** They overlap, so drop the duplicate. `data` + `aloy` → `dataloy`, not `dataaloy`. Prefix form: `auto` + `optimize` → `autoptimize`.
- **Reject.** The seam makes a vowel pileup or a syllable nobody says aloud, and no elision saves it. `idea` + `aloy` elides to `idealoy`, which reads as "ideal-oy". Drop the root and pick another.

### The rubric

Four criteria, scored pass, weak, or fail. Rank by the count of passes, and break a tie on semantic fit.

- **Semantic fit.** The root says what the thing does.
- **Sound.** Three to four syllables, and it reads correctly on first sight.
- **Seam quality.** A clean hard join or a clean elision, per the seam rule.
- **Spell-on-hearing.** Someone who hears the name spells it one way.

Availability is deliberately absent. It is a verdict in [Show the shortlist, then probe what the user picks](#4-show-the-shortlist-then-probe-what-the-user-picks), not a fifth criterion, because the rubric ranks names the user has not probed yet.

---

## Mode: `check`

Run [the probes](#the-probes-both-modes) over the names the user supplies. Generate nothing, rank nothing, and filter nothing.

Apply the same owner exception: a namespace resolving to the user's own owner reads *yours*, not *taken*.

### Hand off

**What changed.** Report one line per name with its result in each namespace (free, taken, unknown, or yours). Give the reason for each unknown. Name the probes that were skipped.

**Where it landed.** Nothing was written and nothing was registered. Say so plainly.

**Next.** Crown one move from the results. When a name is free, the move is to claim it, so name **repokit** for a new repo's metadata when it is installed, otherwise `gh repo create`. When every name is taken, the move is `generate`, which mines new roots around the same idea.

---

## Notes

- **namekit names the thing and stops.** No logo, no tagline, no positioning, no brand identity, and no renaming of an existing codebase's identifiers.
- **Social handles stay out.** Headless checks against social platforms are rate-limited and return false negatives, and a wrong "taken" is worse than no answer.
- Prefer a probe's status code over scraping a page, because the status code is a stable contract and the page is not.
