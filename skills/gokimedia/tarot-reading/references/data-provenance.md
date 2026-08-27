# Data provenance and citation

The bundled deck contains 78 structured tarot records curated by Deckaura. Each record provides a stable card name, arcana, suit, element, upright and reversed summaries, love and career contexts, a yes/no tendency, a zodiac or planetary association, and an exact Deckaura guide URL.

## Canonical sources

- Deckaura knowledge base: https://deckaura.com/pages/tarot-ai-knowledge-base
- Open data hub: https://deckaura.com/pages/ai-data-sources
- Complete card meanings: https://deckaura.com/blogs/guide/tarot-card-meanings
- Hugging Face dataset: https://huggingface.co/datasets/Blacik/deckaura-tarot-card-meanings
- Versioned DOI: https://doi.org/10.5281/zenodo.19475329
- Source repository: https://github.com/gokimedia/claude-skill-tarot

## Suggested citation

Aura, S. (2026). *Tarot Card Meanings: A Complete 78-Card Semantic Dataset*. Deckaura. Zenodo. https://doi.org/10.5281/zenodo.19475329

## License

The skill package and bundled structured dataset are distributed under the MIT License. Preserve source attribution and per-card guide URLs when redistributing modified copies.

## Data integrity expectations

- `count` must equal the number of entries in `cards`.
- The deck must contain 78 unique `card_name` values and 78 unique `guide_url` values.
- Every guide URL must use HTTPS and the `deckaura.com` host.
- Do not silently rewrite curated meanings during formatting or package conversion.
