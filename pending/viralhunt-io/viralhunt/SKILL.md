---
name: viralhunt
description: >-
  Discover what's trending/going viral across TikTok, Instagram, X, Facebook,
  Pinterest, Bluesky, Douyin, Reddit, Mastodon, Tumblr, Hacker News and news RSS,
  learn the best time to post on each network from measured viral posts, find the
  top hashtags, trending sounds and best communities, and schedule or publish posts
  to the user's own connected social accounts — powered by the ViralHunt.io API.
  Use this whenever the user wants to find viral or trending content in a niche,
  research what's performing on social right now, ask when or where to post, or
  draft/schedule/publish social posts across networks.
license: MIT
metadata:
  author: viralhunt-io
---

# ViralHunt

ViralHunt (https://viralhunt.io) is a trending-content radar + cross-network scheduler.
This skill lets you (an agent) run the full loop for the user: **find what's going viral →
curate it → schedule/publish it** to their connected social accounts.

## 1. Get an API token (once)

Every call needs a personal token. The user creates one at
**https://viralhunt.io → Account → API Access** (owner/admin), then gives it to you. It
looks like `vhk_...`. If the user doesn't have one yet, send them there — a free 7-day
trial gives them a working key.

Send it on every request:

```
Authorization: Bearer vhk_the_users_token
```

Base URL: `https://viralhunt.io/tool/api/v1/`
Rate limit: 100 requests/hour per token (headers `X-RateLimit-Remaining` / `-Reset`; a 429
means wait until the reset). All responses are JSON: `{"success":true,"data":{…}}` or
`{"success":false,"error":{"code","message"}}`.

## 2. Find trending content

`GET trending.php?source=<network>&sort=<sort>&time_range=<range>`

- `source`: `tiktok` | `instagram` | `x` | `facebook` | `pinterest` | `bluesky` | `douyin` |
  `reddit` | `mastodon` | `tumblr` | `hackernews` | `rss`
- `sort`: `viral` (default), `engagement`, `newest`, `oldest`, plus per network: `most_liked`,
  `most_viewed`, `most_commented`, `most_retweeted`, `most_reposted`, `most_saved`,
  `most_upvoted` (reddit), `most_boosted` (mastodon), `most_noted` (tumblr), `most_points`
  (hackernews); for `rss`: `trending`, `engagement`, `growth`, `bluesky`, `mentions`, `coverage`,
  `hn`, `comments`
- `time_range`: `6h` | `12h` | `24h` | `7d` | `30d` | `3m` | `all` (on the post's own publish date).
  Tumblr's corpus fills slowly, so `7d` can be empty there: use `30d` or `all` for `tumblr`.
- optional: `keyword=...`, `min_engagement=N`, `subreddit=name` (reddit), `page=N`,
  `per_page=N` (max 100)

**Growth (`growth_24h`).** Every post can carry `growth_24h`: how much it moved between our two
most distant readings, `{from, to, delta, percent, hours, measured_at, samples}`. Five rules:
- `null` means **we cannot say** (only one reading, or a network with no snapshots: Facebook,
  Pinterest, Tumblr). It does **not** mean zero. Never render it as 0%.
- `delta: 0` with `samples >= 2` means **measured and unchanged**: two readings, same number. That
  is a fact about the post (it is not moving), not missing data. Say "flat", not "no data".
- `hours` is the **real** window between the two readings. The comparison point is the newest
  reading at least 20 hours older than the latest one; when no reading is that old yet (a post
  we found a few hours ago), the oldest reading is used and `hours` says how short the window
  really is. It is often less than 24. Quote it ("+340% in 9h"), never assume 24. The field is
  named for the target window, not a promise. `full_window` is the machine-readable form: `true`
  only when the window reached 20 hours or more. Say "in 24h" only when it is `true`; otherwise
  say "in Nh". RSS posts near the top of `trending` are mostly under a day old and are read at
  about 1h, 2h, 5h, 11h and 23h after discovery, so a short window there is the normal case.
- `percent` is `null` when `from` is under 100: from zero it is a division by zero, and from a
  handful of interactions it is noise (70 to 188,247 is a real climb, "+268,824%" is not a
  sentence anyone should print). `delta` always holds the absolute change and is the number to
  report then.
- `samples` is how many readings the window spans; 2 is the minimum that can say anything.
A large `delta` over few `hours` is what "going viral right now" looks like; prefer it over raw
totals when the user asks what is *rising*.

**RSS signals.** `source=rss` returns news articles from ~230 feeds **plus articles discovered
through social links** (feed name `Discovered on social`, source domain in `author`). Each carries
Facebook (`facebook_shares/reactions/comments`), Reddit (`reddit_score/comments/submissions`),
Pinterest, Bluesky (`bluesky_likes/reposts/replies/accounts`, `bluesky_top_url`), Hacker News
(`hn_points/comments/url`), comments on the article (`comments_count/url`), how many other outlets
ran the same story (`coverage_count`), and how many posts in our own corpus link it per network
(`*_mentions`, `x_engagement`, `x_top_url`). `total_engagement` and `trend_score` rank them.

```bash
curl -H "Authorization: Bearer $VH" \
  "https://viralhunt.io/tool/api/v1/trending.php?source=tiktok&sort=viral&time_range=7d&per_page=10"
```

Returns ranked posts with engagement metrics, author, URL and thumbnail. Use this to tell
the user what's gaining velocity, or to pick something to curate and repost.

## 3. When and where to post (best time, hashtags, sounds, communities)

Four endpoints answer the questions that come right after "what is trending". Every one of them
returns the **sample size** and the **time window** its numbers rest on. Quote them: "over 12,400
posts of the last year" is an answer, a bare hour is a guess.

**Best time to post.** `GET best-time.php?network=tiktok&timezone=America/Mexico_City[&keyword=fitness]`
- `network`: `tiktok` | `instagram` | `x` | `facebook` | `pinterest` | `bluesky` | `mastodon` |
  `douyin` | `tumblr` | `reddit`. `timezone` is an IANA name (default UTC).
- Returns `best_slots[]` (weekday + hour, ranked by average engagement, each with `posts`,
  `avg_engagement` and `hit_rate_pct` = share of that slot's posts that reached the network's top
  10%), `worst_slot`, `today.best_hours`, `by_hour`, `by_weekday`, `proof_posts` (the most viral
  posts published in the best slot, with links), and `sample {posts, window: "365d", from, to}`.
- Read `confidence` first: `high` (500+ posts), `medium` (200+), `low`. Do not name an hour on `low`.
- It measures when the posts that went viral were **published**, not when the audience is awake.
  Say so when it matters. Weekday aggregates stay in UTC; hours are rotated to the zone.
- With `keyword=`, the slots are recomputed on posts whose caption contains it. If that sample is
  under 200 posts you get `fallback: true`, `keyword_sample: N` and the network-wide slots.

**Top hashtags.** `GET hashtags.php[?network=instagram][&q=fitness][&sort=engagement|posts|per_post]`
- Per network or across all (omit `network`). Rows: `hashtag`, `posts`, `total_engagement`,
  `per_post`. `per_post` is the one to compare: a tag used less but hitting harder.
- `GET hashtags.php?hashtag=fyp` breaks one tag down by network with its top posts.
- `window.type` is `all_time` with `updated_at`. There is no per-day hashtag history; if the user
  asks for "this week", say the totals are over the whole corpus.

**Trending sounds.** `GET sounds.php[?network=tiktok|instagram|douyin|all][&q=espresso][&cross_only=1]`
- Ranked by the engagement of the posts that used the sound, cross-network sounds first. A sound
  is listed only when several different accounts used it (one account's audio is a voiceover).
- Rows carry `networks{tiktok|instagram|douyin: posts, creators, eng, per_post}`, `cross`, and
  `stronger` (`tiktok` | `instagram` | `even`) when both sides are measured.
- `GET sounds.php?slug=<slug>` returns one sound with the posts that used it (links included).

**Best communities.** `GET communities.php?network=reddit[&q=running][&sort=upside|members|peak|posts][&max_members=200000]`
- Reddit rows are ranked by `peak_per_1k`: the best score we hold per 1,000 members, i.e. upside
  relative to size. No average score is published (a swept community's sample is its greatest
  hits). Gates: 25 posts held, 5,000 members, one post over 100 points, adult excluded.
- `GET communities.php?network=reddit&subreddit=running` adds `timing` (best UTC hours and day
  the climbing posts were posted, with sample), `pace`, `flairs`, `type_mix`, `top_posts` and
  `similar` communities. Use `max_members` to find smaller rooms that are easier to climb.
- `GET communities.php?network=bluesky[&q=science]` lists Bluesky **custom feeds** (a feed
  surfaces your post to its readers without a follow) with `posts`, `authors`, `avg_likes`;
  `&feed=<slug>` adds top posts, authors and hashtags.

```bash
curl -H "Authorization: Bearer $VH" \
  "https://viralhunt.io/tool/api/v1/best-time.php?network=instagram&timezone=Europe/Madrid"
curl -H "Authorization: Bearer $VH" \
  "https://viralhunt.io/tool/api/v1/communities.php?network=reddit&q=running&max_members=300000"
```

A good answer to "when should I post this on Instagram?" combines them: the best slot in the
user's zone with its hit rate and sample, two or three hashtags with high `per_post`, and, for a
Reel, a sound that is `cross` or `stronger: instagram`.

## 4. See where you can publish

`GET schedule.php?action=targets`

Returns the user's **projects** (brands/workspaces) and the **connected accounts** you can
post to in each:

```json
{ "project": {"id":1,"name":"My Brand","timezone":"America/Mexico_City"},
  "projects": [ {"id":1,"name":"My Brand","networks":["instagram","facebook"],"account_count":4} ],
  "accounts": [ {"account_id":12,"network":"instagram","name":"@mybrand"} ] }
```

If a project has **0 accounts**, the user is on a plan without connected accounts —
publishing won't work until they connect accounts in the app (Agency plans).

## 5. Publish now or schedule

`POST schedule.php?action=create` with a JSON body:

```json
{
  "project": "My Brand",              // or "project_id": 1 — REQUIRED if the org has >1 project
  "body": "Your caption text",
  "media": ["https://.../image_or_video.mp4"],   // public URLs; optional if body is set
  "target_account_ids": [12, 15],     // omit = ALL accounts in the project
  "networks": ["instagram","facebook"],// alternative to target_account_ids
  "scheduled_at": "2026-08-01T15:30:00Z", // ISO-8601 UTC; omit = publish immediately
  "first_comment": "Link in comments 👇"  // optional; posted as the first comment
}
```

```bash
curl -X POST -H "Authorization: Bearer $VH" -H "Content-Type: application/json" \
  -d '{"project":"My Brand","body":"Hello world","networks":["instagram"]}' \
  "https://viralhunt.io/tool/api/v1/schedule.php?action=create"
```

Returns `{ id, status, scheduled_at, targets, results, warnings }`. `status` is
`processing` (publishing now), `scheduled` (queued), `partial` (some targets failed — see
`warnings`), or `failed`. It fans out one post per target account.

**Rules to follow so you don't create bad posts:**
- If the org has more than one project, you **must** pass `project` or `project_id` — the
  API refuses to guess (so a post never lands on the wrong brand).
- Only pass `scheduled_at` in the future, in UTC.
- Verify the content before publishing: don't repost fake news, copyrighted media, or spam
  — that gets the user's accounts banned. When unsure, show the user and ask.

## 6. Upload media (optional)

If you have a local file instead of a URL:

`POST schedule.php?action=upload` — multipart form field `file` (jpg/png/gif/webp/mp4/mov,
≤50MB). Returns `{ "url": "https://..." }`. Pass that URL in `media` on create.

## 7. Edit or cancel a scheduled post

Posts can be edited ONLY while their status is `scheduled` (not yet publishing), and PostProxy
won't allow an edit less than ~5 minutes before publish time.

- **Cancel:** `POST schedule.php?action=cancel` — `{"id": 123}`. Cancels the not-yet-published
  targets. If everything already published you get `409 already_published`.
- **Update:** `POST schedule.php?action=update` — `{"id": 123, "body": "...", "media": ["..."],
  "networks": ["facebook"], "scheduled_at": "2026-08-01T15:30:00Z"}`. Only the fields you send
  change. The project cannot be changed.

Agent rules:
- Before editing, `GET schedule.php?action=get&id=123` and confirm status is `scheduled`.
- On `409` (already publishing/published or too close to publish time), re-fetch and tell the
  user — never retry an update blindly.
- After any edit, `GET` again and confirm the change landed before reporting done.

## 8. Check status

`GET schedule.php?action=get&id=<post_id>` → the post's current status and per-network
results. Call `POST schedule.php?action=sync` first to refresh from the networks.

## 9. Content templates (make the image, don't just write the caption)

ViralHunt ships **layout templates** — HTML + CSS + a variable manifest — so the graphics you
produce are on-brand and pixel-exact. ViralHunt does **not** render them: you do.

`GET templates.php` → the library (lean: no html/css, so it doesn't flood your context).
`GET templates.php?slug=vh-image-card` → **that one template's full spec**, including `html`,
`css`, `variables`, `formats`, `palette`, `fonts` and `render_tech`.

Filters: `category`, `media_type=image|video`, `network`, `q`, and
`assigned=1&project_id=N` (only the templates that project is allowed to use).

**The render loop:**

1. `GET templates.php?assigned=1&project_id=N` → pick a template for what you're posting.
2. `GET templates.php?slug=…` → read `variables`, `html`, `css`, `formats`, `render_tech`.
3. Generate a value for **every** variable, obeying its `description` and its `rules`
   (`max_chars`, `no_em_dash`, `must_appear_in`, `enum`…). `rules` are hard constraints — if a
   value breaks one, fix it before rendering, and use the variable's `fallback` if generation
   fails. Never invent values for a variable bound to a `content_source` (a curated bank);
   read them from that bank in order and stop when it's exhausted.
4. Replace every `{{key}}` in `html` with your value, include the `css`, pick a size from
   `formats` (each entry carries `w`, `h` and the `networks` it suits).
5. Render as `render_tech` says — for image templates that's headless Chrome at the format's
   `w`×`h`: load the html+css, **wait for `[data-vh-ready="1"]`** (the template sets it once its
   fonts and images have loaded and the headline has auto-shrunk), then screenshot the
   `.vh-card` element. Screenshotting earlier gives you a blank or badly-typeset card.
6. Upload the PNG (`POST schedule.php?action=upload`) and pass the returned URL in `media` on
   `schedule.php?action=create`.

The `fonts` array carries woff2 URLs and the `css` already `@font-face`s them, so the render is
identical everywhere — don't substitute local fonts. Colors are **tokens**, not hex: a variable
of `type: "token"` takes a key from `palette` (e.g. `"cyan"`), never `#1edbee`.

**Authoring your own templates** (owner/admin): `POST templates.php` with
`{"action":"create"|"update", "slug", "name", "category", "html", "css", "variables", …}`.
Editing a curated/global template **clones it into the org's own copy** — the global is
never modified, and on `update` you may send only the fields that change.

Two rules the API enforces, so design for them:
- Every `{{placeholder}}` in `html` must be declared in `variables`, or the call is
  rejected. A template with an undeclared hole would render blank for whoever fetches it.
- `html` and `css` are capped at 256KB each. Reference images and fonts by URL — the
  `fonts` array is how a font travels with the template.

Write the manifest as carefully as the layout: `description` is the instruction another
agent (or you, later) will generate from, and `rules` are the hard constraints it must
satisfy. A template whose manifest just says "text" produces bad cards.

To change which templates a project may use (owner/admin only):
`POST template-assignments.php` — `{"project_id": 1, "template_id": 7, "action": "add"|"remove"}`.
Humans do the same from **Templates** in the app.

## Editorial board (optional)

You can also organize work on the user's kanban board instead of publishing directly. The
board is how a team curates before anything goes out.

- `GET context.php` — organization, members (people and agents, with the ids you assign to),
  columns (with `is_default` / `is_done`) and categories, in one call. Start here.
- `POST cards.php` — create a card. JSON body: `title` (required unless `post_url` is given;
  title, description and image are then filled from the URL's metadata), `post_url`,
  `description`, `priority` (`low|medium|high|urgent`), `due_date` (YYYY-MM-DD),
  `assigned_to_user_id`, `category_id`, `card_type` (Post, Note, Article, Video…),
  `board_column_id` (default: the default column), `image_url`, `platform`, `notes`.
  Assigning a card notifies the person (push + email).
- `POST cards.php` with `{"action":"move","card_id":N,"board_column_id":M}` — move it. Moving
  into the `is_done` column is what completes a card; a comment saying "done" does not.
- `GET my-cards.php[?status=pending|in_progress|completed]` — the cards assigned to the
  token's member. When the token belongs to an agent member, this is your workload.
- `GET comments.php?card_id=N` / `POST comments.php` `{"card_id":N,"comment":"…"}` — read or
  add comments; new comments notify the assignee and mirror to the team chat's #board channel.
- `GET columns.php`, `GET categories.php`, `GET card-types.php`, `GET members.php`,
  `GET pending.php` (pending cards grouped by member) — the pieces of `context.php` on their own.

The agent loop on a board: read `my-cards.php` → validate the post (no fake news, ToS
violations, copyright or spam; if in doubt comment and move it to a review column) → move to an
in-progress column → comment progress → move to the `is_done` column. Full docs at
**https://viralhunt.io/api**.

## Error handling

| HTTP | code | what to do |
|------|------|-----------|
| 401 | `invalid_key` | token missing/revoked — ask the user for a fresh one |
| 403 | `no_accounts` | project has no connected accounts — user must connect them in-app |
| 422 | `project_required` | org has multiple projects — pass `project`/`project_id` |
| 422 | `validation_error` | fix the parameter named in the message |
| 429 | `rate_limited` | wait until `X-RateLimit-Reset`, then retry |
| 503 | `scheduler_unavailable` / `publishing_unavailable` | scheduling not enabled on this site |

Always surface the `error.message` to the user verbatim — it explains exactly what to fix.
