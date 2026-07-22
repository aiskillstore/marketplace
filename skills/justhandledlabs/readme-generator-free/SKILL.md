---
name: readme-generator-free
description: Generate polished README files from project code. Use when the user says "generate readme", "create README", "write project documentation", "make a readme", or asks for README generation, project documentation, installation docs, usage docs, API docs, badges, or repository onboarding documentation derived from an existing codebase.
metadata:
  version: 1.0.0
  author: JustHandled Labs
  triggers:
  - generate readme
  - create README
  - write project documentation
  - make a readme
---
# README Generator

Create a polished, accurate `README.md` from the project files that actually exist. Prefer evidence from manifests, source files, comments, and command output over generic filler.

## Workflow

1. Inspect the project root before writing:
   - Node: `package.json`
   - Python: `requirements.txt`, `pyproject.toml`, `setup.py`, or `setup.cfg`
   - Go: `go.mod`
   - Rust: `Cargo.toml`
   - Java: `pom.xml`, `build.gradle`, or `build.gradle.kts`
   - Make commands: `Makefile`
   - License: `LICENSE`, `LICENSE.md`, or package manifest license fields
2. Detect the main entry point:
   - Node/TypeScript: `package.json` `main`, `bin`, `exports`, `src/index.ts`, `src/index.js`, `index.js`, or `server.js`
   - Python: `main.py`, `app.py`, package console scripts, or `__main__.py`
   - Go: `main.go` or `cmd/*/main.go`
   - Rust: `src/main.rs`, `src/lib.rs`, or `[[bin]]` entries in `Cargo.toml`
   - Java: Maven/Gradle application plugin config or `src/main/java/**/Main.java`
3. Extract dependencies only from actual manifests:
   - Node: `dependencies`, `devDependencies`, `peerDependencies`, and `optionalDependencies`
   - Python: `requirements.txt`, `pyproject.toml`, `setup.py`, or `setup.cfg`
   - Go: `require` blocks in `go.mod`
   - Rust: `[dependencies]`, `[dev-dependencies]`, and `[build-dependencies]`
   - Java: Maven dependencies or Gradle dependencies
4. Extract scripts and commands:
   - Node: `package.json` `scripts`
   - Make: targets from `Makefile`
   - Python: console scripts in package metadata, common commands from project files
   - Go/Rust/Java: standard build, test, and run commands when the matching manifest exists
5. Infer description cautiously:
   - Prefer `package.json`/manifest description fields.
   - Otherwise use top-level comments, module docstrings, existing docs, or repository/folder name.
   - If there is not enough evidence, write a modest one-sentence description and mark unknown specifics as TODO.
6. Generate the README with:
   - Title from package name, manifest name, or directory name
   - Badges for license, primary language, version, and build status placeholder
   - Description
   - Installation instructions for the detected language
   - Usage examples from `--help` output when safe to run, otherwise from scripts and entry points
   - API documentation when JSDoc, docstrings, Go comments, Rust doc comments, or JavaDoc are present
   - Contributing guidelines
   - License section from detected license or a prompt/TODO when unknown

## Template Reference

Read `references/templates.md` when choosing language-specific README sections, badge patterns, or install command templates. Keep the final README tailored to the current repository rather than copying every optional section.

## Accuracy Rules

- Do not hallucinate dependencies, commands, entry points, environment variables, APIs, or deployment steps.
- Only include dependencies and scripts that were found in real files.
- Use TODO markers for important unknowns instead of inventing facts.
- Do not run commands that mutate the project while collecting README evidence.
- Only run `--help` commands when they are likely safe and local; skip them if the command may start servers, install packages, modify files, or call external services.
- Keep Markdown valid with one `#` title, proper heading levels, fenced code blocks, and no broken table syntax.

## Output Shape

When asked to create or update a README, write or update `README.md` in the project root unless the user specifies another path. Summarize the evidence used and list any TODOs that remain because the repository did not contain enough information.
