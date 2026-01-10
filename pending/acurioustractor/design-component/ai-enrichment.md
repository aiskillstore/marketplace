# AI Enrichment Patterns for Storyteller Data

## Overview

This document details how to enrich storyteller profiles and cards with AI-generated content while maintaining cultural sensitivity and user control.

## Enrichment Types

### 1. Bio Enhancement

**Source**: User-provided bio text
**Output**: Improved grammar, flow, and extracted keywords

```typescript
interface BioEnhancementRequest {
  storyteller_id: string
  original_bio: string
  preserve_voice: boolean  // Keep storyteller's authentic voice
  extract_keywords: boolean
}

interface BioEnhancementResponse {
  enhanced_bio: string
  key_themes: string[]
  cultural_keywords: string[]
  tone_analysis: {
    warmth: number      // 0-1
    formality: number   // 0-1
    storytelling: number // 0-1
  }
  suggestions: string[]  // Optional improvements user can accept
}
```

**API Endpoint**: `POST /api/storytellers/{id}/enhance-bio`

**Usage in Card**:
```tsx
// Show enhanced bio with indicator
{storyteller.enhanced_bio ? (
  <div className="relative">
    <p className="text-sm text-muted-foreground">
      {storyteller.enhanced_bio}
    </p>
    <Tooltip content="AI-enhanced for clarity">
      <Sparkles className="absolute -top-1 -right-1 w-3 h-3 text-amber-500" />
    </Tooltip>
  </div>
) : (
  <p className="text-sm text-muted-foreground">{storyteller.bio}</p>
)}
```

### 2. Quote Extraction

**Source**: All stories authored by storyteller
**Output**: Compelling quotes ranked by impact

```typescript
interface QuoteExtractionRequest {
  storyteller_id: string
  max_quotes: number
  min_length: number
  max_length: number
  themes_to_highlight?: string[]
}

interface ExtractedQuote {
  id: string
  text: string
  story_id: string
  story_title: string
  themes: string[]
  impact_score: number    // 0-1, based on engagement + sentiment
  cultural_significance: 'standard' | 'significant' | 'sacred'
  extraction_confidence: number
}

interface QuoteExtractionResponse {
  quotes: ExtractedQuote[]
  suggested_featured: ExtractedQuote  // Best for card display
  theme_distribution: Record<string, number>
}
```

**API Endpoint**: `GET /api/storytellers/{id}/quotes`

**Card Integration**:
```tsx
// Featured quote on card
{storyteller.featured_quote && (
  <blockquote className="mt-3 pl-3 border-l-2 border-amber-400 italic text-sm">
    "{storyteller.featured_quote.text}"
    <cite className="block text-xs text-muted-foreground mt-1">
      — from "{storyteller.featured_quote.story_title}"
    </cite>
  </blockquote>
)}
```

### 3. Theme Expertise Analysis

**Source**: All stories + transcripts by storyteller
**Output**: Primary expertise areas with depth scores

```typescript
interface ThemeAnalysisRequest {
  storyteller_id: string
  include_transcripts: boolean
  min_stories_for_expertise: number
}

interface ThemeExpertise {
  theme: string
  story_count: number
  depth_score: number      // 0-1, how deeply they explore this theme
  unique_angle?: string    // What's unique about their perspective
  sample_quotes: string[]
}

interface ThemeAnalysisResponse {
  primary_expertise: ThemeExpertise[]     // Top 3
  secondary_expertise: ThemeExpertise[]   // Next 5
  emerging_themes: string[]               // Themes appearing recently
  unique_voice: string                    // What makes them distinct
  suggested_connections: string[]         // Storyteller IDs with complementary expertise
}
```

**API Endpoint**: `GET /api/storytellers/{id}/theme-expertise`

**Card Integration**:
```tsx
// Expertise badges with depth indicator
<div className="flex flex-wrap gap-2 mt-3">
  {storyteller.theme_expertise?.slice(0, 3).map((theme) => (
    <Badge
      key={theme.theme}
      variant="outline"
      className="relative pr-6"
    >
      {theme.theme}
      {/* Depth indicator */}
      <div
        className="absolute right-1 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full"
        style={{
          background: `conic-gradient(var(--primary) ${theme.depth_score * 360}deg, transparent 0)`
        }}
        title={`${Math.round(theme.depth_score * 100)}% depth`}
      />
    </Badge>
  ))}
</div>
```

### 4. Connection Suggestions

**Source**: Theme overlap + geographic proximity + community ties
**Output**: Recommended storyteller connections

```typescript
interface ConnectionRequest {
  storyteller_id: string
  max_suggestions: number
  connection_types: ('theme' | 'geographic' | 'community' | 'language')[]
}

interface SuggestedConnection {
  storyteller_id: string
  display_name: string
  avatar_url?: string
  connection_type: string
  strength_score: number  // 0-1
  reason: string          // Human-readable explanation
  shared_themes: string[]
  shared_communities: string[]
}

interface ConnectionResponse {
  suggestions: SuggestedConnection[]
  network_position: {
    centrality: number     // How connected they are
    cluster: string        // What community cluster
    bridge_potential: number // Could connect different groups
  }
}
```

**API Endpoint**: `GET /api/storytellers/{id}/connections`

**Profile Integration**:
```tsx
// Connection suggestions section
<section className="mt-8">
  <h3 className="text-lg font-semibold flex items-center gap-2">
    <Users className="w-5 h-5" />
    Related Storytellers
    <Sparkles className="w-4 h-4 text-amber-500" />
  </h3>

  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
    {connections.map((conn) => (
      <Link href={`/storytellers/${conn.storyteller_id}`} key={conn.storyteller_id}>
        <Card className="p-3 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <Avatar src={conn.avatar_url} size="sm" />
            <div>
              <p className="font-medium text-sm">{conn.display_name}</p>
              <p className="text-xs text-muted-foreground">{conn.reason}</p>
            </div>
          </div>
        </Card>
      </Link>
    ))}
  </div>
</section>
```

### 5. Summary Generation

**Source**: Bio + stories + themes + cultural background
**Output**: Various length summaries for different contexts

```typescript
interface SummaryRequest {
  storyteller_id: string
  formats: ('one_liner' | 'card' | 'profile' | 'featured')[]
}

interface GeneratedSummary {
  one_liner: string        // 20-30 words, for search results
  card_summary: string     // 50-80 words, for card hover
  profile_summary: string  // 150-200 words, for profile header
  featured_summary: string // 100-150 words, for featured sections
  voice_style: string      // e.g., "Warm, reflective, community-focused"
  storytelling_approach: string // e.g., "Weaves personal experience with traditional knowledge"
}
```

**API Endpoint**: `POST /api/storytellers/{id}/generate-summary`

## Enrichment Workflow

### Automatic Enrichment
```
Trigger: Story published / Profile updated
    ↓
Queue enrichment job
    ↓
Extract quotes from new story
    ↓
Update theme expertise scores
    ↓
Refresh connection suggestions
    ↓
Regenerate summaries
    ↓
Mark profile as enriched
```

### Manual Enrichment
```typescript
// Admin can trigger full re-enrichment
POST /api/admin/storytellers/{id}/enrich-full

// Storyteller can request specific enrichments
POST /api/storytellers/{id}/enrich
{
  "types": ["bio", "quotes", "themes"],
  "preserve_manual_edits": true
}
```

## Database Schema for Enrichment

```sql
-- Enrichment metadata
ALTER TABLE profiles ADD COLUMN enrichment_data JSONB DEFAULT '{
  "status": "pending",
  "last_enriched_at": null,
  "enrichment_version": 0,
  "manual_overrides": []
}';

-- Separate table for quotes (many per storyteller)
CREATE TABLE storyteller_quotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  storyteller_id UUID REFERENCES profiles(id),
  story_id UUID REFERENCES stories(id),
  quote_text TEXT NOT NULL,
  themes TEXT[],
  impact_score DECIMAL(3,2),
  is_featured BOOLEAN DEFAULT false,
  extraction_confidence DECIMAL(3,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for quote retrieval
CREATE INDEX idx_quotes_storyteller ON storyteller_quotes(storyteller_id);
CREATE INDEX idx_quotes_featured ON storyteller_quotes(storyteller_id) WHERE is_featured = true;

-- Connection suggestions cache
CREATE TABLE storyteller_connections (
  storyteller_id UUID REFERENCES profiles(id),
  connected_id UUID REFERENCES profiles(id),
  connection_type TEXT,
  strength_score DECIMAL(3,2),
  reason TEXT,
  shared_themes TEXT[],
  computed_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (storyteller_id, connected_id)
);
```

## UI States for Enrichment

### Loading State
```tsx
{enrichmentStatus === 'processing' && (
  <div className="flex items-center gap-2 text-sm text-muted-foreground">
    <Loader2 className="w-4 h-4 animate-spin" />
    <span>Enhancing profile...</span>
  </div>
)}
```

### Enriched Indicator
```tsx
{storyteller.enrichment_data?.status === 'complete' && (
  <Tooltip content={`Last enhanced ${formatRelative(storyteller.enrichment_data.last_enriched_at)}`}>
    <div className="flex items-center gap-1 text-xs text-amber-600">
      <Sparkles className="w-3 h-3" />
      <span>AI Enhanced</span>
    </div>
  </Tooltip>
)}
```

### Manual Override Notice
```tsx
{storyteller.enrichment_data?.manual_overrides?.includes('bio') && (
  <span className="text-xs text-muted-foreground">
    (manually edited)
  </span>
)}
```

## Cultural Considerations

### Do's
- Always allow storyteller to override AI suggestions
- Mark AI-generated content clearly
- Respect cultural sensitivity levels in quotes
- Exclude sacred content from auto-extraction
- Preserve authentic voice in bio enhancement

### Don'ts
- Don't auto-publish AI-generated content
- Don't extract quotes from sacred stories
- Don't suggest connections across cultural boundaries inappropriately
- Don't override Elder-approved content with AI
- Don't use AI summaries for official/legal contexts

## Testing AI Enrichment

```typescript
// Mock enrichment for development
const mockEnrichment: EnrichmentResponse = {
  bio_enhanced: true,
  quotes_extracted: 5,
  themes_analyzed: true,
  connections_suggested: 3,
  summaries_generated: ['one_liner', 'card', 'profile']
}

// Verify enrichment quality
expect(enrichedBio).toContain(originalKeyThemes)
expect(suggestedQuotes).not.toIncludeSacredContent()
expect(connectionReasons).toBeHumanReadable()
```
