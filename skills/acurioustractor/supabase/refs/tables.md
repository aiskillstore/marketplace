# Database Tables Reference

## Core Tables

### Identity & Access
| Table | Purpose |
|-------|---------|
| `tenants` | Top-level multi-tenant isolation |
| `profiles` | User accounts (syncs with auth.users) |
| `organisations` | Community groups with tier/policy |
| `organization_members` | User ↔ Org membership |
| `storytellers` | Storyteller personas (canonical source) |

### Content
| Table | Purpose |
|-------|---------|
| `stories` | Core storytelling content |
| `transcripts` | Audio/text transcriptions |
| `media_assets` | Images, videos, audio |
| `extracted_quotes` | AI-extracted quotes |

### Analysis
| Table | Purpose |
|-------|---------|
| `transcript_analysis_results` | Versioned AI analysis |
| `narrative_themes` | AI-extracted themes |
| `story_themes` | Story-theme junction |
| `knowledge_chunks` | RAG vector embeddings |

### Cultural Safety
| Table | Purpose |
|-------|---------|
| `elder_review_queue` | Elder approval workflow |
| `cultural_protocols` | Community protocols |
| `consent_change_log` | GDPR audit trail |

## Key Relationships

```
profiles → storytellers → stories → transcripts
                               ↓
                    transcript_analysis_results
                               ↓
                    narrative_themes + extracted_quotes
```

## Multi-Tenant Pattern

All tables have:
- `tenant_id UUID REFERENCES tenants(id)`
- RLS policies enforcing tenant isolation

## Common Queries

### Get storyteller with stories
```sql
SELECT st.*, COUNT(s.id) as story_count
FROM storytellers st
LEFT JOIN stories s ON s.storyteller_id = st.id
WHERE st.id = 'uuid'
GROUP BY st.id;
```

### Get stories with themes
```sql
SELECT s.*, array_agg(nt.theme_name) as theme_names
FROM stories s
LEFT JOIN story_themes st ON st.story_id = s.id
LEFT JOIN narrative_themes nt ON nt.id = st.theme_id
WHERE s.status = 'published'
GROUP BY s.id;
```

### Theme frequency
```sql
SELECT unnest(cultural_themes) as theme, COUNT(*)
FROM stories WHERE status = 'published'
GROUP BY theme ORDER BY count DESC;
```
