# Voice profiles

For sample intake, ongoing learning, destination voices, history and portable cards, use [voice collections](voice-collection.md). This page documents the legacy compact profile format and its standalone commands. Collection compilation produces this format without its source corpus.

Use only samples or preferences the writer deliberately supplies. Distill a few actionable observations: word choice, sentence rhythm, openings, transitions, punctuation, emotional register, and distinctive devices. Distinguish repeated habits from one-off choices. Keep the profile small; do not reproduce the entire corpus.

Store a profile only when the writer explicitly asks to create one or save feedback. That request is sufficient authorization. Never learn silently from a rejected edit. Keep project profiles separate; never infer one person's style from another person's messages.

Use the JSON shape in `assets/voice.example.json`. `preferences` and `avoid` are explicit guidance; `traits` records up to six distilled observations, each at most 120 characters. `contexts` stores destination conventions; see [context](context.md). `preserve` locks exact phrases when they occur in the source. Optional `samples` allows two excerpts of at most 500 characters each. Sample facts never enter the edited text. The CLI rejects unknown fields. Profile writes use private file permissions and only the explicitly supplied path. Standalone commands make no model calls and have no background learning; the opt-in collection workflow uses the host model for bounded refinement.

```bash
python3 scripts/reword.py voice init /path/to/my-voice.json --name 'My voice'
python3 scripts/reword.py voice learn /path/to/my-voice.json --prefer 'Put the request early' --avoid 'Generic praise'
python3 scripts/reword.py voice context /path/to/my-voice.json --destination text-message --case lowercase --punctuation light
python3 scripts/reword.py voice distill samples.md --name 'My voice' --destination essay
python3 scripts/reword.py voice apply /path/to/my-voice.json accepted-proposal.json
```

`voice distill` builds a one-time model request; it neither calls a model nor saves a profile. Its samples are data and may contain up to 6,000 characters. Ask the host model for supported style traits, preferences, and avoid entries. Review that proposal, then use `voice apply` to save it. A proposal cannot replace locks or contexts. Once traits exist, normal edits omit raw samples and send a compact author card. Without traits, supplied samples remain separate style-only input so the model can observe semantic habits.

Repeated feedback is deduplicated. A new explicit preference replaces an identical item in the opposing list. Conflicting preferences in one command are rejected. Stored profiles allow 6,000 characters; only the selected context enters an edit. The smaller request budget includes the complete author card. Required preferences are retained or the request fails visibly; distill them rather than accumulating history. `prompt`, `style`, `focus`, and `check` never change profiles.

For example, a sample saying the writer spent six hours fixing a service can teach vocabulary and cadence. It cannot supply the duration of a different incident. A signature dash, image, or long sentence can remain when it fits the draft. Do not convert observations into arbitrary quotas.
