# Override Patterns

## Common override keys

| Key | Typical use |
|-----|-------------|
| `image` | lightboxes, captions, lazy-loading wrappers |
| `link` | analytics, router integration, custom tooltip behavior |
| `code_block` | replace regular fenced code blocks |
| `mermaid` | customize Mermaid only |
| `d2` | customize D2 only |
| `infographic` | customize infographic blocks only |
| `inline_code` | typography or special inline behavior |
| `heading`, `paragraph`, `list_item` | container overrides that must render children |

## Trusted custom-tag pattern

1. register the tag in `customHtmlTags`
2. map the same tag name with `setCustomComponents(customId, { tagName: Component })`
3. if the tag body contains Markdown, render `node.content` with a nested renderer
4. pass the same `customHtmlTags` list to the nested renderer

## Nested renderer defaults

- `typewriter: false`
- `viewportPriority: false`
- `deferNodesUntilVisible: false`
- `maxLiveNodes: 0`
- `batchRendering: false`

Use those defaults when predictable nested streaming behavior matters more than optimization.
