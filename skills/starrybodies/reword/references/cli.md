# Local commands

Run Reword here with Python 3.10+. Standard library only; no model calls, network, telemetry, or API keys. `reword.py` is the primary entry point; `editor.py` and `unformula.py` remain compatible.

For “Build my voice,” chosen writing samples, and opt-in ongoing learning, start with [voice collections](voice-collection.md). A collection is selected with `--voice STORE` or the explicitly configured `REWORD_VOICE`; `--no-voice` skips it for one request. `--profile` still accepts a standalone compact profile. Personalized prompts use the smaller voice-first method and include only the selected compact guidance, never the saved corpus. Semantic learning uses the host model through an explicit bounded learning request, not a hidden local model call.

```bash
python3 scripts/reword.py prompt draft.md --destination linkedin --profile /path/to/voice.json
python3 scripts/reword.py prompt draft.md --destination text-message --case lowercase --punctuation light
python3 scripts/reword.py style --destination text-message --profile /path/to/voice.json
python3 scripts/reword.py focus draft.md --destination email
python3 scripts/reword.py lint draft.md
python3 scripts/reword.py check original.md edited.md --destination cover-letter --lock 'Starry Bodies'
python3 scripts/reword.py diff original.md edited.md
```

`prompt` builds a provider-neutral request; it does not rewrite prose itself. Send `instructions` as the host's instruction message and `input` as data. `meta` reports destination resolution and budgets. A direct invocation uses the host model and reads the shared editorial method instead.

Destinations: `text-message`, `chat`, `email`, `linkedin`, `cover-letter`, `essay`, `web-copy`, `general`, or conservative `auto`. Use `style` to inspect settings. See [context](context.md) for casing, punctuation, spelling, regional spelling, abbreviations, contractions, and preference precedence. Each has a per-call override. Destination conventions never authorize changing protected quotations, names, code, or factual claims.

Modes: `light`, `rewrite` (default), `deep`. Genres: `general`, `professional`, `creative`, `technical`. Mode controls editorial scope; destination controls conventions. Optional `--audience` and `--purpose` allow 240 characters each; `--context` allows 1,000. `--max-words` must be positive.

The default guidance cap is 4,000 characters across instructions and all non-source fields, including samples and task context. At most two relevant examples share a 900-character selection budget; whole examples are omitted first when they do not fit. Required preferences are never silently discarded: distill them or explicitly increase `--guidance-chars`. Tokens are estimates unless an exact counter is available; the 1,000-token target is not enforced. Source text and provider framing cost extra. See [budget](budget.md).

`focus` selects at most two examples without loading the catalogue into model context. Examples include rewrites and deliberate unchanged prose; their facts never enter the target. Clean prose usually needs none. `lint` returns up to eight editorial suggestions, excluding protected material; `--limit` accepts 1–100. Findings are not an authorship assessment.

`check` compares numeric literals and common units, English month/day and ISO dates, named quote attributions, quotations, code, initial YAML frontmatter, links, reference definitions, URLs, citations, and locks. Short-claim alignment flags possible changes to direction, quantity-to-subject pairings, uncertainty, negation, commitments, ability, causality, and small spelled-out counts. Protected spans may move; contents and counts must survive. Numbered list markers are excluded. `omitted_errors` and `omitted_review` count findings beyond the displayed limit.

Pass the same destination and style overrides to `check` to flag some clear missed conventions. These warnings never edit text or claim complete style coverage. `--profile` also applies locks and saved destination preferences. Profile writes occur only through explicitly requested `voice` commands; see [voice](voice.md).

Exit codes: `0` no blocking/review findings; `1` blocking differences; `3` review needed; `2` invalid input. Editorial lint alone does not block. A `clear` result establishes neither truth nor complete meaning preservation. Numeric spelling checks are conservative. Claim alignment can miss paraphrases and raise false alarms.

Use Markdown/plain text. The scanner is not a full Markdown parser; nested syntax may be overprotected. Other languages, unfamiliar units, and ambiguous claims require semantic review. Use a source-aware tool for JSX, rich text, or binary documents. Confirm the diff before replacement; editing commands never modify files.

# Provenance

The editorial method is informed by the pinned upstream projects in [the method reference](editorial.md). Their notices are retained in [LICENSE](../LICENSE). Runtime code depends on neither project. Local checks describe implementation behavior; they do not establish superior writing or measured voice fidelity.
