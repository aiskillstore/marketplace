# Voice Profile Cards

Use this reference when the user asks Dittobot to infer, refine, apply, or compare a reusable voice profile.

A voice profile transfers editing taste, not facts. It should help preserve how the user tends to make choices while still obeying the current draft, current audience, and current constraints.

## Default Shape

```md
## Use
- ...

## Avoid
- ...

## Rhythm/Diction
- ...

## Protected quirks
- ...

## Evidence phrases
- "..."

## When not to apply
- ...

## Editing rules
- ...
```

## Rules

- Keep the card compact enough to paste into a future prompt.
- Prefer editing guidance over biography, personality labels, or abstract adjectives.
- Treat evidence phrases as proof of the profile, not phrases to copy into every draft.
- Do not import old profile facts, claims, names, dates, or opinions into a new piece.
- Current user instructions beat the profile.
- Current draft facts and emotional stance beat the profile.
- Current audience and artifact type can override a style habit.
- Include `When not to apply` so a casual Slack voice does not leak into sensitive, legal, medical, financial, academic, or public-facing text.

## JSON Contract

Use `scripts/voice_profile.py` when a profile should be portable and auditable. The contract shape is:

```json
{
  "schema_version": 1,
  "profile_id": "default",
  "profile_type": "voice_taste",
  "token_budget": {
    "max_card_words": 220,
    "max_evidence_phrases": 5
  },
  "use": [],
  "avoid": [],
  "rhythm_diction": [],
  "protected_quirks": [],
  "evidence_phrases": [],
  "when_not_to_apply": [],
  "editing_rules": [],
  "forbidden_imports": [],
  "probe": {},
  "warnings": []
}
```

Validate contracts before reuse. Warnings about private facts, generic markers, or evidence phrases used as recipes should be reviewed before the profile is pasted into a prompt.

## Good Card Traits

- Names what to preserve: bluntness, asymmetry, dry humor, skepticism, warmth, sentence shape, punctuation, or favorite plain words.
- Names what to avoid: corporate filler, forced cheer, tidy triples, fake casualness, over-explaining, needless dashes, or inflated claims.
- Includes only short evidence phrases.
- Gives rules Dittobot can act on during a rewrite.

## Bad Card Traits

- Turns a person into broad labels such as "quirky," "professional," or "friendly" without editing rules.
- Stores private facts as if they were style.
- Tells Dittobot to always reuse a catchphrase.
- Has no boundaries for serious or precision-sensitive writing.
