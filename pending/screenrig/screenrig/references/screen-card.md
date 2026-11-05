# Screen cards without connector rendering

The `screenrig-views` connection renders its own cards where the host shows
them. Where the host returns tool results as text, build the card from
CLI data and render it with whatever inline surface the runtime offers.

## Decide the surface

Read your own tool list. A tool that renders inline HTML or SVG in the
conversation is the render surface; the exact name varies by runtime. With no
such tool, print the markdown table at the end of this file and stop. Never
describe a card you did not render.

## Collect the data

Commands go through the helper (`SKILL.md`, "Install and call the CLI").

```sh
screenrig screen list --json
```

`screen show SCREEN_ID` returns the same fields for one screen; `list` already
carries every field below, so one call serves a card or a fleet. `--tag TAG`
narrows to one tag, `--folder ID|root` to the screens directly inside one
screen folder (or outside every folder), and `--state archived` lists archived
screens.

Take every displayed value from that envelope. Do not retype a number, an id,
a revision or a timestamp from a previous reply: re-read it here, so the card
and the API agree.

Read `data.next_cursor`. Where it is not null the list continues past what you
hold; say how many screens the card covers rather than implying it is the whole
fleet.

## Fields

Group the facts into these sections, in this order. A field absent from the
envelope reads `Not reported`, so a reader can tell it was looked for. Players
report what their platform measures: a browser Player carries a thinner health
set than a native one, and the empty rows are the honest answer.

**Content** — `playlist_id` (assigned), `effective_playlist.id` and
`.source`, `manifest_upgrade.desired_playlist` (target) and `.active_playlist`
(loaded, each as `name · revision N`), `manifest_upgrade.state`,
`manifest_upgrade.reported_at`. Where `desired_revision` differs from
`active_revision` the screen is still converging; say so rather than printing
the state word alone.

**Device and health** — `host.platform`, `player.kind` and `player.version`,
`host.device.manufacturer`, `.model`, `.firmware`, `health.uptime_s` and
`health.app_uptime_s` as `Nh Nm`, `health.memory.used_bytes` over
`.total_bytes` in MB, `health.cpu.cores`, `.load_1m`, `.utilization_percent`,
`.app_percent`, `health.temperature_c`, `health.crashes_24h`,
`health.renderer_restarts_24h`, `health.reported_at`, `health.stale`.

**Connection** — `state`, `online`, `last_seen_at`, `last_online_at`,
`health.network.kind`, `health.network.wifi_rssi_dbm` in dBm, `timezone` with
`timezone_source`, `tags`, `created_at`, `updated_at`.

**Storage** — `storage.volume.available_bytes` over `.total_bytes`,
`storage.cache.house_used_bytes` over `.capacity_bytes`, `storage.plan.fit`
and `.required_bytes`, `storage.transfer_24h`, `storage.observed_at`.

**Surfaces** — one row per `observation.surfaces[]`:
`width × height · presentation · pixel ratio N · N° rotation`, then
`observation.observed_at`.

**Identifiers** — `id`, `public_id`, `revision`, `manifest_revision`.

Report bytes in MB to one decimal and durations as whole hours and minutes.

## Still

A still is one capture plus two local steps:

```sh
screenrig screen screenshot SCREEN_ID --output CAPTURE.webp
ffmpeg -y -loglevel error -i CAPTURE.webp -vf scale=240:-2 -q:v 60 THUMB.webp
base64 -w0 THUMB.webp
```

Width 240 keeps the encoded string near 4 KB. Full-resolution captures encode
past 40 KB, which crowds the conversation for no visible gain. `ffmpeg` is the
same dependency `media upload` uses and `doctor` reports; without it, render
the card with no image rather than installing software.

The screenshot envelope carries `capture_id`, `width`, `height`, `bytes` and
`sha256`. Each run requests a new capture, so the still belongs to this run:
label it with `capture_id` and its dimensions, and write no capture time the
envelope did not carry. A still is one frame at one instant, never live video.

Capture needs `online` true and `state` active, and Propose or Manage access.
For an offline screen, render the card with no image and say the screen is
offline.

## Render

Substitute into this shell. Each placeholder is replaced whole, including the
braces. An online screen takes `var(--bg-success)` for `{{STATE_BG}}` and
`var(--text-success)` for `{{STATE_FG}}`; any other state takes
`var(--bg-warning)` and `var(--text-warning)`. Those are the host's own tokens,
so the card follows the conversation's light and dark modes.

```html
<div style="background: var(--surface-2); border-radius: 12px; border: 0.5px solid var(--border); padding: 1rem 1.25rem;">
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
    <div style="flex:1">
      <p style="font-weight: 500; font-size: 15px; margin: 0;">{{LABEL}}</p>
      <p style="font-size: 13px; color: var(--text-secondary); margin: 0; font-family: var(--font-mono);">{{SCREEN_ID}}</p>
    </div>
    <span style="background: {{STATE_BG}}; color: {{STATE_FG}}; font-size: 12px; padding: 4px 12px; border-radius: var(--radius);">{{STATE}}</span>
  </div>
  <div style="border-radius: var(--radius); overflow: hidden; border: 0.5px solid var(--border); background: #000; margin-bottom: 6px;">
    <img alt="{{ALT}}" style="display:block; width:100%; height:auto;" src="data:image/webp;base64,{{BASE64}}">
  </div>
  <p style="font-size: 12px; color: var(--text-muted); margin: 0 0 14px;">Capture {{CAPTURE_ID}} · {{WIDTH}} × {{HEIGHT}}</p>
  {{SECTIONS}}
</div>
```

`{{SECTIONS}}` is one block per section above that has at least one field,
in the section order given:

```html
<div style="border-top: 0.5px solid var(--border); padding-top: 10px; margin-top: 10px;">
  <p style="font-size: 12px; color: var(--text-secondary); margin: 0 0 6px;">{{SECTION_NAME}}</p>
  <table style="width: 100%; font-size: 13px; table-layout: fixed;">{{ROWS}}</table>
</div>
```

`{{ROWS}}` is one of these per field:

```html
<tr><td style="color: var(--text-secondary); padding: 3px 0;">{{FIELD}}</td><td style="text-align: right; padding: 3px 0;">{{VALUE}}</td></tr>
```

## More than one screen

One card per screen, newest first, for up to three screens. Beyond that render
the first three and give every remaining screen as the table below: a column of
full cards buries the fleet it is meant to show. Say how many screens the cards
cover and how many the table carries.

## Table

The same reading, for a runtime with no inline render surface and for the tail
of a fleet:

```markdown
| Screen | State | Playing | Player | Content update | Last contact |
| --- | --- | --- | --- | --- | --- |
| LABEL (scr_ID) | active, online | NAME rev N | KIND VERSION | current | TIME |
```
