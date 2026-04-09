---
name: soultrace
description: "Take a personality assessment via the SoulTrace API. Use when the user wants to take a personality test, discover their psychological archetype, understand their personality traits, or get a color-based personality profile. The API uses a 5-color psychological model (White=structure, Blue=understanding, Black=agency, Red=intensity, Green=connection) with Bayesian adaptive question selection to classify users into one of 25 archetypes. Triggers on: personality test, personality assessment, what's my personality, take a quiz, archetype test, color personality, soultrace."
---

# SoulTrace Personality Assessment

Take an adaptive personality assessment through the SoulTrace API. Answer 24 questions on a 1-7 Likert scale and receive your personality archetype based on a 5-color psychological model.

## API Endpoint

```
POST https://soultrace.app/api/agent
```

No authentication required. Rate limited to 100 requests/hour per IP.

## How It Works

The API is **stateless**. You pass all accumulated answers with every request, and the server replays the Bayesian inference to select the next optimal question.

### Step 1: Start the test

Send an empty answers array to get the first question:

```bash
curl -X POST https://soultrace.app/api/agent \
  -H "Content-Type: application/json" \
  -d '{"answers": []}'
```

Response:
```json
{
  "status": "in_progress",
  "question": {
    "id": 42,
    "text": "I find deep satisfaction in mastering complex systems."
  },
  "currentDistribution": {
    "white": 0.2,
    "blue": 0.2,
    "black": 0.2,
    "red": 0.2,
    "green": 0.2
  },
  "entropy": 2.322,
  "progress": { "answered": 0, "total": 24 }
}
```

### Step 2: Answer questions

The user answers each question on a scale of 1-7:
- **1** = Strongly Disagree
- **4** = Neutral
- **7** = Strongly Agree

Append the answer and send all answers so far:

```bash
curl -X POST https://soultrace.app/api/agent \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"questionId": 42, "score": 6}]}'
```

Keep accumulating answers. Each response gives the next question.

### Step 3: Get results

After 24 answers, the response automatically returns the final result:

```json
{
  "status": "complete",
  "resultId": "abc-123-def",
  "resultUrl": "https://soultrace.app/en/results/abc-123-def",
  "distribution": {
    "white": 0.15,
    "blue": 0.35,
    "black": 0.25,
    "red": 0.10,
    "green": 0.15
  },
  "entropy": 1.89,
  "archetype": {
    "key": "blue-black",
    "name": "Strategist",
    "alignmentScore": 87.3,
    "coreDynamic": "...",
    "strengths": ["..."],
    "weaknesses": ["..."]
  },
  "topMatches": [
    { "key": "blue-black", "name": "Strategist", "alignmentScore": 87.3 },
    { "key": "blue", "name": "Rationalist", "alignmentScore": 82.1 },
    { "key": "black-blue", "name": "Operator", "alignmentScore": 78.5 }
  ],
  "shadowColors": [
    { "color": "red", "score": 0.10 },
    { "color": "green", "score": 0.15 }
  ],
  "progress": { "answered": 24, "total": 24 }
}
```

## Agent Interaction Protocol

When a user asks to take the personality test:

1. **Start** by calling the API with `{"answers": []}`.
2. **Present** each question to the user clearly. Tell them to answer 1-7 (1=Strongly Disagree, 4=Neutral, 7=Strongly Agree).
3. **Collect** the user's numeric answer (1-7). If they give a non-numeric or descriptive answer, map it to the scale:
   - "strongly disagree" / "not at all" → 1
   - "disagree" / "not really" → 2
   - "slightly disagree" → 3
   - "neutral" / "maybe" / "sometimes" → 4
   - "slightly agree" → 5
   - "agree" / "yes" → 6
   - "strongly agree" / "absolutely" → 7
4. **Accumulate** answers and send ALL previous answers plus the new one each time.
5. **After all 24 questions**, present the results with:
   - Their archetype name and alignment score
   - Their color distribution (show as percentages)
   - Their top 3 archetype matches
   - The link to their full results page
6. **Never skip questions** or auto-answer on behalf of the user.

## Score Scale

| Score | Meaning |
|-------|---------|
| 1 | Strongly Disagree |
| 2 | Disagree |
| 3 | Slightly Disagree |
| 4 | Neutral |
| 5 | Slightly Agree |
| 6 | Agree |
| 7 | Strongly Agree |

## The 5 Colors

| Color | Drive | Essence |
|-------|-------|---------|
| White | Structure, fairness | Order, responsibility |
| Blue | Understanding, mastery | Curiosity, precision |
| Black | Agency, achievement | Ambition, strategy |
| Red | Intensity, expression | Passion, honesty |
| Green | Connection, growth | Belonging, patience |

## Rate Limits

- 100 requests per hour per IP
- Each test requires 25 requests (1 start + 24 answers)
- Maximum ~4 complete tests per hour

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body or answers format |
| 429 | Rate limit exceeded (check `Retry-After` header) |
| 500 | Server error |

## API Info

```bash
GET https://soultrace.app/api/agent
```

Returns API metadata (version, question count, score range).
