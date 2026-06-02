# Dittobot

Voice-faithful rewrites for people who want AI to sound like them, not like a committee laminated a thesaurus.

[![Validate](https://github.com/RegionallyFamous/dittobot/actions/workflows/validate.yml/badge.svg)](https://github.com/RegionallyFamous/dittobot/actions/workflows/validate.yml)
![License: GPL-2.0-or-later](https://img.shields.io/badge/license-GPL--2.0--or--later-blue.svg)
![Runtime dependencies: none](https://img.shields.io/badge/runtime_deps-none-brightgreen.svg)

![A risograph-style Dittobot workshop turning messy notes into clean prose](assets/readme-riso-banner.jpg)

Paste messy notes. Get sharp prose that still sounds like you.

That should not be controversial, but apparently here we are.

## Start Here

In Codex, paste this:

```text
Use $skill-installer to install Dittobot from GitHub repo RegionallyFamous/dittobot. Use path "." and install it as "dittobot".
```

Then start a new Codex session and paste the mess:

```text
Use $dittobot on this:

[paste the draft, notes, rant, email, announcement, post, caption, or half-formed thought]
```

That is the streamlined path: let Codex install the skill, then use the skill. No git ceremony. No tiny terminal archaeology expedition before you can fix a sentence.

## The Point

The answer is not "never use AI." The answer is "teach the tool your voice."

This started because I watched the dumbest possible version of the argument show up in real life: people saw bad AI writing, decided they could write better than AI, and jumped straight to "nobody should use AI for writing." The evidence was the usual stuff: too verbose, too generic, weird grammar, dash crimes, and that unmistakable smell of a draft trying to sound important while saying almost nothing.

I agreed with the diagnosis and hated the prescription. Yes, bad AI writing is bad. Congratulations, we have discovered bad tools used badly. The interesting answer is not to ban the tool and hand everyone a purity badge. The interesting answer is to teach the tool taste, voice, restraint, and facts.

Bad AI writing is real. It gets verbose. It invents confidence. It uses phrases nobody says unless a webinar has taken them hostage. I get why people hate it. I hate it too.

But banning AI because bad AI writing exists is the wrong fight. That treats the worst workflow as the only workflow, which is a very confident way to lose the plot.

If your AI writes badly, the answer is not to throw away the tool. The answer is to teach it taste.

Dittobot is not a ghostwriter. It is a voice-preserving editor. It starts with your draft, protects your facts, keeps the human texture, cuts the fog, and hands back the version that sounds like you on a good day.

The better move, the more hopeful move, and frankly the less exhausting move is to encode taste.

## The AI Hater Case, Answered

The AI-writing backlash has a point. People have seen enough soulless, padded, fake-confident slop to be annoyed. Good. Stay annoyed. Just aim the annoyance at the right thing.

- **"AI writing has no soul."** Correct, if you ask it to invent one. Dittobot starts from your words. The stance, rhythm, humor, pressure, and weird little phrase are already there.
- **"It is too verbose."** Bad AI writes like it is being paid by the clause. Dittobot cuts filler and returns the rewrite without a lecture unless you ask for one.
- **"It all sounds the same."** Yes, if everyone accepts the first generic draft. Dittobot keeps dry jokes, justified edge, warmth, awkwardness, and useful rough edges.
- **"It makes things up."** That is a real failure mode. Dittobot does not add numbers, customers, citations, examples, legal certainty, or convenient details that were not in the source.
- **"It hides who wrote it."** Editing is not the same as outsourcing authorship. Dittobot keeps your claims, taste, and decisions in charge.
- **"The dashes give it away."** Dashes are not the crime. Predictability is. Dittobot can obey no-dash rules, but the deeper fix is cadence and taste.

The lazy move is not using AI. The lazy move is accepting output without taste, then blaming the whole category because nobody bothered to steer.

## Watch It Work

### Stream Of Consciousness

Source:

```text
ok the launch note is somehow both too long and says nothing. what i actually mean is we fixed the importer bug, people can retry failed rows now, and i need it to sound calm but not like a haunted changelog
```

Dittobot notices:

- The facts are "importer bug fixed" and "failed rows can be retried."
- The voice marker worth keeping is "haunted changelog."

Rewrite:

```text
We fixed the importer bug. People can retry failed rows now, so the launch note should be calm and useful, not a haunted changelog.
```

### Generic AI Paste

Source:

```text
In today's rapidly evolving landscape, our robust platform empowers teams to unlock seamless collaboration and drive meaningful impact.
```

Dittobot notices:

- The sentence sounds confident but says almost nothing.
- Inventing specifics would make it worse.

Rewrite:

```text
We are updating the platform so teams can find the work, make a decision, and move on. The draft still needs specifics: what changed, who it helps, and what people can do now.
```

### Voice Worth Keeping

Source:

```text
This draft is not bad. It just walks into the room and immediately apologizes for existing.
```

Dittobot notices:

- The image is the point.
- A smoother rewrite would be worse.

Rewrite:

```text
The draft is not bad. It just walks into the room and immediately apologizes for existing. The idea works; the framing is getting in its way.
```

### Precision-Sensitive Writing

Source:

```text
I think we probably need to send notice within 10 business days, but I am not counsel and the clause had weird carveouts.
```

Dittobot notices:

- "Probably," "I think," and "not counsel" are precision, not clutter.
- The rewrite must not turn uncertainty into legal certainty.

Rewrite:

```text
I think we may need to send notice within 10 business days. I would not state that as definitive, though, because I am not counsel and the clause had unusual carveouts.
```

### Mixed Human Stance

Source:

```text
I am a little angry that people saw bad AI writing and decided the answer was banning the tool, but I am also genuinely excited because we can teach it taste instead of pretending pencils are holy now.
```

Dittobot notices:

- The anger and hope both matter.
- The rewrite should be sharp without turning into a personal attack.

Rewrite:

```text
I am annoyed that people saw bad AI writing and decided the answer was banning the tool. But I am also genuinely excited, because we can teach it taste instead of pretending pencils are holy now.
```

## What Dittobot Is

Dittobot is a Codex skill for rewriting, tightening, diagnosing, and punching up prose while preserving the user's voice, intent, facts, stance, rhythm, humor, and formality.

It does four things by default:

- finds the point hiding inside the mess;
- protects facts, claims, constraints, and uncertainty;
- keeps the writer's rhythm, stance, jokes, and useful rough edges;
- removes bland AI tells without adding fake human mess.

For hard work, it expands into a silent 20-pass editorial loop. For proof, the repo ships a 100-case regression suite, model-free rewrite audits, privacy-first failure fixtures, compact voice profiles, fact fences, and public release scorecards.

Normal use is still simple: paste the mess and get the clean version.

## Use It

Most people should install from inside Codex:

```text
Use $skill-installer to install Dittobot from GitHub repo RegionallyFamous/dittobot. Use path "." and install it as "dittobot".
```

Terminal fallback:

```bash
curl -fsSL https://raw.githubusercontent.com/RegionallyFamous/dittobot/main/install.sh | bash
```

If you want a live symlink, clone the repo instead:

```bash
git clone https://github.com/RegionallyFamous/dittobot.git
cd dittobot
python3 scripts/install.py
```

Then:

```text
Use $dittobot on this:

[paste the messy draft, notes, rant, email, announcement, post, caption, or half-formed thought]
```

Most of the time, that is enough. Add instructions only for hard constraints like exact word count, no dashes, a specific audience, options, diagnosis-only mode, or a request to show what changed.

Discovery directories are useful too. Dittobot is built as a normal `SKILL.md` repo, so it can be listed by skills.sh-style directories and agentskill.sh-style browsers. That helps people find it. `$skill-installer` is still the cleanest path from "this looks useful" to "I am using it."

## Proof, Not Vibes

Dittobot's quality story is not "trust me, it feels good." The repo checks voice preservation, protected facts, uncertainty, claim fidelity, source-only thought-dump handling, exact word counts, no-dash constraints, and anti-generic behavior.

The scorecard is intentionally boring: complete-suite gates, stable failure codes, hashes, package checks, and public-safe reporting.

Taste up front. Receipts in the back.

## The Useful Boring Stuff

The manuals live in the wiki so the README can stay focused on the why and the examples:

- [Install](https://github.com/RegionallyFamous/dittobot/wiki/Install)
- [Validation](https://github.com/RegionallyFamous/dittobot/wiki/Validation)
- [Dittobot Lab](https://github.com/RegionallyFamous/dittobot/wiki/Dittobot-Lab)
- [Voice Profiles](https://github.com/RegionallyFamous/dittobot/wiki/Voice-Profiles)
- [Privacy And Fixtures](https://github.com/RegionallyFamous/dittobot/wiki/Privacy-And-Fixtures)
- [Live Eval And Scorecards](https://github.com/RegionallyFamous/dittobot/wiki/Live-Eval-And-Scorecards)
- [Release Checklist](https://github.com/RegionallyFamous/dittobot/wiki/Release-Checklist)

## Research Thread

The critique is worth taking seriously. Research on human-AI co-writing has found that writers care about preserving authentic voice, and other work has found AI suggestions can flatten writing toward dominant styles. Dittobot is a practical answer to that risk: keep the speed, reject the flattening.

This README also follows plain-language guidance: lead with the point, write for the audience, use short sections, prefer active voice, and let examples do real work.

- ["It was 80% me, 20% AI": Seeking Authenticity in Co-Writing with Large Language Models](https://arxiv.org/abs/2411.13032)
- [AI Suggestions Homogenize Writing Toward Western Styles and Diminish Cultural Nuances](https://arxiv.org/abs/2409.11360)
- [Digital.gov: Principles of plain language](https://digital.gov/guides/plain-language/principles)
- [CPSC: Plain Language Principles](https://www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/plain-language-principles)

## About The Name

The name is a playful nod to Ditto from Pokemon: transformation without losing the original shape. Also, "ditto" is a perfectly normal English word, so please do not sue me, Nintendo. Dittobot is unofficial and unaffiliated.

## License

SPDX-License-Identifier: GPL-2.0-or-later.

Copyright (C) 2026 Regionally Famous.

Dittobot does not claim ownership of text you write, rewrite, or edit with it. Your drafts and outputs are yours.
