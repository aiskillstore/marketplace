# Claude Code Statusline Market Scan

> Source: claude-pace project research
> Collected: 2026-03-19 (GitHub stars verified via gh api)
> Published: Unknown

Market data below is as of 2026-03-19.

## Competitive Landscape

| Project | Stars | Language | Form | Last Update | Features |
|---------|------:|----------|------|-------------|----------|
| [ccusage](https://github.com/ryoppippi/ccusage) | 11,693 | TypeScript | CLI + statusline | 03-18 | Usage analysis + burn rate |
| [claude-hud](https://github.com/jarrodwatts/claude-hud) | 7,038 | JavaScript | statusline | 03-15 | Most features, pioneer |
| [Claude-Code-Usage-Monitor](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) | 7,009 | Python | Standalone dashboard | 2025-09 | ML prediction, unmaintained |
| [ccstatusline](https://github.com/sirmalloc/ccstatusline) | 5,421 | TypeScript | statusline | 03-16 | Highly customizable + themes |
| [CCometixLine](https://github.com/Haleclipse/CCometixLine) | 2,227 | Rust | statusline | 03-14 | High-performance binary |
| [claude-powerline](https://github.com/Owloops/claude-powerline) | 931 | TypeScript | statusline | 03-18 | vim powerline style |
| [kamranahmedse/claude-statusline](https://github.com/kamranahmedse/claude-statusline) | 726 | Shell | statusline | 03-10 | Minimalist |
| [claude-code-statusline](https://github.com/rz1989s/claude-code-statusline) | 397 | Shell | statusline | 03-14 | 4-line enhanced + themes |
| [claude-code-usage-bar](https://github.com/leeguooooo/claude-code-usage-bar) | 159 | Python | statusline | 2025-11 | burn rate + depletion prediction |
| [claudia-statusline](https://github.com/hagan/claudia-statusline) | 21 | Rust | statusline | 2026-01 | SQLite persistence + cloud sync |
| [felipeelias/claude-statusline](https://github.com/felipeelias/claude-statusline) | 2 | Go | statusline | 03-17 | Single binary, minimalist |
| claude-pace | 3 | Bash+jq | statusline | 03-19 | pace tracking, zero runtime deps |

Plus 6+ npm packages: ccstatusline, @owloops/claude-powerline, @illumin8ca/claude-statusline, @chongdashu/cc-statusline, @sponzig/cc-statusline, @this-dot/claude-code-context-status-line.

## Detailed Competitor Analysis

### ccusage (11,693 stars) - Overall Strongest

- Positioning: CLI usage analysis tool, statusline is a sub-feature
- Statusline display: model, session cost, today cost, 5h block remaining time, burn rate, context usage
- Tech: TypeScript, default offline mode (cached pricing data), no network latency
- Advantages: Largest user base, broad feature coverage, active maintenance
- Diff from claude-pace: ccusage's burn rate shows trends, no predictive alerts; requires Node.js runtime

### claude-hud (7,038 stars) - Pioneer

- Most features: context progress bar, rate limit usage, tool activity, subagent status, Todo progress, Git integration
- Usage API cache TTL 60s (success) / 15s (failure)
- Known issues: Cold start fails due to cold cache/API timeout (#214), 0-byte lock file permanent block (#220), Windows compatibility (#196)
- Not in awesome-claude-code list (29K stars, lists 5 statusline tools but excludes claude-hud)

### Claude-Code-Usage-Monitor (7,009 stars) - Unmaintained

- Standalone terminal dashboard (not embedded statusline), Python implementation
- Strongest prediction: P90 ML + burn rate, using past 192 hours of history
- HN: 245 points / 135 comments, but code quality criticized ("vibe-coding style", main file 1000+ lines)
- Last update 2025-09-14, no active maintenance

### ccstatusline (5,421 stars) - Customizable

- Positioned as "formatter", no API calls
- Powerline style, interactive TUI config, multiple themes
- npm distribution, performance determined by Node.js startup overhead

### CCometixLine (2,227 stars) - Rust Performance

- Git integration, model display, usage tracking, interactive TUI config
- Only Rust solution in awesome-claude-code
- Documentation lacks specific ms performance numbers

## Community Distribution Channels

| Channel | Stars | claude-pace Status |
|---------|------:|--------------------|
| [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 29,014 | Not listed |
| Anthropic official plugin directory | 12,653 | Zero statusline listings |

awesome-claude-code currently lists 5 statuslines: CCometixLine, ccstatusline, claude-code-statusline, claude-powerline, claudia-statusline.

## User Pain Points & Unmet Needs

### Core Pain Point: Quota Opacity

1. **Sudden limit hit with no warning** - $200/month Max users hit limit in 10-15 minutes, only see "usage limit reached" (The Register, 2026-01-05)
2. **Quota reset time invisible** - 3 independent issues on same day 2026-03-18 requesting this (#35747, #35672, #35827)
3. **5h + 7d dual window cognitive load** - Users confused about which limit they hit

### Official Stance

- **Explicitly rejected native token indicator**: issue #10593 marked "Not Planned" (2026-01-19), recommends ccusage
- **statusline stdin JSON doesn't expose quota fields**: session_used_percentage, weekly_used_percentage, resets_at all missing
- Third-party tools must workaround via Usage API or parse local JSONL files

### Other Requests

- Auto-resume task execution after limit hit (#18980, #26775, #35744)
- Push-based quota warning (alert at 80%) vs query-based (#35947)
- Cross-session cumulative usage tracking (#13891, #13892)

## Tech Trends

- **Migration from Node.js to lightweight runtimes**: Rust (CCometixLine, claudia-statusline), Go (felipeelias), Shell (kamranahmedse, rz1989s, claude-pace)
- **Zero-dep install as selling point**: Go single binary, Bash script curl one-line install
- **No public performance benchmarks**: No tool has published hyperfine or equivalent ms-level benchmark numbers

## User Feedback Analysis (2026-03-24补充)

### Cross-session Daily Cost Summary - Best Feedback

ccusage's core value is "one command to see costs" and "verify if monthly fee worth it". Multiple independent reviews consistently list "cost visualization" as primary reason for choosing ccusage.

### Context Progress Bar - Primary Install Motivation

Multiple independent sources agree: context bar is "install reason". SAP community author wrote "context bar alone is worth the install".

### Rate Limit 5h/7d Visualization - Second Biggest Need

After v2.1.80, stdin provides official data, all tools have equal opportunity, differentiation shifts from "have or not" to "accurate or not".

### Subagent Status Monitoring - Blog Hot, User Voting Weak

claude-hud's subagent monitoring listed as second value point by multiple blogs. But actual data doesn't support "strong demand" judgment:
- 6 subagent-related issues all 0 reactions
- All consecutive numbers, suspected maintainer or AI batch creation, not user-driven

### Burn Rate / Consumption Rate - Competitors Already Failed

ccusage's Live Blocks feature (real-time token consumption monitoring) formally removed due to accuracy issues (issue #782). Issue #288 (16 reactions) and #483 (11 reactions) documented persistent user complaints about "shows not at limit but actually hit".

### Zero Runtime Dependencies - Real Differentiator

ccusage statusline has severe process management bug (issue #459, 10 reactions, 17 comments): `bun x ccusage statusline` in hooks causes infinite process spawning, CPU 100%.

Multiple community authors explicitly list "reduce dependencies" as tool selection factor. Go/Rust single binary and pure Bash solutions' motivation includes this.

### Feature Creep is Explicitly Warned Anti-pattern

- Ovidiu (Substack): "When everything is highlighted, nothing is"
- ccusage's Live Blocks from feature to removal is a live case study.

## Contradictions & Uncertainties

1. **Subagent monitoring demand strength contradiction**: Blog authors highly rate vs GitHub issues 0 reactions. Possible explanation: Blog authors evaluate from feature completeness perspective, actual user voting reflects "most painful needs"
2. **ccusage statusline user stickiness vs bug severity contradiction**: Depended by multiple third parties (accuracy recognized), but most accuracy complaints. Possible: CLI reports accurate, statusline/live components inaccurate
3. **claude-hud stars jumped from 7,038 (3/19) to 11,842 (3/24)**: 4,804 stars in 5 days, consistent with Trending effect

## Competitor Feature Feedback Ranking

| Rank | Feature | Evidence Strength | Worth Doing |
|------|---------|-------------------|-------------|
| 1 | Cross-session daily cost summary | High (multi-source independent positive feedback) | Worth evaluating - but subscription users may not care about cost |
| 2 | Subagent/tool activity monitoring | Low (blog hot issue cold) | Not recommended - wait for CC stdin to expose related fields |
| 3 | Multi-device data sync | Low | Not recommended |
| 4 | Per-project grouped usage | Low | Not recommended |

## Conclusion

**More valuable direction is not "add features competitors have", but "make existing features most accurate and reliable".** ccusage's live blocks removed due to inaccuracy, claude-hud's 429 permanent warning bug, both show statusline competition focus shifted from "feature count" to "data accuracy and runtime reliability".