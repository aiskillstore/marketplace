---
name: blocklet-converter
description: Converts static web or Next.js projects into ArcBlock blocklets using provided DID. Analyzes project structure, generates configuration files, and validates setup. Requires blocklet DID as parameter.
---

# Blocklet Converter

Converts static web projects and Next.js applications into ArcBlock blocklets with proper configuration and validation.

## Parameters

**`did`** (required): Pre-generated blocklet DID (format: `z8ia...`)

Example: `"Convert this project to blocklet using DID z8ia4e5vAeDsQEE2P26bQqz9oWR1Lxg9qUMaV"`

If missing or invalid, exit immediately with error message: "Blocklet DID parameter is required."

## Workflow

### 1. Project Analysis

**Skip directories**: `node_modules/`, `.pnpm/`, `.yarn/`, `.cache/`, `.turbo/`, `bower_components/`

#### Verify Web Application Exists

Check for ANY of:

- `package.json` with web-related dependencies
- `index.html` in root, `public/`, or `src/` or common locations
- Web framework config (`vite.config.*`, `webpack.config.*`, `next.config.*`, etc.)

**If none found → EXIT** with error message: "No web application detected."

#### Detect Project Type

Check `package.json` dependencies for:

- **Next.js**: `next` in dependencies → **Next.js project**
- **Backend frameworks**: express, koa, fastify, nest, etc. → **EXIT** with error: "Only static webapp and next.js projects are supported."
- **Otherwise** → **Static webapp**

#### Extract & Emit Metadata (Early)

**Immediately after confirming project type**, extract metadata from `package.json`:

- `title`: Human-friendly project name suitable for public display (e.g., `my-cool-app` → `My Cool App`)
- `description`: A clear, non-technical description for end users. If package.json description is too technical, rewrite it to be user-friendly.

**Emit using the protocol below**, then continue with the workflow:

```
<<<BLOCKLET_PROJECT>>>
{"title": "...", "description": "..."}
<<<END_BLOCKLET_PROJECT>>>
```

#### Build (if build script exists)

```bash
bun install && bun run build
```

**If either fails → EXIT** with error output.

#### Locate Output Directory

**For Next.js projects**: Output directory is always `.next` — skip detection.

**For static webapps**: Find `index.html` in: `dist/` → `build/` → `out/` → `public/` → `./`, or any other common locations. **If not found → EXIT** with error message: "No index.html entry point found."

#### Confirm Output Directory

Verify the output directory exists and contains expected files before proceeding.

### 2. Asset Preparation

- **README.md**: If missing, generate from `{baseDir}/templates/README-template.md`
- **logo.png**: If missing, copy from `{baseDir}/assets/default-blocklet-logo.png`
- **index.js** (Next.js only): Copy `{baseDir}/assets/nextjs-entry.txt` to project root as `index.js`

### 3. Generate blocklet.yml

**For Next.js projects**: Use template from `{baseDir}/templates/nextjs-blocklet.yml`

**For static webapps**: Use template from `{baseDir}/templates/static-blocklet.yml`

Populate with:

- `did` and `name`: Use provided DID
- `title`: Human-readable project name
- `description`: From package.json

### 4. Verification

```bash
blocklet meta
```

**For Next.js projects**:

```bash
blocklet bundle --simple --create-release --external="*"
```

**For static webapps**:

```bash
blocklet bundle --create-release
```

Fix any errors and retry.

### 5. Finalization

**Do NOT output any summary or recap after completion.** Simply end silently after successful verification. The tool outputs already provide sufficient feedback to the user.

## Error Reference

See `{baseDir}/errors.md` for all error conditions and suggestions.

## Supporting Files

- `assets/default-blocklet-logo.png` - Default logo
- `assets/nextjs-entry.txt` - Next.js entry point sample
- `templates/static-blocklet.yml` - Static webapp config template
- `templates/nextjs-blocklet.yml` - Next.js config template
- `templates/README-template.md` - README template
- `examples.md` - Workflow examples
- `errors.md` - Error reference

`{baseDir}` resolves to the skill's installation directory.

## Output Protocol

This skill emits structured data that callers can parse programmatically.

### Project Metadata Event

Emitted immediately after project validation succeeds (before build):

```
<<<BLOCKLET_PROJECT>>>
{"title": "...", "description": "..."}
<<<END_BLOCKLET_PROJECT>>>
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-friendly project name for public display |
| `description` | string | Non-technical description for end users |

