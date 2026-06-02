# Fact Fences

Use this reference when the user supplies explicit protected facts, claims, voice markers, or boundaries alongside draft text.

Fact fences are lightweight markup for saying what must survive, what must not be invented, and what voice evidence matters. They are optional; normal Dittobot use should still work when the user only pastes messy notes.

## Inline Syntax

```text
[[keep: Acme contract, 10 business days, not counsel]]
[[claim: may need to send notice]]
[[voice: haunted changelog, somehow both too long and says nothing]]
[[avoid: robust, seamless, Legal has approved]]
[[boundary: casual Slack voice does not apply to the customer notice]]
```

## How To Treat Fences

- Treat `keep` as protected facts or phrases.
- Treat `claim` as required claims that must not be strengthened or removed.
- Treat `voice` as source voice markers, not decoration to paste everywhere.
- Treat `avoid` as forbidden terms, assertions, or generic moves.
- Treat `boundary` as `When not to apply` guidance for profiles or tone habits.
- Remove fence markup from the final rewrite unless the user asks to keep it.
- Current draft facts beat older profile facts.
- Fences can make a rewrite safer, but they cannot authorize invented details.

## Conflict Rules

- Current explicit user instruction wins.
- Legal, medical, financial, technical, academic, and factual precision wins over style.
- A fact fence wins over an old voice profile.
- A boundary can disable profile habits for a specific artifact.
- If fences conflict with each other and the conflict affects meaning or risk, ask one concise clarifying question.
