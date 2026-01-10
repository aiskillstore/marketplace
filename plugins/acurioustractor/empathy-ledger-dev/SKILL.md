# Empathy Ledger Development Skill

This skill provides comprehensive context for developing the Empathy Ledger v2 platform - a multi-tenant storytelling platform for Indigenous communities with cultural safety protocols.

## Quick Reference

### Project Structure
```
src/
├── app/                    # Next.js 15 App Router
│   ├── api/               # API routes
│   ├── vault/             # Story Vault dashboard
│   └── stories/           # Story pages
├── components/            # React components
│   ├── ui/               # shadcn/ui base
│   ├── vault/            # Story Vault components
│   └── cultural/         # Cultural protocol UI
├── lib/                   # Utilities and services
│   ├── services/         # Business logic services
│   ├── hooks/            # React hooks
│   └── ai/               # AI integration
└── types/                # TypeScript types
    └── database/         # Supabase types by domain
```

### Key Concepts

**OCAP Principles** (Indigenous Data Sovereignty):
- **Ownership**: Storytellers own their narratives
- **Control**: Users control who accesses their stories
- **Access**: Tiered access based on cultural sensitivity
- **Possession**: Data can be exported/deleted anytime

**Multi-Tenant Architecture**:
- All tables have `tenant_id` for isolation
- RLS policies enforce tenant boundaries
- Organizations = tenants

**Cultural Sensitivity Levels**:
- `standard` - General sharing allowed
- `medium` - Community context required
- `high` - Elder review recommended
- `sacred` - Elder approval mandatory, no external sharing

### Common Patterns

**API Route Authentication**:
```typescript
const supabase = createRouteHandlerClient({ cookies })
const { data: { user }, error } = await supabase.auth.getUser()
if (error || !user) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
}
```

**Story Ownership Check**:
```typescript
const isOwner = story.author_id === user.id || story.storyteller_id === user.id
```

**Cultural Color Palette**:
- `clay-*` - Primary, storyteller elements
- `sage-*` - Community, elder approval
- `sky-*` - Organization, trust
- `ember-*` - Warnings, sensitivity

### Database Domains

| Domain | File | Contents |
|--------|------|----------|
| User/Profile | `user-profile.ts` | Profiles, preferences |
| Organization | `organization-tenant.ts` | Tenants, memberships |
| Projects | `project-management.ts` | Projects, milestones |
| Content | `content-media.ts` | Stories, media |
| Cultural | `cultural-protocols.ts` | Sensitivity, approvals |
| Legal | `consent-legal.ts` | Consent, GDPR |
| Story Ownership | `story-ownership.ts` | Distributions, embeds |

### Key Services

- `EmbedService` - Manage story embeds with domain restrictions
- `DistributionService` - Track external shares
- `RevocationService` - Cascade revocation
- `GDPRService` - Anonymization, data export
- `AuditService` - Action logging

### Slash Commands

- `/design-component [description]` - Create React component
- `/database-migration [description]` - Create Supabase migration
- `/review-cultural [code/feature]` - Cultural sensitivity review
- `/review-security [code/endpoint]` - Security audit
- `/generate-e2e-test [feature]` - Create Playwright test
- `/api-endpoint [description]` - Create API route

### Specialized Agents

- `frontend-designer` - UI/UX with cultural design
- `database-architect` - Supabase/PostgreSQL
- `cultural-reviewer` - OCAP compliance
- `security-auditor` - GDPR and security
- `testing-automation` - Playwright E2E

## When to Use This Skill

Invoke this skill when:
- Starting work on any Empathy Ledger feature
- Need quick reference to project patterns
- Reviewing code for compliance
- Creating new components/endpoints

## Reference Files

The following files provide detailed context:
- `CLAUDE.md` - Project instructions
- `.claude/agents/*.md` - Specialized agent prompts
- `.claude/commands/*.md` - Slash command definitions
- `src/types/database/` - Database type definitions
