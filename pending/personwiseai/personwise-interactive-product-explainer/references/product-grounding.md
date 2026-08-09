# Ground a product explainer

## Build a claim ledger

Before `course create`, list the claims the explainer may make. For each claim, record:

```text
claim
source name and current location
source date or observed date
support strength: direct | qualified | absent
allowed wording
```

The ledger is working state, not course copy. Do not retain private source text beyond the user's
request, and never record credentials or signed URLs.

Prefer sources in this order:

1. current user-supplied product documentation, pricing, security, and release materials;
2. current first-party product pages and demos;
3. user-confirmed internal briefs;
4. current third-party evidence for externally verifiable claims.

A source's marketing confidence is not evidence strength. Cross-check time-sensitive pricing,
availability, integration, certification, and roadmap statements against a current first-party
source. Use exact dates when “current” could become ambiguous.

## Choose the grounding path

### Strict document grounding

Use `materials_only` when the user supplies authoritative PDF, PPTX, DOCX, Markdown, or TXT files
and the course must stay within them. Set `declared_sources` to the exact retained count, upload all
documents, and wait for canonical processing before advancing; while any source is `pending` or
`processing`, `run advance` is a 200 no-op and `allowed_actions` omits `continue`.

When supported, a concise UTF-8 Markdown or TXT product brief assembled only from verified facts is
the preferred source for a website explainer. It should contain the claim ledger's allowed wording,
audience, verified workflow, proof, limitations, and CTA.

### Supplied text or researched brief

When no document can be uploaded, use `knowledge_source_mode=open` with a compact constitution in
`topic` and the verified brief in `content`. State explicitly that product facts may not exceed the
brief. Because the mode can supplement general knowledge, perform a sentence-level claim audit at
both `outline_ready` and `script_ready`.

Do not convert uncertainty into a polished assertion. Use “designed to,” “supports,” or other
qualified wording only when that qualification accurately matches the source.

## Safe page content

The course may explain:

- the verified audience and problem;
- the product category and supported outcome;
- a documented process, architecture, or user journey;
- supported use cases and differentiators;
- current evidence and limitations;
- a supplied next step.

The course must not manufacture:

- interface screens, clicks, menu names, or workflow steps;
- customer logos, quotes, case studies, adoption, or revenue;
- performance, ROI, conversion, time-saved, or accuracy numbers;
- integrations, platforms, file types, languages, or regions;
- pricing, discounts, trial terms, availability, or roadmap;
- compliance, privacy, security, certification, or legal claims;
- competitor facts, rankings, or “best” claims without current evidence.

If a useful field is absent, omit it or name it as an open question for the product owner.

## Image boundary

Use exact supplied screenshots as Pins when their fidelity matters. Use References only when a new
editorial image may borrow subject, palette, or composition.

For pages without verified product UI, direct the image system toward editorial diagrams,
metaphors, workflows, objects, environments, or typography. Include an explicit exclusion such as:

```text
Do not depict an application screen, dashboard, browser chrome, controls, metrics, customer logos,
or interface text.
```

Inspect generated images for implied facts. A convincing invented dashboard is still a factual
failure and must be regenerated.
