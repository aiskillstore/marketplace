---
name: faceless
description: Create, render and publish AI faceless videos with Faceless.so. Use when the user asks about creating faceless videos, AI video generation from a script, auto-posting to YouTube, TikTok, Instagram or X, automated video series, scheduling short-form content across platforms, or checking Faceless credits and post analytics.
---

# Faceless.so

Faceless.so turns a narration script into a finished faceless video: TTS voiceover, AI-generated visuals, captions and music. Videos render in the cloud and publish to connected YouTube, TikTok, Instagram, X, Facebook, LinkedIn and Threads accounts, either immediately or on a schedule. Series generate and post new episodes automatically.

## When to use this skill

- "Make a faceless video from this script" -> videos create, poll status, render, publish
- "Post this to YouTube Shorts / TikTok" or "schedule it for Friday 6pm" -> posts publish or posts schedule
- "Set up a channel that posts a scary story every day" -> series create
- "Generate the next episode now" -> series generate
- "What is queued? How did my posts do?" -> calendar, analytics
- "How many Faceless credits do I have?" -> credits

## Setup: install the CLI if missing

1. Check the CLI: `faceless --version`
2. If not found, install it: `npm install -g faceless-cli` (or use `npx -y faceless-cli <command>` without installing)
3. Authenticate, one of:
   - `FACELESS_API_KEY` environment variable already set: nothing to do
   - Otherwise ask the user for an API key (created at https://faceless.so/developers) and run `faceless login`
4. Verify: `faceless whoami`

If npm is unavailable, fall back to the raw HTTP API (see the last section).

## Core concepts

- A team owns credits, API keys and connected social accounts; every command runs in the key's team context (`faceless whoami` shows it).
- Credits are charged at video creation time, by model: storyboard 20, motion_lite 50, motion_pro 100 credits per video. Rendering and publishing are free.
- Videos generate asynchronously: `videos create` returns an id immediately; poll `videos status` until completed, then `videos render` and poll `renders get` for the MP4 URL.
- Series are set-and-forget channels: they generate and auto-post a new episode on their schedule, charging the per-episode model cost each time.
- Scheduling to a platform requires that platform's post metadata on the video first (`videos update`), and a connected account (`faceless accounts`).
- Always pass `--json` when running commands from a script or agent and parse the `success` field.

## Command reference

| Command | What it does | Endpoint |
| --- | --- | --- |
| `faceless whoami` | Identify the caller | GET /me |
| `faceless credits` | Credit balance and history | GET /credits |
| `faceless videos create` | Create a faceless video from a script | POST /videos |
| `faceless videos captions` | Caption an existing video or audio file | POST /videos/captions |
| `faceless videos list` | List the team's videos | GET /videos |
| `faceless videos get` | Get one video | GET /videos/{id} |
| `faceless videos update` | Update a video's name or post metadata | PATCH /videos/{id} |
| `faceless videos status` | Poll video generation progress | GET /videos/{id}/status |
| `faceless videos render` | Render a video to MP4 | POST /videos/{id}/render |
| `faceless videos delete` | Delete a video | DELETE /videos/{id} |
| `faceless renders get` | Poll render progress | GET /renders/{id} |
| `faceless series create` | Create an automated video series | POST /series |
| `faceless series list` | List the team's series | GET /series |
| `faceless series get` | Get one series | GET /series/{id} |
| `faceless series update` | Update a series | PATCH /series/{id} |
| `faceless series delete` | Delete a series | DELETE /series/{id} |
| `faceless series generate` | Generate the next episode now | POST /series/{id}/generate |
| `faceless series episodes` | List a series' episodes | GET /series/{id}/episodes |
| `faceless posts publish` | Publish a rendered video to a platform now | POST /posts |
| `faceless posts schedule` | Schedule a video to one or more platforms | POST /posts/schedule |
| `faceless posts cancel` | Cancel a scheduled post | DELETE /posts/{id} |
| `faceless calendar` | Posting calendar | GET /calendar |
| `faceless accounts` | List connected social accounts | GET /accounts |
| `faceless voices` | List TTS voices | GET /voices |
| `faceless options` | List content option catalogs | GET /options |
| `faceless assets create` | Register a media asset by URL | POST /assets |
| `faceless analytics` | Cross-platform posting analytics | GET /analytics |

Full flag-level detail: references/api-reference.md (or https://faceless.so/llms-full.txt).

## Common workflows

### Script to published video, end to end

```bash
faceless videos create --script "Did you know the ocean has rivers of its own? ..." \
  --voice-id EXAVITQu4vr4xnSDxMaL --model storyboard --json   # charges 20 credits, returns id
faceless videos status <videoId> --json    # poll every 10-30s until status "completed"
faceless videos render <videoId> --json    # returns renderId
faceless renders get <renderId> --json     # poll every 5-15s until status "done", gives the MP4 url
faceless posts publish --video-id <videoId> --platform youtube --title "Underwater rivers are real" --json
```

Pick a voice with `faceless voices --json`; enumerate styles, niches, models and more with `faceless options --kind <kind> --json`.

### Automated series

```bash
faceless series create --name "Deep sea facts" --source "Facts & stories" \
  --niche "Ocean facts" --voice EXAVITQu4vr4xnSDxMaL --duration 60 \
  --auto-post-time 18:00 --timezone America/New_York --json
faceless series generate <seriesId> --json   # force the next episode now (charges the model cost)
faceless series episodes <seriesId> --json   # track output
```

### Schedule one video to several platforms

```bash
faceless videos update <videoId> \
  --youtube-title "Underwater rivers are real" --tiktok-title "underwater rivers #ocean" --json
faceless posts schedule --video-id <videoId> --platforms youtube,tiktok \
  --scheduled-time "2026-08-01T18:00:00Z" --json
faceless calendar --start-date 2026-08-01 --end-date 2026-08-07 --json   # confirm the queue
```

Every platform in `--platforms` must have its post metadata set on the video first; scheduling rejects platforms whose metadata is missing. Cancel with `faceless posts cancel <videoId> --json`.

## Error handling

Errors look like `{ "success": false, "error": { "type", "message" } }`.

- `unauthorized` (401): re-run `faceless login` (or fix `FACELESS_API_KEY`)
- `forbidden_scope` (403): the key lacks a scope; ask the user to create a key with the needed scopes at https://faceless.so/developers
- `insufficient_credits` (402): tell the user to buy credits at https://faceless.so/credits
- `rate_limited` (429): respect the Retry-After header, wait and retry
- `invalid_input` (400): fix the flags per references/api-reference.md
- `not_found` (404): the id is wrong or belongs to another team

## Raw HTTP fallback (no CLI)

Base URL `https://faceless.so/api/v1`, header `Authorization: Bearer $FACELESS_API_KEY`.

```bash
curl -s https://faceless.so/api/v1/me -H "Authorization: Bearer $FACELESS_API_KEY"
```

Machine-readable surface: https://faceless.so/api/v1/openapi.json and https://faceless.so/llms-full.txt. A remote MCP server is also available at https://faceless.so/api/v1/mcp (same Authorization header).
