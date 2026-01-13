# Supabase Entity Relationship Diagram

Complete visual map of how all tables connect.

## Full Relationship Map

```
                                    ┌─────────────────┐
                                    │     TENANTS     │
                                    │  (isolation)    │
                                    └────────┬────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              │                              │                              │
              ▼                              ▼                              ▼
    ┌─────────────────┐            ┌─────────────────┐            ┌─────────────────┐
    │  tenant_members │            │   ORGANISATIONS │            │    PROFILES     │
    │  (user access)  │◄───────────│  (communities)  │───────────►│ (user accounts) │
    └─────────────────┘            └────────┬────────┘            └────────┬────────┘
                                            │                              │
         ┌──────────────────────────────────┼──────────────────────────────┤
         │                                  │                              │
         ▼                                  ▼                              ▼
┌─────────────────┐               ┌─────────────────┐            ┌─────────────────┐
│ org_members     │               │    PROJECTS     │            │ is_storyteller  │
│ (membership)    │               │  (collections)  │            │    = true       │
└─────────────────┘               └────────┬────────┘            └────────┬────────┘
                                           │                              │
         ┌─────────────────────────────────┼──────────────────────────────┤
         │                                 │                              │
         ▼                                 ▼                              ▼
┌─────────────────┐               ┌─────────────────┐            ┌─────────────────┐
│ project_        │               │     STORIES     │◄───────────│  TRANSCRIPTS    │
│ participants    │               │  (core content) │            │ (raw interviews)│
└─────────────────┘               └────────┬────────┘            └────────┬────────┘
                                           │                              │
    ┌──────────────────────────────────────┼──────────────────────────────┤
    │                    │                 │                │             │
    ▼                    ▼                 ▼                ▼             ▼
┌─────────┐      ┌─────────────┐   ┌─────────────┐  ┌─────────────┐ ┌──────────┐
│ consent │      │ story_      │   │ media_      │  │ cultural_   │ │ themes[] │
│ _proofs │      │distributions│   │ assets      │  │ safety_mod  │ │ quotes[] │
└─────────┘      └──────┬──────┘   └──────┬──────┘  └─────────────┘ │ai_summary│
                        │                 │                         └──────────┘
                        ▼                 ▼
                ┌─────────────┐   ┌─────────────┐
                │ embed_      │   │ media_usage │
                │ tokens      │   │ _tracking   │
                └─────────────┘   └─────────────┘
```

## Table Relationships (All Foreign Keys)

### profiles (users)
```
profiles.tenant_id → tenants.id
```

### organisations
```
organisations.tenant_id → tenants.id
```

### organization_members
```
organization_members.profile_id → profiles.id
organization_members.organization_id → organisations.id
```

### tenant_members
```
tenant_members.profile_id → profiles.id
tenant_members.tenant_id → tenants.id
```

### projects
```
projects.organization_id → organisations.id
projects.tenant_id → tenants.id
```

### project_participants
```
project_participants.project_id → projects.id
project_participants.storyteller_id → profiles.id
```

### stories
```
stories.storyteller_id → profiles.id
stories.author_id → profiles.id
stories.project_id → projects.id
stories.organization_id → organisations.id
stories.tenant_id → tenants.id
stories.featured_media_id → media_assets.id
```

### transcripts
```
transcripts.storyteller_id → profiles.id
transcripts.tenant_id → tenants.id
```

### media_assets
```
media_assets.organization_id → organisations.id
media_assets.project_id → projects.id
media_assets.tenant_id → tenants.id
media_assets.uploader_id → profiles.id
media_assets.gallery_id → galleries.id
```

### story_distributions
```
story_distributions.story_id → stories.id
story_distributions.created_by → users.id (auth.users)
story_distributions.revoked_by → users.id (auth.users)
```

### embed_tokens
```
embed_tokens.story_id → stories.id
embed_tokens.distribution_id → story_distributions.id
```

### extracted_quotes
```
extracted_quotes.author_id → profiles.id
extracted_quotes.organization_id → organisations.id
extracted_quotes.project_id → projects.id
```

### audit_logs
```
audit_logs.actor_id → users.id (auth.users)
```

### deletion_requests
```
deletion_requests.user_id → users.id (auth.users)
deletion_requests.processed_by → users.id (auth.users)
```

### profile_locations
```
profile_locations.profile_id → profiles.id
profile_locations.location_id → locations.id
```

### profile_organizations
```
profile_organizations.profile_id → profiles.id
profile_organizations.organization_id → organisations.id
```

### profile_projects
```
profile_projects.profile_id → profiles.id
profile_projects.project_id → projects.id
```

### media_usage_tracking
```
media_usage_tracking.media_id → media_assets.id
media_usage_tracking.profile_id → profiles.id
media_usage_tracking.tenant_id → tenants.id
```

### user_reports
```
user_reports.profile_id → profiles.id
user_reports.reported_by → profiles.id
user_reports.resolved_by → profiles.id
user_reports.tenant_id → tenants.id
```

### user_sessions
```
user_sessions.profile_id → profiles.id
user_sessions.tenant_id → tenants.id
```

## Data Flow: Story Creation to Distribution

```
1. USER CREATES STORY
   profiles (storyteller) → stories
                              ↓
2. AI ANALYSIS
   stories → transcripts → [AI Processing]
                              ↓
                         themes[], key_quotes[], ai_summary
                              ↓
3. CULTURAL REVIEW (if needed)
   stories → cultural_safety_moderation
                              ↓
                         elder_review if sensitivity_level = 'high'
                              ↓
4. CONSENT GRANTED
   stories → consent_proofs
                              ↓
                         verification_status = 'verified'
                              ↓
5. DISTRIBUTION
   stories → story_distributions
                              ↓
                         platform = 'embed', status = 'active'
                              ↓
6. EMBED TOKEN GENERATED
   story_distributions → embed_tokens
                              ↓
                         token, allowed_domains[]
                              ↓
7. EMBED SERVED
   embed_tokens → usage_count++, last_used_at
                              ↓
8. AUDIT LOGGED
   all actions → audit_logs
```

## Tenant Isolation Pattern

Every query MUST include tenant filtering:

```typescript
// ❌ WRONG - No tenant isolation
const { data } = await supabase
  .from('stories')
  .select('*')
  .eq('status', 'published')

// ✅ CORRECT - With tenant isolation
const { data: profile } = await supabase
  .from('profiles')
  .select('tenant_id')
  .eq('id', userId)
  .single()

const { data } = await supabase
  .from('stories')
  .select('*')
  .eq('tenant_id', profile.tenant_id)  // ← Required!
  .eq('status', 'published')
```

## Common Join Patterns

### Story with Full Context
```typescript
const { data } = await supabase
  .from('stories')
  .select(`
    *,
    storyteller:profiles!stories_storyteller_id_fkey(
      id, display_name, profile_image_url, bio
    ),
    author:profiles!stories_author_id_fkey(
      id, display_name
    ),
    project:projects(
      id, name
    ),
    organization:organisations(
      id, name, logo_url
    ),
    featured_media:media_assets(
      id, public_url, thumbnail_url
    )
  `)
  .eq('id', storyId)
  .single()
```

### Transcript with Analysis
```typescript
const { data } = await supabase
  .from('transcripts')
  .select(`
    *,
    storyteller:profiles!transcripts_storyteller_id_fkey(
      id, display_name, profile_image_url
    )
  `)
  .not('themes', 'is', null)
  .order('created_at', { ascending: false })
```

### Organization Dashboard
```typescript
const { data } = await supabase
  .from('organisations')
  .select(`
    *,
    members:organization_members(
      id,
      role,
      profile:profiles(id, display_name, profile_image_url, is_elder)
    ),
    projects:projects(
      id, name, status,
      stories:stories(count)
    )
  `)
  .eq('id', orgId)
  .single()
```
