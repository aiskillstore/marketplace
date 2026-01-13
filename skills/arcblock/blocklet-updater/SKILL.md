---
name: blocklet-updater
description: Creates a new release for a blocklet project by bumping version, building, and bundling. Use when asked to "create a new release", "bump and bundle", or "update blocklet version".
---

# Blocklet Updater

Bumps a blocklet project version and creates a release bundle.

## Workflow

### 1. Version Bump

```bash
blocklet version patch
```

**If fails → EXIT** with error output.

### 2. Build System Detection

Check if `package.json` exists and contains a `build` script.

#### If Build Script Exists

Install dependencies and build:

```bash
pnpm install && pnpm run build
```

**If either fails → EXIT** with error output.

#### If No Build Script

Skip build step - project is likely pre-built or static.

### 3. Entry Point Verification

#### Locate Output Directory & Entry Point

Find `index.html` in common locations: `dist/` → `build/` → `out/` → `public/` → `./`

**If not found → EXIT** with error message: "No index.html entry point found."

#### Verify blocklet.yml Main Field

Read `blocklet.yml` and check the `main` field:

- If `main` points to directory containing `index.html` → valid
- If `main` is misaligned → update it to the correct output directory
- After any update, inform user of the change

### 4. Metadata Verification

```bash
blocklet meta
```

**If fails → EXIT** with error output and suggestions.

### 5. Bundle Creation

```bash
blocklet bundle --create-release
```

**If fails → EXIT** with error output.

### 6. Finalization

**Do NOT output any summary or recap after completion.** Simply end silently after successful bundle creation. The tool outputs already provide sufficient feedback to the user.

## Error Reference

See `{baseDir}/errors.md` for all error conditions and suggestions.

## Supporting Files

- `errors.md` - Error reference
- `examples.md` - Workflow examples

`{baseDir}` resolves to the skill's installation directory.
