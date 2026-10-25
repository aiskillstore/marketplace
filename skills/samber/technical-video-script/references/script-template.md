# Script template

Copy this structure. Delete any block the video genuinely does not need - an empty heading is worse than a missing one.

## Header

```
Title (working):
Promise:            For <viewer>, this video shows <specific thing> working.
Shape:              feature walkthrough | error fix | build-along | explainer | changelog clip | deep dive | short
Audience:           evaluator | user with this error | existing user | buyer-adjacent
Surface:            video platform | docs embed | release post | social feed | internal library
Target runtime:     mm:ss        Estimated runtime: mm:ss
Recorder:           who shoots it, on which machine
Speaking rate:      measured wpm (time a 200-word read once; do not guess)
Companion:          repo / branch / gist / docs page
Off-limits:         what must never appear on screen
```

## Beat table

One row per beat. A segment is a run of beats proving one claim; mark segment boundaries with a divider row.

| #   | Visual                              | On-screen action         | Narration                                                                                                            | Starting state                                     | Est. s | Core/cut |
| --- | ----------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------ | -------- |
| 1   | Terminal, split with browser        | Run `demo up`, app loads | "Ninety seconds from now this API will reject an unsigned webhook and log why. You need Node 20 and a free account." | `main` @ tag `v2.3.0`, seeded DB, terminal cleared | 22     | core     |
| 2   | Editor, `handler.ts`                | Highlight lines 14-18    | "The handler trusts every request body. That's the bug."                                                             | same tree, file open at line 12                    | 15     | core     |
| -   | **Segment 2: verify the signature** |                          |                                                                                                                      |                                                    |        |          |

Rules the table enforces:

- **No beat depends on a previous beat's live output.** Each starting state is enterable on its own, so any beat can be re-shot without re-shooting the video.
- **Est. s includes dead time**: builds, installs, page loads, and the deliberate pause after a result appears. Estimate it per beat rather than discovering it in the edit.
- **Core/cut is decided while writing.** Cutting every `cut` row must still deliver the promise.

## Chapter list

Written from the segments, timecodes filled after the edit. First entry is always `00:00`, at least three entries, each chapter 10 seconds or longer, ascending.

```
00:00 The unsigned webhook problem
00:34 Where the handler trusts the body
02:10 Verify the signature
04:05 Replay an attack and watch it fail
05:12 What to change in your own service
```

Titles are tasks or outcomes in search vocabulary - "Verify the signature", not "Implementation".

## Cut plan

```
If long by ~1 min:   drop beats 7, 12 (second example of the same pattern)
If long by ~3 min:   drop segment 4 entirely (nice-to-have, not part of the promise)
Never cut:           beats 1-3 (opening), 9 (the claim), 15 (call to action)
```

## Metadata block

Everything below already exists in the script; collecting it here saves the publishing step from re-reading the whole document.

```
Description opening (2 sentences): the problem statement from beat 1, plus the promise.
Prerequisites line:                verbatim from the opening beat.
Links named in beats:              repo, docs page, related video, issue.
Clip-able beats:                   beat numbers that stand alone as short-form.
Caption correction list:           identifiers, flags and package names auto-captioning will mangle.
Claims to re-verify before publish: version numbers, benchmark figures, pricing statements.
```

## Narration column conventions

- Write spoken words only. Stage directions live in the visual and action columns.
- Mark exact-wording sentences with `[verbatim]` - claims, versions, terminology, the call to action.
- Write identifiers as they should be _said_ on first use: "kubectl - kube control".
- Keep sentences short enough to say in one breath.
- Never write a sentence whose meaning depends on punctuation the listener cannot hear.
