# Analysis Patterns Reference

## AI Analysis Service

### Complete Analysis Flow

```typescript
// lib/ai/analysis-service.ts

import { createClient } from '@/lib/supabase/client'
import Anthropic from '@anthropic-ai/sdk'

interface AnalysisResult {
  themes: string[]
  key_quotes: string[]
  ai_summary: string
  sentiment: {
    positive: number
    reflective: number
    hopeful: number
  }
  cultural_elements: string[]
}

export async function analyzeTranscript(transcriptId: string): Promise<AnalysisResult> {
  const supabase = createClient()

  // 1. Fetch transcript content
  const { data: transcript } = await supabase
    .from('transcripts')
    .select('transcript_content, title')
    .eq('id', transcriptId)
    .single()

  if (!transcript?.transcript_content) {
    throw new Error('Transcript content not found')
  }

  // 2. Mark as processing
  await supabase
    .from('transcripts')
    .update({ ai_processing_status: 'processing' })
    .eq('id', transcriptId)

  // 3. Call AI for analysis
  const anthropic = new Anthropic()

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2000,
    messages: [{
      role: 'user',
      content: `Analyze this storytelling transcript and extract:

1. THEMES (5-7 key themes, using single words or short phrases)
2. KEY QUOTES (3-5 impactful, quotable passages, 50-150 words each)
3. SUMMARY (2-3 paragraph summary of the story's essence)
4. CULTURAL ELEMENTS (any cultural practices, traditions, or knowledge mentioned)
5. SENTIMENT (rate positive, reflective, hopeful from 0-1)

Transcript:
${transcript.transcript_content}

Respond in JSON format:
{
  "themes": ["theme1", "theme2", ...],
  "key_quotes": ["quote1", "quote2", ...],
  "ai_summary": "summary text...",
  "cultural_elements": ["element1", ...],
  "sentiment": { "positive": 0.8, "reflective": 0.7, "hopeful": 0.9 }
}`
    }]
  })

  // 4. Parse and store results
  const result = JSON.parse(response.content[0].text) as AnalysisResult

  await supabase
    .from('transcripts')
    .update({
      themes: result.themes,
      key_quotes: result.key_quotes,
      ai_summary: result.ai_summary,
      ai_processing_status: 'completed',
      updated_at: new Date().toISOString()
    })
    .eq('id', transcriptId)

  return result
}
```

## Quote Extraction Patterns

### Selecting Best Quotes

```typescript
// lib/ai/quote-extractor.ts

interface Quote {
  text: string
  significance: 'highlight' | 'supporting' | 'context'
  themes: string[]
  position: number // Position in transcript (0-1)
}

function selectFeaturedQuote(quotes: Quote[]): Quote {
  // Prefer highlight quotes from the middle of the content
  const highlights = quotes.filter(q => q.significance === 'highlight')

  if (highlights.length > 0) {
    // Select quote closest to middle (often most impactful)
    return highlights.reduce((best, q) =>
      Math.abs(q.position - 0.5) < Math.abs(best.position - 0.5) ? q : best
    )
  }

  return quotes[0]
}

// For story cards - get the most impactful quote
export function getCardQuote(story: Story): string | null {
  if (story.featured_quote) return story.featured_quote
  if (story.key_quotes?.length > 0) return story.key_quotes[0]
  return null
}
```

### Quote Formatting

```typescript
// components/quote/QuoteDisplay.tsx

interface QuoteDisplayProps {
  quote: string
  attribution?: string
  themes?: string[]
  variant?: 'card' | 'full' | 'highlight'
}

export function QuoteDisplay({ quote, attribution, themes, variant = 'card' }: QuoteDisplayProps) {
  return (
    <blockquote className={cn(
      "border-l-4 pl-4 italic",
      variant === 'card' && "border-sage-400 text-sm line-clamp-3",
      variant === 'full' && "border-clay-500 text-lg py-4",
      variant === 'highlight' && "border-earth-500 bg-earth-50 p-4 rounded-r-lg"
    )}>
      <p className="text-stone-700">"{quote}"</p>
      {attribution && (
        <footer className="text-stone-500 mt-2 not-italic">
          — {attribution}
        </footer>
      )}
      {themes && themes.length > 0 && (
        <div className="flex gap-1 mt-2">
          {themes.slice(0, 3).map(theme => (
            <ThemeBadge key={theme} theme={theme} size="sm" />
          ))}
        </div>
      )}
    </blockquote>
  )
}
```

## Theme Matching Algorithms

### Calculate Theme Overlap

```typescript
// lib/utils/theme-matching.ts

export function calculateThemeOverlap(
  themesA: string[],
  themesB: string[]
): number {
  if (!themesA?.length || !themesB?.length) return 0

  const setA = new Set(themesA.map(t => t.toLowerCase()))
  const setB = new Set(themesB.map(t => t.toLowerCase()))

  const intersection = [...setA].filter(t => setB.has(t))
  const union = new Set([...setA, ...setB])

  // Jaccard similarity
  return intersection.length / union.size
}

export function findRelatedByThemes(
  sourceThemes: string[],
  candidates: Array<{ id: string; themes: string[] }>,
  minOverlap = 0.2
): Array<{ id: string; overlap: number; sharedThemes: string[] }> {
  return candidates
    .map(candidate => ({
      id: candidate.id,
      overlap: calculateThemeOverlap(sourceThemes, candidate.themes),
      sharedThemes: sourceThemes.filter(t =>
        candidate.themes.map(ct => ct.toLowerCase()).includes(t.toLowerCase())
      )
    }))
    .filter(r => r.overlap >= minOverlap)
    .sort((a, b) => b.overlap - a.overlap)
}
```

### Generate Suggestion Reasons

```typescript
// lib/ai/suggestion-reasons.ts

export function generateSuggestionReason(
  sharedThemes: string[],
  overlap: number,
  sourceTitle: string,
  targetTitle: string
): string {
  if (overlap > 0.6) {
    return `Strongly related through themes of ${sharedThemes.slice(0, 2).join(' and ')}`
  }

  if (sharedThemes.length >= 2) {
    return `Both explore ${sharedThemes[0]} and ${sharedThemes[1]}`
  }

  if (sharedThemes.length === 1) {
    return `Also explores the theme of ${sharedThemes[0]}`
  }

  return 'Related content you might enjoy'
}
```

## Story Suggestions Component

```tsx
// components/story/SuggestedStories.tsx

interface SuggestedStoriesProps {
  storyId: string
  maxSuggestions?: number
  showReason?: boolean
}

export function SuggestedStories({
  storyId,
  maxSuggestions = 5,
  showReason = true
}: SuggestedStoriesProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])

  useEffect(() => {
    async function loadSuggestions() {
      const res = await fetch(`/api/stories/${storyId}/suggestions?limit=${maxSuggestions}`)
      const data = await res.json()
      setSuggestions(data.suggestions)
    }
    loadSuggestions()
  }, [storyId, maxSuggestions])

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-stone-900">
        Related Stories
      </h3>
      <div className="grid gap-4">
        {suggestions.map(suggestion => (
          <Link
            key={suggestion.id}
            href={`/stories/${suggestion.id}`}
            className="block p-4 border rounded-lg hover:border-sage-400 transition-colors"
          >
            <h4 className="font-medium text-stone-900">{suggestion.title}</h4>
            {showReason && (
              <p className="text-sm text-stone-500 mt-1">{suggestion.reason}</p>
            )}
            <div className="flex gap-1 mt-2">
              {suggestion.sharedThemes.map(theme => (
                <ThemeBadge key={theme} theme={theme} size="sm" />
              ))}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
```

## API Route Pattern

```typescript
// app/api/stories/[id]/suggestions/route.ts

import { NextResponse } from 'next/server'
import { createRouteHandlerClient } from '@/lib/supabase/server'

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const supabase = createRouteHandlerClient()
  const { searchParams } = new URL(request.url)
  const limit = parseInt(searchParams.get('limit') || '5')

  // Get source story themes
  const { data: story } = await supabase
    .from('stories')
    .select('themes, storyteller_id, tenant_id')
    .eq('id', params.id)
    .single()

  if (!story) {
    return NextResponse.json({ error: 'Story not found' }, { status: 404 })
  }

  // Find related stories with theme overlap
  const { data: related } = await supabase
    .from('stories')
    .select(`
      id,
      title,
      themes,
      key_quotes,
      storytellers!inner(display_name)
    `)
    .eq('tenant_id', story.tenant_id)
    .eq('status', 'published')
    .neq('id', params.id)
    .overlaps('themes', story.themes || [])
    .limit(limit * 2) // Fetch more to filter

  // Calculate overlap and sort
  const suggestions = (related || [])
    .map(r => {
      const sharedThemes = (story.themes || [])
        .filter(t => r.themes?.includes(t))
      return {
        id: r.id,
        title: r.title,
        storyteller: r.storytellers?.display_name,
        featuredQuote: r.key_quotes?.[0],
        sharedThemes,
        overlap: sharedThemes.length / (story.themes?.length || 1),
        reason: generateSuggestionReason(
          sharedThemes,
          sharedThemes.length / (story.themes?.length || 1),
          '', // source title not needed
          r.title
        )
      }
    })
    .sort((a, b) => b.overlap - a.overlap)
    .slice(0, limit)

  return NextResponse.json({ suggestions })
}
```
