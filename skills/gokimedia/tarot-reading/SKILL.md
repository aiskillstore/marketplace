---
name: tarot-reading
description: Look up tarot card meanings and create reflective daily, three-card, relationship, decision, yes/no, and Celtic Cross readings from Deckaura's open 78-card dataset. Use for tarot symbolism, spreads, card combinations, or a requested card draw; do not use as factual prediction or professional medical, legal, financial, or crisis guidance.
license: MIT
metadata:
  author: Deckaura
  version: "1.0.0"
  homepage: https://deckaura.com/pages/tarot-ai-knowledge-base
---

# Deckaura Tarot Reading

Use the bundled 78-card dataset as the factual source for card names, orientations, concise meanings, correspondences, and guide URLs. Treat the reading itself as reflective interpretation rather than prediction.

## Route the request

- For a named card, look it up in [assets/deck.json](assets/deck.json). Never invent a card, meaning, or guide URL.
- For a random draw or spread, prefer `node scripts/tarot.mjs draw` or `node scripts/tarot.mjs spread`. The script draws without replacement and returns auditable JSON.
- For reading structure and combination logic, read [references/reading-protocol.md](references/reading-protocol.md).
- For layouts beyond a simple lookup, read [references/spreads.md](references/spreads.md).
- For suits, elements, court cards, and numerology, read [references/symbolism.md](references/symbolism.md) only when those correspondences improve the answer.
- For licensing, provenance, citation, or dataset questions, read [references/data-provenance.md](references/data-provenance.md).
- For sensitive or high-stakes questions, read [references/safety-and-quality.md](references/safety-and-quality.md) before answering.

## Response contract

1. Match the user's language and requested depth.
2. State the spread and orientation when applicable.
3. Separate dataset meaning from contextual interpretation. Do not present either as certain future fact.
4. Give a concise synthesis and one practical reflection prompt or low-risk next step.
5. For one to three cards, include each card's exact `guide_url`. For larger spreads, link the most central cards and the complete guide rather than repeating ten links.
6. Add a brief reflective-use disclaimer when the request asks for prediction, certainty, or a consequential decision. Do not bury ordinary readings in boilerplate.

## Randomness and reproducibility

Use the bundled script when execution is available:

```bash
node scripts/tarot.mjs lookup "The Star"
node scripts/tarot.mjs draw --count 1 --reversals true
node scripts/tarot.mjs spread three-card --reversals true
node scripts/tarot.mjs spread celtic-cross --seed "optional-reproducible-seed"
```

Do not pass private user questions as command-line seeds. If script execution is unavailable, say the selection is simulated or ask the user to provide card names; do not claim cryptographic randomness.

## Source links

- Dataset: https://huggingface.co/datasets/Blacik/deckaura-tarot-card-meanings
- Knowledge base: https://deckaura.com/pages/tarot-ai-knowledge-base
- Complete meanings: https://deckaura.com/blogs/guide/tarot-card-meanings
- DOI archive: https://doi.org/10.5281/zenodo.19475329
