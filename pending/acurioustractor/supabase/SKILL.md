---
name: supabase
description: Navigate Supabase database tables, relationships, and query patterns. Use when you need to understand how tables connect, write queries, or find the right data source.
---

# Supabase Database Skill

Navigate and query the Empathy Ledger Supabase database with confidence.

## Database Relationship Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TENANTS (top-level)                            │
│                                    │                                        │
│    ┌───────────────────────────────┼───────────────────────────────┐        │
│    │                               │                               │        │
│    ▼                               ▼                               ▼        │
│ ┌──────────────┐           ┌──────────────┐           ┌──────────────────┐  │
│ │ organisations │◄──────────│   profiles   │──────────►│  tenant_members  │  │
│ └──────────────┘           └──────────────┘           └──────────────────┘  │
│        │                          │                                         │
│        │                          │ is_storyteller                          │
│        ▼                          ▼                                         │
│ ┌──────────────┐           ┌──────────────┐                                 │
│ │   projects   │◄──────────│    stories   │                                 │
│ └──────────────┘           └──────────────┘                                 │
│        │                          │                                         │
│        │                          ├────────────────────┐                    │
│        ▼                          ▼                    ▼                    │
│ ┌──────────────┐           ┌──────────────┐    ┌──────────────┐             │
│ │ transcripts  │           │media_assets  │    │story_distribs│             │
│ └──────────────┘           └──────────────┘    └──────────────┘             │
│        │                          │                    │                    │
│        │                          │                    ▼                    │
│        ▼                          ▼             ┌──────────────┐            │
│ ┌──────────────┐           ┌──────────────┐    │ embed_tokens │            │
│ │ key_quotes[] │           │media_usage   │    └──────────────┘            │
│ │ themes[]     │           │_tracking     │                                 │
│ │ ai_summary   │           └──────────────┘                                 │
│ └──────────────┘                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Complete Table Inventory

**Live Supabase:** 165 objects (153 tables, 7 views, 3 partitions, 2 system)
**Migration-defined:** 71 tables
**With TypeScript Types:** 35 tables

**See also:** [DATABASE_ALIGNMENT_AUDIT.md](../../../docs/DATABASE_ALIGNMENT_AUDIT.md)

> ⚠️ **Schema Drift Alert**: ~80 tables exist in Supabase but have no migration files.
> Use `npx supabase gen types typescript --local` to generate accurate types.

### 1. Identity & Access (12 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `tenants` | Top-level multi-tenant isolation | ✅ |
| `profiles` | User accounts (syncs with auth.users) | ✅ |
| `organisations` | Community groups with tier/policy | ✅ |
| `organization_members` | User ↔ Org membership | ✅ |
| `organization_roles` | RBAC roles within orgs | ⚠️ |
| `organization_invitations` | Pending invites | ⚠️ |
| `tenant_members` | User ↔ Tenant membership | ✅ |
| `profile_organizations` | Profile-org join | ✅ |
| `profile_locations` | User locations | ✅ |
| `profile_projects` | User-project join | ✅ |
| `user_sessions` | Session tracking | ✅ |
| `user_reports` | User reports | ✅ |

### 2. Projects & Context (9 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `projects` | Story collections | ✅ |
| `project_participants` | Project members | ✅ |
| `project_contexts` | AI-extracted project context | ⚠️ |
| `organization_contexts` | AI-extracted org context | ⚠️ |
| `project_profiles` | Extended project metadata | ⚠️ |
| `project_seed_interviews` | Seed interview data | ⚠️ |
| `project_analyses` | Cached AI analyses | ⚠️ |
| `seed_interview_templates` | Interview templates | ⚠️ |
| `development_plans` | User development plans | ✅ |

### 3. Stories & Content (10 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `stories` | Core storytelling content | ✅ |
| `transcripts` | Audio/text transcriptions | ✅ |
| `media_assets` | Images, videos, audio | ✅ |
| `media_usage_tracking` | Media access tracking | ✅ |
| `extracted_quotes` | AI-extracted quotes | ✅ |
| `transcription_jobs` | Transcription queue | ⚠️ |
| `media_import_sessions` | Bulk import tracking | ⚠️ |
| `title_suggestions` | AI title suggestions | ⚠️ |
| `galleries` | Photo galleries | ✅ |
| `gallery_photos` | Gallery items | ✅ |

### 4. Distribution & Syndication (11 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `story_distributions` | External platform tracking | ✅ |
| `story_access_tokens` | Ephemeral share links (revocable, time-limited) | ✅ |
| `embed_tokens` | Secure embed tokens | ✅ |
| `story_syndication_consent` | Partner consent records | ⚠️ |
| `external_applications` | Partner apps registry | ⚠️ |
| `story_access_log` | External access log | ⚠️ |
| `webhook_subscriptions` | Partner webhooks | ⚠️ |
| `webhook_delivery_log` | Webhook attempts | ⚠️ |
| `consent_change_log` | Consent audit trail | ⚠️ |
| `consent_proofs` | GDPR consent proofs | ⚠️ |
| `story_review_invitations` | Storyteller review links | ⚠️ |

### 5. Partner Portal (6 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `partner_projects` | Partner curated projects | ⚠️ |
| `story_syndication_requests` | Content requests | ⚠️ |
| `partner_messages` | Partner-storyteller messages | ⚠️ |
| `partner_team_members` | Partner team access | ⚠️ |
| `partner_analytics_daily` | Partner analytics | ⚠️ |
| `partner_message_templates` | Message templates | ⚠️ |

### 6. Analytics & Insights (17 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `storyteller_analytics` | Aggregated storyteller stats | ⚠️ |
| `narrative_themes` | Platform-wide themes | ⚠️ |
| `storyteller_themes` | Per-storyteller themes | ⚠️ |
| `storyteller_quotes` | Impactful quotes | ⚠️ |
| `storyteller_connections` | Network connections | ⚠️ |
| `storyteller_demographics` | Demographics data | ⚠️ |
| `storyteller_recommendations` | AI recommendations | ❌ ORPHANED |
| `storyteller_dashboard_config` | Dashboard prefs | ⚠️ |
| `storyteller_milestones` | Achievements | ⚠️ |
| `storyteller_engagement` | Engagement metrics | ⚠️ |
| `storyteller_impact_metrics` | Impact tracking | ⚠️ |
| `cross_narrative_insights` | Cross-story insights | ❌ ORPHANED |
| `cross_sector_insights` | Sector analysis | ⚠️ |
| `geographic_impact_patterns` | Geographic patterns | ❌ ORPHANED |
| `theme_evolution_tracking` | Theme trends | ⚠️ |
| `analytics_processing_jobs` | Analytics job queue | ❌ ORPHANED |
| `platform_analytics` | Platform-wide stats | ⚠️ |

### 7. Engagement Tracking (2 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `story_engagement_events` | Per-view events | ⚠️ |
| `story_engagement_daily` | Daily aggregates | ⚠️ |

### 8. AI & Safety (9 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `ai_usage_events` | AI cost/usage tracking | ⚠️ |
| `tenant_ai_policies` | Per-tenant AI limits | ⚠️ |
| `ai_agent_registry` | AI agent configs | ⚠️ |
| `ai_usage_daily` | Daily AI aggregates | ⚠️ |
| `elder_review_queue` | Elder review workflow | ⚠️ |
| `moderation_results` | Moderation decisions | ⚠️ |
| `moderation_appeals` | Appeal requests | ⚠️ |
| `ai_moderation_logs` | AI moderation log | ⚠️ |
| `ai_safety_logs` | Safety check log | ⚠️ |

### 9. Admin & System (8 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `audit_logs` | Compliance audit trail | ✅ |
| `deletion_requests` | GDPR deletion queue | ✅ |
| `activity_log` | Admin activity feed | ⚠️ |
| `notifications` | In-app notifications | ⚠️ |
| `admin_messages` | Admin broadcasts | ⚠️ |
| `message_recipients` | Message delivery | ⚠️ |
| `ai_analysis_jobs` | AI job queue | ⚠️ |
| `platform_stats_cache` | Cached platform stats | ⚠️ |

### 10. World Tour (3 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `tour_requests` | Tour visit requests | ⚠️ |
| `tour_stops` | Completed tour stops | ⚠️ |
| `dream_organizations` | Target organizations | ⚠️ |

### 11. Cultural & Impact (5 tables)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `cultural_protocols` | Cultural guidelines | ✅ |
| `cultural_tags` | Cultural tags | ✅ |
| `community_impact_insights` | Impact moments | ✅ |
| `community_impact_metrics` | Aggregated impact | ✅ |
| `live_community_narratives` | Auto-generated narratives | ✅ |
| `locations` | Geographic locations | ✅ |
| `events` | Event tracking | ✅ |

### 12. Additional Tables (in Supabase, no migrations)

These tables exist in live Supabase but have no migration files:

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `activities` | Activity tracking (52 columns!) | ❌ |
| `outcomes` | Outcome tracking (38 columns) | ❌ |
| `annual_reports` | Annual reports | ❌ |
| `annual_report_stories` | Report-story links | ❌ |
| `report_sections` | Report sections | ❌ |
| `report_templates` | Report templates | ❌ |
| `blog_posts` | Blog content | ❌ |
| `testimonials` | User testimonials | ❌ |
| `services` | Service definitions | ❌ |
| `service_impact` | Service impact metrics | ❌ |
| `partners` | Partner organizations | ❌ |
| `team_members` | Team member profiles | ❌ |

### 13. Photo System (in Supabase only)

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `photo_analytics` | Photo view tracking | ❌ |
| `photo_faces` | Face detection data | ❌ |
| `photo_galleries` | Photo galleries | ❌ |
| `photo_gallery_items` | Gallery items | ❌ |
| `photo_locations` | Photo locations | ❌ |
| `photo_memories` | Photo memories | ❌ |
| `photo_organizations` | Photo org links | ❌ |
| `photo_projects` | Photo project links | ❌ |
| `photo_storytellers` | Photo storyteller links | ❌ |
| `photo_tags` | Photo tags | ❌ |

### 14. Legacy/Sync Tables

| Table | Purpose | Has Types |
|-------|---------|-----------|
| `empathy_entries` | Legacy empathy data | ❌ |
| `empathy_sync_log` | Sync tracking | ❌ |
| `syndicated_stories` | Syndicated content | ❌ |
| `scraped_services` | Web scraper data | ❌ |
| `scraper_health_metrics` | Scraper health | ❌ |
| `scraping_metadata` | Scraper metadata | ❌ |

---

## ⚠️ Spelling Note

**Supabase uses `organizations` (US spelling)**
**TypeScript types use `organisations` (UK spelling)**

When querying, use the Supabase spelling. The types may need updating.

## Foreign Key Relationships

### Stories Table (Central Hub)
```typescript
stories.storyteller_id  → profiles.id       // Who told this story
stories.author_id       → profiles.id       // Who authored/recorded
stories.project_id      → projects.id       // Which project it belongs to
stories.organization_id → organisations.id  // Which org owns it
stories.tenant_id       → tenants.id        // Tenant isolation
stories.featured_media_id → media_assets.id // Cover image
```

### Transcripts Table
```typescript
transcripts.storyteller_id → profiles.id   // Who is speaking
transcripts.tenant_id      → tenants.id    // Tenant isolation
// Note: stories can link to transcripts via content or transcript_id
```

### Organization Hierarchy
```typescript
tenants.organization_id        → organisations.id  // Primary org for tenant
organisations.tenant_id        → tenants.id        // Tenant ownership
organization_members.profile_id     → profiles.id      // User
organization_members.organization_id → organisations.id // Org
```

### Distribution Chain
```typescript
story_distributions.story_id     → stories.id  // Which story
story_distributions.tenant_id    → tenants.id  // Tenant isolation
embed_tokens.story_id            → stories.id  // Which story
embed_tokens.distribution_id     → story_distributions.id  // Parent distribution
story_access_tokens.story_id     → stories.id  // Which story (ephemeral share links)
story_access_tokens.created_by   → profiles.id // Who created the link
story_access_tokens.tenant_id    → tenants.id  // Tenant isolation
```

## Type Files by Domain

| Domain | Type File | Tables Covered |
|--------|-----------|----------------|
| Users | `src/types/database/user-profile.ts` | profiles, profile_locations, profile_organizations, user_sessions |
| Orgs | `src/types/database/organization-tenant.ts` | organisations, organization_members, tenants, tenant_members |
| Projects | `src/types/database/project-management.ts` | projects, project_participants |
| Content | `src/types/database/content-media.ts` | stories, transcripts, media_assets, extracted_quotes |
| Distribution | `src/types/database/story-ownership.ts` | story_distributions, embed_tokens, audit_logs, deletion_requests |
| Share Control | `src/types/database/story-access-tokens.ts` | story_access_tokens |
| Cultural | `src/types/database/cultural-sensitivity.ts` | cultural_safety_moderation |
| Locations | `src/types/database/location-events.ts` | locations, events |
| Analysis | `src/types/database/analysis-support.ts` | transcript_analysis, themes, quotes |

## Supabase Client Usage

### Client Types
```typescript
// Browser client (uses cookies, respects RLS)
import { createSupabaseBrowserClient } from '@/lib/supabase/client'
const supabase = createSupabaseBrowserClient()

// Server SSR client (for API routes, server components)
import { createSupabaseServerClient } from '@/lib/supabase/client-ssr'
const supabase = createSupabaseServerClient()

// Service role client (bypasses RLS - admin only!)
import { createSupabaseServiceClient } from '@/lib/supabase/service-role-client'
const supabase = createSupabaseServiceClient()
```

### When to Use Each Client

| Client | Use Case | RLS | Auth |
|--------|----------|-----|------|
| Browser | React components | Yes | User session |
| Server SSR | API routes, server components | Yes | User session |
| Service Role | Admin operations, background jobs | No | Service key |

## Common Query Patterns

### Get Stories with Storyteller
```typescript
const { data } = await supabase
  .from('stories')
  .select(`
    *,
    storyteller:profiles!stories_storyteller_id_fkey(
      id, display_name, profile_image_url
    )
  `)
  .eq('status', 'published')
  .eq('tenant_id', tenantId)
```

### Get Transcripts with Themes
```typescript
const { data } = await supabase
  .from('transcripts')
  .select('id, title, themes, key_quotes, ai_summary')
  .not('themes', 'is', null)
  .order('created_at', { ascending: false })
```

### Get Organization with Members
```typescript
const { data } = await supabase
  .from('organisations')
  .select(`
    *,
    members:organization_members(
      profile:profiles(id, display_name, profile_image_url),
      role
    )
  `)
  .eq('id', orgId)
  .single()
```

### Get Story with All Relationships
```typescript
const { data } = await supabase
  .from('stories')
  .select(`
    *,
    storyteller:profiles!stories_storyteller_id_fkey(*),
    project:projects(*),
    organization:organisations(*),
    distributions:story_distributions(*),
    featured_media:media_assets(*)
  `)
  .eq('id', storyId)
  .single()
```

### Theme-Based Story Search (Array Overlap)
```typescript
// Stories with ANY matching theme
const { data } = await supabase
  .from('stories')
  .select('*')
  .overlaps('ai_themes', ['identity', 'heritage'])

// Stories with ALL themes
const { data } = await supabase
  .from('stories')
  .select('*')
  .contains('ai_themes', ['identity', 'heritage'])
```

### Count by Status
```typescript
const { count } = await supabase
  .from('stories')
  .select('*', { count: 'exact', head: true })
  .eq('status', 'published')
  .eq('tenant_id', tenantId)
```

### Story Access Tokens (Share Control)

#### Validate Token and Get Story
```typescript
// Use database function for validation + view count increment
const { data: validation } = await supabase.rpc('validate_and_increment_token', {
  p_token: 'abc123xyz'
})

if (validation[0]?.is_valid) {
  const { data: story } = await supabase
    .from('stories')
    .select('*, storyteller:profiles(*)')
    .eq('id', validation[0].story_id)
    .single()
}
```

#### Get Active Share Links for Story
```typescript
const { data: tokens } = await supabase
  .from('story_access_tokens')
  .select('*')
  .eq('story_id', storyId)
  .eq('revoked', false)
  .gt('expires_at', new Date().toISOString())
  .order('created_at', { ascending: false })
```

#### Create Share Link
```typescript
import { nanoid } from 'nanoid'

const token = nanoid(21)
const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days

const { data } = await supabase
  .from('story_access_tokens')
  .insert({
    story_id: storyId,
    token,
    expires_at: expiresAt.toISOString(),
    purpose: 'social-media',
    created_by: userId,
    tenant_id: tenantId
  })
  .select()
  .single()

const shareUrl = `https://empathy-ledger.org/s/${token}`
```

#### Revoke Share Link
```typescript
const { error } = await supabase
  .from('story_access_tokens')
  .update({ revoked: true })
  .eq('id', tokenId)
  .eq('story_id', storyId) // Ensure user owns the story
```

#### Get Share Analytics
```typescript
// View counts, most shared stories
const { data: analytics } = await supabase
  .from('story_access_tokens')
  .select('story_id, view_count, purpose, shared_to')
  .eq('story_id', storyId)
  .order('view_count', { ascending: false })
```

## Multi-Tenant Query Pattern

**IMPORTANT**: Always filter by tenant_id for data isolation.

```typescript
// Standard pattern for all queries
async function getStories(userId: string) {
  const supabase = createSupabaseServerClient()

  // 1. Get user's tenant
  const { data: profile } = await supabase
    .from('profiles')
    .select('tenant_id')
    .eq('id', userId)
    .single()

  // 2. Query with tenant filter
  const { data } = await supabase
    .from('stories')
    .select('*')
    .eq('tenant_id', profile.tenant_id)  // Always include!
    .eq('status', 'published')

  return data
}
```

## Database Functions

Available RPC functions:
```typescript
// Calculate tenant analytics
const { data } = await supabase.rpc('calculate_tenant_analytics', {
  tenant_uuid: tenantId
})

// Get organization stats
const { data } = await supabase.rpc('get_organization_stats', {
  org_id: orgId
})

// Search quotes with full-text
const { data } = await supabase.rpc('search_quotes', {
  query: 'wisdom ancestors'
})

// Search media
const { data } = await supabase.rpc('search_media', {
  query: 'interview video'
})
```

## Migrations Location

All database schema in: `supabase/migrations/`

Key migrations:
- `20251220093000_multi_org_tenants.sql` - Multi-org tenant structure
- `20251207_story_ownership_distribution.sql` - Distribution system
- `20251209000000_cultural_safety_moderation_tables.sql` - Cultural safety
- `20251210000000_partner_portal_system.sql` - Partner distribution

## When to Use This Skill

Invoke when:
- Needing to understand table relationships
- Writing Supabase queries
- Finding the right type definitions
- Understanding foreign key constraints
- Debugging data access issues
- Implementing new features that touch the database

---

## MCP Access

This project has MCP configured for direct Supabase access:

**Read-only (default):**
```
https://mcp.supabase.com/mcp?project_ref=yvnuayzslukamizrlhwb&read_only=true
```

**With write access:**
```
https://mcp.supabase.com/mcp?project_ref=yvnuayzslukamizrlhwb&features=database,docs,debugging,development,functions,branching
```

**Available MCP Tools:**
- `list_tables` - View all tables and columns
- `execute_sql` - Run SQL queries
- `list_migrations` - View migration history
- `generate_typescript_types` - Generate types from schema
- `get_logs` - View application logs

See: [SUPABASE_ACCESS_GUIDE.md](../../../docs/SUPABASE_ACCESS_GUIDE.md)

---

**Trigger:** User asks about database tables, relationships, queries, or "how do I get X from Supabase"
