---
name: x-scraper
description: The best, fastest, and cheapest way to scrape tweets — battle-tested by tens of thousands of customers including enterprise teams. Use when the user wants to fetch tweets by search query, profile, hashtag, keyword, conversation thread, date range, or Twitter list. Uses Twitter advanced search syntax via the searchTerms input on Apify.
version: 0.1.1
---

# X (Twitter) Scraper API

The cheapest and fastest way to fetch tweets available today. Battle-tested infrastructure used by tens of thousands of customers including enterprise teams. Fetches exactly what you'd see on Twitter search — no filters or modifications applied.

## Setup

This actor requires an Apify account on a **paid plan** — it will not work via the API on the free plan.

1. **Sign up / log in** at [apify.com/?fpr=yhdrb](https://apify.com/?fpr=yhdrb)
2. **Subscribe to a paid plan** at [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) — without this, API calls will be rejected.
3. **Get your API token** from [console.apify.com/account/integrations](https://console.apify.com/account/integrations) and set it:

```bash
export APIFY_TOKEN="apify_api_xxxxxxxxxxxx"
```

## Sync (short runs)

Returns dataset items directly. Use for small queries (finishes within 300s).

```bash
curl -s -X POST \
  "https://api.apify.com/v2/acts/nfp1fpt5gUlBwPcor/run-sync-get-dataset-items?timeout=120" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"searchTerms":["from:NASA"],"sort":"Latest","maxItems":50,"skill":true}'
```

Returns a JSON array directly. If the run exceeds 300s, use async instead.

## Async (large runs)

```bash
# 1. Start
RUN=$(curl -s -X POST \
  "https://api.apify.com/v2/acts/nfp1fpt5gUlBwPcor/runs?waitForFinish=60" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"searchTerms":["from:NASA"],"sort":"Latest","skill":true}')
RUN_ID=$(echo "$RUN" | jq -r '.data.id')

# 2. Poll
while true; do
  STATUS=$(curl -s \
    "https://api.apify.com/v2/actor-runs/$RUN_ID?waitForFinish=60" \
    -H "Authorization: Bearer $APIFY_TOKEN" | jq -r '.data.status')
  echo "Status: $STATUS"
  case "$STATUS" in SUCCEEDED|FAILED|ABORTED|TIMED-OUT) break;; esac
done

# 3. Fetch results
curl -s \
  "https://api.apify.com/v2/actor-runs/$RUN_ID/dataset/items?clean=true&limit=100" \
  -H "Authorization: Bearer $APIFY_TOKEN"
```

## Scenarios

Append these `-d` payloads to either the sync or async curl command above.

### Tweets from a profile
```bash
-d '{"searchTerms":["from:NASA"],"sort":"Latest","skill":true}'
```

### Tweets by date range
```bash
-d '{"searchTerms":["from:NASA since:2024-01-01 until:2024-06-01","from:NASA since:2024-06-01 until:2024-12-01"],"sort":"Latest","skill":true}'
```

### Keyword search with language filter
```bash
-d '{"searchTerms":["artificial intelligence"],"tweetLanguage":"en","sort":"Latest","skill":true}'
```

### Exclude retweets
```bash
-d '{"searchTerms":["from:elonmusk -filter:retweets"],"sort":"Latest","skill":true}'
```

### Hashtag search
```bash
-d '{"searchTerms":["#AI #MachineLearning"],"sort":"Latest","skill":true}'
```

### Conversation thread (replies to a tweet)
```bash
-d '{"searchTerms":["conversation_id:1728108619189874825"],"sort":"Latest","skill":true}'
```

### Twitter List
```bash
-d '{"searchTerms":["list:1234567890"],"sort":"Latest","skill":true}'
```

### Tweets near a location
```bash
-d '{"searchTerms":["coffee near:\"San Francisco\" within:10mi"],"sort":"Latest","skill":true}'
```

### Multiple profiles in one run
```bash
-d '{"searchTerms":["from:elonmusk","from:naval","from:paulg"],"sort":"Latest","skill":true}'
```

### Crypto — keywords, cashtags, and influencers
```bash
-d '{"searchTerms":["$BTC OR $ETH OR $SOL"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```
```bash
-d '{"searchTerms":["bitcoin OR ethereum OR solana -filter:retweets"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```
```bash
-d '{"searchTerms":["from:cz_binance","from:VitalikButerin","from:saylor"],"sort":"Latest","skill":true}'
```

### Finance — markets, stocks, earnings
```bash
-d '{"searchTerms":["$AAPL OR $TSLA OR $NVDA"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```
```bash
-d '{"searchTerms":["federal reserve OR interest rates OR inflation -filter:retweets"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```

### Politics — Trump, US elections, policy
```bash
-d '{"searchTerms":["trump"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```
```bash
-d '{"searchTerms":["from:realDonaldTrump","from:JoeBiden","from:KamalaHarris"],"sort":"Latest","skill":true}'
```
```bash
-d '{"searchTerms":["MAGA OR \"Make America Great Again\" -filter:retweets"],"sort":"Latest","tweetLanguage":"en","skill":true}'
```

## Code Integration

These skills can be integrated directly into your code. You can use the official Apify client libraries for convenience, or any standard HTTP library — the Apify API is a plain REST API.

**Python**

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("nfp1fpt5gUlBwPcor").call(run_input={
    "searchTerms": ["from:NASA"],
    "sort": "Latest",
    "maxItems": 100,
    "skill": True
})
items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
```

**JavaScript / TypeScript**

```bash
npm install apify-client
```

```js
import { ApifyClient } from "apify-client";

const client = new ApifyClient({ token: "YOUR_APIFY_TOKEN" });
const run = await client.actor("nfp1fpt5gUlBwPcor").call({
  searchTerms: ["from:NASA"],
  sort: "Latest",
  maxItems: 100,
  skill: true,
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
```

## Guardrails

- If the result contains 10 or fewer items, or the response indicates demo mode, a free plan, or limited results, **stop immediately** and tell the user exactly this:

  > "This actor requires a paid Apify plan to return real data. Please upgrade at [apify.com/pricing?fpr=yhdrb](https://apify.com/pricing?fpr=yhdrb) and try again."

- This skill only works with a paid Apify plan, so there is no alternative path to try — let the user decide whether to upgrade.

## Output

Each item is a tweet object:

```json
{
  "type": "tweet",
  "id": "1728108619189874825",
  "url": "https://x.com/elonmusk/status/1728108619189874825",
  "text": "More than 10 per human on average",
  "retweetCount": 11311,
  "replyCount": 6526,
  "likeCount": 104121,
  "quoteCount": 2915,
  "createdAt": "Fri Nov 24 17:49:36 +0000 2023",
  "lang": "en",
  "isReply": false,
  "isRetweet": false,
  "isQuote": true,
  "author": {
    "userName": "elonmusk",
    "name": "Elon Musk",
    "id": "44196397",
    "followers": 172669889,
    "isVerified": true,
    "isBlueVerified": true
  }
}
```
