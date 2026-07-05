# Entity Signal Checklist

> Part of [entity-optimizer](../SKILL.md). See also: [knowledge-graph-guide.md](knowledge-graph-guide.md)

Work through signals by priority tier. Mark each: present/correct, incomplete, or absent.

## Priority 1: Foundation Signals (Must-Have)

### On-Site Structured Data
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 1 | Organization/Person schema on homepage | name, url, logo, description present |
| 2 | sameAs links to authoritative profiles | Wikipedia, Wikidata, LinkedIn, social |
| 3 | Consistent @id across all pages | Same @id on every page |
| 4 | About page with entity-rich content | First paragraph defines entity; founding date, key people, mission |
| 5 | Contact page with verifiable info | Physical address, phone, email matching directory listings |

### Key External Profiles
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 6 | Wikidata entry | Label, description, key properties, references |
| 7 | Google Business Profile (if applicable) | Claimed, verified, complete |
| 8 | LinkedIn page | Complete, matches entity name/description |
| 9 | CrunchBase profile (companies/products) | Description, founding info, key people |
| 10 | Primary industry directory listing | Listed with correct info |

### Branded Search Presence
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 11 | Branded search returns correct entity | Website #1; KP appears or SERP identifies entity |
| 12 | No disambiguation confusion | No other entity dominates results |
| 13 | Branded search volume exists | Measurable volume > 0 |

## Priority 2: Authority Signals (Should-Have)

### Knowledge Graph Depth
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 14 | Google Knowledge Panel present | Displayed with correct info |
| 15 | KP attributes complete | Key attributes filled (founded, CEO, location, industry) |
| 16 | KP image correct | Preferred image displayed |
| 17 | Wikipedia article (or notability path) | Article exists, or 3+ independent reliable sources available |
| 18 | Wikidata properties complete | 10+ properties with references |

### Third-Party Validation
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 19 | Authoritative media mentions | 3+ in recognized publications |
| 20 | Industry awards/recognitions | At least 1 verifiable |
| 21 | Co-citation with established entities | Appears in comparisons, listicles, roundups |
| 22 | Speaking/publications | Appears as speaker, author, or contributor |
| 23 | Third-party platform reviews | Reviews exist with reasonable volume |

### Content Authority
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 24 | Topical content depth | 10+ pages covering target topics |
| 25 | Author pages with credentials | Author schema, credentials, sameAs |
| 26 | Original research/data | At least 1 piece cited by others |
| 27 | Entity mentioned naturally in content | Name appears contextually, not just header/footer |

## Priority 3: AI-Specific Signals (Must-Have for GEO)

### AI Recognition
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 28 | ChatGPT recognizes entity | Correct description returned |
| 29 | Perplexity recognizes entity | Correct description with citations |
| 30 | Google AI Overview mentions entity | Entity appears in AI overview |
| 31 | AI description accurate | No factual errors |
| 32 | AI associates correct topics | Correct topic associations |

### AI Optimization
| # | Signal | Pass Criteria |
|---|--------|---------------|
| 33 | Quotable entity definition in first paragraph | Clear, factual, self-contained |
| 34 | Factual claims verifiable | All claims cross-referenceable |
| 35 | Entity name used consistently | Identical format everywhere |
| 36 | Content crawlable by AI systems | Not blocking GPTBot, ClaudeBot (unless intentional) |
| 37 | Fresh information available | Key pages updated within 6 months |

## Priority 4: Advanced Signals (Nice-to-Have)

| # | Signal | Pass Criteria |
|---|--------|---------------|
| 38 | Multi-language Wikidata entries | Labels in target market languages |
| 39 | Google KG ID known | Entity has kg: identifier |
| 40 | Social profiles bidirectionally linked | Website <-> social verified both directions |
| 41 | Consistent entity description across social | Same core description, adapted for platform |
| 42 | Strong homepage backlink profile | DR/DA above industry median |
| 43 | Branded anchor text in backlinks | Entity name appears naturally in anchors |

## Priority Action Matrix

| Current State | Focus Area | Timeline |
|--------------|-----------|----------|
| Most P1 signals absent | P1 foundation only | 2-4 weeks |
| P1 mostly done, P2 mixed | P2 authority signals | 1-2 months |
| P1-2 mostly done | P3 AI-specific | 2-3 months |
| P1-3 mostly done | Selective P4 | Ongoing |
| All tiers mostly done | Maintenance + quarterly re-audit | Quarterly |

---

## Report & Action Plan Template

```markdown
## Entity Optimization Report
- **Entity**: [name] | **Type**: [type] | **Date**: [date]

### Signal Category Summary
| Category | Status | Key Findings |
|----------|--------|-------------|
| Structured Data | Strong / Gaps / Missing | [findings] |
| Knowledge Base | Strong / Gaps / Missing | [findings] |
| Consistency (NAP+E) | Strong / Gaps / Missing | [findings] |
| Third-Party | Strong / Gaps / Missing | [findings] |
| AI-Specific | Strong / Gaps / Missing | [findings] |

### Top 5 Priority Actions
1. **[Signal]** — [action] | Impact: [H/M] | Effort: [L/M/H]
2-5. [Same format]

### Roadmap
**Week 1-2 (Foundation)**: Schema, sameAs, NAP+E consistency, About page
**Month 1 (Knowledge Bases)**: Wikidata, CrunchBase, directories, Wikipedia notability path
**Month 2-3 (Authority)**: Authoritative mentions, co-citation, topical clusters, PR
**Ongoing (AI)**: Quarterly AI testing, update factual claims, monitor AI output
```

## Tips for Success

1. **Start with Wikidata** — most influential editable KB; often triggers KP creation within weeks
2. **sameAs is your most powerful Schema.org property** — always include Wikidata URL first
3. **Test AI recognition before and after** — query ChatGPT, Claude, Perplexity, Google AI Overview
4. **Entity signals compound** — 5 weak signals together > 1 strong signal alone
5. **Consistency beats completeness** — consistent name across 10 platforms > perfect profile on 2
6. **Don't neglect disambiguation** — if name is shared, disambiguation is first priority
