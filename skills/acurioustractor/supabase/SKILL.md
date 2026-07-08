---
name: supabase
description: Navigate Supabase database tables, relationships, and query patterns. Schema reference for Empathy Ledger.
---

# Supabase Database

Navigate and query the Empathy Ledger Supabase database.

## When to Use
- Understanding table relationships
- Writing database queries
- Finding the right data source
- Checking schema structure

## Quick Relationship Map
```
tenants
   └── profiles → storytellers → stories → transcripts
                                    ↓
                        transcript_analysis_results
                                    ↓
                        narrative_themes + extracted_quotes
```

## Core Tables

### Storytelling
| Table | Purpose |
|-------|---------|
| `storytellers` | Storyteller personas (canonical) |
| `stories` | Core content |
| `transcripts` | Audio/text transcriptions |

### Analysis
| Table | Purpose |
|-------|---------|
| `transcript_analysis_results` | Versioned AI analysis |
| `narrative_themes` | AI-extracted themes |
| `knowledge_chunks` | RAG embeddings (22k+) |

### Multi-Tenant
| Table | Purpose |
|-------|---------|
| `tenants` | Top-level isolation |
| `profiles` | User accounts |
| `organisations` | Community groups |

## Common Queries
```sql
-- Storyteller with story count
SELECT st.*, COUNT(s.id) as story_count
FROM storytellers st
LEFT JOIN stories s ON s.storyteller_id = st.id
GROUP BY st.id;

-- Stories by theme
SELECT * FROM stories
WHERE 'healing' = ANY(cultural_themes);

-- Theme frequency
SELECT unnest(cultural_themes) as theme, COUNT(*)
FROM stories WHERE status = 'published'
GROUP BY theme ORDER BY count DESC;
```

## Reference Files
| Topic | File |
|-------|------|
| Full table list | `refs/tables.md` |
| Relationship diagram | `refs/relationship-diagram.md` |

## Related Skills
- `supabase-connection` - Database clients
- `supabase-deployment` - Migrations
- `database-navigator` - Schema exploration
