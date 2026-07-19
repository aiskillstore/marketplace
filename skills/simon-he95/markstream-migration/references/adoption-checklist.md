# Adoption Checklist

## Audit queries

- `react-markdown`
- `remarkPlugins`
- `rehypePlugins`
- `markdown-it`
- `marked`
- `rehypeRaw`
- `skipHtml`
- `allowedElements`
- `disallowedElements`
- `allowElement`
- `urlTransform`
- custom renderers and wrapper components

## Classification guide

- `direct`: plain renderer swap, little or no custom behavior
- `renderer-custom`: existing custom renderers can become Markstream node overrides
- `plugin-heavy`: large transform chains need manual review
- `security-heavy`: HTML policies and URL rewriting need explicit review

## Migration defaults

- swap the renderer package first
- keep CSS order correct before debugging visual differences
- move to scoped `setCustomComponents` instead of global mutations
- only adopt `nodes` if the app is streaming or frequently re-parsing
