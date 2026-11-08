# Exploratory deck generator

`deck-generator-template.mjs` imports the adjacent `theme-packs.generated.mjs`. Copy both files into
a new run directory before adapting the generator:

```sh
cp <skill-root>/assets/examples/generator/deck-generator-template.mjs <run-dir>/generate.mjs
cp <skill-root>/assets/examples/generator/theme-packs.generated.mjs <run-dir>/theme-packs.generated.mjs
node <run-dir>/generate.mjs --theme corporate-blue --style consulting --layout executive-grid
```

Layouts are `executive-grid`, `narrative-split`, and `data-room`. Output is an xdoc patch; run the normal
schema, dry-run, semantic and visual gates before delivery. Prefer an existing eligible DeckKit for
ordinary creation.

Themes are generated from `assets/themes/catalog.json`. Maintainers refresh or check them with
`nu tools/generate-pptx-theme-catalog.nu --skip-moonbit` or the same command with `--check`.
Skill consumers use the bundled file without maintainer tooling.
