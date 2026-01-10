# Analysis Sync Status Report

Last updated: 2024-12-19

## Current Database Status

### Transcripts
| Metric | Count | Change |
|--------|-------|--------|
| Total Transcripts | 251 | - |
| Analyzed (AI processed) | 17 | +7 |
| With Themes Extracted | 9 | +7 |
| Pending Analysis | 234 | -7 |

### Themes
| Metric | Count | Change |
|--------|-------|--------|
| Total in `narrative_themes` | 64 | +43 |
| Unique Theme Names | 61 | +42 |
| Categories | 9 | +1 |

### Quotes
| Metric | Value | Change |
|--------|-------|--------|
| Total in `storyteller_quotes` | 43 | +33 |
| Unique Storytellers | 12 | +9 |
| Avg Impact Score | 0.54 | - |

### Recent Analysis (Dec 19)
- 7 new transcripts analyzed via batch process
- 43 themes synced from transcript metadata
- Bloomfield family interviews processed with rich cultural themes
- OpenAI quota limit reached - additional analysis requires billing update

### Sample Themes Extracted
- Family and Generational Legacy
- Connection to Land and Cultural Heritage
- Community Engagement and Healing
- Youth Resilience and Independence
- Education and Cultural Exchange
- Partnership and Collaboration for Community Development

## Sync Commands

### Check Current Status
```bash
npx tsx scripts/analysis/sync-all-analysis.ts --dry-run --verbose
```

### Run Full Sync (themes + quotes)
```bash
npx tsx scripts/analysis/sync-all-analysis.ts --fix-themes --fix-quotes --verbose
```

### Run Complete Resync
```bash
npx tsx scripts/analysis/sync-all-analysis.ts --full-sync
```

### Run Batch AI Analysis (standalone script)
```bash
# Preview what would be analyzed
npx tsx scripts/analysis/run-batch-analysis.ts --dry-run

# Run analysis on 20 transcripts
npx tsx scripts/analysis/run-batch-analysis.ts --limit=20 --batch-size=5 --verbose

# Run all pending (requires OpenAI quota)
npx tsx scripts/analysis/run-batch-analysis.ts --verbose
```

### Via API (requires dev server + auth)
```bash
curl -X POST http://localhost:5050/api/ai/batch-analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batchSize": 10, "skipAnalyzed": true}'

# Check batch status
curl http://localhost:5050/api/ai/batch-analyze
```

## UI Component Integration Status

### Actively Displaying Analysis Data

| Component | Location | Themes | Quotes | Analysis |
|-----------|----------|--------|--------|----------|
| ThemeCloud | `/stories` | ✅ | - | - |
| StorytellerInsights | `/storytellers/[id]/dashboard` | ✅ | ✅ | ✅ |
| SuggestedStories | `/stories/[id]` | ✅ | - | Score |
| ValueShowcase | `/world-tour` | ✅ | ✅ | Stats |

### Built But Underutilized

| Component | File | Issue |
|-----------|------|-------|
| QuoteCard (full) | `quote-card.tsx` | Multiple variants built, rarely used |
| AnalysisSummary | `AnalysisSummary.tsx` | Only used in StorytellerInsights |
| StoryCard analysis props | `story-card.tsx` | Props exist but not populated |

### Pages Needing Analysis Integration

1. **Story Detail (`/stories/[id]`)** - No AI analysis displayed
2. **Storyteller Profile (`/storytellers/[id]`)** - No quote gallery
3. **Organisation Analysis (`/organisations/[id]/analysis`)** - Placeholder only
4. **Project Analysis (`/projects/[id]/analysis`)** - Empty shell

## API Endpoints

### Working
- `GET /api/themes` - Theme list with counts
- `GET /api/stories/suggestions` - Related stories
- `GET /api/world-tour/value-dashboard` - Platform analytics
- `GET /api/storytellers/{id}/analytics` - Storyteller insights
- `POST /api/ai/batch-analyze` - Batch AI analysis
- `GET /api/ai/batch-analyze` - Batch status

### To Create/Verify
- `GET /api/quotes/search` - Quote search
- `GET /api/stories/{id}/analysis` - Story-level analysis
- `GET /api/organisations/{id}/themes` - Org theme aggregation

## Recommended Next Steps

1. **Resolve OpenAI quota** - Check billing to continue batch analysis
2. **Run remaining analysis** on 234 pending transcripts
3. **Add AnalysisSummary** to story detail pages
4. **Populate StoryCard** `analysisScore` and `featuredQuote` props
5. **Create QuoteGallery** on storyteller profiles
6. **Implement org-level** theme aggregation

## Database Tables

### narrative_themes
- `id`, `tenant_id`, `theme_name`, `theme_category`
- `ai_confidence_score`, `usage_count`

### storyteller_themes
- `storyteller_id`, `theme_id`, `tenant_id`
- `prominence_score`, `frequency_count`, `source_transcripts`

### storyteller_quotes
- `storyteller_id`, `tenant_id`, `quote_text`
- `source_type`, `source_id`, `source_title`
- `emotional_impact_score`, `wisdom_score`, `quotability_score`
- `themes`, `quote_category`, `is_public`

### storyteller_analytics
- `storyteller_id`, `total_stories`, `total_transcripts`
- `primary_themes`, `last_calculated_at`

## Scripts Created

| Script | Purpose |
|--------|---------|
| `scripts/analysis/sync-all-analysis.ts` | Sync themes, quotes, analytics from analyzed transcripts |
| `scripts/analysis/run-batch-analysis.ts` | Run AI analysis on pending transcripts (standalone) |
| `scripts/analysis/deep-transcript-analysis.ts` | Deep analysis with sentiment and narrative arc |
| `scripts/analysis/build-theme-connections.ts` | Build theme relationship networks |
