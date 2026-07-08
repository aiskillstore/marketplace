# Storyteller Card Variants & Data Mapping

## Card Variants Overview

| Variant | Use Case | Size | Data Shown |
|---------|----------|------|------------|
| Default | Directory listing | 320px | Avatar, name, culture, stories, specialties |
| Compact | Sidebar, mentions | 280px | Avatar (sm), name, story count |
| Featured | Homepage, highlights | Full width | All + quote, themes, enhanced bio |
| List | Admin, search results | Full width | Horizontal layout, more actions |
| Mini | Tooltips, autocomplete | 200px | Avatar (xs), name only |
| Profile Header | Profile page | Full width | Large avatar, full details |

## Data Field Mapping

### Default Card Fields
```typescript
// Fields always shown
const defaultFields = {
  required: [
    'display_name',
    'cultural_background',
    'story_count',
    'is_elder',
    'is_featured'
  ],
  optional: [
    'bio',              // Truncated to 100 chars
    'specialties',      // Max 3 shown
    'avatar_url',       // Fallback to initials
    'location'          // If available
  ]
}
```

### Featured Card Fields
```typescript
// Extended fields for featured display
const featuredFields = {
  ...defaultFields,
  enhanced: [
    'featured_quote',       // Primary quote
    'theme_expertise',      // Top 3 themes
    'ai_summary',          // Short summary
    'years_of_experience',
    'organisations',        // First org
    'languages_spoken'      // First 2
  ]
}
```

### Compact Card Fields
```typescript
// Minimal display
const compactFields = {
  required: [
    'display_name',
    'avatar_url'
  ],
  badges: [
    'is_elder',
    'story_count'
  ]
}
```

## Visual Specifications

### Default Card
```
┌─────────────────────────────────────┐
│  ┌──────┐                           │
│  │Avatar│  Display Name        ★ 👑 │
│  │  64  │  Cultural Background      │
│  └──────┘  📍 Location              │
│                                     │
│  Bio text truncated to two lines    │
│  maximum before ellipsis...         │
│                                     │
│  ┌─────────┐ ┌──────────┐ ┌─────┐  │
│  │Specialty│ │Specialty │ │+2   │  │
│  └─────────┘ └──────────┘ └─────┘  │
│                                     │
│  📖 12 Stories    🗓️ 5 Years       │
│                                     │
│  [View Profile →]                   │
└─────────────────────────────────────┘

Dimensions: 320px min-width, auto height
Padding: 24px
Border radius: 12px
Shadow: shadow-sm, shadow-lg on hover
```

### Featured Card
```
┌───────────────────────────────────────────────────────────┐
│  ★ Featured Storyteller                                   │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────┐                                               │
│  │ Avatar │  Display Name                          👑     │
│  │   80   │  Cultural Background • Location               │
│  │        │  Languages: Warlpiri, English                 │
│  └────────┘                                               │
│                                                           │
│  "Featured quote from one of their stories appears here   │
│   with proper attribution and styling..."                 │
│                                — Story Title              │
│                                                           │
│  Extended bio or AI summary text showing more detail      │
│  about the storyteller's background and expertise...      │
│                                                           │
│  Theme Expertise:                                         │
│  ┌──────────┐ ┌────────┐ ┌─────────────┐                │
│  │ Identity │ │ Healing│ │ Land Connect│                 │
│  │   ●●●●○  │ │  ●●●○○ │ │    ●●○○○   │                 │
│  └──────────┘ └────────┘ └─────────────┘                 │
│                                                           │
│  📖 24 Stories    🗓️ 15 Years    🏛️ Organisation         │
│                                                           │
│  [View Full Profile]  [Read Stories]  [Connect]          │
└───────────────────────────────────────────────────────────┘

Dimensions: Full width (constrained to container)
Background: Gradient (muted to card)
Special elements: Quote block, theme depth indicators
```

### List View Row
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ┌────┐                                                                      │
│ │ 48 │ Display Name 👑★     Cultural Background    📖 12    [View] [Edit]  │
│ └────┘ Bio preview text...  📍 Location            Stories                  │
│        Specialty • Specialty • Specialty                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Dimensions: Full width, fixed 72px height
Use: Admin panels, search results with actions
```

## Badge Specifications

### Elder Badge
```tsx
<Badge className="bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
  <Crown className="w-3 h-3 mr-1" />
  Elder
</Badge>
```

### Featured Badge
```tsx
<Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
  <Star className="w-3 h-3 mr-1" />
  Featured
</Badge>
```

### Knowledge Keeper Badge
```tsx
<Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
  <Shield className="w-3 h-3 mr-1" />
  Knowledge Keeper
</Badge>
```

### Story Count Badge
```tsx
<Badge variant="secondary" className="tabular-nums">
  <BookOpen className="w-3 h-3 mr-1" />
  {count} {count === 1 ? 'Story' : 'Stories'}
</Badge>
```

## Responsive Behavior

### Mobile (< 640px)
- Cards stack vertically
- Full width cards
- Reduced padding (16px)
- Smaller avatars (48px)
- Max 2 specialty badges

### Tablet (640px - 1024px)
- 2 column grid
- Standard padding (20px)
- Standard avatars (56px)
- Max 3 specialty badges

### Desktop (> 1024px)
- 3 column grid
- Full padding (24px)
- Large avatars (64px)
- All visible badges

## Loading States

### Skeleton Card
```tsx
<Card className="p-6 animate-pulse">
  <div className="flex gap-4">
    {/* Avatar skeleton */}
    <div className="w-16 h-16 rounded-full bg-muted" />

    <div className="flex-1 space-y-2">
      {/* Name skeleton */}
      <div className="h-5 w-2/3 bg-muted rounded" />
      {/* Culture skeleton */}
      <div className="h-4 w-1/2 bg-muted rounded" />
    </div>
  </div>

  {/* Bio skeleton */}
  <div className="mt-4 space-y-2">
    <div className="h-3 w-full bg-muted rounded" />
    <div className="h-3 w-4/5 bg-muted rounded" />
  </div>

  {/* Badges skeleton */}
  <div className="mt-4 flex gap-2">
    <div className="h-6 w-20 bg-muted rounded-full" />
    <div className="h-6 w-24 bg-muted rounded-full" />
  </div>
</Card>
```

## Empty States

### No Storytellers Found
```tsx
<div className="text-center py-16">
  <Users className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
  <Typography variant="h3" className="text-muted-foreground mb-2">
    No Storytellers Found
  </Typography>
  <Typography variant="body" className="text-muted-foreground/70 mb-6">
    Try adjusting your search or filters
  </Typography>
  <Button variant="outline" onClick={resetFilters}>
    Clear Filters
  </Button>
</div>
```

### No Profile Photo
```tsx
// Initials fallback with gradient background
<div className="w-16 h-16 rounded-full bg-gradient-to-br from-sage-200 to-earth-200
               dark:from-sage-800 dark:to-earth-800 flex items-center justify-center
               text-foreground font-semibold text-lg">
  {getInitials(displayName)}
</div>
```

## Interactive States

### Hover Effects
```tsx
<Card className={cn(
  "transition-all duration-200",
  "hover:shadow-lg hover:scale-[1.02]",
  "hover:border-primary/20"
)}>
```

### Focus States
```tsx
<Card className={cn(
  "focus-within:ring-2 focus-within:ring-primary/50",
  "focus-within:border-primary"
)}>
```

### Selected State
```tsx
<Card className={cn(
  isSelected && "ring-2 ring-primary border-primary bg-primary/5"
)}>
```

## Accessibility Requirements

- All images have alt text: `alt={storyteller.display_name}`
- Elder/Featured badges have aria-labels
- Cards are keyboard navigable (Link wrapper)
- Color contrast meets WCAG AA
- Focus indicators visible
- Screen reader announces card content logically
