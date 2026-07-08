# Storyteller Card Component

## Data Model
```typescript
interface StorytellerCardData {
  // Identity (Always Show)
  id: string
  display_name: string
  avatar_url?: string
  pronouns?: string

  // Cultural Context
  cultural_background?: string
  cultural_affiliations?: string[]
  traditional_territory?: string
  languages_spoken?: string[]

  // Status
  is_elder: boolean
  is_featured: boolean
  status: 'active' | 'inactive' | 'pending'
  traditional_knowledge_keeper?: boolean

  // Metrics
  story_count: number
  featured_quote?: string
  expertise_themes?: string[]

  // AI-Enriched
  ai_summary?: string
  theme_expertise?: string[]
}
```

## Display Hierarchy
```
TIER 1 - Always Show:
├── display_name
├── avatar (or initials)
├── cultural_background
└── story_count

TIER 2 - Show on Card:
├── elder_status badge
├── featured badge
├── top 3 specialties
└── primary location

TIER 3 - Hover/Expand:
├── full bio
├── all specialties
└── theme expertise

TIER 4 - Profile Page Only:
├── contact info
├── full story list
└── connection graph
```

## Badge Priority
1. Elder (gold crown)
2. Featured (star)
3. Knowledge Keeper (book)
4. Verified (check)
