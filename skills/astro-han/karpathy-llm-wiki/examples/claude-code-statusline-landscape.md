# Claude Code Statusline Tool Ecosystem

> Sources: claude-pace project research, 2026-03-19; 2026-03-24
> Raw: [raw/ai-coding-tools/2026-03-19-claude-code-statusline-landscape.md](../../raw/ai-coding-tools/2026-03-19-claude-code-statusline-landscape.md)
> Updated: 2026-03-24

## Overview

Around Claude Code's opaque quota problem, the community has spawned over a dozen statusline tools, forming a rapidly evolving ecosystem. By mid-March 2026, competitive focus shifted from "feature count" to "data accuracy and runtime reliability", with zero runtime dependencies becoming a differentiation point.

## Competitive Landscape (2026-03-19 Data)

| Project | Stars | Language | Positioning |
|---------|------:|----------|-------------|
| ccusage | 11,693 | TypeScript | CLI usage analysis tool, statusline is a sub-feature; core selling point: cost visualization |
| claude-hud | 7,038 | JavaScript | Most feature-complete pioneer: context progress bar, rate limit, sub-agent status, Git integration |
| Claude-Code-Usage-Monitor | 7,009 | Python | Standalone dashboard, ML prediction; discontinued (last update 2025-09) |
| ccstatusline | 5,421 | TypeScript | Positioned as "formatter", no API calls; highly customizable + themes |
| CCometixLine | 2,227 | Rust | High-performance binary; only Rust solution in awesome-claude-code |
| claude-powerline | 931 | TypeScript | vim powerline style |

**Primary distribution channels**:
- awesome-claude-code (29,014 stars): currently includes 5 statusline tools, excludes claude-hud
- Anthropic official plugin directory (12,653 stars): zero statusline entries

## User Pain Points

### Opaque Quota (Root Problem)

1. **Sudden limit hit without warning**: $200/month Max users hit limits in 10-15 minutes, only see "usage limit reached"
2. **Invisible quota reset time**: On 2026-03-18, 3 independent issues requested this feature on the same day
3. **5h + 7d dual window cognitive burden**: Users can't distinguish which limit they're under

### Officially Not Doing

Anthropic marked issue #10593 as "Not Planned" (2026-01-19), rejecting native token indicator, recommending ccusage. Meanwhile, statusline stdin JSON doesn't expose `session_used_percentage`, `weekly_used_percentage`, `resets_at` quota fields, forcing third-party tools to use Usage API or parse local JSONL files.

## User Feedback Analysis

### Best-Received Features

**Context progress bar**: Multiple independent sources consistently call it "install reason". SAP community author: "context bar alone is worth the install".

**Cross-session daily cost summary**: ccusage's core selling point, Japanese user community extensively documents "one command to see costs" experience. Multiple independent reviews list "cost visualization" as primary reason for choosing ccusage.

**Rate Limit 5h/7d visualization**: After v2.1.80, stdin provides official data, all tools have equal opportunity, differentiation space shifts from "having it" to "being accurate".

### Pitfalls Already Hit

**ccusage Live Blocks removed**: Real-time token consumption monitoring was officially removed due to accuracy issues (issue #782). Issues #288 (16 reactions) and #483 (11 reactions) document persistent user complaints about "shows not at limit but actually hit".

**ccusage process management bug** (issue #459, 10 reactions): `bun x ccusage statusline` in hooks causes infinite process spawning, CPU 100%. This is structural risk from Node.js runtime.

**claude-hud sub-agent monitoring**: Blog authors highly praise it, but 6 subagent-related issues all have 0 reactions, suspected maintainer or AI bulk creation, not user-driven. This shows **systematic bias between blog review perspective (feature completeness) and user voting (most painful needs)**.

### Feature Creep Warning

Ovidiu (Substack): "When everything is highlighted, nothing is"

ccusage's Live Blocks from feature to removal全过程 is a live lesson: real-time features with inadequate accuracy反而 damage tool credibility.

## Technical Trends

**Migration from Node.js to lightweight runtimes**:
- Rust: CCometixLine, claudia-statusline
- Go: felipeelias (single binary, minimal)
- Shell/Bash: kamranahmedse, rz1989s (curl one-line install)

**Zero-dependency install as selling point**: Multiple community authors list "reduce dependencies" as tool selection factor, Go single binary and pure Bash solutions' motivation both include this.

**No public performance benchmarks**: No tool has published hyperfine or equivalent ms-level benchmark numbers, this is unoccupied differentiation space.

## Impact

Statusline track in March 2026 saw rapid growth (claude-hud gained 4,804 stars in 5 days, mainly GitHub Trending effect), but the track has become crowded. Real competitive advantage doesn't come from feature count, but from:

1. **Data reliability**: ccusage's live blocks removed due to inaccuracies, shows "accurate" is more important than "rich"
2. **Zero dependencies**: Node.js tools' process management bugs show runtime dependency is structural risk, not just installation inconvenience
3. **Differentiated features**: Unique core concepts (like pace tracking: is current speed enough) are more competitive than "me too" features

**Features not worth pursuing**: Sub-agent monitoring (data source not in stdin, actual user demand evidence insufficient), Multi-device data sync (high engineering complexity, weak demand evidence).