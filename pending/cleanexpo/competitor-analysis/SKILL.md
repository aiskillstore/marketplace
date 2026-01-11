---
name: competitor-analysis
description: Analyze competitor website structures, messaging patterns, and unique features. Use when researching competition, identifying gaps, or informing content strategy.
allowed-tools: Read, Write, mcp__playwright__browser_snapshot, mcp__playwright__browser_navigate, mcp__exa__web_search_exa
---

# Competitor Analysis Skill

## Purpose
Analyze top competitors page-by-page to understand their structure, messaging, and features for gap analysis.

## Analysis Framework

### Pages to Analyze
1. **Homepage** - First impression, main value prop
2. **About** - Story, team, credentials
3. **Services/Products** - Offering structure
4. **Pricing** - Pricing model and presentation
5. **Contact** - Conversion points
6. **Blog/Resources** - Content strategy

### Per-Page Breakdown
For each page, extract:

#### 1. Section Structure
Order of sections from top to bottom:
- Hero
- Problem statement
- Value propositions
- Social proof
- Process/How it works
- Pricing teaser
- FAQ
- CTA

#### 2. Headlines & Subheadlines
Capture the exact wording used:
- Main headlines
- Section headlines
- Supporting copy

#### 3. Trust Signals
What builds credibility:
- Review counts
- Star ratings
- Certifications
- Logos (clients, partners)
- Awards
- Guarantees

#### 4. CTAs
Call-to-action patterns:
- Button text
- Placement
- Urgency language
- Form fields

#### 5. Unique Features
What they have that others don't:
- Interactive tools
- Calculators
- Chat widgets
- Video content
- Custom features

## Competitor Ranking

### National Leader
- Highest authority sites
- Largest market share
- Reference for industry best practices

### Regional Top
- Strong in specific markets
- May have niche advantages

### Local Competitor
- Direct competition in service area
- Similar size and offering

### Emerging
- New entrants with interesting approaches
- Potential disruptors

## Gap Analysis Output
After analyzing competitors, identify:

1. **Missing Features** - What do they have that we don't?
2. **Missing Trust Signals** - What credibility markers are we lacking?
3. **Messaging Gaps** - What are they saying that we're not?
4. **Recommendations** - Prioritized action items

## When to Use
- Before website redesign
- When entering new market
- For quarterly competitive review
- Before pricing changes
- When creating new pages

## Integration Points
- `src/lib/agents/competitor-analyzer.ts` - Main agent
- `competitor_analysis` table - Storage
- ConversionCopywritingEngine - Consumer

## Output Format
```json
{
  "competitor": "Competitor Name",
  "url": "https://competitor.com",
  "rank": "national_leader",
  "page_structures": {
    "homepage": {
      "sections": [...],
      "headlines": [...],
      "ctas": [...]
    }
  },
  "unique_features": [...],
  "trust_signals": [...],
  "messaging_patterns": {...}
}
```

## Quality Rules
1. **Analyze, don't copy** - Learn patterns, don't plagiarize
2. **Focus on structure** - Why it works, not just what it is
3. **Date your analysis** - Websites change frequently
4. **Note what's missing** - Gaps are opportunities
5. **Prioritize insights** - Not everything matters equally
