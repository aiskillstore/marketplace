# Faceless.so workflows for agents

Step-by-step recipes using the CLI (always with `--json`). The raw API equivalents are in api-reference.md.

## 1. First contact with a new account

```bash
faceless whoami --json     # team, credits, plan, granted scopes
faceless credits --json    # balance + transaction history
faceless accounts --json   # connected socials; empty means the user must connect accounts in the web app first
faceless voices --json     # TTS voices; note an id for videos create
```

If `accounts` is empty, stop and tell the user to connect an account at https://faceless.so/accounts. Publishing requires at least one connected account.

## 2. Script to published video

```bash
faceless videos create --script "Did you know the ocean has lakes and rivers of its own? ..." \
  --voice-id EXAVITQu4vr4xnSDxMaL --model storyboard --json
# charges credits now: storyboard 20, motion_lite 50, motion_pro 100

faceless videos status <videoId> --json   # poll every 10-30s until status "completed"
faceless videos render <videoId> --json   # returns renderId
faceless renders get <renderId> --json    # poll every 5-15s until status "done"; url is the MP4
faceless posts publish --video-id <videoId> --platform youtube \
  --title "Underwater rivers are real" --json
```

A failed generation shows up in `videos status` as status "failed" with errorMessages; do not keep polling past a terminal state.

## 3. Schedule one video across platforms

```bash
faceless videos update <videoId> \
  --youtube-title "Underwater rivers are real" \
  --tiktok-title "underwater rivers are real #ocean" --json
faceless posts schedule --video-id <videoId> --platforms youtube,tiktok \
  --scheduled-time "2026-08-01T18:00:00Z" --json
```

Set post metadata for every platform BEFORE scheduling; the request is rejected for platforms whose metadata is missing. Times are ISO 8601. Cancel while still pending with `faceless posts cancel <videoId> --json`.

## 4. Run an automated series

```bash
faceless options --kind sources --json    # pick a content source
faceless options --kind niches --json     # and a niche (or use --custom-prompt)
faceless series create --name "Deep sea facts" --source "Facts & stories" \
  --niche "Ocean facts" --voice EXAVITQu4vr4xnSDxMaL --duration 60 \
  --auto-post-time 18:00 --timezone America/New_York --json
faceless series generate <seriesId> --json    # force the next episode now (charges the model cost)
faceless series episodes <seriesId> --json    # generation status + scheduled post times
faceless series update <seriesId> --paused true --json   # pause anytime
```

Each generated episode charges the series' model cost like a single video. Episodes auto-post to the series' destination accounts at the configured time.

## 5. Check the queue and performance

```bash
faceless calendar --start-date 2026-08-01 --end-date 2026-08-07 --json   # scheduled, posted, failed
faceless analytics --range 30 --json                                     # views, likes, comments per platform
faceless analytics --platform youtube --json                             # one platform only
```

## 6. Caption footage you already have

```bash
faceless videos captions --video-url https://example.com/clip.mp4 --language English --json
faceless videos status <videoId> --json   # poll until "completed", then render + publish as in workflow 2
```

Also works with `--audio-url` to turn an audio file into a captioned video. Media URLs must be publicly reachable.
