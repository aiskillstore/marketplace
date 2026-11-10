# PPTX Nova Assets

This directory is the local asset catalog used by the `pptx-nova` skill.

The catalogs are intentionally small and metadata-first. They define stable IDs,
selection hints, and generator/patch entry points. Bundled binary assets include
the Tabler icon pack and curated DeckKit showcases.

## Directories

- `brands/` - brand profiles, logo references, and font preferences.
- `layouts/` - reusable grid systems and layout-contract mappings.
- `decks/` - complete sample deck generators or patch bundles.
- `deckkits/` - creation DeckKits, design contracts, schemas, and content examples.
- `themes/` - themePack/stylePack catalog consumed by `catalog themes`.
- `charts/` - native chart/table/diagram presets, not SVG-only templates.
- `icons/` - icon metadata and migration policy for vector/native assets.
- `schemas/` - run-level JSON Schemas such as `assets_manifest.json`.
- `examples/` - end-to-end examples and generator templates.

## Rules

- Prefer JSON catalogs over undocumented loose files.
- Treat `themes/catalog.json` as the source of truth for built-in
  themePack/stylePack data. If maintainers edit it in the source repository,
  regenerate the derived catalogs before publishing the skill. Packaged skill
  consumers should use the bundled generated catalogs as-is.
- Keep binary and licensed assets out until their license source is recorded.
- Tabler icons are vendored as a deterministic Brotli pack at
  `icons/tabler-icons.pack.br`, with the Tabler MIT license copied to
  `icons/icon-license`. Refresh both from the local Tabler checkout with:

  ```bash
  node <skill-root>/scripts/cli/assets/icons.mjs generate --source-root <tabler-icons-checkout>
  node <skill-root>/scripts/cli/assets/icons.mjs generate --source-root <tabler-icons-checkout> --check
  ```

  Maintainers may set `TABLER_ICONS_ROOT=<tabler-icons-checkout>` instead of
  passing `--source-root`; the published skill must not contain machine-local
  checkout paths.

  During PPTX generation, DeckKit code should consume this pack through
  `assets/deckkits/shared/icon-assets.kit.mjs`; agents should search/get icons through
  `node <skill-root>/scripts/cli/assets/icons.mjs ...`. Do not fetch icons from the network or
  scan the Tabler checkout in the deck generation path.

- Use `xdoc pptx extract-style reference.pptx --output style.json --json` to
  create a draft profile before adding a new brand or theme entry.
- Use `xdoc pptx import-template reference.pptx --name stable-id --output-dir <skill-root>/assets --json`
  to copy a reference PPTX into `decks/<id>/`, write brand/layout/theme/style
  profiles, and register the imported entries in the local catalogs.
- Use `xdoc pptx slide-copy -i target.pptx --source source.pptx --slides 1,3,5-8 --output out.pptx`
  for transactional whole-slide reuse. `--slides` is 1-based and `--all` selects
  the whole source; the two selectors are mutually exclusive, and omitting both
  copies only the first source slide.
- Use `node <skill-root>/scripts/cli/deckkits/benchmark.mjs --deckkit <id> --all --repeat 3 --clean`
  plus `node <skill-root>/scripts/cli/deckkits/readiness.mjs --deckkit <id> --target delivery --benchmark-mode required-live`
  for production visual gates. Store long-lived benchmark inputs under
  `<skill-root>/benchmarks/visual/`, not under `assets/decks/`.
- Keep routine generated `.pptx`, previews, contact sheets, patches, and reports
  in run directories. Intentional curated showcases belong under
  `examples/deckkits/`, with their source content and manifest hashes.
