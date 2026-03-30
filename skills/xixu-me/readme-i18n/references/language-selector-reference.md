# Language Selector Reference

Use one selector block near the top of every README variant.

## Placement

- Put the selector immediately after the opening title and badge cluster.
- If the file opens with a hero image, HTML banner, or short intro block, place the selector right after that opening block.
- Keep the selector position consistent across all variants.

## Canonical Selector Block

When adding a new selector, use these markers so future runs can update it in place:

```md
<!-- README-I18N:START -->

**English** | [汉语](./README.zh.md) | [Español](./README.es.md)

<!-- README-I18N:END -->
```

Rules:

- The current language is emphasized and not linked.
- Other languages are linked.
- Use human-readable autonyms when practical, for example `English`, `汉语`, `Español`, `Français`.
- Keep the same language order in every file.

## Updating Existing Selectors

- If a selector already uses `README-I18N` markers, replace only the contents inside that block.
- If the README has an obvious unmarked language switcher near the top, normalize it in place rather than inserting a second selector elsewhere.
- Do not leave multiple selector blocks in the same README.

## Filename Pattern

Default localized sibling naming:

```text
README.md
README.zh.md
README.es.md
README.fr.md
```

If the repository already uses another multilingual naming scheme, preserve that existing scheme instead of forcing the default.

## Variant Examples

Current file: `README.md`

```md
<!-- README-I18N:START -->

**English** | [汉语](./README.zh.md) | [Español](./README.es.md)

<!-- README-I18N:END -->
```

Current file: `README.zh.md`

```md
<!-- README-I18N:START -->

[English](./README.md) | **汉语** | [Español](./README.es.md)

<!-- README-I18N:END -->
```

Current file: `README.es.md`

```md
<!-- README-I18N:START -->

[English](./README.md) | [汉语](./README.zh.md) | **Español**

<!-- README-I18N:END -->
```
