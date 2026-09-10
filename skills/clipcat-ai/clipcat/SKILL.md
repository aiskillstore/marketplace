---
name: clipcat
description: All-in-one TikTok Shop selling-video skill for any AI agent (Claude Code, Codex, WorkBuddy, OpenClaw). Find viral TikTok videos, research TikTok Shop products, shops, creators and live rooms, break down why a video sells (script, scenes, hooks, music), search the largest library of real high-GMV AI selling videos and their reverse-engineered prompts and turn the closest match into a ready-to-shoot prompt for your own product, replicate a winning video, turn product photos into AI selling / UGC / talking-head / product-demo videos, generate e-commerce images from a text prompt, upscale results to 1080p or 2K, and download TikTok or Douyin videos. Keywords — AI selling video, TikTok viral replication, TikTok Shop product research, competitor shop analysis, creator and influencer ranking, AI selling video prompt library, product-to-video, UGC video generator, AI product image, TikTok video downloader. Use whenever the user needs TikTok e-commerce data, viral video research, or AI video/image generation.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["CLIPCAT_API_KEY"] },
        "primaryEnv": "CLIPCAT_API_KEY",
      },
    "homepage": "https://clipcat.ai",
  }
---

# Clipcat CLI

This skill is intentionally short. Detailed flags and supported values belong to the CLI itself — always treat `clipcat -h` and `clipcat <subcommand> -h` as the primary reference. The one thing `-h` cannot be current about is the model catalog: models come and go between releases, so `clipcat models` is the authority on which models, resolutions and durations exist right now.

## Installation

Run `clipcat --version` first — if it prints a version, clipcat is installed; skip to API key. If the command is missing, install for the platform:

macOS / Linux / Git Bash:

```bash
curl -fsSL https://clipcat.ai/cli | bash
```

Windows (PowerShell, no bash):

```powershell
irm https://clipcat.ai/cli.ps1 | iex
```

Then set the API key (see below). Update later with `clipcat update` (re-runs the installer; your saved config is preserved).

### Windows sandbox note (Codex etc.)

If the Windows install fails with `SEC_E_NO_CREDENTIALS`, `AcquireCredentialsHandle`, `0x8009030E`, "The underlying connection was closed", or 「基础连接已经关闭」, you are in a restricted sandbox (e.g. the Codex Windows sandbox) where the Windows TLS stack (Schannel) can't open credentials — `Invoke-WebRequest` and system `curl.exe` both fail there. The installer automatically retries the download through Node (its OpenSSL bypasses Schannel), so installing Node in the sandbox usually fixes it. If it still fails, **show the install command to the user and ask them to run it in a normal PowerShell outside the sandbox, or to approve running it outside the sandbox — do not keep retrying with different commands.**

## API key

Configure the key in the local config file — the only reliable method:

```bash
clipcat config --api-key <your-key> --base-url https://clipcat.ai
```

Get the key at https://clipcat.ai/workspace?modal=settings&tab=apikeys. Prefer the config file over the `CLIPCAT_API_KEY` environment variable: sandboxed agents (e.g. Codex) filter out env vars whose names contain KEY/SECRET/TOKEN, so it is usually invisible there. (OpenClaw injects `CLIPCAT_API_KEY` automatically; when set, it overrides the config file.)

## What this CLI is for

`clipcat` is the local entrypoint for all Clipcat AI video generation workflows:

- Query TikTok e-commerce data: creators, products, shops, videos, lives, search
- Generate a ready-to-shoot selling-video prompt from the viral prompt library
- Replicate viral videos with your product
- Generate product videos from images
- Generate AI images from text prompts using GPT Image 2 (with optional reference images)
- Analyze videos (script, scenes, music)
- Download TikTok/Douyin videos
- Query async task status

## Default agent workflow

1. Start with `clipcat -h` to see all commands.
2. Before using any command, run `clipcat <subcommand> -h` to see flags.
3. Default to JSON output.
4. Before any credit-consuming video command, quote the exact cost with
   `clipcat quote`, confirm it with the user, and submit with
   `--expected-credits` (see "Confirming cost before paid video commands").
5. If any command prints an update notice on stderr (`⬆ clipcat X is
   available … Run: clipcat update`), run `clipcat update` once, then continue.
   It self-skips when already up to date, so it is safe to run.

## Choosing the right command

### TikTok e-commerce data — entity commands

These are noun-verb commands: `clipcat <entity> <verb>`. Run `clipcat <entity> -h`
to list verbs and `clipcat <entity> <verb> -h` for flags.

- `creator <list|rank|profile|enrich|trend|posts|sales-videos|lives|products|followers|following|region|milestones>` — TikTok creators/influencers
- `product <list|rank|detail|trend|reviews|live-comments|creators|videos|lives>` — TikTok Shop products
- `seller <list|rank|detail|trend|catalog|inventory|creators|videos|lives>` — TikTok Shop shops
- `video <list|rank|snapshot|sales|trend|comments|captions|products|hashtag>` — TikTok videos
- `live detail` — live-room detail (only while live)
- `find <creators|products|videos|lives|hashtags|music|photo|all>` — keyword/image search; `find all` is the broad fallback

**Two data sources, and the command name already picks one for you.** There is no
`--mode` flag to reason about — pick by what you need back:

| You need | Command | What you get | What you don't |
|---|---|---|---|
| A creator's recent posts | `creator posts` | any public creator, newest first | no per-video sales/GMV |
| A creator's shoppable videos | `creator sales-videos` | sales + GMV per video, sortable | only creators in the historical dataset |
| A creator's profile now | `creator profile` | any public creator | no cumulative commerce metrics |
| Commerce metrics for many creators | `creator enrich` | batch ≤10, cumulative metrics | only collected creators |
| One video's current state | `video snapshot` | any public video | no sales/GMV |
| Sales for videos you already have ids for | `video sales` | batch ≤10, sales + GMV | only collected videos |
| Reviews you can filter by rating | `product reviews` | rating filters, paging | slightly staler |
| The freshest comments | `product live-comments` | latest, needs `--region` | no rating filter |
| A shop's history incl. removed items | `seller catalog` | sales + GMV, sortable | not what's listed right now |
| What a shop lists right now | `seller inventory` | current, needs `--region` | no sales/GMV |

**The historical dataset does not cover everything** (collection is capped by cost),
so the `sales` / `catalog` / `enrich` side answers "not collected" fairly often —
roughly 4-6 times in 10 when the id came from a live search. Ids taken from
`… rank` / `… list` are in the dataset by construction and hit nearly every time.
An empty result there means *not collected*, not *does not exist* — check with the
live command instead of retrying. Never expose the words offline/realtime to end
users; say historical vs. latest data.

**Pagination**: each call returns one page and is billed once. Historical
list/rank commands take `--page` / `--page-size` (**`--page-size` maxes out at 10**;
larger values are clamped and the response says so in `pagination_corrected` — get
more rows with `--page 2`, `--page 3`, …); live lists take `--offset` /
`--cursor` / `--scroll-param` echoed back from a prior page. Fetch more by
repeating the command page by page (`--max-pages` is deprecated and ignored).

**The two data sources do not share a paging scheme.** Historical commands
(`creator sales-videos`, `product reviews`, `seller catalog`) page by number; their
live counterparts (`creator posts`, `product live-comments`, `seller inventory`)
page by cursor, and a page number cannot become a cursor. If you page a live list
with `--page`, the CLI rejects it outright; if an older client sends it anyway,
the response carries `pagination_ignored` — that means **this is the source's first
page**, not the page you asked for. Stop paging by your original number and continue
with the token in `next`; repeating the number returns the same rows and bills 6
credits again.

**Empty is an answer, not a failure.** The historical dataset does not cover
everything, so an empty result usually means "not in that dataset" rather than "no
such thing". The response then carries `try_instead` with a ready-to-run command for
the other source, plus what you gain (live: full coverage, no sales/GMV; historical:
sales/GMV and sorting, covered entities only) and any flags you still need to add.
Switching sources is a separate billed call — switch only if you need those fields.
Do not retry the same empty query.

**Errors tell you whether to retry.** Failures carry `error_kind` and `retryable`:
`transient` (rate limit or a brief wobble — retry the same command in a few
seconds), `invalid_params` (the message says exactly what is wrong — fix the flag,
never retry as-is), `temporarily_unavailable` (retrying will not help; change the
query or come back later).

**Insufficient credits**: read commands cost 6 credits each (`prompt search` is 3, charged only after the free allowance included with your plan is used up); below that balance they error out and return no data.

**Data-query playbook (dense):**

- **Chain ids, don't guess them.** Discover first (`<entity> list|rank`, `find …`),
  take the id from the result, then call detail / trend / relationship verbs.
  Batch verbs take **comma-separated ids** (`--user-ids`, `--product-ids`,
  `--video-ids`, ≤10).
- **Where the id came from decides which command can answer.** Ids from `find …`
  (live search) are any public entity, so follow them with the live commands —
  `video snapshot`, `creator posts`, `creator profile`. Ids from `… rank` / `… list`
  are in the historical dataset by construction, so those are the ones to follow with
  `video sales`, `creator sales-videos`, `creator enrich`, `seller catalog`. Running a
  live-search id straight into a sales command is the single most common way to burn
  credits on empty results — a `find videos` id misses the sales dataset about 4 times
  in 10. If you need sales figures for something you found live, say so plainly rather
  than paging for data that was never collected.
- **Seed relationships from commerce-active entities.** Sub-resource verbs
  (`creator products|lives`, `product creators|videos|lives`, `seller lives`,
  `video products`) return `[]` for low-activity ids. Pull seeds from `… rank` or a
  sorted `… list` (top sales/followers), not an arbitrary row, or expect empties.
- **`… rank` needs a *recent* `--date`.** Pass any day in the target period — the backend
  auto-snaps it to the period anchor (week→that week's Monday, month→that month's 1st).
  It never silently serves a *different* period: if the period hasn't ended, or its data
  isn't generated yet (T+1, usually after midday), you get `data: []` plus `period`
  (`requested` / `latest_available` / `previous`, each with `anchor`/`start`/`end`) and a
  `hint` naming the exact `--date` to retry with — follow it instead of re-querying the same
  period. The date must fall within the freshness window keyed to `--rank-type`:
  **day ≤30d, week ≤6mo, month ≤12mo** back from *today*. A too-**old** date (e.g. last year)
  is rejected upstream as `rant_type N only support …` — move it **forward toward today**;
  don't switch rank-type.
- **Category filtering is numeric and split by level.** To scope `rank` / `list` to a
  category, first run `category resolve --keyword <term>` (e.g. `lipstick` / `口红`; CJK
  auto-uses the zh tree). It returns each match's level + ancestor ids `{l1_id, l2_id?,
  l3_id?}` (ids work for any region). Pass the id for the level the target command takes:
  **product/seller** rank/list use **L1→`--category-id`, L2→`--category-l2-id`,
  L3→`--category-l3-id`** (`--category-id` is L1-only — don't put an L2/L3 id there).
  The levels you pass must form **one parent-child chain**; a repeated or mismatched id is
  rejected locally (costs nothing) with the offending fields in `issues` and the correct ids
  in `suggested` — copy those and resend. Each entry in `issues` carries `field`, `reason`,
  `value`, a localized `message`, and a structured `detail` (the machine-readable form of
  the same thing — prefer `detail` when branching in code, `message` when showing a human). Then:
  **creator** rank takes any level via `--product-category-id`; **video** rank only
  accepts L1 (`l1_id`) — pass an L2/L3 id there and it is auto-lifted to its L1 ancestor,
  which **widens** the filter (the response says so in `category_level_corrected`). Low-confidence `hint` → run `category tree` (L1+L2 overview), pick
  the branch by meaning, then `category tree --parent <that L2 id>` to drill into its L3
  leaves. For plain keyword *search* (no leaderboard), `find products --keyword` needs no id.
- **`find products` returns product_id only** (it's a search index). For title /
  price / metrics, chain the ids into `product detail`.
- **Empty `[]` / `null` means "none", not an error.** A repeat of the same empty query may
  come back with `cached: true` + `retry_after` (an ISO timestamp): the backend remembered
  that this filter has no data and re-probes automatically after that time — don't poll it,
  change the filter or move on. Known thin/quirky:
  `creator region` (unreliable → read `region` from `creator profile` instead),
  `video captions` (many videos have none), `live detail` (only while a room is
  live), `seller inventory` (empty when a shop lists nothing right now — use
  `seller catalog` for its history).
- Responses are **server-trimmed to signal** (ids, core metrics, names, key links;
  images already converted to accessible URLs) — no raw-blob handling needed.
- **All monetary values are USD.** Every price / avg-price / GMV field (`min_price`,
  `max_price`, `spu_avg_price`, `*_gmv_*_amt`, …) is a USD-converted number, regardless
  of `--region`; the response carries `"currency": "USD"` to confirm it. Never label
  them with a local symbol like `¥`/`円`. If a report needs the local currency (e.g.
  JPY for a Japan market study), convert from USD using a current FX rate and mark the
  result approximate.

### Viral selling-prompt generator — `clipcat prompt search`

Clipcat's own library of **structured prompts**, each reverse-engineered from a TikTok
video that actually drove sales — every TikTok market and category, ranked by real GMV.
This is not TikTok search: entries here are already broken down and rewritten into a
prompt you can hand to a video model as-is.

**When the user asks for a prompt, idea, script or angle for a selling video, start here
instead of writing one from scratch.** A prompt with a proven video behind it is the whole
point; an invented one is only a guess, and the user cannot tell the two apart.

#### Step 1 — find the closest proven videos

- `prompt search --query "<what you want>"` — semantic + keyword search over the library.
  Describe a feel ("warm indoor light, handheld close-up, real person on camera") or
  name something exact (a brand, `ASMR`, `OOTD`) — both work; the two are fused, so you
  do not have to guess which style of query fits. Optional filters: `--region` (lowercase
  market code), `--category` (TikTok Shop L1 code, e.g. `beauty-personal-care`),
  `--video-type` (`real-review` | `ootd` | `asmr` | `unboxing-pov` | …), `--limit` (1-20).
  Build the query from the user's own product and audience — what it is, who it is for,
  the market, the vibe they asked for. A bare category name ("skincare") retrieves the
  generic middle of the library.
  Priced apart from the other read commands: each paid plan comes with an allowance of
  free searches, and calls beyond it cost 3 credits each (other reads are a flat 6).
  The response carries `quota.remaining` / `quota.free_quota` / `quota.cost_after_quota` —
  tell the user what is left when it runs low instead of letting the next call surprise them.
- **Check `weak_match` and `degraded` before you trust the hits.** The library returns the
  nearest entries it has, so a full result list does not by itself mean the results fit.
  `weak_match: true` means nothing closely matches — say so and suggest rewording or
  dropping a filter, rather than presenting the nearest entries as the answer.
  `degraded: true` means semantic search was unavailable and only keyword matching ran:
  results may be incomplete, and **that search is not charged** (quota is refunded).
  Fewer hits than `--limit` is normal and healthy — only entries relevant enough are
  returned, so a narrow `--region` + `--category` combination legitimately returns a few.

Each hit carries the full `prompt` text (`prompt_en` for the English version), the metrics
of the original video (GMV, sales, views), `matched_facet` (which part of the prompt your
query hit — style / camera / voiceover / …), `source_video_url` for the original TikTok
video, and `detail_url` for the public page.

#### Step 2 — rewrite the hit into the user's own prompt

Never hand back a library prompt unchanged: it sells someone else's product. Rewrite the
best hit (or 2-3 hits that agree on structure — averaging ones that disagree yields a
template) into a prompt for this user's product:

- **Keep what made it sell**: the opening hook and what happens in its first 1-2 seconds,
  shot order and pacing, camera language, lighting, whether a presenter is on camera and
  what kind, voiceover tone, promo mechanic, closing CTA.
- **Swap** the product and its selling points, on-screen text, voiceover lines, and
  anything market-specific (language, currency, local wording).
- **Carry over no claim you cannot back.** Ratings, sales numbers, awards, before/after and
  efficacy claims belong to the original product — drop them, or ask the user for their own.
- **Fit the target model**: keep the prompt inside the `--duration` you will submit and the
  shot count it implies (a 5s clip holds 2 shots, not 6), and pick the voiceover language
  with `--lang`.
- Show the user the finished prompt with the `detail_url` (and `source_video_url`) it was
  built from **before** spending credits — citing the real video is what separates this
  from a prompt you made up.

#### Step 3 — shoot it

- Product images only → `product_video`, passing the rewritten prompt via `--prompt-file -`.
- Want the original video's motion and cuts as the reference → `replicate
  --url <source_video_url>` with the user's `--image`s (a TikTok link adds the 10-credit
  download surcharge).
- Both are paid: `quote` with the exact parameters → confirm with the user → submit with
  `--expected-credits` (see "Confirming cost before paid video commands").

```bash
clipcat prompt search --query "handheld close-up of a serum bottle, warm bathroom light, real user voiceover" \
  --region us --category beauty-personal-care --limit 5
# pick a hit → rewrite its prompt for the user's product → quote and confirm:
clipcat quote --model seedance2 --resolution 480p --duration 8
clipcat product_video --image serum.jpg --model seedance2 --duration 8 \
  --resolution 480p --size 9:16 --expected-credits <totalCredits> --prompt-file - <<'EOF'
<the rewritten prompt>
EOF
```

### Video generation & tools

- `quote` — return the exact credit cost of one specific generation (`--model` + `--resolution` + `--duration`, plus `--url`/`--social` for a TikTok/Douyin replicate, plus `--enhance` for super-resolution). The primary way to quote a paid command: the server does all the math and hands back `totalCredits` (already includes the enhance fee) plus `enhanceCredits` / `enhanceBlocked` (see "Confirming cost before paid video commands" and "Super-resolution").
- `models` — browse all available video models with their credit costs (discrete → `prices`, range → `creditsPerSecond`) and your balance. Use it when the user hasn't picked a model yet, or an unavailable one is reported. **The listing is live and only contains tiers that currently have a provider** — a resolution or duration missing from `resolutions` / `prices` is rejected on submit, so never submit a combination you did not see here.
- `replicate` — replicate a viral video with your product images. Reference video via **`--url`** (TikTok/Douyin link or direct URL, auto-detects type) **or `--video`** (local video file, max 100MB, uploaded via presigned URL then downscaled server-side; re-replicating the same file reuses the upload; no download surcharge) — provide exactly one. Product images via `--image` (local) or `--image-url` (URL); local files and URLs can be mixed. Supports `--model`, `--duration`, `--size` (only `9:16` or `16:9`), `--lang`, `--resolution`, `--enhance` (super-resolution, see below), `--character-id`, `--expected-credits`
- `product_video` — generate video from product images only (no reference video); images via `--image` (local) or `--image-url` (URL); local files and URLs can be mixed; `--size` only accepts `9:16` or `16:9`; supports `--enhance` (super-resolution, see below), `--expected-credits`
- `image` — generate an AI image from a text prompt using **GPT Image 2** model; optionally supply up to 5 reference images via `--image` (local file) or `--image-url` (URL). Use `--aspect-ratio` to pick `1:1` (default) / `16:9` / `9:16`. **Dimension hints (9:16/16:9/1:1, portrait/landscape/square, 竖版/横版/方图, banner, wallpaper) must appear in BOTH `--prompt` and `--aspect-ratio`** — `--aspect-ratio` sets canvas, the prompt hint anchors framing. Don't invent dimensions the user didn't ask for.
- `list_images` — list image generation tasks from server; supports `--status` / `--limit` / `--page` filters, plus `--scope all` / `--scope <member-user-id>` (owners/admins only; adds `creatorName`)
- `breakdown` — analyze a video (script, scenes, music); returns cached result immediately if previously analyzed
- `download` — download TikTok/Douyin video (returns signed URL); cached results return immediately
- `query_task` — check status of a task by ID and type (`--type replicate | product | breakdown | download | image`). Omit `--task-id` to resume the latest local task. With `--enhance`, each `videos[]` item carries its own `status` / `enhanceStatus` (see "Super-resolution"). Workspace owners/admins may also query their members' tasks.
- `list_tasks` — list recent **video-related** tasks from server (`--type` required: `replicate | product | breakdown | download`). Image tasks use `list_images`. `--scope all` / `--scope <member-user-id>` widens to the workspace (owners/admins only; adds `creatorName`), default is your own tasks.
- `character list` — list the characters saved to your account (`id`, `name`, `status`, `type`). The `id` is what you pass to `--character-id` on `replicate` / `product_video`; only `status: completed` characters are usable. Supports `--status` / `--limit` / `--page` / `--sort-by` / `--sort-order`, plus `--scope all` / `--scope <member-user-id>` (owners/admins only; adds `creatorName`). Free (account metadata, no credits).

## Passing prompts (never let the shell mangle them)

A mis-escaped `--prompt \"Create a 5s video\"` reaches the CLI as `"Create` — cut at the
first space. Both the CLI and the server now reject that instead of charging for a garbage
video, but the fix is to pass prompts so it cannot happen:

- Prompt contains quotes, newlines, `$`, or backticks → use stdin, not an inline flag:

  ```bash
  clipcat product_video --image-url <url> --model seedance2 --duration 5 \
    --expected-credits 100 --prompt-file - <<'EOF'
  Create a 5-second UGC demo. The narrator says "this changed my routine".
  EOF
  ```

  The quoted delimiter `<<'EOF'` disables every kind of expansion — zero escaping needed.
  This works in bash / zsh / Git Bash. **On Windows PowerShell, do NOT pipe — write a UTF-8
  file and pass its path:**

  ```powershell
  Set-Content -Encoding utf8 prompt.txt @'
  Create a 5-second UGC demo. The narrator says "this changed my routine".
  '@
  clipcat product_video --image-url <url> --prompt-file prompt.txt
  ```

  Why not pipe on Windows: **Windows PowerShell 5.1** encodes pipe output to native programs
  with `$OutputEncoding`, which **defaults to ASCII** — every Chinese/non-ASCII character
  silently becomes `?`, and a prompt of `????????` looks perfectly valid to every quoting check.
  If you must pipe, run `$OutputEncoding = [System.Text.Encoding]::UTF8` first. (PowerShell 7
  defaults to UTF-8 everywhere and is not affected, but the file-based form above works on both,
  so just use it.) Also note `@'` must end its line and `'@` must start its own line — a
  single-line `@' … '@` is a syntax error. On 5.1, `Out-File` is not a substitute for
  `Set-Content -Encoding utf8`: it defaults to UTF-16, which the CLI rejects outright.

- **Never read a file into a string and pass it inline** — no `--prompt (Get-Content p.txt)`.
  On PowerShell 5.1 `Get-Content` decodes a UTF-8 file as ANSI, producing mojibake that is
  valid UTF-8 with no quoting anomaly: every check passes and you get charged for a garbage
  video. Pass the **path** (`--prompt-file p.txt`) and let the CLI read the bytes.

- Short single-line prompts may stay inline as `--prompt "…"`. Never backslash-escape the
  outer quotes, and never wrap an already-quoted string in another layer of quotes.
- `--prompt` and `--prompt-file` are mutually exclusive (`-` = stdin, otherwise a file path).
- After submit the CLI prints `Prompt sent (N chars): …`. Check it against what you intended;
  a wrong N means the command line was mangled, not the prompt you wrote.
- If a submit is rejected for a mis-quoted prompt, do NOT retry the same command — re-send it
  via `--prompt-file -`. Rejections happen before any charge.

## Confirming cost before paid video commands

`replicate` and `product_video` consume credits. Always confirm cost first — and
**never compute the credits yourself**, let `clipcat quote` return them:

1. Run `clipcat quote` with the SAME parameters you'll submit (`--model`,
   `--resolution`, `--duration`; for a TikTok/Douyin replicate also pass the
   `--url`, which auto-adds the download surcharge; for super-resolution also pass
   `--enhance`). It returns `totalCredits` (the server does all the math —
   per-second rates, download surcharge, deferred enhance fee) and your
   `remainingCredits`.
2. Show the user the model, duration, resolution and that `totalCredits`, and get
   explicit approval.
3. Submit with `--expected-credits <totalCredits>`. The server rejects the request
   only if the real cost is **higher** than what you pass, so you can never
   overcharge (a cheaper real cost — cache hit, promo — just goes through). On a
   rejection it returns the current cost — re-confirm that number with the user
   and resubmit with the updated `--expected-credits`.

Example — quote, then submit the confirmed cost (Seedance 2, 480p default, 8s, TikTok link):

```bash
clipcat quote --model seedance2 --resolution 480p --duration 8 \
  --url "https://www.tiktok.com/@u/video/123"
# → seedance2 480p 8s → 160 credits  + 10 download → total 170 credits
clipcat replicate --url "https://www.tiktok.com/@u/video/123" \
  --image product.jpg --model seedance2 --duration 8 --resolution 480p \
  --size 9:16 --expected-credits 170
```

When the user hasn't chosen a model yet (or you need the full menu), run `clipcat
models` to list every available model and its cost, then `clipcat quote` the pick.

Premium models (e.g. `seedance2`, `happyhorse10`) require a paid plan; `clipcat
quote` flags them (`premiumBlocked`) and the server rejects them for free users.

## Super-resolution (`--enhance`)

`replicate` and `product_video` accept `--enhance 720p|1080p|2k` to upscale the
finished video. Rules:

- **Tier must be strictly higher than the generated resolution**: 480p → 720p /
  1080p / 2k, 720p → 1080p / 2k, 1080p → 2k, 2k → no option. The CLI only
  enum-checks the value; the server enforces the tier ladder.
- **Paid plans only.** Free users are rejected on submit; `clipcat quote --enhance`
  flags this as `enhanceBlocked: true` (upgrade needed).
- **Cost** = ceil(duration_sec / 10) × tier rate (`720p`=10, `1080p`=20, `2k`=30
  credits per 10s). It is **deferred** — charged only after the base video
  succeeds. `quote` returns it as `enhanceCredits`, already folded into
  `totalCredits`; submit that `totalCredits` via `--expected-credits`.
- **Status semantics** (`query_task`): once the base video is ready it appears in
  `videos[]` with `status: enhancing` and a usable `videoUrl` (the original), but
  the **task reaches its final completed state only after enhance finishes** (a
  standard 1-min video takes ~6-10 min extra). `enhanceStatus: failed` → the task
  still completes and delivers the original video, and the enhance fee is refunded.

```bash
clipcat quote --model seedance2 --resolution 480p --duration 8 --enhance 1080p
# → seedance2 480p 8s → 160 credits  + 20 enhance (1080p) → total 180 credits
clipcat product_video --image product.jpg --model seedance2 --duration 8 \
  --resolution 480p --size 9:16 --enhance 1080p --expected-credits 180
```

## replicate: reference video source

`clipcat replicate` takes the reference video via **exactly one** of `--url` / `--video`:

- `--url` **TikTok/Douyin link** → calls `/replicate_from_social` (costs **10 extra credits** for download)
- `--url` **direct video URL** → calls `/replicate`
- `--video` **local file** (max 100MB) → uploaded via presigned URL, then `/replicate` (no download surcharge). Uploading the same file again is deduplicated (content-hashed, per-user), so repeat replications skip the upload.

Always inform the user about the extra 10 credits before running with a social `--url`.

## clipcat:// asset references

`clipcat://...` strings seen in earlier turns are stable asset references. Pass them **verbatim** to any `--image-url` / `--character-id` flag — never prepend `https://` or modify them; the server resolves them to a signed URL. A mistyped reference is rejected up front (no credits charged), so never retype one from memory. See subcommand `-h` for details.

`--character-id` accepts three forms: a numeric id from `clipcat character list` (never guess ids), `@<sora-username>`, or an image URL / `clipcat://` reference.

## Async task rules

`replicate`, `product_video`, `image`, and `breakdown` are async. All four
**submit and return immediately** with a task ID — they never block.

Typical durations: `image` ~3 min, `breakdown` a few minutes, `product_video` /
`replicate` 10+ min. **Never try to wait synchronously inside a single tool
call** — every realistic agent harness has a tool-call timeout (commonly 60s)
that will kill the call long before the task is done. Always go submit → return
→ poll across turns.

1. Task ID is saved locally to `~/.clipcat/tasks.json` automatically.
2. Check status with `clipcat query_task --task-id <id> --type <type>`. Each
   call returns immediately with the current status. Omit `--task-id` to resume
   the latest task. Re-invoke the command across turns (suggested cadence:
   ~30s for `image`, ~1-2 min for `breakdown` / `product_video` / `replicate`)
   until `status` is `completed` or `failed`.
3. Use `clipcat list_tasks --type <replicate|product|breakdown|download>` to
   see tasks of a given type from the server.

## query_task: auto-resume

`clipcat query_task` with no flags automatically reads the latest task from `~/.clipcat/tasks.json` and resumes it. No need to remember task IDs.

## Available models

Trial models are available to all users; standard models require a paid plan.

| Model ID             | Duration              | Resolution        | Notes                                                             |
| -------------------- | --------------------- | ----------------- | ----------------------------------------------------------------- |
| `grok_imagine`       | 10s, 15s              | 480p, 720p        | **Trial**, default. xAI Grok Imagine 1.5, 9:16 aspect ratio only   |
| `veo3.1fast`         | 8s, 16s, 24s          | 720p              | **Trial**. Google Veo 3.1 Fast, balanced quality and cost          |
| `omini_flash`        | 10s, 20s              | 720p, 1080p       | **Trial**. Gemini Omni Flash, Google's newest model                |
| `seedance2_mini`     | 4-15s (any integer)   | 480p, 720p        | **Trial**. Seedance 2 Mini, value tier. Free plans are 480p only — **pass `--resolution 480p` explicitly** |
| `mmh3_promo`         | 10s, 15s              | 480p, 720p, 2K    | **Trial**. Subsidized MiniMax H3 channel, open to free plans       |
| `seedance2`          | 4-15s (any integer)   | 480p, 720p, 1080p | Standard (paid). ByteDance Seedance 2, top quality. **Default 480p** |
| `seedance2_5`        | 4-30s (any integer)   | 480p, 720p        | Standard (paid). ByteDance Seedance 2.5, newest generation, clips up to 30s. **Default 480p** |
| `seedance2_fast`     | 4-15s (any integer)   | 480p, 720p        | Standard (paid). ByteDance Seedance 2 Fast, fast variant. **Default 480p** |
| `wan30`              | 5-30s (any integer)   | 480p, 720p, 1080p | Standard (paid). Alibaba Wan 3.0, clips up to 30s                  |
| `minimax_h3`         | 10s, 15s              | 768p, 2K          | Standard (paid). MiniMax H3                                        |
| `happyhorse10`       | 3-15s (any integer)   | 720p, 1080p       | Standard (paid). Alibaba HappyHorse 1.1                            |

`clipcat models` is the authority on both the model list and the live
per-combination credit costs — a model missing there has been retired and is
rejected on submit, whatever `-h` or this table says. Prefer `mmh3_promo` over
`minimax_h3` whenever `clipcat models` lists it: same model on a limited-time
subsidized channel, a fraction of the credits, and free plans may use it.

The tiers in this table are what each model *offers*; `clipcat models` is what is
*available right now*. Providers get disabled for maintenance, so a listed tier can
temporarily disappear. If a submit is rejected with **"no available channel"**, the
parameters were valid but that tier has no provider at the moment — re-run `clipcat
models`, pick another resolution/duration/model from the fresh listing, re-quote and
re-confirm with the user. Do not retry the same combination.

**`seedance2`, `seedance2_5` and `seedance2_fast` default to `--resolution 480p`** (the CLI
applies this in `quote`, `replicate` and `product_video` when `--resolution` is
omitted). Only pass a higher resolution when the user explicitly asks for one,
and keep `quote` and the submit on the same value.

`seedance2_mini` is **not** covered by that automatic default: free plans can only
use its 480p tier, so omitting `--resolution` sends the server default (720p) and
the submit is rejected. Pass `--resolution 480p` explicitly on both the `quote` and
the submit.

## Supported languages (`--lang`)

`en` `zh` `fr` `de` `ms` `vi` `th` `ja` `ko` `id` `fil` `es`

## Region (`--region`)

ISO 3166-1 alpha-2, uppercase: `US` `GB` `DE` `ES` `FR` `IT` `JP` `MX` `BR` `ID` `MY` `PH` `SG` `TH` `VN`. Server-enforced; an out-of-range code returns the current allowed list.

## Good agent behavior

- Run `clipcat -h` first if unsure which command to use.
- Asked for a selling-video prompt / idea / script: run `clipcat prompt search` first,
  rewrite the closest proven hit for the user's product, and cite its `detail_url`.
  Writing one from imagination throws away the only thing that makes it a viral prompt.
- For paid video commands (`replicate`, `product_video`): quote the exact cost with `clipcat quote` (same params you'll submit), show the user the model / duration / resolution / `totalCredits`, get explicit approval, then submit with `--expected-credits <totalCredits>`. Never compute the credits yourself — let `clipcat quote` return them.
- Resolution: always quote and submit at the model's default (`480p` for `seedance2` / `seedance2_5` / `seedance2_fast`) unless the user explicitly asked for a higher one. Never silently upgrade to 720p/1080p — higher resolution costs more credits.
- Pass any non-trivial prompt via `--prompt-file -` with a quoted heredoc (see "Passing prompts"); verify the `Prompt sent (N chars)` echo after submit.
- Keep record of task IDs; re-invoke `query_task` across turns to track long-running tasks.
- Preserve signed video URLs intact — they contain `X-Amz-*` params that break if truncated.
- Agents should prefer the default JSON output.
