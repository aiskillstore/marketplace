# GitHub Raw Strategy

Fetch documentation directly from GitHub repositories. Supports multiple documentation frameworks.

## Overview

Many documentation sites are built from GitHub repos. Fetching raw markdown/MDX is often cleaner than scraping rendered HTML.

## Detection

```bash
# Check for common doc framework configs
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs.yml"
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/fern/docs.yml"
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docusaurus.config.js"
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mkdocs.yml"
curl -sI "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mint.json"
```

## Fetch Commands

```bash
# Raw file
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/path/to/file.md"

# API (for listing directories)
curl -s "https://api.github.com/repos/{owner}/{repo}/contents/docs" \
  -H "Accept: application/vnd.github.v3+json"
```

## Framework-Specific Patterns

### Fern

```bash
# Nav config
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/fern/docs.yml"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/fern/pages/intro.mdx"
```

### Docusaurus

```bash
# Sidebar config (may need parsing)
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/sidebars.js"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs/intro.md"
```

### MkDocs

```bash
# Nav config
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mkdocs.yml"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs/index.md"
```

### Mintlify

```bash
# Nav config (JSON, easy to parse)
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/mint.json"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/introduction.mdx"
```

### Sphinx

```bash
# Config
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs/conf.py"

# Index (RST format)
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/docs/index.rst"
```

### Nextra

```bash
# Nav config (per-directory)
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/pages/_meta.json"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/pages/docs/intro.mdx"
```

### Astro Starlight

```bash
# Config
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/astro.config.mjs"

# Pages
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/src/content/docs/intro.md"
```

## Registry Configuration

### Fern Example

```json
{
  "baml": {
    "name": "BAML",
    "strategy": "github_raw",
    "github": {
      "owner": "BoundaryML",
      "repo": "baml",
      "branch": "canary",
      "docs_path": "fern",
      "nav_config": "fern/docs.yml"
    },
    "paths": {
      "homepage": "https://docs.boundaryml.com"
    }
  }
}
```

### Docusaurus Example

```json
{
  "react": {
    "name": "React",
    "strategy": "docusaurus",
    "github": {
      "owner": "facebook",
      "repo": "react",
      "branch": "main",
      "docs_path": "docs",
      "nav_config": "sidebars.js"
    }
  }
}
```

## Advantages

- Clean markdown content
- Version controlled (can target specific commits)
- No HTML parsing needed
- Often includes nav structure in config files

## Disadvantages

- Need to find repo URL
- Config files may require parsing (JS, YAML, etc.)
- Structure varies by framework
- Private repos need authentication

## Finding the Repo

1. Look for GitHub link in docs site footer
2. Check page source for repo references
3. Search GitHub for project name
4. Check `package.json` or similar for repo field
