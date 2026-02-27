---
name: humanize
description: Transform AI-generated text into natural, human-like content that bypasses AI detectors like GPTZero, Turnitin, and Originality.ai. Uses credits based on word count.
user-invocable: true
argument-hint: "[text to humanize] [--intensity light|medium|aggressive]"
allowed-tools: WebFetch
---

# Humanize AI Text

Transform AI-generated content into natural, human-like writing using the HumanizerAI API.

## How It Works

When the user invokes `/humanize`, you should:

1. Parse $ARGUMENTS for text and optional --intensity flag
2. Call the HumanizerAI API to humanize the text
3. Present the humanized text with before/after scores
4. Show remaining credits

## Parsing Arguments

The user may provide:
- Just text: `/humanize [their text]`
- With intensity: `/humanize --intensity aggressive [their text]`

Default intensity is `medium`.

## Intensity Levels

| Value | Name | Description | Best For |
|-------|------|-------------|----------|
| `light` | Light | Subtle changes, preserves style | Already-edited text, low AI scores |
| `medium` | Medium | Balanced rewrites (default) | Most use cases |
| `aggressive` | Bypass | Maximum bypass mode | High AI scores, strict detectors |

## API Call

Make a POST request to `https://humanizerai.com/api/v1/humanize`:

```
Authorization: Bearer $HUMANIZERAI_API_KEY
Content-Type: application/json

{
  "text": "<user's text>",
  "intensity": "medium"
}
```

## Response Format

Present results like this:

```
## Humanization Complete

**Score:** X → Y (improvement)
**Words Processed:** N
**Credits Remaining:** X

---
### Humanized Text

[The humanized text]

---

[Recommendation based on final score]
```

## Credit Usage

- 1 word = 1 credit
- Detection is free
- Check credits at https://humanizerai.com/dashboard

## Error Handling

### Insufficient Credits
If the user doesn't have enough credits:
1. Show how many credits are needed vs available
2. Direct them to https://humanizerai.com/dashboard to top up

### Invalid API Key
1. Check HUMANIZERAI_API_KEY environment variable
2. Direct to https://humanizerai.com to get a key

### Rate Limit
If rate limited, suggest waiting or upgrading to Business plan.
