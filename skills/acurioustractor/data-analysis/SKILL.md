---
name: data-analysis
description: AI-powered data analysis for Empathy Ledger. Use when working with themes, quotes, story suggestions, transcript analysis, storyteller connections, or any feature requiring extracted insights. Ensures consistent analysis patterns across the platform.
---

# Data Analysis Skill

This skill provides patterns and best practices for AI-powered data analysis across the Empathy Ledger platform, ensuring quotes, themes, summaries, and suggestions appear consistently everywhere.

## Core Data Model

### Analysis Pipeline
```
Transcript (raw audio/text)
    ↓ AI Analysis
Theme Extraction → themes[] array
Quote Extraction → key_quotes[] array
Summary Generation → ai_summary text
Sentiment Analysis → sentiment_scores{}
    ↓ Story Creation
Story (authored content)
    ↓ Connections
Related Stories ← theme matching
Suggested Content ← AI recommendations
```

### Key Tables for Analysis

| Table | Analysis Fields | Purpose |
|-------|-----------------|---------|
| `transcripts` | `themes`, `key_quotes`, `ai_summary`, `ai_processing_status` | Raw interview analysis |
| `stories` | `themes`, `cultural_tags`, `featured_quote` | Published story metadata |
| `storytellers` | `expertise_themes`, `connection_strength` | Storyteller insights |
| `story_suggestions` | `reason`, `confidence_score`, `theme_overlap` | AI recommendations |

## Theme System

### Standard Theme Categories
```typescript
const THEME_CATEGORIES = {
  cultural: ['identity', 'heritage', 'tradition', 'language', 'ceremony'],
  family: ['kinship', 'elders', 'children', 'ancestors', 'community'],
  land: ['country', 'connection', 'seasons', 'wildlife', 'sacred-sites'],
  resilience: ['survival', 'adaptation', 'strength', 'healing', 'hope'],
  knowledge: ['wisdom', 'teaching', 'learning', 'stories', 'dreams']
}
```

### Theme Extraction Pattern
```typescript
// When extracting themes from content:
interface ThemeExtraction {
  themes: string[]           // Max 5-7 primary themes
  theme_confidence: number   // 0-1 confidence score
  cultural_relevance: 'high' | 'medium' | 'low'
}

// Supabase query for theme-based matching
const { data } = await supabase
  .from('stories')
  .select('*')
  .overlaps('themes', ['identity', 'heritage'])
  .order('view_count', { ascending: false })
  .limit(5)
```

## Quote System

### Quote Extraction Standards
```typescript
interface ExtractedQuote {
  text: string              // The quote itself (50-300 chars ideal)
  context?: string          // Surrounding context
  themes: string[]          // Themes this quote relates to
  significance: 'highlight' | 'supporting' | 'context'
  speaker_attribution?: string
}

// Store quotes in transcripts
UPDATE transcripts SET key_quotes = ARRAY[
  'When I walk on Country, I feel my ancestors with me.',
  'Our language carries the wisdom of thousands of years.'
]
```

### Quote Display Patterns
```tsx
// Story cards should show featured quotes
<StoryCard
  story={story}
  featuredQuote={story.key_quotes?.[0]}
  showThemes={true}
/>

// Quote highlight component
<QuoteHighlight
  quote={quote}
  attribution={storyteller.display_name}
  themes={quote.themes}
/>
```

## AI Analysis Integration

### Transcript Analysis Flow
```typescript
// 1. Trigger analysis
POST /api/transcripts/{id}/analyze

// 2. AI extracts:
{
  themes: ['identity', 'land-connection', 'healing'],
  key_quotes: [
    "The river taught me patience...",
    "Our stories are our survival..."
  ],
  ai_summary: "This transcript explores themes of cultural...",
  sentiment: { positive: 0.7, reflective: 0.8 }
}

// 3. Store and index
UPDATE transcripts SET
  themes = $themes,
  key_quotes = $key_quotes,
  ai_summary = $ai_summary,
  ai_processing_status = 'completed'
```

### Story Suggestion Algorithm
```typescript
// Find related content based on theme overlap
async function getSuggestedStories(storyId: string) {
  const { data: story } = await supabase
    .from('stories')
    .select('themes, storyteller_id')
    .eq('id', storyId)
    .single()

  // Find stories with overlapping themes
  const { data: related } = await supabase
    .from('stories')
    .select('*, storytellers!inner(display_name)')
    .neq('id', storyId)
    .overlaps('themes', story.themes)
    .limit(5)

  return related.map(r => ({
    ...r,
    theme_overlap: calculateOverlap(story.themes, r.themes),
    reason: generateReason(story.themes, r.themes)
  }))
}
```

## Supabase Best Practices

### Array Operations for Themes
```sql
-- Find stories with ANY matching theme
SELECT * FROM stories WHERE themes && ARRAY['identity', 'heritage'];

-- Find stories with ALL themes
SELECT * FROM stories WHERE themes @> ARRAY['identity', 'heritage'];

-- Count theme occurrences
SELECT unnest(themes) as theme, count(*)
FROM stories
GROUP BY theme
ORDER BY count DESC;
```

### Full-Text Search Integration
```sql
-- Add search vector for quotes
ALTER TABLE transcripts ADD COLUMN
  quote_search tsvector GENERATED ALWAYS AS (
    to_tsvector('english', array_to_string(key_quotes, ' '))
  ) STORED;

CREATE INDEX idx_quote_search ON transcripts USING GIN(quote_search);

-- Search quotes
SELECT * FROM transcripts
WHERE quote_search @@ to_tsquery('english', 'ancestor & wisdom');
```

### Materialized View for Analytics
```sql
-- Theme analytics across platform
CREATE MATERIALIZED VIEW theme_analytics AS
SELECT
  unnest(themes) as theme,
  count(*) as story_count,
  count(DISTINCT storyteller_id) as storyteller_count,
  avg(view_count) as avg_views
FROM stories
WHERE status = 'published'
GROUP BY theme;

-- Refresh periodically
REFRESH MATERIALIZED VIEW theme_analytics;
```

## Component Integration Points

### Where Analysis Should Appear

| Location | What to Show | Source |
|----------|--------------|--------|
| Story Cards | Featured quote, top 3 themes | `stories.key_quotes[0]`, `stories.themes` |
| Story Detail | All quotes, full theme list | Full arrays |
| Storyteller Profile | Expertise themes, quote count | Aggregated from stories |
| World Tour Map | Theme clusters, quote highlights | `theme_analytics` view |
| Search Results | Theme badges, quote snippets | Full-text search |
| Related Stories | Theme overlap %, suggestion reason | Calculated on query |
| Dashboard | Theme trends, popular quotes | Analytics views |

### React Components for Analysis

```tsx
// Theme badge with cultural coloring
<ThemeBadge theme="identity" variant="cultural" />

// Quote card with attribution
<QuoteCard
  quote={quote}
  storyteller={storyteller}
  showThemes
  linkToStory
/>

// Theme cloud visualization
<ThemeCloud
  themes={allThemes}
  onThemeClick={handleFilter}
  highlightActive={activeThemes}
/>

// Story suggestions panel
<SuggestedStories
  currentStory={story}
  maxSuggestions={5}
  showReason
/>
```

## Analysis API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/transcripts/{id}/analyze` | Trigger AI analysis |
| `GET /api/transcripts/{id}/analyze` | Check analysis status |
| `GET /api/stories/{id}/suggestions` | Get related stories |
| `GET /api/themes` | List all themes with counts |
| `GET /api/themes/{theme}/stories` | Stories by theme |
| `GET /api/quotes/search` | Search across quotes |
| `GET /api/storytellers/{id}/themes` | Storyteller expertise |

## When to Use This Skill

Invoke when:
- Adding quotes to story cards or displays
- Implementing story suggestions/related content
- Building theme-based filtering or search
- Creating analytics dashboards
- Integrating AI analysis results
- Designing data visualization components
- Optimizing Supabase queries for analysis data

## Reference Files

- [analysis-patterns.md](analysis-patterns.md) - Detailed code patterns
- [supabase-queries.md](supabase-queries.md) - Optimized query examples
- [theme-taxonomy.md](theme-taxonomy.md) - Complete theme hierarchy
