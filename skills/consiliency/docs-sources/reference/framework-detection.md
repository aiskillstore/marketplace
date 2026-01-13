# Framework Detection Reference

Detailed patterns for detecting documentation frameworks from config files and project structure.

## Detection Matrix

| Framework | Primary Config | Secondary Signs | Package.json Deps |
|-----------|---------------|-----------------|-------------------|
| Fern | `fern/docs.yml` | `fern.config.json` | `fern-api` |
| Docusaurus | `docusaurus.config.js` | `sidebars.js` | `@docusaurus/core` |
| MkDocs | `mkdocs.yml` | `docs/` dir | (Python) `mkdocs` |
| Mintlify | `mint.json` | - | `mintlify` |
| Sphinx | `conf.py` | `*.rst` files | (Python) `sphinx` |
| Nextra | `_meta.json` in pages | `theme.config.tsx` | `nextra`, `nextra-theme-docs` |
| Starlight | `@astrojs/starlight` in config | `src/content/docs/` | `@astrojs/starlight` |
| Antora | `antora.yml` | `*.adoc` files | (Ruby/Node) |
| GitBook | `SUMMARY.md` | `book.json` | `gitbook-cli` |
| VuePress | `.vuepress/config.js` | `docs/` dir | `vuepress` |
| ReadTheDocs | `readthedocs.yml` | `*.readthedocs.io` URL | - |

## Fern

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/fern/docs.yml"
```

### Config Structure (docs.yml)

```yaml
instances:
  - url: docs.viperjuice.dev

navigation:
  - section: Getting Started
    contents:
      - page: Introduction
        path: ./pages/intro.mdx
```

### Doc Paths

- Config: `fern/docs.yml`
- Pages: `fern/pages/*.mdx`
- API: `fern/api/*.yaml`

## Docusaurus

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docusaurus.config.js"
```

### Config Structure (sidebars.js)

```javascript
module.exports = {
  docs: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['installation', 'configuration'],
    },
  ],
};
```

### Doc Paths

- Config: `docusaurus.config.js`, `sidebars.js`
- Pages: `docs/*.md`, `docs/**/*.md`
- Versioned: `versioned_docs/version-X.X/`

## MkDocs

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mkdocs.yml"
```

### Config Structure (mkdocs.yml)

```yaml
site_name: My Docs
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Configuration: getting-started/configuration.md
```

### Doc Paths

- Config: `mkdocs.yml`
- Pages: `docs/*.md`
- Theme: Often `mkdocs-material`

## Mintlify

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mint.json"
```

### Config Structure (mint.json)

```json
{
  "name": "My Docs",
  "navigation": [
    {
      "group": "Getting Started",
      "pages": ["introduction", "quickstart"]
    }
  ]
}
```

### Doc Paths

- Config: `mint.json`
- Pages: `*.mdx` in root or subdirs

## Sphinx

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs/conf.py"
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/conf.py"
```

### Config Structure (conf.py)

```python
project = 'My Project'
extensions = ['sphinx.ext.autodoc']
```

### Navigation (index.rst)

```rst
.. toctree::
   :maxdepth: 2

   getting-started
   api-reference
```

### Doc Paths

- Config: `docs/conf.py` or `conf.py`
- Pages: `docs/*.rst` or `*.rst`

## Nextra

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/pages/_meta.json"
```

### Config Structure (_meta.json)

```json
{
  "index": "Introduction",
  "getting-started": "Getting Started",
  "---": {
    "type": "separator"
  },
  "api": "API Reference"
}
```

### Doc Paths

- Config: `pages/_meta.json` (per directory)
- Pages: `pages/**/*.mdx`
- Theme: `theme.config.tsx`

## Astro Starlight

### Detection

```bash
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/astro.config.mjs" | \
  grep "@astrojs/starlight"
```

### Config Structure

```javascript
import starlight from '@astrojs/starlight';

export default defineConfig({
  integrations: [
    starlight({
      sidebar: [
        { label: 'Guides', items: [
          { label: 'Introduction', link: '/guides/intro/' },
        ]},
      ],
    }),
  ],
});
```

### Doc Paths

- Config: `astro.config.mjs`
- Pages: `src/content/docs/**/*.md`

## Antora

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/antora.yml"
```

### Config Structure (antora.yml)

```yaml
name: my-component
version: '1.0'
nav:
  - modules/ROOT/nav.adoc
```

### Doc Paths

- Config: `antora.yml`, `antora-playbook.yml`
- Pages: `modules/ROOT/pages/*.adoc`
- Nav: `modules/ROOT/nav.adoc`

## GitBook

### Detection

```bash
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/SUMMARY.md"
```

### Navigation (SUMMARY.md)

```markdown
# Summary

* [Introduction](README.md)
* [Getting Started](getting-started/README.md)
  * [Installation](getting-started/installation.md)
```

### Doc Paths

- Config: `book.json` (optional)
- Nav: `SUMMARY.md`
- Pages: `**/*.md`
