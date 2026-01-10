---
name: codebase-explorer
description: Explore and understand the Empathy Ledger codebase architecture, data flows, database schema, services, and how components connect. Use when you need to understand where things are, how data flows, or how different parts of the system relate to each other.
---

# Codebase Explorer Skill

Explore and document the Empathy Ledger codebase architecture, data flows, and system relationships.

## Instructions

When this skill is invoked, help the user understand:

1. **Database Schema** - Tables, relationships, migrations
2. **Data Flow** - Supabase → Services → API Routes → Components
3. **Service Layer** - Business logic patterns
4. **API Routes** - Endpoints and their purposes
5. **Type Definitions** - Where to find types for each domain
6. **Multi-Tenant Architecture** - How tenant isolation works

## Quick Reference Files

### Database & Types
| Domain | Types File | Key Tables |
|--------|-----------|-----------|
| Users/Profiles | `src/types/database/user-profile.ts` | profiles, profile_settings |
| Organizations | `src/types/database/organization-tenant.ts` | organisations, organization_members, tenants |
| Projects | `src/types/database/project-management.ts` | projects, project_participants |
| Stories/Content | `src/types/database/content-media.ts` | stories, transcripts, media_assets |
| Distribution | `src/types/database/story-ownership.ts` | story_distributions, consent_proofs |
| Cultural Safety | `src/types/database/cultural-sensitivity.ts` | cultural_safety_moderation |
| Locations | `src/types/database/location-events.ts` | locations, events |
| Analysis | `src/types/database/analysis-support.ts` | transcript_analysis, themes, quotes |

### Supabase Clients
| Client | File | Usage |
|--------|------|-------|
| Browser | `src/lib/supabase/client.ts` | React components |
| Server SSR | `src/lib/supabase/client-ssr.ts` | API routes, server components |
| Service Role | `src/lib/supabase/service-role-client.ts` | Admin operations (bypasses RLS) |

### Core Services (src/lib/services/)
| Service | Purpose |
|---------|---------|
| consent.service.ts | GDPR consent proof system |
| distribution.service.ts | Story distribution with policy enforcement |
| revocation.service.ts | Revoke distributed content |
| embed.service.ts | Embedded story tokens |
| organization.service.ts | Org management and metrics |
| audit.service.ts | Compliance logging |
| gdpr.service.ts | Data privacy operations |
| webhook.service.ts | Event distribution to partners |

### API Routes (src/app/api/)
| Route | Purpose |
|-------|---------|
| /api/stories | Story CRUD |
| /api/stories/[id]/consent | Consent management |
| /api/stories/[id]/distributions | Distribution tracking |
| /api/stories/[id]/revoke | Revocation |
| /api/storytellers | Storyteller profiles |
| /api/projects | Project management |
| /api/projects/[id]/transcripts | Transcript access |
| /api/embed/stories/[id] | Embedded content |
| /api/admin/* | Admin operations |

## Data Flow Pattern

```
User Action (React Component)
    ↓
fetch('/api/endpoint')
    ↓
API Route (src/app/api/*)
    ↓
Service Layer (src/lib/services/*)
    ↓
Supabase Client (RLS enforced)
    ↓
PostgreSQL (supabase/migrations/*)
```

## Multi-Tenant Isolation

Every query filters by tenant:
```typescript
// In API route
const profile = await supabase.from('profiles').select('tenant_id').eq('id', user.id).single()
query = query.eq('tenant_id', profile.tenant_id)
```

## Role Hierarchy (highest → lowest)
1. elder (100) - Cultural authority
2. cultural_keeper (90) - Knowledge preservation
3. admin (70) - System management
4. project_leader (60) - Project management
5. storyteller (50) - Content creation
6. community_member (40) - Participant
7. guest (10) - Read-only

## Common Exploration Commands

```bash
# Find all services
ls src/lib/services/

# Find API routes for a feature
ls src/app/api/stories/

# Check database types
cat src/types/database/index.ts

# View latest migration
ls -la supabase/migrations/ | tail -5

# Find where a table is used
grep -r "from('stories')" src/

# Find component for a feature
ls src/components/stories/
```

## Output Format

When exploring, provide:
1. **File locations** with clickable links
2. **Key relationships** between tables/services
3. **Code snippets** showing patterns
4. **Diagrams** using ASCII or markdown tables

## When to Use This Skill

Invoke when:
- Asking "where is X located?"
- Asking "how does X connect to Y?"
- Needing to understand data relationships
- Looking for the right service or API route
- Understanding the database schema
- Finding component or type definitions

## Reference Documentation

For comprehensive documentation with full code examples, see:
- [ARCHITECTURE_REFERENCE.md](../../../docs/ARCHITECTURE_REFERENCE.md) - Complete system documentation

---

**Trigger:** User asks about codebase structure, data flow, or "how does X connect to Y"
