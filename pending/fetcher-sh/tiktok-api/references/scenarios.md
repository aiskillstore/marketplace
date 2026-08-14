---
name: tiktok-api-scenarios
description: Worked curl examples for every TikTok endpoint on tiktok.fetcher.sh, one per endpoint, including pagination.
---

# TikTok — full scenario cookbook

Every call below assumes:

```bash
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
```

Swap the `curl -H "Authorization: Bearer $FETCHER_API_KEY"` prefix for a bare
`curl` if you're paying per call with x402 instead — see the [`fetcher`
skill](../../fetcher/SKILL.md).

## Search

**Keyword search, default relevance ranking:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=matcha latte" -G \
  "https://tiktok.fetcher.sh/api/post/search"
```

**Most-liked posts this month:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=ai agents" -G \
  --data-urlencode "sortType=MOST_LIKED" \
  --data-urlencode "dateRange=THIS_MONTH" \
  "https://tiktok.fetcher.sh/api/post/search"
```

**Region-scoped search with pagination:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "keyword=streetwear" -G \
  --data-urlencode "region=US" \
  --data-urlencode "cursor=<cursor from previous response>" \
  "https://tiktok.fetcher.sh/api/post/search"
```

## Profiles

**Resolve a profile by handle:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/handle/khaby.lame"
```

## Users

**A user's posts:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6820094808943265798/posts"
```

**A user's followers, paginated:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6820094808943265798/followers"

# next page
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "cursor=<cursor from previous response>" -G \
  "https://tiktok.fetcher.sh/api/user/6820094808943265798/followers"
```

**Accounts a user follows:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/user/6820094808943265798/followings"
```

## Posts

**Look up a post by URL (no need to extract the ID yourself):**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "url=https://www.tiktok.com/@khaby.lame/video/7137423965982686469" -G \
  "https://tiktok.fetcher.sh/api/post"
```

**Look up a post by numeric ID:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/7137423965982686469"
```

**A post's comments:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/7137423965982686469/comments"
```

**Replies to a specific comment:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/post/7137423965982686469/comments/<commentId>/replies"
```

## Hashtags, sounds, and locations

**Resolve a hashtag to its numeric ID:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/handle/fyp"
```

**Posts under a hashtag:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/hashtag/<hashtagId>/posts"
```

**Posts using a specific sound:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/music/<musicId>/posts"
```

**Posts tagged at a location:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://tiktok.fetcher.sh/api/location/<locationId>/posts"
```

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official TikTok API vs. a browser scraper
