---
name: detect-ai
description: Analyze text to detect if it was written by AI. Returns a score from 0-100 with detailed metrics. Use when checking content before publishing or submitting.
user-invocable: true
argument-hint: [text to analyze]
allowed-tools: WebFetch
---

# Detect AI Content

Analyze text to determine if it was written by AI using the HumanizerAI API.

## How It Works

When the user invokes `/detect-ai`, you should:

1. Extract the text from $ARGUMENTS
2. Call the HumanizerAI API to analyze the text
3. Present the results in a clear, actionable format

## API Call

Make a POST request to `https://humanizerai.com/api/v1/detect`:

```
Authorization: Bearer $HUMANIZERAI_API_KEY
Content-Type: application/json

{
  "text": "<user's text>"
}
```

## API Response Format

The API returns JSON like this:

```json
{
  "score": {
    "overall": 82,
    "perplexity": 96,
    "burstiness": 15,
    "readability": 23,
    "satPercent": 3,
    "simplicity": 35,
    "ngramScore": 8,
    "averageSentenceLength": 21
  },
  "wordCount": 82,
  "sentenceCount": 4,
  "verdict": "ai"
}
```

**IMPORTANT:** The main AI score is `score.overall` (not `score` directly). This is the score to display to the user.

## Present Results Like This

```
## AI Detection Results

**Score:** [score.overall]/100 ([verdict])
**Words Analyzed:** [wordCount]

### Metrics
- Perplexity: [score.perplexity]
- Burstiness: [score.burstiness]
- Readability: [score.readability]
- N-gram Score: [score.ngramScore]

### Recommendation
[Based on score.overall, suggest whether to humanize]
```

## Score Interpretation (use score.overall)

- 0-20: Human-written content
- 21-40: Likely human, minor AI patterns
- 41-60: Mixed signals, could be either
- 61-80: Likely AI-generated
- 81-100: Highly likely AI-generated

## Error Handling

If the API call fails:
1. Check if HUMANIZERAI_API_KEY is set
2. Suggest the user get an API key at https://humanizerai.com
3. Provide the error message for debugging
