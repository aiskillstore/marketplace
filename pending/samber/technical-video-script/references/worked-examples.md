# Worked examples

Each pair shows a common draft and the rewrite, with the reason the rewrite wins.

## Table of Contents

- [1. The opening beat](#1-the-opening-beat)
- [2. Deictic narration](#2-deictic-narration)
- [3. Pacing around code](#3-pacing-around-code)
- [4. The pause after a result](#4-the-pause-after-a-result)
- [5. Transposing a written source](#5-transposing-a-written-source)
- [6. Chapter titles](#6-chapter-titles)
- [7. Negative example: a walkthrough written to be watched once](#7-negative-example-a-walkthrough-written-to-be-watched-once)
- [8. Negative example: inventing what the user never said](#8-negative-example-inventing-what-the-user-never-said)
- [9. Reviewing a script you did not write - output shape](#9-reviewing-a-script-you-did-not-write-output-shape)
- [Script review: "Verify webhook signatures" (7 beats, est. 4:10)](#script-review-verify-webhook-signatures-7-beats-est-410)

## 1. The opening beat

**Weak (0:00-0:48)**

> [Logo animation, 6s] "Hey everyone, welcome back to the channel. Today we're going to be looking at webhooks. Webhooks are a really important part of modern APIs, and there's a lot to cover, so let's jump into the terminal and get our environment set up. First I'll create a new directory…"

Four failures:

- Six seconds of ceremony.
- No problem named.
- No result shown.
- Setup inside the window the platform measures.

**Rewrite (0:00-0:26)**

> [Screen: terminal on the left, browser on the right. A `curl` fires a forged webhook; the API returns `403 invalid_signature` and the log line appears.]
>
> "That's a forged webhook getting rejected. Most webhook handlers I read trust the request body completely - this one used to. In the next four minutes we'll verify signatures on an Express handler, then replay an attack against it. You need Node 20 and a free test account; the finished code is linked below."

- Problem in the viewer's words.
- Result already running.
- Prerequisites.
- Runtime.

The environment setup that used to be here is now a pre-supplied repository.

## 2. Deictic narration

| Draft                                                     | Rewrite                                                                             | Why                                                                           |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| "Now I'll just change this to that and we should be good" | "I'm setting `maxRetries` to 3 so the client stops after three attempts"            | The draft is meaningless in audio, in the transcript and in the caption track |
| "Click here, then over here"                              | "Open Settings, then the Webhooks tab"                                              | Names survive a UI redesign; positions don't                                  |
| "And as you can see it works now"                         | "The same forged request now returns 403 with `invalid_signature`"                  | States the evidence instead of asserting the conclusion                       |
| "This function does a bunch of stuff"                     | "`verify()` recomputes the HMAC over the raw body and compares it in constant time" | The one sentence the viewer came for                                          |

## 3. Pacing around code

**Draft beat**

> [Types 24 lines of imports and Express boilerplate while talking through unrelated background about HMAC history.]

**Rewrite, split into three beats**

| #   | Visual                              | Action                                         | Narration                                                                                                  |
| --- | ----------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 4   | Editor, `handler.ts` open at line 1 | Boilerplate already present, scroll to line 30 | "The server setup is in the starter repo - nothing here is specific to signatures."                        |
| 5   | Same file                           | Highlight the empty `verify()` body            | "`verify()` needs to do three things: read the raw body, recompute the HMAC, compare it in constant time." |
| 6   | Same file                           | Paste the three-line implementation, zoom in   | "Raw body, HMAC, `timingSafeEqual`. That's the whole fix."                                                 |

Narration precedes each reveal, boilerplate is never typed, and the zoom signals the lines that matter.

## 4. The pause after a result

**Draft**

> [Runs the test suite.] "So we run the tests and - while that's going, I wanted to mention that there's also a plugin approach which some people prefer, and actually in version 3 they changed how…"

**Rewrite**

> [Runs the test suite. Silence.] [Suite finishes: 12 passing, 1 failing, failure highlighted.] "One failure - the replay test. That's the next segment."

Two seconds of silence are how the viewer reads the output. The plugin tangent is a `cut` beat or a separate video.

## 5. Transposing a written source

Source: a 1,800-word blog post, "How we cut cold start from 4s to 300ms".

**Wrong transposition** - one beat per heading: Background, Our architecture, Profiling methodology, Attempt 1, Attempt 2, The fix, Results, Conclusion. This produces a 14-minute video whose first three minutes prove nothing.

**Right transposition** - list what the post _proves_, keep what the promise needs:

| Claim                                               | Beat?                                                  |
| --------------------------------------------------- | ------------------------------------------------------ |
| Cold start was 4s, measured                         | Yes - beat 1, the number on screen                     |
| The profiler pointed at module loading              | Yes - the flamegraph, 20s                              |
| Two earlier attempts failed                         | One sentence, no beats - it is a paragraph, not a demo |
| Lazy-loading the SDK cut it to 300ms                | Yes - the diff, then the measurement                   |
| The trade-off: first request after deploy is slower | Yes - this is the credibility beat, never cut it       |
| Company background, team size, framework history    | No                                                     |

Result: a 3-minute video where the number appears twice - once as the problem, once as the proof.

## 6. Chapter titles

| Weak               | Strong                                      |
| ------------------ | ------------------------------------------- |
| `01:12 Setup`      | `01:12 Install the CLI and authenticate`    |
| `04:30 Part 2`     | `04:30 Verify the signature`                |
| `07:45 Misc`       | `07:45 What breaks when the secret rotates` |
| `09:02 Conclusion` | `09:02 Apply this to your own handler`      |

A chapter list is read alone, by someone who has already watched the video once and came back for one thing.

## 7. Negative example: a walkthrough written to be watched once

This is the most common defect in a technical script, and it survives review because nothing in it looks wrong.

**The script** - an 11-minute "Deploy your first service" walkthrough, written as one continuous piece:

- A spoken agenda at 0:20.
- Background on the platform's architecture until 2:10.
- Eight steps that each start with "so now that we've done that…".
- No segment titles.
- No on-screen state anywhere.
- A closing recap.

Why it fails: procedural video is not watched the way this script assumes. Guo et al. measured tutorials being watched 2-3 minutes on average _regardless of length_, re-watched more often than lectures, and paused selectively at step boundaries.

This script is optimised for a linear first viewing that mostly does not happen, and it is unusable for the viewing that does:

- A returning viewer cannot find step 6.
- They cannot tell what state step 6 starts from.
- They hit "so now that we've done that" with no idea what "that" was.

**The fix, without rewriting the content:**

- Cut it into eight titled segments in the viewer's search vocabulary.
- Give each one a starting state so it stands alone.
- Replace every back-referencing transition with a state sentence ("The service is deployed and returning 502 - now we fix the health check").
- Move the architecture background to a linked post and keep the one sentence the deploy actually needs.

Notice which lever did the work. The material did not change and the runtime barely moved. What changed is that the video became addressable.

## 8. Negative example: inventing what the user never said

**Interview answer:** "It's for the docs site, probably a few minutes, our users are mostly backend engineers."

**Script that must not be written:** an opening beat asserting "you're losing hours a week to flaky local environments", a claimed 40% setup-time reduction, a persona named "Platform Engineer Priya", and a call to action pointing at a pricing page.

Every one of those is invented. A script is shot, published and quoted; a fabricated pain, number or CTA becomes a public claim nobody at the company made.

Write what the source and the interview support, and where the promise genuinely needs a fact the user has not given, name the gap in the script: `[unconfirmed - need the measured setup time before this beat can claim one]`. Ask for it, or cut the claim.

## 9. Reviewing a script you did not write - output shape

```markdown
## Script review: "Verify webhook signatures" (7 beats, est. 4:10)

| #   | Beat                    | Function   | Status      |
| --- | ----------------------- | ---------- | ----------- |
| 1   | Forged webhook rejected | Opening    | ok          |
| 2   | Why signatures exist    | Background | medium risk |
| 3   | Reading the raw body    | Argument   | ok          |
| 4   | HMAC recompute          | Argument   | high risk   |
| ... |

### High risk - beat 4 → 5, missing bridge

> Beat 4 ends: "…and that's the HMAC."
> Beat 5 opens: "So the replay attack fails."

The viewer is not told that the comparison happens in constant time, which is the
only reason the replay fails. Add one sentence at the end of beat 4.

### Medium risk - beat 2, density drop

Three sentences restating what beat 1 already showed on screen. Cut to one, or mark
the beat cuttable.

### Verdict

Two changes needed before recording; the rest is shootable. Want the marked-up script?
```

Two rules make this review usable:

- Keep the author's text - show the original line and the proposed replacement side by side rather than silently overwriting, so a rejected suggestion can be traced next round.
- Do not manufacture findings: if the script is clean, the report is three lines saying so.
