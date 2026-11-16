---
name: reword
description: Learn the author's writing voice and make agent writing sound like them. Build and evolve a saved voice profile from chosen writing samples, relevant copy, author revisions and explicit preferences. Use for learning my voice, writing in my style, personalized drafting, humanizing, rewriting, voice matching, destination-aware style and prose review.
---

# Reword

Run bundled commands from the directory containing this file. Use Python 3.10+;
the scripts use only the standard library and make no model or network calls.
The host agent's model performs writing and semantic voice distillation. Follow
[installation](INSTALL.md) for supported host setup.

For “Build my voice” or continuing voice learning, read [voice collections](references/voice-collection.md).
Offer [the invitation](assets/voice_onboarding.txt) once. Use only deliberately
supplied material; distinguish authored samples from reference inspiration.
Create a chosen private collection outside the skill and public project folders.
Establish ongoing consent once before automatically saving later corrections.

Select a collection with `--voice STORE`, or a legacy `--profile FILE`.
An explicitly configured `REWORD_VOICE` selects a default; `--no-voice` bypasses it.
For original drafting, export the selected voice card and apply it to the current
brief's facts. Style samples never supply biography, experiences or other claims.

For editing, use [voice_kernel.txt](assets/voice_kernel.txt) with author guidance,
otherwise [editorial_kernel.txt](assets/editorial_kernel.txt). Fit the destination
and current explicit preferences. Use one writing pass and one bounded source
comparison; avoid repeated polishing loops. Return finished copy by default.

`python3 scripts/reword.py prompt FILE --destination DESTINATION` assembles the
method, compact voice, destination card and sparse examples. Send `instructions`
as host instructions and `input` as data; `meta` is bookkeeping. Keep the default
4,000-character guidance cap. Required preferences must fit or fail visibly;
never silently discard them. Normal edits never load the saved corpus.

Preserve the original. Run `python3 scripts/reword.py check ORIGINAL CANDIDATE
--destination DESTINATION` with the same voice and overrides before replacement.
Resolve blocking differences and assess review warnings. These heuristic checks
do not establish truth or complete semantic equivalence.

With ongoing consent, save actual author corrections and explicit preferences;
refresh eligible evidence in bounded batches. Acceptance alone does not make
model prose authored evidence. Offer inspection, export, pause, forget and
rollback controls when requested.

Load [commands](references/cli.md), [destination context](references/context.md),
[legacy profiles](references/voice.md), [guidance budgets](references/budget.md),
or [the editorial method](references/editorial.md) only when needed. For the
public author pilot, follow [try Reword in your own agent](references/pilot.md).
