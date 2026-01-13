# Theme Taxonomy

## Primary Theme Categories

### Cultural Identity
Core themes around cultural belonging and heritage.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `identity` | Personal and cultural identity | self, belonging, heritage |
| `heritage` | Cultural traditions passed down | tradition, legacy, ancestry |
| `language` | Indigenous languages and communication | mother-tongue, words, speaking |
| `ceremony` | Ceremonial and spiritual practices | ritual, sacred, gathering |
| `art` | Traditional and contemporary art forms | painting, weaving, craft |

### Family & Community
Themes around relationships and kinship.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `family` | Immediate and extended family | parents, children, siblings |
| `kinship` | Traditional kinship systems | relations, connections, ties |
| `elders` | Elder knowledge and guidance | wisdom, teaching, respect |
| `community` | Community bonds and support | village, mob, people |
| `ancestors` | Connection to ancestors | spirits, dreamtime, lineage |

### Land & Country
Themes around connection to land and environment.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `country` | Connection to traditional lands | homeland, territory, place |
| `land` | Relationship with the land | earth, soil, ground |
| `seasons` | Seasonal knowledge and practices | weather, cycles, timing |
| `wildlife` | Animals and their significance | totems, creatures, spirits |
| `water` | Rivers, oceans, and water sources | rivers, rain, sea |
| `sacred-sites` | Significant spiritual locations | dreaming, ceremony-ground |

### Resilience & Survival
Themes around strength and overcoming challenges.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `resilience` | Strength through adversity | strength, endurance, spirit |
| `survival` | Stories of survival | perseverance, determination |
| `healing` | Personal and collective healing | recovery, restoration, peace |
| `resistance` | Standing against colonization | fight, protest, rights |
| `hope` | Looking toward the future | future, dreams, possibility |

### Knowledge & Learning
Themes around wisdom and education.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `wisdom` | Traditional knowledge and insight | knowledge, understanding |
| `teaching` | Passing on knowledge | education, instruction |
| `stories` | Oral traditions and storytelling | narrative, tale, legend |
| `dreams` | Dream stories and visions | vision, sleep, prophecy |
| `law` | Traditional law and governance | rules, custom, lore |

### Daily Life
Themes around everyday experiences.

| Theme | Description | Related Tags |
|-------|-------------|--------------|
| `food` | Traditional foods and gathering | bush-tucker, hunting, fishing |
| `work` | Work and livelihood | jobs, career, skills |
| `home` | Home and shelter | house, dwelling, living |
| `travel` | Journeys and movement | journey, walking, moving |
| `play` | Games and recreation | fun, sport, games |

## Theme Normalization

### Mapping Variations to Standard Themes

```typescript
const THEME_ALIASES: Record<string, string> = {
  // Identity variations
  'who-i-am': 'identity',
  'belonging': 'identity',
  'self': 'identity',

  // Heritage variations
  'tradition': 'heritage',
  'customs': 'heritage',
  'culture': 'heritage',
  'legacy': 'heritage',

  // Family variations
  'relatives': 'family',
  'kin': 'kinship',
  'mob': 'community',

  // Land variations
  'homeland': 'country',
  'territory': 'country',
  'place': 'country',
  'nature': 'land',

  // Elders variations
  'grandparents': 'elders',
  'old-people': 'elders',
  'aunties': 'elders',
  'uncles': 'elders',

  // Healing variations
  'recovery': 'healing',
  'wellbeing': 'healing',
  'wellness': 'healing',
}

export function normalizeTheme(theme: string): string {
  const lower = theme.toLowerCase().trim()
  return THEME_ALIASES[lower] || lower
}

export function normalizeThemes(themes: string[]): string[] {
  return [...new Set(themes.map(normalizeTheme))]
}
```

## Theme Colors

### Cultural Color Mapping

```typescript
const THEME_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  // Cultural identity - Earth tones
  identity: { bg: 'bg-earth-100', text: 'text-earth-800', border: 'border-earth-200' },
  heritage: { bg: 'bg-earth-100', text: 'text-earth-800', border: 'border-earth-200' },
  language: { bg: 'bg-earth-100', text: 'text-earth-800', border: 'border-earth-200' },
  ceremony: { bg: 'bg-clay-100', text: 'text-clay-800', border: 'border-clay-200' },

  // Family & Community - Sage tones
  family: { bg: 'bg-sage-100', text: 'text-sage-800', border: 'border-sage-200' },
  kinship: { bg: 'bg-sage-100', text: 'text-sage-800', border: 'border-sage-200' },
  elders: { bg: 'bg-sage-200', text: 'text-sage-900', border: 'border-sage-300' },
  community: { bg: 'bg-sage-100', text: 'text-sage-800', border: 'border-sage-200' },
  ancestors: { bg: 'bg-sage-200', text: 'text-sage-900', border: 'border-sage-300' },

  // Land & Country - Clay/Earth blend
  country: { bg: 'bg-clay-100', text: 'text-clay-800', border: 'border-clay-200' },
  land: { bg: 'bg-clay-100', text: 'text-clay-800', border: 'border-clay-200' },
  water: { bg: 'bg-sky-100', text: 'text-sky-800', border: 'border-sky-200' },
  wildlife: { bg: 'bg-earth-100', text: 'text-earth-800', border: 'border-earth-200' },

  // Resilience - Warm tones
  resilience: { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-200' },
  healing: { bg: 'bg-sage-100', text: 'text-sage-800', border: 'border-sage-200' },
  hope: { bg: 'bg-sky-100', text: 'text-sky-800', border: 'border-sky-200' },

  // Knowledge - Stone tones
  wisdom: { bg: 'bg-stone-200', text: 'text-stone-800', border: 'border-stone-300' },
  stories: { bg: 'bg-stone-100', text: 'text-stone-700', border: 'border-stone-200' },

  // Default
  default: { bg: 'bg-stone-100', text: 'text-stone-600', border: 'border-stone-200' }
}

export function getThemeColors(theme: string) {
  return THEME_COLORS[theme.toLowerCase()] || THEME_COLORS.default
}
```

## Theme Badge Component

```tsx
// components/ui/theme-badge.tsx

import { cn } from '@/lib/utils'
import { getThemeColors } from '@/lib/theme-colors'

interface ThemeBadgeProps {
  theme: string
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  active?: boolean
}

export function ThemeBadge({
  theme,
  size = 'md',
  onClick,
  active = false
}: ThemeBadgeProps) {
  const colors = getThemeColors(theme)

  return (
    <span
      onClick={onClick}
      className={cn(
        "inline-flex items-center rounded-full font-medium border",
        colors.bg, colors.text, colors.border,
        size === 'sm' && "px-2 py-0.5 text-xs",
        size === 'md' && "px-3 py-1 text-sm",
        size === 'lg' && "px-4 py-1.5 text-base",
        onClick && "cursor-pointer hover:opacity-80",
        active && "ring-2 ring-offset-1 ring-sage-400"
      )}
    >
      {theme.replace(/-/g, ' ')}
    </span>
  )
}
```

## Theme Hierarchy

### Parent-Child Relationships

```typescript
const THEME_HIERARCHY = {
  'cultural': {
    parent: null,
    children: ['identity', 'heritage', 'language', 'ceremony', 'art']
  },
  'identity': {
    parent: 'cultural',
    children: []
  },
  'family-community': {
    parent: null,
    children: ['family', 'kinship', 'elders', 'community', 'ancestors']
  },
  'land-country': {
    parent: null,
    children: ['country', 'land', 'seasons', 'wildlife', 'water', 'sacred-sites']
  },
  'resilience-strength': {
    parent: null,
    children: ['resilience', 'survival', 'healing', 'resistance', 'hope']
  },
  'knowledge-wisdom': {
    parent: null,
    children: ['wisdom', 'teaching', 'stories', 'dreams', 'law']
  }
}

export function getParentTheme(theme: string): string | null {
  const entry = Object.entries(THEME_HIERARCHY)
    .find(([_, v]) => v.children.includes(theme))
  return entry ? entry[0] : null
}

export function getRelatedThemes(theme: string): string[] {
  const parent = getParentTheme(theme)
  if (!parent) return []
  return THEME_HIERARCHY[parent].children.filter(t => t !== theme)
}
```

## Theme Analytics Queries

### Most Common Themes

```sql
-- Top 10 themes by story count
SELECT
  unnest(themes) as theme,
  count(*) as story_count,
  round(count(*) * 100.0 / (SELECT count(*) FROM stories WHERE status = 'published'), 1) as percentage
FROM stories
WHERE status = 'published'
GROUP BY theme
ORDER BY story_count DESC
LIMIT 10;
```

### Theme Co-occurrence

```sql
-- Find themes that often appear together
WITH theme_pairs AS (
  SELECT
    a.theme as theme1,
    b.theme as theme2,
    count(*) as co_occurrence
  FROM stories s,
    LATERAL unnest(s.themes) as a(theme),
    LATERAL unnest(s.themes) as b(theme)
  WHERE a.theme < b.theme
    AND s.status = 'published'
  GROUP BY a.theme, b.theme
)
SELECT * FROM theme_pairs
ORDER BY co_occurrence DESC
LIMIT 20;
```

### Theme Trends Over Time

```sql
-- Monthly theme popularity
SELECT
  date_trunc('month', created_at) as month,
  unnest(themes) as theme,
  count(*) as story_count
FROM stories
WHERE status = 'published'
  AND created_at >= now() - interval '1 year'
GROUP BY month, theme
ORDER BY month DESC, story_count DESC;
```
