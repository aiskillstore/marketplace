# Memory Management Examples

---

## Example 1: Update Rankings for Hero Keywords

**User**: "Update rankings for our hero keywords"

```markdown
I'll update rankings for your hero keywords.
[Reads memory/hot-cache.md -> Hero Keywords section]
[If ~~SEO tool connected: runs automated ranking check]
[If manual: asks user for current rankings]

## Ranking Update - December 15, 2024

| Keyword | Previous | Current | Change | Target | Status |
|---------|----------|---------|--------|--------|--------|
| keyword research tools | #15 | #12 | up 3 | #5 | Improving |
| best seo software | #23 | #24 | down 1 | #10 | Stable |
| free backlink checker | #8 | #6 | up 2 | #3 | Near target |

### Updated Files
1. memory/hot-cache.md -> Hero Keywords table updated
2. memory/monitoring/rank-history/2024-12-15-ranks.csv -> New row added

### Recommendations
1. Push additional content/backlinks to "free backlink checker" to hit #3
2. Investigate "keyword research tools" +3 gain (replicate success)
3. Monitor "best seo software" for negative trends

Hot cache refreshed. Next ranking check: December 22, 2024.
```

---

## Example 2: Glossary Lookup

**User**: "What does 'quick wins' mean in our project?"

```markdown
[Check memory/hot-cache.md -> not found]
[Check memory/glossary.md -> found!]

**Quick Wins**
- **Definition**: Low-difficulty, high-value target keywords
- **Keyword Count**: 25
- **Context**: Keywords achievable for page 1 within 30-60 days due to low competition

Current list stored in: `memory/research/keywords/long-tail-keywords.md` (tagged "quick-win")
```

---

## Example 3: Initialize Memory for New Project

**User**: "Set up memory for a new e-commerce site selling outdoor gear"

```markdown
I'll set up the two-layer memory system.
[Creates: memory/glossary.md, memory/research/, memory/content/, memory/monitoring/, etc.]

To populate hot cache, I need:
1. **Target Keywords**: Top 10 hero keywords
2. **Primary Competitors**: Top 3-5 competitors
3. **Current Metrics**: DA, organic traffic, existing rankings
4. **Active Initiatives**: New categories, content campaigns, product focus
5. **Project Terminology**: Internal names, abbreviations, keyword segmentation

Once provided, I'll generate:
- memory/hot-cache.md, memory/glossary.md
- memory/research/keywords/ and memory/research/competitors/ structures
- memory/content/calendar/active-calendar.md
```

---

## Advanced Features

- **Smart Context Loading**: `Load full context for [campaign name]`
- **Memory Health Check**: `Run memory health check` — orphaned files, missing timestamps, stale items
- **Bulk Promotion/Demotion**: `Promote all keywords ranking in top 10 to hot cache`
- **Memory Snapshot**: `Create memory snapshot for [date/milestone]`
- **Cross-Project Memory**: `Compare memory with [other project]`

---

## Practical Limitations

- **Concurrent access**: Use timestamped filenames to avoid overwrites from parallel sessions.
- **Cold storage retrieval**: WARM/COLD files only load on demand. Hot cache is primary cross-session mechanism.
- **Data freshness**: Stale data (>90 days) should be flagged for refresh.

---

## Auditor Pointer Index Format

Append to `memory/indexes/audits/YYYY-MM.md`, newest at bottom:

```markdown
## 2026-07-10 · paid-search-q3 · ROAS/direct-response
- artifact: memory/audits/ad/2026-07-10-paid-search-q3.md
- artifact_sha256: <sha256 of the validated file>
- schema_version: 3.0
- runbook_version: 3.0.0
- observed_at: 2026-07-10
```

**Rules**:
- One pointer block per immutable audit artifact; do not copy scores, findings, vetoes, status, or verdict into the index.
- Verify the artifact with `validate-audit-artifact.py` before indexing it and retain framework/profile/version in the heading.
- Never place the index itself under `memory/audits/`; that namespace accepts only typed auditor artifacts.
- Attribution workbooks and other non-auditor reports remain in their discipline paths and may use separate pointer indexes without being represented as gate results.
- Subject erasure updates the working artifact and then refreshes its hash pointer. Record the operation separately in `memory/privacy/erasure-log.md`; never turn a privacy log into an audit artifact.
- If the monthly index does not exist, create it with `# Audit Artifact Index — YYYY-MM`.
