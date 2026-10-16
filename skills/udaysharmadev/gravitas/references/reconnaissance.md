# Gravitas -- Reconnaissance Reference

## Recon Principle

Inspect enough context to reduce relevant uncertainty -- not the whole repository. Recon scope is determined by the task's impact graph, not by default thoroughness.

## Standard Recon (Tier 1 tasks)

Run these in parallel:
- Read the target file
- Find and read direct importers: grep_search for imports of target
- Read the test file
- Recent changes: git log --oneline -5 -- target
- Config: read tsconfig.json or pyproject.toml or go.mod or Cargo.toml

## Extended Recon (unfamiliar codebase or high fan-out)

Add:
- Architecture overview: list_dir src/, read README.md
- Pattern discovery: grep similar patterns across codebase
- Full caller graph for changed symbol
- Related test files

## Dependency-Directed Recon

For functions or APIs with high caller counts, recon must cover:
- Changed symbol
  -> direct callers (read all)
  -> public interface files (read all)
  -> test files for callers (read)
  -> config/schema if behavior changes

This is the impact graph. It determines verification scope too.

## What Not to Do

- Do not read the entire repository for a single-function change
- Do not skip the test file because the change is simple
- Do not assume a file's content based on its name
- Do not start recon after writing (Rule 1 violation)

## Recon Completeness Check

Before moving to planning, confirm:
- I have read the target file (not assumed its content)
- I know which files import or call the target
- I know the test coverage for the target
- I know whether recent changes are relevant
- I know the blast radius of the proposed change

If any item is unchecked and relevant, recon is incomplete.
