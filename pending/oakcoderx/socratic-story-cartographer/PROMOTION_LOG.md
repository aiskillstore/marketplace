# Socratic Story Cartographer — Promotion Log

Last updated: 2026-08-31

This file is the working record for distribution experiments. The goal is not maximum posting volume; it is to learn which channels produce real installs, real story tests, and useful feedback.

## Distribution strategy

Target: **15 channels in three waves**. Do not publish the identical article everywhere. Registries get structured metadata, developer communities get methodology/benchmark framing, and creator communities get the editing problem + first-test framing.

### Wave A — Agent / Skill discovery (highest intent)

| Channel | Why it matters | Action owner | Status | Result / next signal |
|---|---|---|---|---|
| skills.sh | Cross-agent install ecosystem; real installs create discovery/leaderboard signals | Automatic after real user installs | HOLD | Exact-name public search still does not surface the skill; do not optimize for registry placement before real usage evidence |
| SkillsMP | Very large GitHub-indexed Agent Skill marketplace | Automatic crawl / monitor | HOLD | Exact-name public search still does not surface the skill; monitor, but do not spend launch effort here yet |
| dmgrok Agent Skills Directory | Quality/security-validated directory with provider submissions | User must submit GitHub issue; current GitHub App has read-only access there | DEFER | Submission body exists, but community-usage evidence is still too weak |
| Claude Skills Directory (skillsdir.dev) | Explicit community submission flow; accepts SKILL.md + links | User | DEFER | Wait for external usage proof |
| SkillsDirectory.com | Large scanned skills catalog with GitHub-authenticated submission | User | DEFER | Wait for external usage proof |
| SkillHub | Writing category + publish flow; supports uploaded SKILL.md/ZIP | User | DEFER | Wait for external usage proof |

### Wave B — AI / developer communities

| Channel | Why it matters | Action owner | Status | Notes |
|---|---|---|---|---|
| r/claudeskills | Direct Skill Share audience | User | NEXT_AFTER_PROOF | Use long-work A/B evidence, not a generic launch post |
| r/ClaudeCode | Large harness audience; benchmark/eval framing fits | User | NEXT_AFTER_PROOF | Lead with “Skill vs one good prompt” evidence on multi-file work |
| V2EX | Chinese Claude Code / Codex / Agent Skill builders are active | User | HOLD | Do not publish until there is one clean external proof case |
| Hacker News Show HN | Good fit for open-source AI tooling with technical methodology | User | HOLD | Current objection is exactly whether Skills add functional depth beyond prompts; answer with evidence before posting |
| X / Twitter | Fast place to test one-line value proposition among Agent builders | Assistant via Metricool after connection | BLOCKED_ON_ACCOUNT | X is still not connected |

### Wave C — creators / professional users

| Channel | Why it matters | Action owner | Status | Notes |
|---|---|---|---|---|
| r/WritingWithAI | Community explicitly discussing AI as editor/co-writer | User | PUBLISHED_LOW_SIGNAL | Creator falsification challenge posted 2026-08-20; public search now shows +1 vote and no visible substantive test report |
| 即刻 | Chinese AI + creative-professional overlap | User | HOLD | Do not reuse generic launch copy; wait for proof-led post |
| 知乎 | Long-form home for methodology and benchmark | User | HOLD | Best used after an external case study exists |
| LinkedIn | Professional AI/content-production audience | Assistant via Metricool | STRONGEST_SIGNAL | 2026-08-21 methodology post has grown to 275 impressions and 17 reactions by 2026-08-31; ~6.18% engagement, with no new LinkedIn post during Aug 24–31 |

## Explicit exclusions

- r/writing: do not post. Its current rules prohibit generative-AI advocacy/content.
- r/selfpublish: do not post. Current rules prohibit AI posts and restrict self-promotion.
- r/Writers: deprioritized. It permits resources but is broad and self-promotion-sensitive.
- Repeated cross-posts of the same launch message: stop.
- Upstream `VoltAgent/awesome-agent-skills` PR: defer until real community usage exists.
- Treating stars/forks on the parent fork as the primary KPI: stop; they are structurally poor adoption proxies for one subdirectory skill.

## What can be automated here vs. what requires the user

### Assistant can execute directly

- Update the public GitHub skill files and documentation in `OakcoderX/awesome-agent-skills`.
- Maintain this promotion log and channel-specific copy kit.
- Monitor public search/indexing signals.
- Publish/schedule LinkedIn through Metricool.
- Prepare A/B proof artifacts and channel-specific posts.

### User action currently required

- Third-party GitHub issues/PRs where the installed GitHub App has read-only access.
- Websites requiring GitHub/user sign-in or form submission.
- Reddit, Hacker News, V2EX, 即刻 and 知乎 posting because no authenticated posting connector is available in this runtime.
- Connect X inside Metricool if X automation is wanted.

## Actions already completed

### 2026-08-19 / 2026-08-20 — Repository conversion funnel

- Added one-command cross-agent install to README.
- Added a 3-minute first-test flow (`FIRST-TEST.md`).
- Added public benchmark methodology and limitations (`BENCHMARK.md`).
- Normalized `SKILL.md` frontmatter so the machine name matches the directory: `socratic-story-cartographer`.
- Added standard `license`, `compatibility`, and `metadata` fields.
- Added `skill.json` and a benchmark reference file for directory/registry compatibility.
- Changed positioning from “Codex skill” to portable Agent Skill across supported harnesses.

### 2026-08-20 — External distribution investigation

- Tested direct issue creation against `dmgrok/agent-plugins`; third-party write access was unavailable.
- Verified that an independent repository is not necessary for adoption.
- Created `PROMOTION_KIT.md` and this persistent log.
- Updated belief: real usage evidence should precede broad directory submission.

### 2026-08-20 — Creator falsification challenge

- User published the creator-facing falsification challenge in `r/WritingWithAI`.
- Message centered on “break the skill” rather than “please star it.”
- Public search later confirmed the post is indexable.

### 2026-08-21 — LinkedIn methodology test

- Assistant published a separate methodology/falsification post through Metricool at 11:00 Asia/Shanghai.
- By 2026-08-24, Metricool reported 57 impressions and 11 reactions (~19.3% engagement).
- By 2026-08-31, without another LinkedIn post, that same post had grown to **275 impressions and 17 reactions**, with Metricool reporting **~6.18% engagement**. The declining ratio is explained by reach expanding faster than reactions; the post continued to accumulate distribution rather than dying after the first day.

### 2026-08-24 — Weekly strategy review

**Channel comparison**

- **LinkedIn:** strongest positive signal. The audience is small but highly responsive to the methodology framing: AI critique has a hidden failure mode because the model tends to defend its first plausible diagnosis.
- **r/WritingWithAI:** appropriate venue and the post remains publicly indexable, but no substantive external test report, reply, or visible conversion signal has surfaced.
- **Skill directories:** exact-name searches still do not surface the skill. No evidence yet that registry work is the best use of launch effort.
- **GitHub:** repository remained at 0 stars / 0 forks at the review point. This was not a clean skill-level metric because the skill lives in a forked monorepo.

**Message comparison**

- The strongest message is not “Socratic storytelling.”
- The strongest current framing is: **AI story critique often locks onto its first plausible diagnosis; this skill forces the model to attack that diagnosis before telling you what to fix.**
- A second important claim remained unproven: **does the Skill reliably outperform one carefully written prompt?** Public Agent-Skill discussions repeatedly raise this objection, so broad developer promotion before answering it would be premature.

**Strongest current user segment**

Professional or serious AI-assisted story developers — people who already use general-purpose models for story/creative review and care about diagnosis quality, revision control, and repeatable workflows.

**Tactics to stop or pause**

1. Stop generic cross-posting of the same launch message.
2. Pause directory-submission work until there is at least one independent usage case or failure report.
3. Stop optimizing for GitHub stars on the fork as the core metric.
4. Pause long-form “what the Skill is” documentation; the repository already has enough explanatory material.

**Next week's highest-leverage distribution strategy: proof-led professional distribution**

Produce one compact public case study on unseen story material comparing the same model with one strong story-diagnosis prompt versus Socratic Story Cartographer. Judge only evidence anchoring, diagnosis update, regression awareness, and stop discipline. Publish the result first to LinkedIn, then use the same evidence — not the same copy — for one Agent-builder community.

**Product / README improvement executed**

Added a no-terminal quick start to the README.

### 2026-08-28 — v2.2 product release

- Released **Socratic Story Cartographer v2.2**.
- Added routed long-work evidence coverage for multi-file / long-form material.
- Added producer-outline review with decision pages, issue routes, hard-error separation, revision task cards, acceptance questions, stop lines, and human-approval boundaries.
- Ran two isolated synthetic behavioral smoke tests: an eight-episode producer-outline fixture and a multi-file fiction coverage fixture. Both passed their predefined criteria.
- Important limitation: these are product smoke tests, not independent-user validation and not evidence of superiority over a strong one-off prompt.

### 2026-08-31 — Weekly strategy review

**What changed this week**

- **LinkedIn remained the only channel with a meaningful positive signal.** The Aug 21 methodology post grew from 57 impressions / 11 reactions at the prior review to **275 impressions / 17 reactions**. No new LinkedIn post was published during Aug 24–31, so this was accumulated organic distribution rather than repeated posting.
- **Reddit did not convert visibly.** The `r/WritingWithAI` tool-thread entry is still indexed, but the public result shows only **+1 vote** and no substantive external break-test report.
- **GitHub moved from 0/0 to 1 star / 1 fork**, while the repo shipped v2.2 on Aug 28. This is a small independent adoption signal, but because the Skill remains a subdirectory inside a forked monorepo it should still be treated as secondary evidence.
- **Directory discoverability is still absent.** Fresh exact-name searches did not surface the Skill on the monitored registries/directories.
- **No independent real-user case study has appeared yet.** The v2.2 smoke tests improve product confidence but do not close the external-validation gap.

**Repeated objection / strategic risk**

The strongest objection is now even clearer: **why should this be a Skill instead of one carefully written prompt?** The Agent-Skills ecosystem itself emphasizes progressive disclosure, references, and scripts as the reason Skills can be more than a permanent prompt blob. For Cartographer, v2.2 finally creates a concrete answer: long-work mode routes to separate protocols, verifies source coverage, distinguishes unread scope from true absence, preserves authority boundaries, and compiles producer handoffs. That is a stronger differentiation surface than the abstract phrase “Socratic storytelling.”

**Strongest user segment**

Narrow the early-adopter segment to **professional AI-assisted story developers, producers, script editors, and long-form series creators** who already review multi-file or multi-episode material with general-purpose models. General fiction writers remain a possible later segment, but the current creator-thread signal is weak while the professional LinkedIn signal is clearly stronger.

**Strongest value proposition**

Use this framing next week:

> **Don’t let AI confidently review a long story it has not actually covered. Socratic Story Cartographer verifies coverage, attacks its first diagnosis, and turns supported findings into revision decisions instead of another list of notes.**

This keeps the proven “attack the first diagnosis” message but adds the v2.2 capability that a one-off critique prompt is least likely to sustain reliably across long work.

**Tactics to stop / keep paused**

1. Keep generic creator outreach paused; do not repost the Reddit launch message elsewhere.
2. Keep directory submissions paused until there is at least one real external use case or a clean A/B proof artifact.
3. Do not publish another “what is this Skill?” post on LinkedIn; the next post must contain evidence or a concrete case.
4. Do not treat v2.2 synthetic smoke tests as marketing proof of superiority.
5. Do not spend another week polishing general documentation unless a specific conversion objection appears.

**Next week's highest-leverage distribution strategy: long-work proof, then professional distribution**

Build one clean, inspectable A/B on **unseen multi-file or multi-episode story material**:

- same model;
- same source material;
- baseline = one strong, carefully written review prompt;
- treatment = Socratic Story Cartographer v2.2;
- blind evaluation on four dimensions: source coverage, diagnosis update/falsification, regression/authority awareness, and usefulness of the final revision handoff.

The test should be difficult enough that partial reading can create a plausible but wrong diagnosis. That is where v2.2 claims its strongest structural advantage.

If the Skill wins clearly, publish the result first on **LinkedIn**, using a compact case-study format rather than product copy. Metricool's current audience timing data peaks around **11:00 Asia/Shanghai on Thursday and Friday**, with Friday 11:00 the strongest slot in the coming week. After 48–72 hours, adapt the evidence for one Agent-builder community (`r/ClaudeCode` or `r/claudeskills`). If the Skill does not win, do not promote the result as a success: use the failure to revise the protocol.

**Product / README improvement executed**

Added a new **“Why a Skill instead of one good prompt?”** section to the README. It explicitly concedes that a good prompt may be enough for one short scene, then explains the narrower case where v2.2 should earn its complexity: long/multi-file work, routed reference protocols, coverage ledgers, protected/locked elements, producer handoffs, and repeatable review discipline. It also turns the claim into a testable A/B rather than an assertion.

**Next success signal**

The next meaningful milestone is no longer another star or another launch post. It is one of:

- a blind long-work A/B where v2.2 clearly beats a strong prompt on the predefined dimensions;
- an independent producer/writer completes a real multi-file review and reports a concrete result;
- an external tester finds a failure that changes v2.2's coverage or producer-review protocol.

Until one of those exists, further broad distribution has lower information value than producing the proof artifact.

## Success metrics

Track these instead of raw post count:

1. Confirmed external installs.
2. Number of people who run the skill on their own story.
3. Useful failure reports: wrong diagnosis, weak evidence, loop not updating, over-editing.
4. Blind A/B evidence against one strong prompt.
5. Registry/directory acceptance after real usage exists.
6. Organic mentions or stars only as secondary signals.

## Experiment rule

For each new channel, log:

- date
- channel
- exact message variant
- hypothesis
- observable result (24h / 72h when available)
- belief update
- next action

Do not repeat a channel until there is new evidence or a materially different message to test.
