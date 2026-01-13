---
name: design-component
description: Design Component skill for Empathy Ledger. Use for storyteller cards, story cards, profile displays, and any UI component requiring cultural sensitivity. Provides data mapping, AI enrichment patterns, and design system guidelines.
---

# Design Component Skill

This skill provides comprehensive guidance for designing and implementing UI components in Empathy Ledger, with special focus on storyteller cards, data display patterns, and AI-powered content enrichment.

## Design System Foundation

### Color Palette (CSS Variables)
```css
/* Use semantic colors for dark mode support */
--background     /* Page background */
--foreground     /* Primary text */
--card           /* Card surfaces */
--card-foreground/* Card text */
--muted          /* Muted backgrounds */
--muted-foreground /* Secondary text */
--popover        /* Dropdown/popover backgrounds */
--border         /* Borders */
--primary        /* Primary actions */
--accent         /* Accent/highlight (sunshine yellow) */
--destructive    /* Errors/warnings */
```

### Cultural Color Meanings
| Color | Meaning | Usage |
|-------|---------|-------|
| Amber/Gold | Elder wisdom, featured | Elder badges, featured indicators |
| Emerald | Growth, community | Story counts, active status |
| Purple | Sacred, knowledge | Knowledge keeper badges |
| Terracotta | Earth, connection | Cultural affiliations |
| Sage | Calm, respectful | General UI elements |

## Storyteller Card Data Model

### Core Display Fields
```typescript
interface StorytellerCardData {
  // Identity (Always Show)
  id: string
  display_name: string
  avatar_url?: string
  pronouns?: string

  // Cultural Context (Show When Available)
  cultural_background?: string
  cultural_affiliations?: string[]
  traditional_territory?: string
  languages_spoken?: string[]

  // Status Indicators
  is_elder: boolean
  is_featured: boolean
  status: 'active' | 'inactive' | 'pending'
  traditional_knowledge_keeper?: boolean

  // Story Metrics
  story_count: number
  featured_quote?: string
  expertise_themes?: string[]

  // Professional Context
  occupation?: string
  years_of_experience?: number
  specialties?: string[]

  // AI-Enriched Fields
  ai_summary?: string
  theme_expertise?: string[]
  connection_strength?: number
  suggested_connections?: string[]
}
```

### Data Priority Hierarchy
```
TIER 1 - Always Display:
├── display_name
├── avatar (or initials fallback)
├── cultural_background
└── story_count

TIER 2 - Show on Card:
├── elder_status badge
├── featured badge
├── top 3 specialties
├── primary location
└── featured_quote (if available)

TIER 3 - Show on Hover/Expand:
├── full bio
├── all specialties
├── languages
├── organisations
└── theme expertise

TIER 4 - Profile Page Only:
├── contact info
├── full story list
├── connection graph
└── detailed analytics
```

## Card Variants

### Default Card
```tsx
<StorytellerCard
  storyteller={storyteller}
  variant="default"
  showStories={true}
  showActions={true}
/>
```
- 320px min width, responsive
- Avatar, name, cultural background
- Story count, specialties (max 3)
- Elder/Featured badges
- Hover effect with arrow

### Compact Card
```tsx
<StorytellerCard
  storyteller={storyteller}
  variant="compact"
/>
```
- 280px width, inline layout
- Avatar (smaller), name only
- Story count as badge
- Good for sidebars, lists

### Featured Card
```tsx
<StorytellerCard
  storyteller={storyteller}
  variant="featured"
/>
```
- Full width, larger avatar
- Featured quote displayed
- Theme expertise badges
- Gradient background
- Enhanced hover animations

### List View Row
```tsx
<StorytellerListCard storyteller={storyteller} />
```
- Full width horizontal
- More data visible
- Action buttons on right
- Good for admin views

## AI Enrichment Opportunities

### 1. Bio Enhancement
```typescript
// API: POST /api/storytellers/{id}/enhance-bio
interface BioEnhancement {
  original_bio: string
  enhanced_bio: string        // Grammar, flow improvements
  key_themes: string[]        // Extracted from bio
  suggested_specialties: string[]
  cultural_keywords: string[]
}
```

### 2. Featured Quote Extraction
```typescript
// From storyteller's stories, extract compelling quotes
interface QuoteExtraction {
  quotes: Array<{
    text: string
    story_id: string
    themes: string[]
    impact_score: number
  }>
  suggested_featured: string  // Best quote for card
}
```

### 3. Theme Expertise Analysis
```typescript
// Analyze all stories to determine expertise areas
interface ThemeExpertise {
  primary_themes: string[]      // Top 3 most discussed
  secondary_themes: string[]    // Supporting themes
  unique_perspective: string    // What makes them unique
  theme_depth_scores: Record<string, number>
}
```

### 4. Connection Suggestions
```typescript
// Find storytellers with complementary themes
interface ConnectionSuggestion {
  storyteller_id: string
  connection_type: 'theme_overlap' | 'geographic' | 'community'
  overlap_score: number
  reason: string  // "Both share expertise in healing stories"
}
```

### 5. Summary Generation
```typescript
// Generate concise storyteller summary
interface StoritellerSummary {
  one_liner: string      // "Elder from Wurundjeri Country..."
  card_summary: string   // 50-100 chars for cards
  full_summary: string   // 200-300 chars for profiles
  voice_style: string    // "Warm and reflective storytelling"
}
```

## Component Implementation Patterns

### Avatar with Status Indicators
```tsx
<div className="relative">
  <Avatar
    src={storyteller.avatar_url}
    fallback={getInitials(storyteller.display_name)}
    className="w-16 h-16 border-2 border-background shadow-md"
  />

  {/* Status Badges - Position top-right */}
  <div className="absolute -top-1 -right-1 flex gap-1">
    {storyteller.is_featured && (
      <Badge variant="featured" size="icon">
        <Star className="w-3 h-3" />
      </Badge>
    )}
    {storyteller.is_elder && (
      <Badge variant="elder" size="icon">
        <Crown className="w-3 h-3" />
      </Badge>
    )}
  </div>
</div>
```

### Cultural Background Display
```tsx
{/* Respectful cultural display */}
<div className="flex items-center gap-2 text-muted-foreground">
  <MapPin className="w-4 h-4 text-terracotta-500" />
  <span className="text-sm">
    {storyteller.cultural_background}
    {storyteller.traditional_territory && (
      <span className="text-xs ml-1">
        ({storyteller.traditional_territory})
      </span>
    )}
  </span>
</div>
```

### Story Metrics Display
```tsx
<div className="flex items-center gap-4">
  <div className="flex items-center gap-1.5">
    <BookOpen className="w-4 h-4 text-emerald-500" />
    <span className="font-semibold">{storyteller.story_count}</span>
    <span className="text-muted-foreground text-sm">
      {storyteller.story_count === 1 ? 'Story' : 'Stories'}
    </span>
  </div>

  {storyteller.years_of_experience && (
    <div className="flex items-center gap-1.5">
      <Calendar className="w-4 h-4 text-blue-500" />
      <span className="font-semibold">{storyteller.years_of_experience}</span>
      <span className="text-muted-foreground text-sm">Years</span>
    </div>
  )}
</div>
```

### Theme/Specialty Badges
```tsx
{/* Show max 3 on card, rest on hover/detail */}
<div className="flex flex-wrap gap-1.5">
  {storyteller.specialties?.slice(0, 3).map((specialty, i) => (
    <Badge
      key={specialty}
      variant="secondary"
      className={cn(
        "text-xs",
        specialtyColors[i % specialtyColors.length]
      )}
    >
      {specialty}
    </Badge>
  ))}
  {(storyteller.specialties?.length || 0) > 3 && (
    <Badge variant="outline" className="text-xs text-muted-foreground">
      +{storyteller.specialties!.length - 3} more
    </Badge>
  )}
</div>
```

### Featured Quote Display
```tsx
{storyteller.featured_quote && (
  <div className="mt-4 p-3 bg-muted/50 rounded-lg border-l-2 border-accent">
    <Quote className="w-4 h-4 text-accent mb-1" />
    <p className="text-sm italic text-foreground/80 line-clamp-2">
      "{storyteller.featured_quote}"
    </p>
  </div>
)}
```

## AI Enrichment API Patterns

### Trigger Enrichment
```typescript
// POST /api/storytellers/{id}/enrich
async function enrichStoryteller(storytellerId: string) {
  const response = await fetch(`/api/storytellers/${storytellerId}/enrich`, {
    method: 'POST',
    body: JSON.stringify({
      enrich_bio: true,
      extract_quotes: true,
      analyze_themes: true,
      suggest_connections: true
    })
  })

  // Returns enrichment job ID for polling
  return response.json()
}
```

### Display Enriched Data
```tsx
// Check for AI-enriched fields
const hasAIData = storyteller.ai_summary || storyteller.theme_expertise?.length

{hasAIData && (
  <div className="flex items-center gap-1 text-xs text-muted-foreground">
    <Sparkles className="w-3 h-3 text-accent" />
    <span>AI Enhanced</span>
  </div>
)}
```

## Database Fields for AI Enrichment

### Profiles Table Additions
```sql
-- AI-generated summary
ALTER TABLE profiles ADD COLUMN ai_summary TEXT;

-- Extracted theme expertise (from stories analysis)
ALTER TABLE profiles ADD COLUMN theme_expertise TEXT[];

-- AI-generated featured quote selection
ALTER TABLE profiles ADD COLUMN featured_quote TEXT;
ALTER TABLE profiles ADD COLUMN featured_quote_story_id UUID;

-- Connection strength scores
ALTER TABLE profiles ADD COLUMN connection_scores JSONB DEFAULT '{}';

-- Enrichment status
ALTER TABLE profiles ADD COLUMN ai_enrichment_status TEXT DEFAULT 'pending';
ALTER TABLE profiles ADD COLUMN ai_enriched_at TIMESTAMPTZ;
```

### Story Suggestions View
```sql
CREATE VIEW storyteller_connections AS
SELECT
  p1.id as storyteller_id,
  p2.id as connected_storyteller_id,
  array_length(
    ARRAY(SELECT unnest(p1.theme_expertise) INTERSECT SELECT unnest(p2.theme_expertise)),
    1
  ) as theme_overlap,
  p1.cultural_background = p2.cultural_background as same_culture
FROM profiles p1
CROSS JOIN profiles p2
WHERE p1.id != p2.id
  AND p1.is_storyteller = true
  AND p2.is_storyteller = true;
```

## Component Checklist

### Before Creating a Card Component
- [ ] Identify all data fields needed
- [ ] Define which fields are required vs optional
- [ ] Plan fallback states for missing data
- [ ] Consider dark mode colors
- [ ] Add hover states
- [ ] Plan loading skeleton
- [ ] Add accessibility labels

### Cultural Sensitivity
- [ ] Respectful terminology used
- [ ] Elder status prominently displayed
- [ ] Cultural background shown with respect
- [ ] Traditional territory acknowledged
- [ ] No appropriation of cultural symbols
- [ ] Languages displayed respectfully

### AI Enrichment
- [ ] Mark AI-generated content
- [ ] Allow user override of AI suggestions
- [ ] Handle missing AI data gracefully
- [ ] Show enrichment in progress states

## Reference Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `StorytellerCard` | `src/components/storyteller/storyteller-card.tsx` | Main card component |
| `UnifiedStorytellerCard` | `src/components/storyteller/unified-storyteller-card.tsx` | Flexible card variants |
| `ElegantStorytellerCard` | `src/components/storyteller/elegant-storyteller-card.tsx` | Premium design variant |
| `StoryCard` | `src/components/story/story-card.tsx` | Story display card |
| `QuoteCard` | `src/components/ui/quote-card.tsx` | Quote display |
| `ThemeBadge` | `src/components/ui/theme-badge.tsx` | Theme display |

## Syndication Dashboard Design Patterns (NEW - Sprint 4)

### Consent Status Badge

**Purpose:** Visual indicator of syndication consent status

**Variants:**
```typescript
type ConsentStatus = 'approved' | 'pending' | 'revoked' | 'expired'

const statusConfig = {
  approved: { color: 'sage', icon: CheckCircle, label: 'Active' },
  pending: { color: 'amber', icon: Clock, label: 'Pending' },
  revoked: { color: 'ember', icon: XCircle, label: 'Revoked' },
  expired: { color: 'muted', icon: AlertCircle, label: 'Expired' }
}
```

**Design:**
```tsx
<Badge className={cn(
  "flex items-center gap-1.5",
  status === 'approved' && "bg-sage-100 text-sage-900",
  status === 'pending' && "bg-amber-100 text-amber-900",
  status === 'revoked' && "bg-ember-100 text-ember-900",
  status === 'expired' && "bg-muted text-muted-foreground"
)}>
  <Icon className="h-3 w-3" />
  {label}
</Badge>
```

---

### Consent Card Layout

**Purpose:** Display individual syndication consent with site info and controls

**Structure:**
```
┌─────────────────────────────────────────────┐
│ [Site Logo]  JusticeHub                    │
│              justicehub.org.au              │
│                                             │
│ Status: [Active Badge]                      │
│ Cultural Level: Public                      │
│ Created: Jan 5, 2026                        │
│                                             │
│ 📊 456 views • Last accessed 2 hours ago    │
│                                             │
│ [View Analytics] [Revoke Access]            │
└─────────────────────────────────────────────┘
```

**Colors:**
- **Card Border:** Use site brand color (if provided)
- **Status Badge:** Follow status config above
- **Cultural Level:** Use cultural color (clay/sage/sky)
- **Actions:** Primary (sage) for analytics, destructive (ember) for revoke

---

### Embed Token Display

**Purpose:** Show token with security-conscious masking

**Pattern:**
```tsx
<div className="flex items-center gap-2">
  <code className="flex-1 px-3 py-2 bg-muted rounded font-mono text-sm">
    {tokenMasked ? 'LRK••••••••••XA' : token}
  </code>
  <Button variant="ghost" size="sm" onClick={() => setTokenMasked(!tokenMasked)}>
    {tokenMasked ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
  </Button>
  <Button variant="ghost" size="sm" onClick={handleCopy}>
    <Copy className="h-4 w-4" />
  </Button>
</div>
```

**Security:**
- Default: Token masked
- Click to reveal (temporary, 10 seconds)
- Copy button with confirmation toast
- Never log unmasked tokens

---

### Analytics Chart Styling

**Purpose:** Consistent chart design across dashboards

**Colors (Recharts):**
```typescript
const siteColors = {
  justicehub: '#C85A54', // Ember
  actfarm: '#6B8E72',    // Sage
  theharvest: '#D97757', // Clay
  actplacemat: '#4A90A4' // Sky
}

// Usage
<Line
  type="monotone"
  dataKey="justicehub"
  stroke={siteColors.justicehub}
  strokeWidth={2}
  dot={{ fill: siteColors.justicehub, r: 4 }}
  activeDot={{ r: 6 }}
/>
```

**Grid & Axes:**
```typescript
<CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
<XAxis
  dataKey="date"
  stroke="hsl(var(--muted-foreground))"
  fontSize={12}
/>
<YAxis
  stroke="hsl(var(--muted-foreground))"
  fontSize={12}
/>
```

---

### Revocation Dialog

**Purpose:** Confirm consent revocation with cultural messaging

**Layout:**
```tsx
<Dialog>
  <DialogHeader>
    <DialogTitle className="text-ember-900">
      Revoke Consent for JusticeHub?
    </DialogTitle>
    <DialogDescription>
      This will immediately remove JusticeHub's access to your story.
      They will no longer be able to display it on their platform.
    </DialogDescription>
  </DialogHeader>

  <div className="space-y-4">
    <div className="rounded-lg bg-sky-50 p-4 border border-sky-200">
      <p className="text-sm text-sky-900 font-medium">
        ✨ You maintain full control
      </p>
      <p className="text-sm text-sky-700 mt-1">
        Your story remains on Empathy Ledger. You can grant consent
        again at any time.
      </p>
    </div>

    <div className="space-y-2">
      <Label htmlFor="reason">Reason for revoking (optional)</Label>
      <Textarea
        id="reason"
        placeholder="E.g., Story needs updating, not ready for external sharing..."
        rows={3}
      />
      <p className="text-xs text-muted-foreground">
        This helps us improve the platform (shared anonymously with
        JusticeHub if consent was active).
      </p>
    </div>
  </div>

  <DialogFooter>
    <Button variant="outline" onClick={onCancel}>
      Keep Consent
    </Button>
    <Button variant="destructive" onClick={handleRevoke}>
      Revoke Access
    </Button>
  </DialogFooter>
</Dialog>
```

**Messaging Principles:**
- ✅ Affirm storyteller control ("You maintain full control")
- ✅ Explain consequences clearly ("immediately remove access")
- ✅ Reassure reversibility ("grant consent again")
- ❌ No guilt-tripping ("Are you sure?")
- ❌ No fear language ("This cannot be undone")

---

### Cultural Permission Level Indicator

**Purpose:** Show content sensitivity level with cultural context

**Levels:**
```typescript
const culturalLevels = {
  public: {
    color: 'sage',
    icon: Globe,
    label: 'Public',
    description: 'Safe to share widely'
  },
  community: {
    color: 'clay',
    icon: Users,
    label: 'Community',
    description: 'Indigenous communities only'
  },
  restricted: {
    color: 'amber',
    icon: Lock,
    label: 'Restricted',
    description: 'Requires elder approval'
  },
  sacred: {
    color: 'ember',
    icon: ShieldAlert,
    label: 'Sacred',
    description: 'Not for external sharing'
  }
}
```

**Component:**
```tsx
<div className="flex items-center gap-2">
  <Icon className="h-4 w-4 text-{color}-700" />
  <div>
    <p className="text-sm font-medium">{label}</p>
    <p className="text-xs text-muted-foreground">{description}</p>
  </div>
</div>
```

---

### Empty States for Syndication

**No Consents Yet:**
```tsx
<div className="text-center py-12 space-y-4">
  <div className="mx-auto w-16 h-16 rounded-full bg-sage-100 flex items-center justify-center">
    <Share2 className="h-8 w-8 text-sage-700" />
  </div>
  <div>
    <h3 className="text-lg font-semibold">No syndication consents yet</h3>
    <p className="text-muted-foreground mt-1">
      Your stories are safe with you. When you're ready to share with
      external platforms like JusticeHub, you'll see them here.
    </p>
  </div>
  <Button onClick={handleCreateConsent}>
    <Plus className="mr-2 h-4 w-4" />
    Share a Story
  </Button>
</div>
```

**All Consents Revoked:**
```tsx
<div className="text-center py-12 space-y-4">
  <div className="mx-auto w-16 h-16 rounded-full bg-sky-100 flex items-center justify-center">
    <ShieldCheck className="h-8 w-8 text-sky-700" />
  </div>
  <div>
    <h3 className="text-lg font-semibold">You're in control</h3>
    <p className="text-muted-foreground mt-1">
      All your stories have been removed from external platforms.
      You can re-share whenever you're ready.
    </p>
  </div>
</div>
```

---

## When to Use This Skill

Invoke when:
- Designing new card components
- Adding fields to storyteller/story cards
- Implementing AI enrichment features
- Creating profile displays
- Building list views with storyteller data
- Adding cultural indicators to UI
- Implementing hover/expand states
- Creating loading skeletons
- **Designing syndication dashboard UI**
- **Building consent management interfaces**
- **Creating analytics visualizations**
- **Implementing revocation workflows**
