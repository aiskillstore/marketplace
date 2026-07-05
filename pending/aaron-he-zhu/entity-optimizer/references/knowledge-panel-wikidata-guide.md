# Knowledge Panel & Wikidata Optimization Guide

## Knowledge Panel Optimization

### Claiming and Editing
1. **Google Knowledge Panel**: Claim via Google's verification (search entity -> "Claim this knowledge panel")
2. **Bing Knowledge Panel**: Driven by Wikidata and LinkedIn -- update those sources
3. **AI Knowledge**: Driven by training data -- ensure authoritative sources describe entity correctly

### Common Issues
| Issue | Root Cause | Fix |
|-------|-----------|-----|
| No panel | Not in Knowledge Graph | Build Wikidata + structured data + authoritative mentions |
| Wrong image | Sourced from incorrect page | Update Wikidata image; ensure preferred image on About page and social |
| Wrong description | Pulled from wrong source | Edit Wikidata description; ensure About page first paragraph is clear |
| Missing attributes | Incomplete structured data | Add to Schema.org and Wikidata |
| Wrong entity | Disambiguation failure | Strengthen unique signals; add qualifiers; resolve Wikidata disambiguation |
| Outdated info | Source data not updated | Update Wikidata, About page, all profiles |

## Wikidata Best Practices

### Creating an Entry
1. **Check notability**: at least one authoritative reference
2. **Create item**: label, description, aliases in relevant languages
3. **Add statements**: instance of, website, social links, founding date, founders, industry
4. **Add identifiers**: P856, social media IDs, CrunchBase ID, ISNI, VIAF
5. **Add references**: every statement needs an authoritative source

**COI Note**: Wikipedia prohibits self-editing. Focus on building notability through independent sources. Use Requested Articles process for Wikipedia involvement.

### Key Properties by Entity Type
| Property | Code | Person | Org | Brand | Product |
|----------|------|:------:|:---:|:-----:|:-------:|
| instance of | P31 | human | org type | brand | product type |
| official website | P856 | yes | yes | yes | yes |
| occupation/industry | P106/P452 | yes | yes | -- | -- |
| founded by | P112 | -- | yes | yes | -- |
| inception | P571 | -- | yes | yes | yes |
| country | P17 | yes | yes | -- | -- |
| social media | various | yes | yes | yes | yes |
| employer | P108 | yes | -- | -- | -- |
| developer | P178 | -- | -- | -- | yes |

## AI Entity Optimization

### Resolution Pipeline
User query -> Entity extraction -> Entity resolution -> Knowledge retrieval -> Answer generation

### Signals AI Systems Use
| Signal Type | How to Optimize |
|-------------|-----------------|
| Training data presence | Get mentioned in high-quality, widely-crawled sources |
| Retrieval augmentation | Strong SEO for branded queries |
| Structured data | Complete Wikidata + Schema.org |
| Contextual co-occurrence | Build consistent topic associations |
| Source authority | Get mentioned by authoritative sources |
| Recency | Keep all entity profiles and content updated |

### Entity-Specific GEO Tactics
1. **Define clearly**: About page first paragraph should be AI-quotable
2. **Be consistent**: Identical description across all platforms
3. **Build associations**: Content connecting entity to target topics
4. **Earn mentions**: Third-party mentions > self-description
5. **Stay current**: Outdated info causes AI to lose confidence
