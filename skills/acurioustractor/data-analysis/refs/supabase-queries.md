# Supabase Query Patterns for Analysis

## Array Operations

### Theme Matching Queries

```sql
-- Stories with ANY of these themes (OR)
SELECT * FROM stories
WHERE themes && ARRAY['identity', 'heritage', 'land']
AND status = 'published';

-- Stories with ALL of these themes (AND)
SELECT * FROM stories
WHERE themes @> ARRAY['identity', 'heritage']
AND status = 'published';

-- Stories with EXACT themes
SELECT * FROM stories
WHERE themes = ARRAY['identity', 'heritage', 'land']
ORDER BY created_at DESC;

-- Count stories per theme
SELECT
  unnest(themes) as theme,
  count(*) as story_count
FROM stories
WHERE status = 'published'
GROUP BY theme
ORDER BY story_count DESC;
```

### JavaScript/TypeScript Equivalents

```typescript
// ANY overlap
const { data } = await supabase
  .from('stories')
  .select('*')
  .overlaps('themes', ['identity', 'heritage', 'land'])
  .eq('status', 'published')

// Contains ALL themes
const { data } = await supabase
  .from('stories')
  .select('*')
  .contains('themes', ['identity', 'heritage'])
  .eq('status', 'published')

// Theme with specific value in array
const { data } = await supabase
  .from('stories')
  .select('*')
  .filter('themes', 'cs', '{"identity"}')
```

## Full-Text Search

### Setup Search Indexes

```sql
-- Add search vector to transcripts
ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(transcript_content, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(ai_summary, '')), 'C')
  ) STORED;

CREATE INDEX IF NOT EXISTS idx_transcripts_search
ON transcripts USING GIN(search_vector);

-- Add search vector to stories
ALTER TABLE stories ADD COLUMN IF NOT EXISTS
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B') ||
    setweight(to_tsvector('english', array_to_string(themes, ' ')), 'C')
  ) STORED;

CREATE INDEX IF NOT EXISTS idx_stories_search
ON stories USING GIN(search_vector);
```

### Search Queries

```sql
-- Basic search
SELECT * FROM stories
WHERE search_vector @@ to_tsquery('english', 'ancestor & wisdom')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'ancestor & wisdom')) DESC;

-- Search with phrase
SELECT * FROM stories
WHERE search_vector @@ phraseto_tsquery('english', 'walking on country')
LIMIT 10;

-- Headline (snippets with highlights)
SELECT
  id,
  title,
  ts_headline('english', content, to_tsquery('ancestor & wisdom'),
    'StartSel=<mark>, StopSel=</mark>, MaxWords=50') as snippet
FROM stories
WHERE search_vector @@ to_tsquery('english', 'ancestor & wisdom');
```

### JavaScript Search

```typescript
// Full-text search with Supabase
const { data } = await supabase
  .from('stories')
  .select('id, title, content')
  .textSearch('search_vector', 'ancestor & wisdom', {
    type: 'websearch',
    config: 'english'
  })
  .limit(10)

// With RPC for more control
const { data } = await supabase
  .rpc('search_stories', {
    search_query: 'ancestor wisdom',
    result_limit: 10
  })
```

### Search RPC Function

```sql
CREATE OR REPLACE FUNCTION search_stories(
  search_query text,
  result_limit int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  title text,
  snippet text,
  themes text[],
  rank real
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    s.id,
    s.title,
    ts_headline('english', s.content,
      websearch_to_tsquery('english', search_query),
      'StartSel=**, StopSel=**, MaxWords=50'
    ) as snippet,
    s.themes,
    ts_rank(s.search_vector,
      websearch_to_tsquery('english', search_query)
    ) as rank
  FROM stories s
  WHERE s.status = 'published'
    AND s.search_vector @@ websearch_to_tsquery('english', search_query)
  ORDER BY rank DESC
  LIMIT result_limit;
END;
$$;
```

## Analytics Views

### Theme Analytics

```sql
-- Materialized view for theme statistics
CREATE MATERIALIZED VIEW theme_analytics AS
SELECT
  unnest(themes) as theme,
  count(*) as story_count,
  count(DISTINCT author_id) as storyteller_count,
  avg(view_count) as avg_views,
  max(created_at) as last_story_date
FROM stories
WHERE status = 'published'
GROUP BY theme
ORDER BY story_count DESC;

-- Refresh command (run periodically)
REFRESH MATERIALIZED VIEW CONCURRENTLY theme_analytics;

-- Create index for fast lookups
CREATE UNIQUE INDEX ON theme_analytics(theme);
```

### Quote Analytics

```sql
-- View for quote statistics
CREATE VIEW quote_analytics AS
SELECT
  t.id as transcript_id,
  t.title,
  cardinality(t.key_quotes) as quote_count,
  t.themes,
  s.display_name as storyteller_name
FROM transcripts t
JOIN storytellers s ON t.storyteller_id = s.id
WHERE t.ai_processing_status = 'completed'
  AND cardinality(t.key_quotes) > 0;

-- Most quoted themes
SELECT
  unnest(themes) as theme,
  sum(quote_count) as total_quotes
FROM quote_analytics
GROUP BY theme
ORDER BY total_quotes DESC;
```

### Storyteller Expertise

```sql
-- Aggregate storyteller themes
CREATE MATERIALIZED VIEW storyteller_expertise AS
SELECT
  s.id as storyteller_id,
  s.display_name,
  array_agg(DISTINCT unnest) as expertise_themes,
  count(DISTINCT st.id) as story_count,
  sum(st.view_count) as total_views
FROM storytellers s
JOIN stories st ON st.author_id = s.id
CROSS JOIN LATERAL unnest(st.themes)
WHERE st.status = 'published'
GROUP BY s.id, s.display_name;

-- Find storytellers by expertise
SELECT * FROM storyteller_expertise
WHERE 'identity' = ANY(expertise_themes)
ORDER BY story_count DESC;
```

## Performance Optimizations

### Indexes for Analysis Queries

```sql
-- GIN index for theme arrays
CREATE INDEX CONCURRENTLY idx_stories_themes
ON stories USING GIN(themes);

CREATE INDEX CONCURRENTLY idx_transcripts_themes
ON transcripts USING GIN(themes);

-- Partial index for published content
CREATE INDEX CONCURRENTLY idx_stories_published_themes
ON stories USING GIN(themes)
WHERE status = 'published';

-- B-tree for status filtering
CREATE INDEX CONCURRENTLY idx_stories_status
ON stories(status);

-- Composite for common queries
CREATE INDEX CONCURRENTLY idx_stories_tenant_status
ON stories(tenant_id, status);
```

### Query Optimization Tips

```typescript
// Bad: Fetches all columns
const { data } = await supabase.from('stories').select('*')

// Good: Only fetch needed columns
const { data } = await supabase
  .from('stories')
  .select('id, title, themes, key_quotes')

// Bad: Client-side filtering
const { data } = await supabase.from('stories').select('*')
const filtered = data.filter(s => s.themes.includes('identity'))

// Good: Server-side filtering
const { data } = await supabase
  .from('stories')
  .select('*')
  .contains('themes', ['identity'])

// Use pagination for large results
const { data, count } = await supabase
  .from('stories')
  .select('*', { count: 'exact' })
  .range(0, 9) // First 10 items
```

## Real-time Subscriptions

### Subscribe to Analysis Updates

```typescript
// Watch for transcript analysis completion
const subscription = supabase
  .channel('analysis-updates')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'transcripts',
      filter: 'ai_processing_status=eq.completed'
    },
    (payload) => {
      console.log('Analysis completed:', payload.new)
      // Update UI with new themes/quotes
      handleAnalysisComplete(payload.new)
    }
  )
  .subscribe()

// Cleanup
subscription.unsubscribe()
```

## Batch Operations

### Bulk Theme Updates

```sql
-- Update themes for multiple stories
UPDATE stories
SET themes = array_cat(themes, ARRAY['new-theme'])
WHERE id = ANY(ARRAY['id1', 'id2', 'id3']::uuid[]);

-- Remove a theme from all stories
UPDATE stories
SET themes = array_remove(themes, 'deprecated-theme')
WHERE 'deprecated-theme' = ANY(themes);
```

### JavaScript Batch

```typescript
// Batch update with upsert
const updates = stories.map(story => ({
  id: story.id,
  themes: [...new Set([...story.themes, 'new-theme'])]
}))

const { error } = await supabase
  .from('stories')
  .upsert(updates)

// Use RPC for complex batch operations
const { data } = await supabase.rpc('batch_update_themes', {
  story_ids: ['id1', 'id2'],
  add_themes: ['identity'],
  remove_themes: ['deprecated']
})
```
