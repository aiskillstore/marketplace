# Examples from Real Wiki

This directory contains real files from a knowledge base maintained with `karpathy-llm-wiki` since April 2026.

## Files

| File | What it shows |
|------|---------------|
| `claude-code-statusline-landscape.md` | Compiled wiki article with structured data (tables, citations, cross-references) |
| `2026-03-19-claude-code-statusline-landscape.md` | Raw source material before compilation |
| `ai-coding-tools-index.md` | One topic section of the global index (summary + Updated per article) |
| `log-sample.md` | Sample entries from operation log (all current entry types) |

## Raw vs Compiled Comparison

**Raw source** (`2026-03-19-claude-code-statusline-landscape.md`):
- Original research notes
- Unstructured content
- Metadata header (Source, Collected, Published dates)

**Compiled article** (`claude-code-statusline-landscape.md`):
- Structured sections (Overview, Competitive Landscape, User Pain Points)
- Tables synthesized from multiple sources
- Cross-references to other wiki articles
- Updated across multiple ingest operations

## Operation Log

The log records every action:
- `ingest` — source collected into raw/ and compiled (with Disposition: New / Update / Disputed, or `no material` when nothing was worth compiling)
- `query` — archived query results
- `lint` — quality checks and their outcomes

Recent activity shows daily maintenance: 87 entries in the last 7 days alone.