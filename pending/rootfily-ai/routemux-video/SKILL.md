---
name: routemux-video
description: Generate video through the RouteMux AI gateway using a RouteMux API key — submit the job, poll until it finishes, download the result. Use when the user asks to generate, create or render a video or clip, asks for text-to-video or image-to-video, or says 生成视频/做个视频/文生视频/图生视频. Requires the ROUTEMUX_API_KEY environment variable.
---

# RouteMux Video

Video generation is **asynchronous**: you submit, you poll, you download. A clip
takes minutes, not seconds. Do not hold a single HTTP request open waiting for it,
and do not tell the user it failed just because the first poll says `queued`.

## Before anything else

`ROUTEMUX_API_KEY` must be set. If it is not, stop and say:

```
Create a key at https://routemux.com/console/keys, then run:

    export ROUTEMUX_API_KEY='sk-...'
```

Do not look for the key anywhere else.

## Workflow

1. **Pick a model from the live catalogue** — never from memory:
   ```bash
   curl -s "https://api.routemux.com/v1/models?output_modality=video" \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY"
   ```
2. **Submit**:
   ```bash
   curl -s https://api.routemux.com/v1/videos \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"<slug>","prompt":"..."}'
   ```
   Keep the id from the response.
3. **Poll** with backoff — start around 10s, back off to 30s. Do not poll every second:
   ```bash
   curl -s https://api.routemux.com/v1/videos/<id> \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY"
   ```
4. **Download** when it reports completion:
   ```bash
   curl -sL https://api.routemux.com/v1/videos/<id>/content \
     -H "Authorization: Bearer $ROUTEMUX_API_KEY" -o /abs/path.mp4
   ```
5. **Tell the user the path.** Report elapsed time too — minutes are normal here and
   a number stops them wondering whether it hung.

## Tell the user before you start

Video is the most expensive thing on the gateway per request. Before submitting a
job the user did not explicitly ask to pay for, say which model you are about to use.
Do not silently submit several jobs to "try a few options".

## When it fails

| What you see | What to do |
|---|---|
| `RMX-BILLING-5001` | Out of credit — https://routemux.com/console/billing |
| `RMX-MODEL-3018` | Model needs a prior top-up on the account |
| Job reports failure | Report the job id and `error.message`; do not silently resubmit — a resubmit is a second charge |
| Poll 404s | The id is wrong or the job expired; do not invent a new one |

## Rules

- Never read the key from anywhere except the `ROUTEMUX_API_KEY` environment variable.
- Never write the key into a file, a log, or your reply.
- Never resubmit a failed job automatically — each submission costs money.
- Never poll faster than every 10 seconds.
- Never claim a duration, resolution or frame rate you have not read from the result.
