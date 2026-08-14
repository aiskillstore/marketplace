---
name: instagram-api-scenarios
description: Worked curl examples for every Instagram endpoint on instagram.fetcher.sh, one per endpoint, including pagination.
---

# Instagram — full scenario cookbook

Every call below assumes:

```bash
export FETCHER_API_KEY="bby_live_xxxxxxxxxxxx"
```

Swap the `curl -H "Authorization: Bearer $FETCHER_API_KEY"` prefix for a bare
`curl` if you're paying per call with x402 instead — see the [`fetcher`
skill](../../fetcher/SKILL.md).

## Profiles

**Full profile by handle (the hero call):**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/handle/natgeo"
```

**Just the numeric ID for a handle:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/userid/natgeo"
```

**Profile by numeric ID:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132"
```

**Search accounts by name:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "query=national geographic" -G \
  "https://instagram.fetcher.sh/api/user/search"
```

## User content

**A user's posts:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/posts"
```

**Posts the user is tagged in (not posted by them):**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/posts/tagged"
```

**A user's reels:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/reels"
```

**A user's currently active stories:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/stories"
```

**A user's followers, paginated:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/followers"

# next page
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  --data-urlencode "cursor=<cursor from previous response>" -G \
  "https://instagram.fetcher.sh/api/user/787132/followers"
```

**Accounts a user follows:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/user/787132/followings"
```

## Posts

**Look up a post by its URL shortcode:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/post/code/CxYzAbC123d"
```

**Comments on a post:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/post/3123456789012345678/comments"
```

## Hashtags, audio, and locations

**Posts under a hashtag:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/hashtag/sunsetphotography/posts"
```

**Reels under a hashtag:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/hashtag/sunsetphotography/reels"
```

**Posts using a specific audio track:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/audio/<audioId>/posts"
```

**Posts tagged at a location:**

```bash
curl -H "Authorization: Bearer $FETCHER_API_KEY" \
  "https://instagram.fetcher.sh/api/location/<locationId>/posts"
```

## See also

- [`endpoints.md`](endpoints.md) — full parameter reference
- [`faq.md`](faq.md) — task-oriented "how do I..." answers
- [`comparison.md`](comparison.md) — fetcher.sh vs. the official Instagram Graph API vs. a browser scraper
