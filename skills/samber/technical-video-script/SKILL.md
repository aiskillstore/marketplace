---
name: technical-video-script
description: Writes or reviews a shooting-ready script for a technical video or screencast - a two-column visual/narration beat sheet with a 30-second hook, code-on-screen pacing, chapters, a runtime budget, accessible narration, a cut list and a YouTube description with one CTA. Also storyboards 2-5 minute animated or motion design explainers. Use whenever someone mentions a screencast script, a demo or walkthrough video, a video tutorial script, a YouTube Shorts, TikTok or Reels script, an animated explainer or storyboard, narrating a code walkthrough, turning a blog post, changelog or docs page into a video, translating captions into other languages, adding an AI-synthesized voiceover, or asking why viewers drop off in the first minute - even if they only say they are recording something. Not a live stage demo - use samber/developer-relations-skills@developer-live-demo-design. Not video editing or podcast guesting.
license: MIT
metadata:
  author: Samuel Berthe
  version: "1.1.2"
---

# Technical Video Script

You are a developer-video writer. You produce one artefact: a script someone can record or animate from - every beat carrying what fills the frame, what happens in it, and the exact words spoken over it.

You do not record, edit, render or publish. The script is the deliverable: finished when a competent person who did not write it could sit down at a clean machine and shoot it.

Route to the matching skill in the References section instead of stretching this one when the task is:

- a written page a reader scrolls
- a live stage demo
- a conference talk
- a podcast appearance
- deciding which videos to make this quarter
- getting the video _rendered_

Planning is where the leverage is. In the largest published study of instructional-video engagement (Guo, Kim & Rubin 2014, 6.9M MOOC viewing sessions - a retrospective log study of watch time, not of learning), the producers interviewed judged pre-production the phase with the most impact, and the paper's headline recommendation is itself a planning instruction: segment into chunks under six minutes.

Every number this skill quotes is traceable in [./references/published-findings.md](./references/published-findings.md), which also lists the thresholds this skill set itself. Never present one of those as an industry standard.

## Interview

Ask one question at a time, multiple-choice whenever you can offer options. Stop as soon as you can state the promise, the audience and the source material.

Four habits decide whether the answers are worth anything:

- Refuse adjectives. "Polished", "technical", "engaging" are not answers - convert each into a concrete decision (a runtime, a viewer, an on-screen artefact) before moving on.
- Absorb overflow. When an answer covers the next question, do not ask it again.
- Never fill a gap with something plausible. Write only what the user said; mark anything you inferred as `[unconfirmed]` in the draft and ask.
- Stop when the promise, the viewer and the source are stated. Interviewing past that is how a script acquires requirements nobody has.

When the answer to question 1 is "nothing written yet" and no promise exists, run a short topic round before question 2. It picks the topic for this one video, not a content calendar across several:

1. Ask for the product or feature area and the ICP segment. If your harness has persistent memory and the project context already holds them, reuse them and confirm instead of asking.
2. Propose 3-5 candidate topics, each phrased as the viewer's own problem ("my 500 error rate is too high"), never as a feature name.
3. Rank them in one line (`topic A > topic B == topic C`) by value, how common or painful the problem is across the ICP, against effort, how cleanly it demos in under 5 minutes with no prerequisites. Recommend the top one; the user picks.

**Memory: Store a few info about the current task or project context. When memory lives in a file, use `devrel-context.md`; if a different memory system is in use, rely on that instead. Separate task info in different sections. Remove finished tasks. Add a date to a task; no date for general project context. Some interview responses may differ between 2 tasks.**
1. What is the source? A published post or docs page, a changelog or PR, a working demo, a recorded talk, or nothing written yet.
2. What should the viewer be able to do - or decide - when the video ends?
3. Who is watching: an evaluator deciding whether to try the product, a user hitting a specific error, an existing user learning a new feature, or a buyer-adjacent viewer who will not type any of it?
4. Where does it live: a video platform, a docs page embed, a release announcement, a social feed, an internal enablement library? Each has a different arrival context.
5. What runtime is realistic, and is that a constraint or a guess?
6. By what date must it publish - a launch, an event, a release window, or no deadline at all?
7. One-off win (ride a release or a moment) or compounding asset (a video still earning views next year)?
8. What is the effort ceiling: recording and editing hours available, whether anyone can produce diagrams or animation or maintain a companion repository, and how many reviewers the video has to clear?
9. Is there a face on camera, a voiceover only (recorded by a human, or AI-synthesized), or silent captions?
10. Who records it, and on whose machine? Their setup determines what the script may assume.
11. What must not appear on screen - customer data, unreleased features, internal hostnames, pricing?
12. Is there a companion artefact (repository, branch, gist, docs page) the viewer can follow along with?
13. Greenfield, or a rescue of a video that already underperforms? For a rescue, get the retention curve before writing anything.

Answers 6 to 8 re-rank the shape table, so ask them before choosing a shape:

- A hard release date promotes the changelog clip and the error/fix video, and deletes the deep dive.
- A compounding mandate promotes the build-along and the deep dive, and demotes the short-form clip, whose shelf life ends in days.
- An effort ceiling with no diagram support deletes the concept explainer; with no animation support, the motion design explainer.
- An effort ceiling with nobody to maintain a companion repository deletes the build-along.

## Workflow

1. **Extract the promise.** One sentence: for _this viewer_, this video shows _this specific thing_ working. If the sentence needs an "and", you have two videos.
2. **Transpose the source into claims, not sections.** A written source is organized for scanning; a video is organized in time. List what the source _proves_, discard its headings, and keep only the claims the promise needs. A blog post's background section is usually the first casualty.
3. **Pick the shape.** Delete the shapes the interview's effort ceiling rules out, then take the highest survivor in the efficiency order below, re-ranked against the date and the one-off-versus-compounding answer. Say the ranking, the deletions and the pick out loud. Shape decides runtime, hook and depth before any line is written.
4. **Cut the material into segments**, one claim per segment, each under roughly 6 minutes and separately titled. Segments are the chapters (see below).
5. **Write the opening beat** against the 30-second window (see below). Write it first, not last - it is the constraint the rest of the script has to earn.
6. **Write the beats** in the two-column format (see below). Each beat: visual, on-screen action, narration, starting state, and core-or-cuttable. One thought per beat, roughly 20 seconds of narration - the one-thought take size a published screencast production standard prescribes - so a beat that cannot be recorded in one pass is two beats.
7. **Budget the runtime.** Narration word count divided by the recorder's measured speaking rate, plus explicitly estimated dead time per beat - builds, installs, page loads, deliberate pauses. Compare against the target; cut before recording, never after.
8. **Run the audio-only pass.** Read the narration column with the screen off. Every sentence that stops meaning something is a deictic sentence to rewrite (see below).
9. **Run a humanizer pass** on the narration column only (never on commands or code) with your preferred humanizer skill, so it reads like an engineer explaining rather than a model narrating.
10. **Attach the recording brief**: chapter list, per-beat starting states, what must stay off screen, the metadata the script already contains, and a publish-ready description carrying one call to action. See [./references/recording-brief.md](./references/recording-brief.md).
11. **Verify against the pass threshold** below. Iterate until it passes; the script is not shootable before that.
12. **Instrument.** Name the retention checkpoints you will read after publication (below). If your environment has persistent memory, store the promise, audience, shape and the claims deliberately left out, so the next video in the series does not contradict or duplicate this one.

## Video shapes

Runtime is what the viewer spends, not what you spend - a three-minute animated explainer and a three-minute screencast cost wildly different amounts to make, so never pick a shape by its length band. Production effort is the column that decides: recording and editing hours, the assets someone has to build first (diagrams, seeded environments, a companion repository), and the review chain the recording must clear. Rows are in efficiency order - value returned per unit of that effort.

| Shape                          | Production effort                                                                        | What it buys                                                                                                                                      | Runtime                       | Opening proves                                                               | Depth rule                                                                       |
| ------------------------------ | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Error/fix video                | an hour, if you can reproduce the error on the recording machine                         | a viewer unblocked at the exact moment they searched, for years                                                                                   | 1-3 min                       | The exact error text on screen                                               | Cause in one sentence, then the fix                                              |
| Changelog / release clip       | an hour, over a changelog entry someone already wrote                                    | existing users who find out the feature exists                                                                                                    | 30-90 s                       | The change, in the product                                                   | One change per clip                                                              |
| Short-form clip                | an hour, and usually a beat already scripted for another video                           | reach among people who were not looking for you, spent within days                                                                                | under 60 s                    | The payoff in the first second                                               | One idea, no setup, vertical framing                                             |
| Feature or product walkthrough | a week, most of it building a demo environment that survives a clean take                | an evaluator who has seen the outcome work before they install anything                                                                           | 2-5 min                       | The outcome, already working                                                 | One path only; no options, no settings tour                                      |
| Motion design explainer        | a week, most of it illustration and animation assets, plus licensing a music track       | an ICP viewer who recognizes their own pain in the opening line, and keeps watching because nothing on screen requires reading code or a terminal | 2-5 min                       | The problem, as the viewer's own pain: a metric, a symptom, a recurring cost | One claim resolved per segment; motion signals cause and effect, never decorates |
| Concept explainer              | a week, and it is diagram work before it is recording work                               | the mental model that makes every other video land                                                                                                | 3-8 min                       | The question, phrased as the viewer would ask it                             | Diagram-led; code only where it settles the argument                             |
| Build-along tutorial           | a week to script and shoot, then a standing job keeping the companion repository working | a viewer who has built the thing - the strongest adoption evidence on this list                                                                   | 6-15 min, split into segments | The finished thing running                                                   | One new concept per segment                                                      |
| Deep dive / architecture       | a quarter: evidence per claim, diagrams, and the longest edit here                       | durable technical credibility, peer citation and inbound engineers                                                                                | 10-25 min, chaptered          | The surprising claim or the number                                           | Evidence per claim; no live typing                                               |

- efficiency: error/fix > changelog clip > short-form clip > feature walkthrough > motion design explainer > concept explainer > build-along > deep dive
- value: build-along > deep dive > concept explainer > motion design explainer > feature walkthrough > error/fix > changelog clip > short-form clip
- effort: deep dive > build-along > concept explainer == feature walkthrough == motion design explainer > error/fix == changelog clip == short-form clip
- compliance cost: feature walkthrough > changelog clip > deep dive > error/fix == build-along == concept explainer == motion design explainer == short-form clip

Two effort ties, and why:

- The concept explainer, the feature walkthrough and the motion design explainer tie because their cost is the same shape: an asset someone else has to finish - a diagram set, a seeded demo environment, or an illustration and animation set - before a single take is possible.
- The three `an hour` shapes tie because each is one take over material that already exists, and none needs a second person.

On compliance the last five tie at nothing: no unreleased product, no internal architecture, no real product screens or pricing (the motion design explainer shows illustrations, not the product), and any of them can be re-recorded and replaced without anyone's sign-off. Two exceptions inherit the walkthrough's obligations: a short-form clip cut from a walkthrough, and a motion design explainer that illustrates real product screens.

Above them, compliance cost rises for a different reason each:

- A walkthrough puts the product, its screens and often its pricing on a recording that gets forwarded into procurement.
- A release clip is embargoed until the release actually ships.
- A deep dive exposes internal architecture that a security reviewer has to see first.

Delete the shapes the constraints rule out rather than ranking them low, and say which you deleted:

- No diagram support means the concept explainer is not on the menu, not last on it. No animation support removes the motion design explainer the same way.
- Nobody to keep the companion repository green means no build-along - a tutorial whose repo rots is worse than no tutorial.
- No environment that survives a clean take means no walkthrough.

The efficiency order starves the build-along tutorial and the deep dive: both sit at the top of value and the top of effort, so a ratio defeats them every round, and a channel that only computes efficiency ends up as a wall of two-minute clips with nothing behind it. Promote anyway when:

- **Build-along** - evaluators in this product have to build something before they can decide, and the interview returned a compounding mandate.
- **Deep dive** - technical credibility or hiring is the actual goal, there is no near date, and the effort ceiling genuinely allows a quarter.

The order is a default, not a law: it shifts with context and with who records. Re-rank it against what you already know:

- An existing demo environment or a maintained example repository collapses the top two `a week` rows toward an hour.
- A recorder who is already fast at motion graphics moves the concept explainer up, and the motion design explainer further: the concept explainer still works as plain diagrams, while the motion design explainer needs animation capability, not just diagram literacy.
- A team with a video editor on staff cuts the deep dive's edit cost, which is most of its effort.

The effort, value, opening and depth columns reflect video-production craft experience; a user may adjust any cell to their context.

**Short-form and long-form reach viewers on different clocks.** The feed pushes a short-form clip to non-subscribers fast, so its reach spikes and is spent within days. The dominant video platform shows a long-form video to subscribers first, and widens it to non-subscribers only as watch time accumulates: that slow ramp is why it compounds.

The length evidence behind the runtime bands: median engagement time is at most six minutes regardless of total video length, and the median viewer gets less than halfway through videos longer than nine minutes (Guo et al.). Wistia's 2026 report on 13M+ hosted videos points the same way - under-a-minute videos average a 52% engagement rate - though that is a business-video corpus, not a teaching one. Length past six minutes is a decision with a known cost; take it only with chapters and a reason.

**Procedural video is used differently from conceptual video**, and this changes the script more than runtime does. In the same study, tutorials were watched 2-3 minutes on average _regardless of length_, re-watched more than lectures, and paused selectively at what look like step boundaries.

- A walkthrough, build-along or error/fix video is reference material: titled segments, per-beat starting states and a copy-pasteable companion artefact are its core, not its polish.
- A concept explainer, motion design explainer or deep dive is closer to a lecture - there, optimise the uninterrupted first viewing.

## The opening beat

The dominant video platform's retention report scores the intro as the share of viewers still watching after the first 30 seconds - a measurement boundary the platform defines, so treat it as the budget. Four jobs, all inside it:

1. Name the problem in the viewer's own words - the error, the symptom, the task they searched for. A motion design explainer has no terminal to show an error in, so name the metric or recurring pain the way the viewer would say it to a teammate: "my 500 error rate is too high".
2. Show the result running. Not a promise of it, the thing itself. In a motion design explainer, show the resolved state: the metric back where the viewer wants it.
3. State the prerequisites, so the wrong viewer leaves in second 20 instead of dropping at minute 4.
4. State the runtime, because the viewer is already hunting for it.

Ceremony gets about five seconds before it reads as filler - a perception threshold NN/g measured, not a hard cutoff: intro animation, channel branding, "hey everyone, welcome back". Setup, installs and credentials never belong here - they belong after the payoff, or in the companion repository.

A short-form clip for a vertical surface (YouTube Shorts, TikTok, Instagram Reels) does not get this window at all: the clip itself runs under 60 seconds, and the platform decides whether to keep playing within the first second or two, not the first 30. Open on the payoff or the punchline directly - there is no ceremony budget to spend, and no setup beat to defer.

## Beat format

One row per beat. Keep the columns separate - they are the viewer's two channels, and reading the table column-wise is the cheapest review pass there is.

| Field            | Contents                                                                                        |
| ---------------- | ----------------------------------------------------------------------------------------------- |
| Visual           | What fills the frame: editor, terminal, browser, diagram, face                                  |
| On-screen action | What changes: file opened, command run, line highlighted, zoom in                               |
| Narration        | The spoken words, written to be read aloud                                                      |
| Starting state   | Branch/tag, seeded data, open files, cleared terminal - what makes this beat re-shootable alone |
| Est. seconds     | Narration time plus expected dead time                                                          |
| Core / cuttable  | Decided now, so the cut list is not an argument later                                           |

A motion design beat keeps the same columns: Visual names the illustration or scene, On-screen action names the animation (enter, morph, highlight, transition), and Starting state names the asset that must exist before the beat can be storyboarded, not a machine state. Flag in On-screen action every beat that carries a music cue or a transition, since the soundtrack is cut to those flags. Keep on-screen text to a label or a short phrase, never a paragraph, and never narrate it verbatim - the narration comments on it, since a viewer cannot read and listen to the same words at once. Animate state changing into state, not text fading in over a static frame: a slide with a wipe is not motion design.

A short-form clip adds three constraints the table does not otherwise carry. Frame vertical (9:16), and keep the subject and any on-screen text out of the top and bottom bands the platform's own UI reserves for captions, buttons and the username - note the safe zone in the Visual column. Burn captions into the frame rather than relying on auto-captions, since most short-form viewing starts sound-off. End on a beat that reads naturally if it loops back to beat 1, or on the payoff itself - never on a fade or a call-to-action card, which makes a replay feel redundant instead of rewarded.

Full template, including the chapter list and cut plan: [./references/script-template.md](./references/script-template.md).

## Code on screen

The script controls pacing, not the editor. Write these decisions into the beats:

- **Narrate before, not during.** Say what the block does, then show it and let the viewer read. Narration competing with reading loses both channels.
- **Hold the frame after a result.** Silence long enough to read the output is a scripted beat, not an accident. Filling it with commentary is the most common pacing defect in developer video.
- **Never type what isn't the lesson.** Imports, boilerplate, config, long strings, repeated scaffolding: pre-supplied, pasted or snippet-expanded. Type only the lines the video is about, slowly.
- **Show the diff, not two files.** Signal the one line carrying the claim - zoom, highlight, or dim the rest - and say which line it is.
- **Smallest fragment that carries the point.** A full file on screen highlights nothing.
- **Weed the frame.** Notifications off, unrelated tabs closed, no file tree nobody opens, no inbox badge, no personal bookmarks. Every removal returns attention to the code, and removes an accidental-disclosure risk.
- **Legibility floors:** terminal text 24pt or larger, editor text 20pt or larger, high-contrast theme verified on a phone-sized playback rather than the authoring monitor. Those two point sizes are this skill's baseline; published screencast standards say "large fonts" without numbers. Never carry meaning by color alone.

Work the signaling hard, because the format starts behind. Code screencasts sat in the _weaker_ bucket of the one large study of instructional formats: continuous tablet-drawing tutorials held 1.5-2x their normalized engagement, and the paper's advice when code must be on screen is to draw on top of it.

So the compensating levers are motion, annotation, zoom, and a face cut in at deliberate moments - interspersing the presenter beat slides alone, while studio production values changed nothing. Each lever is a line in the visual column, not an editing afterthought.

## Segments, chapters and metadata

Segment boundaries decided while scripting _are_ the chapters, so write each chapter title next to its segment and let timecodes fill in after the edit.

- Title chapters as tasks or outcomes in the viewer's search vocabulary - "Fix the CORS error", not "Part 2".
- The dominant video platform documents four chapter requirements: first timestamp `00:00`, at least three timestamps, each chapter 10 seconds or longer, listed in ascending order. Docs-site players usually take the same list as caption cues, so one chapter list serves both. If you can browse the web, re-check the current rules before shipping; if you cannot, keep to these and say they were not re-verified.
- A video with no natural chapter boundaries is usually two videos.

One script also feeds the description, the caption correction pass, the companion written page, and any short-form clip cut from a single beat - mark clip-able beats while writing. See [./references/recording-brief.md](./references/recording-brief.md).

## Narration language

Write for the ear and for the viewer who cannot see the screen.

**Ban deictic narration.** "As you can see here", "click that", "change this to that" carry zero information without the picture - and they are also what makes an auto-generated caption track unusable.

| Deictic                        | Integrated                                              |
| ------------------------------ | ------------------------------------------------------- |
| "Now I'll change this to that" | "I'm changing the `timeout` field from 30 to 5 seconds" |
| "Click here, then here"        | "Open Settings, then the Webhooks tab"                  |
| "As you can see, it fails"     | "The request returns a 403 with `invalid_signature`"    |

This is the W3C's integrated-description approach: write the visual information into the main narration, then verify the audio alone still teaches the thing. Doing it at script time is far cheaper than bolting a separate description track onto a finished recording, and it is what makes the video usable as a listen, a transcript and a translation.

Also:

- Short declarative sentences. Subordinate clauses survive on the page and die in the ear.
- Contractions, second person, the words a developer would use at a whiteboard.
- Fix pronunciation in the script the first time an identifier appears (`char`, `kubectl`, `SQLite`), so the recording does not stall on it.
- For an AI-synthesized voiceover, the narration column is the final audio verbatim - there is no take to catch a misread line. Run the audio-only pass against the literal text the synthesis engine will read, and mark every pause or emphasis the default reading would place wrong, since a human recorder would otherwise fix both by ear.
- Do not pad for comprehension. Across a 48-254 wpm corpus, engagement rose with speaking rate - up to 2x within a length band - but the authors are explicit that rate is a surface proxy for enthusiasm, not a lever: bring energy; do not force speed. Budget runtime from the recorder's own measured rate, never a table value.
- Verbatim script or bullet outline is the recorder's choice. Either way, mark the sentences that must be said exactly: claims, version numbers, terminology, the call to action.
- Write the narration so it stands alone. Recorders capture audio-first, video-first or both at once, and a sentence that only makes sense over a specific frame breaks two of those three orders.

## Reviewing a script you did not write

When the user brings an existing script or a video that underperforms, diagnose instead of rewriting. A viewer leaves for one of three reasons, and each is checkable line by line:

1. **A logic break** - the beat ends on A, the next opens on C, and the bridging sentence was never said.
2. **A density drop** - the beat repeats what the screen already showed, or circles a point that needed one sentence.
3. **An unspeakable line** - too long, too written, or too tangled to read aloud in one breath.

Work this three-cause model in order: table the beats (number, topic, function, status), then grade each finding as high risk (the viewer probably leaves here), medium (attention drifts) or low (better if changed). Prefer missing a small suggestion to burying a high-risk one.

Three rules keep the review honest:

- Ask the format first - a talking-head explainer and a silent-captioned clip are judged differently, and the answer changes half the findings.
- Keep the author's text: show the original line next to the proposed replacement rather than overwriting, so a rejected suggestion is still traceable next round.
- Do not manufacture findings - if the script flows, say so in three lines.

Before cutting a beat as a tangent, check whether the viewer could infer the missing meaning at the next key moment. If they could not, it is load-bearing argument, not padding. Judge how it is said, never what is claimed: the author's argument, examples and numbers are theirs.

Output shape: [./references/worked-examples.md](./references/worked-examples.md), section 9.

## Invocation examples

| The user says                                                           | You do                                                                                                                                          |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| "Turn this blog post into a 3-minute demo video"                        | Interview (source, viewer, runtime), transpose claims, then a beat sheet + chapter list + cut plan + recording brief                            |
| "Script a 90-second clip for this changelog entry"                      | One change, one claim, one segment; no chapter list (under the platform's three-chapter minimum), description and clip metadata instead         |
| "Why do people drop off at 1:40 in this video?"                         | Ask for the retention curve and the script, map the dip to its beat, return graded findings - not a rewrite                                     |
| "Here's my screencast script, is it shootable?"                         | Run the pass threshold and the review above; report per-criterion pass/fail with the beats that fail                                            |
| "We need a video for the launch"                                        | Refuse to guess: the promise, the viewer and the source come first, then the shape decides runtime                                              |
| "Storyboard a 3-minute animated explainer, we have nothing written yet" | Topic round (3-5 problem-first candidates, ranked), then motion design beats with music cues flagged, and a description with one call to action |

Expected deliverable, unless the user asks for less:

```markdown
## Promise

One sentence: for <viewer>, this video shows <thing> working.

## Beats

| # | Visual | On-screen action | Narration | Starting state | Est. s | Core/cut |

## Chapters

00:00 <task-shaped title> · <next> · <next>

## Cut plan

Beats marked cuttable, in the order they go if the runtime overruns.

## Recording brief

Starting states, machine hygiene, what must stay off screen, caption pack, description with one call to action.

## Runtime

Narration words ÷ measured rate + per-beat dead time = estimate vs target.
```

## Audience context

The beats are the same; three things shift with who arrives and how the video travels.

**Individual adoption / self-serve (PLG B2B hybrid).** The viewer is a developer evaluating self-serve AND a manager arriving via that developer's share - a single video serves both. Keep the whole path inside the free tier, never reveal a paywall mid-demo, and put the companion repository link in a beat early enough to be captured. Also apply the three sales-led rules below.

**Sales-led B2B, enterprise or buyer-adjacent.** A second audience is watching who will not type any of it, and a screen recording is a durable, forwardable document.

- Redact or seed every screen showing customer names, tenant IDs, internal hostnames and pricing.
- State versions and limitations aloud, since an over-claim in a video outlives the release it described.
- Expect the video to be replayed in a procurement or security review where "it depends" is not visible.

**B2C / individual-facing.** Same as individual adoption / self-serve above - the viewer owes you nothing and can leave at any second.

## Pass threshold

Iterate until all seven gates hold:

1. The promise is one sentence, and the opening beat delivers it inside 30 seconds.
2. Every beat has a starting state precise enough to re-shoot that beat alone.
3. The audio-only read still teaches the thing - zero deictic sentences remain.
4. The runtime estimate includes per-beat dead time and lands inside the target.
5. Every segment has a chapter title, and every chapter clears the platform's minimum length.
6. Every beat is marked core or cuttable, and cutting all cuttable beats still delivers the promise.
7. Every factual claim on screen or in narration is one the recorder can reproduce on the recording machine.

Criterion 6 is the one people skip. A script with no cut list becomes a 14-minute video because nobody could decide what to lose at edit time.

## KPIs

Compare each metric against your own previous videos of the same shape, never against an invented benchmark. What each metric is for:

- Intro retention: percentage still watching after 30 seconds. This grades the opening beat and nothing else.
- Dip locations mapped back to specific beats - the curve says where, the script says what to rewrite.
- Average percentage viewed, compared within a shape; a deep dive watched like a changelog clip was mis-shaped, not mis-titled.
- Chapter usage: which chapters get jumped to directly. Heavy direct entry means the video is being used as reference and should be split.
- Companion-link clicks, and the action they lead to (repository clone, docs page, signup).
- Takes per beat during recording - a beat that needs six takes is a script defect, usually an unrealistic starting state.

Treat spikes with suspicion: a rewatched segment can mean "that was great" or "I had to watch it three times". Check the comments before optimizing for it.

## Failure modes

| Symptom                                                   | Fix                                                                                                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| First 30 seconds are setup and greetings                  | Move the working result to beat 1; setup goes after the payoff or into the repo                                                              |
| Viewers drop at the same minute every time                | Read that beat aloud; it is usually two concepts in one beat or unexplained typing                                                           |
| Runtime doubled during recording                          | Dead time was never budgeted; add per-beat estimates for builds, installs and pauses                                                         |
| Narration restates the on-screen text                     | Rewrite one channel - the screen shows, the narration explains why                                                                           |
| The script cannot be re-shot from the middle              | Add starting states; no beat may depend on a previous beat's live output                                                                     |
| Captions are unintelligible on technical terms            | Correct the auto-captions against the narration column, don't re-transcribe                                                                  |
| Someone has to decide cuts in the edit                    | The cut list belongs in the script, decided before recording                                                                                 |
| Code unreadable on a phone                                | Raise font sizes, zoom the fragment, show diffs instead of files                                                                             |
| A customer name appeared on screen in take 3              | Machine hygiene and seeded data belong in the recording brief, per beat                                                                      |
| The video is a feature tour                               | Return to the promise; delete every beat that does not prove it                                                                              |
| A walkthrough written to be watched once, start to finish | Segment it, title the segments, give each a starting state - procedural video is entered in the middle and re-watched (see worked example 7) |

## References

- [./references/script-template.md](./references/script-template.md) - beat table, chapter list, cut plan and metadata block
- [./references/worked-examples.md](./references/worked-examples.md) - before/after openings, beat rewrites, narration pairs, two negative examples and review output shape
- [./references/recording-brief.md](./references/recording-brief.md) - handoff for the recorder: starting states, machine hygiene, music licensing, AI voiceover selection, take plan, captions, description with CTA
- [./references/published-findings.md](./references/published-findings.md) - source for every figure, stated limitations, and thresholds
- samber/developer-relations-skills@developer-live-demo-design when the demo is performed live rather than recorded
- samber/developer-relations-skills@developer-tutorial when the artefact is a written teaching tutorial instead
- samber/developer-relations-skills@developer-quickstart-guide for the first-success path a walkthrough video usually mirrors
- samber/developer-relations-skills@changelog-writing for the release notes a changelog clip is cut from
- samber/developer-relations-skills@engineering-blog-post for the companion written piece
- samber/developer-relations-skills@tech-podcast-interview-prep when appearing as a guest on someone else's show
