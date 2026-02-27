---
name: readability
description: Analyze text readability with Flesch-Kincaid, Gunning Fog, SMOG, and other metrics. Returns objective scores with interpretation and recommendations.
user-invocable: true
argument-hint: "[text to analyze]"
---

# Analyze Readability

Calculate and display readability metrics for the provided text.

## Input

The user provides text in $ARGUMENTS. If no text provided, ask for it.

## Metrics to Calculate

### Core Scores

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **Flesch Reading Ease** | 206.835 - 1.015(words/sentences) - 84.6(syllables/words) | 0-100, higher = easier |
| **Flesch-Kincaid Grade** | 0.39(words/sentences) + 11.8(syllables/words) - 15.59 | US grade level |
| **Gunning Fog Index** | 0.4[(words/sentences) + 100(complex words/words)] | Years of education |
| **SMOG Index** | 1.043 × √(complex words × 30/sentences) + 3.1291 | Grade level |

*Complex words = 3+ syllables*

### Text Statistics

- Word count
- Sentence count
- Average sentence length (words)
- Average word length (characters)
- Complex words count and %
- Passive voice sentences (estimate)

## Output Format

```
## Readability Analysis

### Scores
| Metric | Score | Meaning |
|--------|-------|---------|
| Flesch Reading Ease | [X] | [interpretation] |
| Flesch-Kincaid Grade | [X] | [grade level] |
| Gunning Fog | [X] | [years education] |
| SMOG | [X] | [grade level] |

### Statistics
- Words: [X]
- Sentences: [X]
- Avg sentence length: [X] words
- Complex words: [X] ([Y]%)

### Target Audience
[Who can easily read this based on scores]

### Recommendations
1. [Specific suggestion]
2. [Specific suggestion]
3. [Specific suggestion]
```

## Interpretation Guide

| Flesch Score | Grade | Audience |
|--------------|-------|----------|
| 90-100 | 5th | Very easy |
| 80-89 | 6th | Easy |
| 70-79 | 7th | Fairly easy |
| 60-69 | 8-9th | Standard |
| 50-59 | 10-12th | Fairly difficult |
| 30-49 | College | Difficult |
| 0-29 | Graduate | Very difficult |

## Recommendations

Based on scores, suggest:
- Sentences to shorten (if avg > 20 words)
- Complex words to simplify
- Passive voice to convert to active
- Specific examples of what to fix
