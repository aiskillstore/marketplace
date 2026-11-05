# Watch a screen live, or sample its frames

`screen screenshot` is a still. Live view is sub-second video of what the
screen plays, shown to a person in the dashboard. You do not receive the video:
start the session, give the person `data.viewer_url`, and use a screenshot for
anything you must inspect yourself. Live view is free.

## Start, watch, stop

```sh
screenrig screen live start SCREEN_ID --duration 5m
screenrig screen live status SCREEN_ID
screenrig screen live stop SCREEN_ID
```

`start` asks the Player to publish and reads the session every second for
`--wait` (default 30s) until `data.publisher.connected` is true. Open or send
`data.viewer_url`: the dashboard page that shows the video. A start on a live
session renews it. A session ends by itself five minutes after it started at
the latest; nothing renews it past that, so start again when the person needs
more. It ends sooner when its lease runs out (`--duration`, 30s to 5m, default 5m)
or on `stop`; stop it when the person is done.

## What the answers mean

- Warning `live_not_ready`: ok, but the Player has not connected yet. Read
  `status` again; do not say the video is showing. On Android someone at the
  screen must allow screen capture once each time the Player starts.
- `live_unavailable`: the screen is offline or the session ended. Its detail
  names `ended_reason`: `consent_denied` and `consent_timeout` mean nobody at
  the screen allowed capture; `capture_failed` and `connection_failed` are the
  Player's.
- `live_unsupported`: this Player cannot publish; update it. Use `screen
  screenshot` meanwhile.
- `feature_unavailable`: the server has no live view. Use `screen screenshot`.

`publisher.connected` is the Player's own report, at most 45 seconds old. It is
not proof of a picture, and live view does not replace a screenshot for
checking layout.

## Sample frames yourself

`screen live frame` saves JPEG frames of what a screen plays, taken from its
live stream, so you can check playback and motion without waiting for
screenshots. It needs only HTTPS. Frames are free.

```sh
screenrig screen live frame SCREEN_ID --output now.jpg --stop
screenrig screen live frame SCREEN_ID --output frames/ --count 5 --interval 1s
```

It starts the live session (`--duration`, default 2m, lengthened to cover the
frames; a session lasts five minutes at most, so `--count` times `--interval`
must fit), waits up to `--wait` (default 30s) for the Player to publish, asks the
media relay for frames, and saves each new frame once as
`frame-<captured_at>.jpg`. `data.frames` lists `path`, `captured_at`, `width`,
`height`, `bytes` and `sha256`. The session is left to its lease, and a person
watching the dashboard shares it; `--stop` ends it, also after a failure.

### Reading frames

- Look at the saved images before saying content is showing or moving.
- To check motion take `--count 5 --interval 1s` and compare the images. Equal
  `sha256` values are the same picture; different ones do not prove motion on
  their own, because video encoding changes bytes of a still scene.
- A frame is what the Player's encoder sent: scaled to at most 1280x720, lossy,
  about one a second. It is not a screenshot; use `screen screenshot` for layout
  and small text. A frame can be black where the Player cannot capture protected
  video, and nothing detects that.

### Frame errors

The answers mean what they mean for live view (above), plus: `live_not_ready`
also when no new frame arrived in time (run it again), and `live_unavailable`
also when the relay delivers no frames (read `screen live status`, then start
again).
