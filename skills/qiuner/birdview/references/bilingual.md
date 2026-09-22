# Architecture language selection

[中文](bilingual.zh.md)

## Select and author

Resolve the delivery language without asking or pausing: explicit output instructions/applicable standing preference, then dominant request prose (ignore code IDs and quoted source). For language-neutral requests, use recent conversation, existing map language, then English. Browser locale and saved UI preferences do not decide authored language.

Support any language. Set `language` to the base language tag; single-language maps need no translations. For multiple languages, use the preferred/first-listed language as base and put others in each text-owning object's `translations.<language-tag>`. Reuse existing structure, base language and translations; add complete missing delivery translations. Infer an absent base tag from prose, using the delivery language if ambiguous. Saved translation changes increment map revision and respect active task bindings.

Describe the same inspected architecture in all languages:

- Translate project/group/module names, responsibilities, relationship labels, evidence notes and nonempty `openQuestions`; preserve question order and uncertainty.
- Keep names short and responsibilities suitable for two lines, with full text in details. Preserve proper names, IDs, paths, symbols, line numbers, enums and layout.
- Use one map; do not invent evidence or remove existing translations unprompted. See [the complete example](../examples/bilingual.architecture.json).
- For multilingual activity, translate every supported language's event `translations[locale].reason` and check `translations[locale].summary`; missing values fall back to original text.

## Validate and display

```sh
node <skill-root>/scripts/validate.mjs <map.json> --bilingual
node <skill-root>/scripts/render.mjs <map.json> <architecture.html>
```

Use `--bilingual` for Chinese/English delivery only. Single-language maps validate without it; other combinations require manual language-coverage review after structural validation. The strict check verifies architecture text coverage and question counts, not translation accuracy or activity translations. Do not claim complete Chinese/English coverage before it passes; inspect both languages' tooltips, details and relationships in the browser, and check activity coverage separately.

Open HTML with `#lang=<delivery-language-tag>`. Display priority is supported URL language, saved preference, then map base (legacy default: Chinese). Switching preserves selection, layout and zoom; missing translations use base text. The selector does not translate content or call a translation API.

UI controls are bundled only in Chinese/English; other languages use English controls with authored project text. Do not claim fully localized UI for them. Right-to-left content is supported, but graph/toolbar layout remains left-to-right.
