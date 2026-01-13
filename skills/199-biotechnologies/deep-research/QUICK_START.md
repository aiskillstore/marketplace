# Deep Research Skill - Quick Start Guide

## What is This?

A comprehensive research engine for Claude Code that **matches and exceeds** Claude Desktop's "Advanced Research" feature. It conducts enterprise-grade deep research with extended reasoning, multi-source synthesis, and citation-backed reports.

## How to Use

### Simple Invocation (Recommended)

Just ask Claude Code to use deep research:

```
Use deep research to analyze the current state of AI agent frameworks in 2025
```

```
Deep research: Should we migrate from PostgreSQL to Supabase?
```

```
Use deep research in ultradeep mode to review recent advances in longevity science
```

### Direct CLI Usage

```bash
# Standard research (6 phases, ~5-10 minutes)
python3 ~/.claude/skills/deep-research/research_engine.py \
  --query "Your research question" \
  --mode standard

# Deep research (8 phases, ~10-20 minutes)
python3 ~/.claude/skills/deep-research/research_engine.py \
  --query "Your research question" \
  --mode deep

# Quick research (3 phases, ~2-5 minutes)
python3 ~/.claude/skills/deep-research/research_engine.py \
  --query "Your research question" \
  --mode quick

# Ultra-deep research (8+ phases, ~20-45 minutes)
python3 ~/.claude/skills/deep-research/research_engine.py \
  --query "Your research question" \
  --mode ultradeep
```

## Research Modes Explained

| Mode | Phases | Time | Use When |
|------|--------|------|----------|
| **Quick** | 3 | 2-5 min | Initial exploration, simple questions |
| **Standard** | 6 | 5-10 min | Most research needs (default) |
| **Deep** | 8 | 10-20 min | Complex topics, important decisions |
| **UltraDeep** | 8+ | 20-45 min | Critical analysis, comprehensive reports |

## What You Get

Every research report includes:

- **Executive Summary** - Key findings in 3-5 bullets
- **Detailed Analysis** - With full citations [1], [2], [3]
- **Synthesis & Insights** - Novel insights beyond sources
- **Limitations & Caveats** - What's uncertain or missing
- **Recommendations** - Actionable next steps
- **Full Bibliography** - All sources with credibility scores
- **Methodology Appendix** - How research was conducted

## Output Location

All research is saved to:
```
~/.claude/research_output/
```

Format: `research_report_YYYYMMDD_HHMMSS.md`

## Features That Beat Claude Desktop Research

✅ **8-Phase Pipeline** - More thorough than Claude Desktop's approach
✅ **Multiple Research Modes** - Choose depth vs speed
✅ **Source Credibility Scoring** - Evaluates each source (0-100 score)
✅ **Graph-of-Thoughts** - Non-linear exploration with branching reasoning
✅ **Citation Management** - Automatic tracking and bibliography generation
✅ **Critique Phase** - Built-in red-team analysis of findings
✅ **Refine Phase** - Addresses gaps before finalizing
✅ **Local File Integration** - Can search your codebase/docs
✅ **Code Execution** - Can run analyses and validations

## Example Use Cases

### Technology Evaluation
```
Use deep research to compare Next.js 15 vs Remix vs Astro for my project
```

### Market Analysis
```
Deep research: What are the key trends in longevity biotech funding 2023-2025?
```

### Technical Decision
```
Use deep research to help me choose between Auth0, Clerk, and Supabase Auth
```

### Scientific Review
```
Use deep research in ultradeep mode to summarize senolytics research progress
```

### Competitive Intelligence
```
Deep research: Who are the top 5 competitors in the AI code assistant space?
```

## Quality Standards

Every report guarantees:
- ✅ 10+ distinct sources (unless highly specialized topic)
- ✅ 3+ source verification for major claims
- ✅ Full citation tracking
- ✅ Credibility assessment for each source
- ✅ Limitations documented
- ✅ Methodology explained

## Tips for Best Results

1. **Be Specific** - "Compare X vs Y for use case Z" is better than "Tell me about X"
2. **State Your Goal** - "Help me decide..." vs "Give me an overview..."
3. **Choose Right Mode** - Use Quick for exploration, Deep for decisions
4. **Check Scope First** - Review Phase 1 output to ensure on track
5. **Use Citations** - Drill deeper by asking about specific sources [1], [2], etc.

## Architecture

```
deep-research/
├── SKILL.md                 # Main skill definition (11KB)
├── research_engine.py       # Core engine (16KB)
├── utils/
│   ├── citation_manager.py # Citation tracking (6KB)
│   └── source_evaluator.py # Credibility scoring (8KB)
├── README.md               # Full documentation
├── QUICK_START.md          # This guide
└── requirements.txt        # No external deps needed!
```

## No Dependencies Required!

The skill uses only Python standard library - no pip install needed for basic usage.

## Version

**v1.0** - Released 2025-11-04

Built to match and exceed Claude Desktop's Advanced Research feature.

---

**Ready to use?** Just type:
```
Use deep research to [your question here]
```

Claude Code will automatically load this skill and execute the research pipeline!
