---
name: twitter-api-scenarios
description: Worked curl examples for every Twitter/X endpoint on twitter.fetcher.sh, one per endpoint, including pagination.
---

# Twitter / X — full scenario cookbook

Every call below assumes:

```bash
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
```

Swap the `curl -H "Authorization: Bearer $FETCHER_API_KEY"` prefix for a bare
`curl` if you're paying per call with x402 instead — see the [`fetcher`
skill](../../fetcher/SKILL.md).

## Search

**Everything from one account, newest first:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=from:OpenAI" -G \
  --data-urlencode "sort=Latest" \
  "https://twitter.fetcher.sh/api/search"
```

**Between two dates:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=x402 since:2026-01-01 until:2026-02-01" -G \
  "https://twitter.fetcher.sh/api/search"
```

**Popular posts only, replies excluded:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ai agents min_faves:500 -filter:replies" -G \
  --data-urlencode "sort=Top" \
  "https://twitter.fetcher.sh/api/search"
```

**Next page of a search (reuse the `cursor` from the previous response):**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=ai agents" -G \
  --data-urlencode "cursor=<cursor from previous response>" \
  "https://twitter.fetcher.sh/api/search"
```

**Search accounts by name:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=climate scientist" -G \
  "https://twitter.fetcher.sh/api/search/users"
```

## Profiles

**Resolve a profile by handle:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/handle/nasa"
```

**Extended about/bio info by handle:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/handle/nasa/about"
```

**Profile by numeric ID (once you have it from the handle lookup):**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282"
```

## Timelines and relationships

**A user's tweets:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/tweets"
```

**A user's replies:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/replies"
```

**A user's followers, paginated:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/followers"

# next page
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "cursor=<cursor from previous response>" -G \
  "https://twitter.fetcher.sh/api/user/11348282/followers"
```

**Accounts a user follows:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/user/11348282/followings"
```

## Tweets

**A single tweet:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789"
```

**Replies to a tweet:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789/replies"
```

**Who retweeted a tweet:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/tweet/1234567890123456789/retweeters"
```

## Lists and trends

**A Twitter List's members:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/list/1234567890/members"
```

**A Twitter List's tweets:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://twitter.fetcher.sh/api/list/1234567890/tweets"
```

**Trending topics for a country:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "country=United States" -G \
  "https://twitter.fetcher.sh/api/trends"
```

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official X API vs. a browser scraper
