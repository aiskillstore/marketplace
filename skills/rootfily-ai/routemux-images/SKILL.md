---
name: routemux-images
description: Generate and edit images through the RouteMux AI gateway using a RouteMux API key, and save the result to a file. Use when the user asks to draw, generate, create, render or edit an image or picture, asks for an illustration/icon/logo/mockup/wallpaper, says 画图/画一张/生成图片/出图/改图, or when a coding agent's built-in image tool is unavailable because it is pointed at a custom API base URL. Requires the ROUTEMUX_API_KEY environment variable.
---

# RouteMux Images

Generate or edit an image with any image model on RouteMux, and write it to a path
the user chose.

Why this skill exists: Codex CLI's built-in `$imagegen` and similar built-in image
tools ride the vendor's own subscription session, not the `base_url` you configured.
Point a coding agent at any third-party gateway and the built-in tool goes dark.
Calling the image endpoint over plain HTTP — which is all this skill does — works
regardless.

## Before anything else

Check `ROUTEMUX_API_KEY` is set. If it is not, stop and tell the user exactly this,
then wait — do not try to find the key anywhere else:

```
Create a key at https://routemux.com/console/keys, then run:

    export ROUTEMUX_API_KEY='sk-...'

Add that line to ~/.zshrc (or ~/.bashrc) so new terminals have it too.
```

## Workflow

1. **Get an absolute output path.** If the user did not give one, ask, or default to
   `./<short-slug>.png` resolved to an absolute path. Never write outside the
   working directory without saying so.
2. **Pick a model from the live catalogue**, never from memory:
   ```bash
   curl -s "https://api.routemux.com/v1/models?capability=image_generation" \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY"
   ```
   Model slugs change. The RouteMux docs themselves shipped a stale example model
   for days after the default moved on — do not hard-code one in your reply either.
3. **Generate**, one image per call:
   ```bash
   scripts/generate-image.sh --prompt "<the user's prompt>" --out /abs/path.png
   ```
   Or directly:
   ```bash
   curl -s https://api.routemux.com/v1/images/generations \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"<slug from step 2>","prompt":"...","n":1}'
   ```
4. **Save the bytes.** The response carries either `data[0].b64_json` (decode it) or
   `data[0].url` (download it). Handle both — which one you get depends on the model.
5. **Report the path and the model that answered.** If the response headers name a
   different model than you requested, say so: RouteMux can serve the request with a
   backup image model when the primary upstream is down, and billing follows the
   model that actually answered.

## Editing an existing image

`POST /v1/images/edits` is multipart, not JSON:

```bash
curl -s https://api.routemux.com/v1/images/edits \
  -H "Authorization: Bearer $ROUTEMUX_API_KEY" \
  -F model="<slug>" \
  -F prompt="make the sky orange" \
  -F image=@/abs/input.png
```

## Size

`size` sets the aspect ratio reliably. It does **not** reliably set the pixel count —
several upstreams have a fixed pixel budget and will return their own resolution
whatever you ask for. Tell the user the aspect ratio you are asking for, not a
promised pixel size.

## When it fails

| What you see | What it means | What to do |
|---|---|---|
| `RMX-BILLING-5001` | Wallet is out of credit | Send them to https://routemux.com/console/billing |
| `RMX-MODEL-3018` | Model needs the account to have topped up once | Suggest a model without that requirement, or a top-up |
| `RMX-LIMIT-4004` | This key hit its daily image allowance | Resets 00:00 UTC. Do not retry in a loop |
| `RMX-LIMIT-4005` | Image generation is paused platform-wide | Text and video still work. Try again later |
| Any 4xx | Bad request | Read `error.message` and fix it. Retrying unchanged will fail again |
| 5xx / timeout | Upstream trouble | Retry at most twice with backoff, then report `request_id` |

Always surface `error.request_id` when you give up — it is what support needs.

## Rules

- Read the key **only** from the `ROUTEMUX_API_KEY` environment variable. Do not go
  looking for it in dotfiles, config files, or any other tool's credential store.
- Never write the key into a file, a log, a commit, or your reply.
- Never `eval` a response body.
- Never write to disk except the artifact path the user asked for.
- Never hard-code a model slug as if it were permanent — query the catalogue.
- Never request several variants in one call to "save a round trip": each image is
  billed separately and the pre-authorisation scales with the count.
- Never claim an exact pixel size you have not verified in the returned file.
