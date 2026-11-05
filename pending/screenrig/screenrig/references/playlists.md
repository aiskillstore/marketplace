# Playlist documents, cards and feeds

The full document reference is "The playlist document" in the
[CLI reference](https://screenrig.ai/docs/cli.md); `playlist validate FILE`
checks a document and `playlist show ID --output FILE` writes an editable one.

## Built-in cards and feeds

A card is a non-interactive live display drawn natively by every Player. Use an
application only for what a card cannot do.

```sh
screenrig cards list --category food        # or --tag weather
screenrig cards show menu                   # schemas, tier, layouts, feed, example
screenrig card create --type menu --file params.json   # returns crd_ID
screenrig card data put crd_ID --file data.json [--expect-rev N] [--ttl 2h]
screenrig card preview crd_ID --output card.png
```

- Put the `crd_` ID in a page primitive: `{"id", "primitive": "card", "card":
  "crd_ID", "layout", "anchor"?, "content_fit": "fill"}`. `layout` is required
  and must be one `cards show` lists for the type; omit `rect` and `layer` unless
  the layout is `free`. Layouts, anchors and per-page limits:
  [cards](https://screenrig.ai/docs/cards.md#layouts-and-anchors). A `fullscreen`
  card takes `full` only.
- Static params belong to the instance: after `card params`, republish. Dynamic
  data (no `document` wrapper, at most 1 MiB) reaches screens without
  republishing. Card images are `media:<id>` references to ready images.
- Remove a card from every playlist before `card delete`.
- Preview locally with installed Chromium (`SCREENRIG_BROWSER` selects it);
  `--now ISO --timezone ZONE` freezes clocks. Resolve every item in
  `data.placeholders` and check a Player screenshot after publishing.
- Weather, air quality, alerts, rates, crypto, earthquakes, headlines and the
  families below come from `screenrig feeds get NAME ...`, cached by screenRIG;
  never call providers. A `state: pending` answer carries
  `retry_after_seconds`: report it and return. Show a feed's `attribution`
  wherever its data shows.

Feed families and the card that reads each. A card takes the params shown
(`cards show TYPE` lists them); where one takes a location, give it the whole
value `"{screen.location}"` so each screen reads its own place, as in
`{"location": "{screen.location}"}`:

| `feeds get` | Card | Placement |
| --- | --- | --- |
| `tides` (`--station ID`, or `--lat` and `--lon`) | `tides` | `station` (a NOAA station id) or `location`: the nearest station within 100 km, United States and territories |
| `launches` | `launch-tracker` | none: the next launches worldwide |
| `drugalerts` (`--country us\|ca\|gb`, `--category drug\|food`) | `drug-alerts` | `country`, `category`: recalls |
| `respiratory` (`--country us\|gb`, `--region`) | `respiratory-activity` | `country`, `region` (a US state, territory or DC, or England or a UKHSA region) |
| `almanac` (`--language`, `--country`, `--lat` and `--lon`, `--date`) | `today` | `location` adds sun and moon, `country` holidays; `language`, `date` |
| `outdoorsafety` (`--lat` and `--lon`) | `outdoor-safety` | `location`: an estimated heat index (WBGT) for open sun; give `show` the value `heat` |
| `departures` (`--provider tfl\|entur\|digitransit`, `--stops IDS`) | `departures` | `provider`, `stops` (the provider's stop ids) |
| `bikeshare` (`--lat` and `--lon`, `--system ID`) | `bike-share` | `location`, optional `system` (a GBFS system id); a place no listed system covers gets no data |

## Card webhooks

An outside system (a CMS, Zapier, a point of sale, a script) pushes data to a
card with one HTTP POST. Create the webhook, give its administrator the url and
secret, and read the delivery log when nothing shows.

```sh
screenrig kv webhook create --card crd_ID --map map.json --description "CMS alerts"   # url and secret, shown once
screenrig kv webhook update kvw_ID --card crd_ID --map map.json    # also --clear-map, --disable, --signing
screenrig kv webhook deliveries kvw_ID --card crd_ID               # why each post was written, unchanged or refused
```

- Without `--map` the posted JSON object (or form) is the card's data document.
  With it, a template builds the document from the body:
  `{"title":"{{body.alert.title}}","body":"{{body.alert.message}}"}`;
  `{{body.items[0].name}}` indexes; a string that is one placeholder keeps the
  value's type; `{"$each":"{{body.items}}","$limit":20,"$template":{"text":"{{item.title}}"}}`
  maps an array (also `$group`, `$number` for `$3.50` or `3,50 €`, `$bool`,
  `$text`); `{{query.NAME}}` reads the URL's query. A missing value is empty in
  text and leaves a lone value out.
- For one document per room, create with `--key-template 'room-{screen.field.room}'`.
  The mapped output (or raw body without `--map`) is
  `{"documents":[{"fields":{"room":"A101"},"document":{"body":"Room A101"}}]}`.
  Place the owning `crd_` instance with `data: "room-{screen.field.room}"`;
  each screen reads the key filled from its own field. JSON, CSV and Sheets
  sources use the same envelope with `key_template` in their settings.
  Preview source mappings with `source test`; all outputs use the owning card's
  schema. Use separate instances, mappings and key prefixes for different cards
  reading the same feed. Missing fields, duplicate keys or invalid documents
  refuse the batch before writing. A storage failure can leave part written:
  retry the identical webhook body with the same `Idempotency-Key`, or refresh
  the source. Omitted keys keep their previous data and expiry; webhook data
  remains until replaced. See https://screenrig.ai/docs/sources for mappings.
- The sender authenticates with the webhook's secret as a bearer credential (or
  HTTP Basic with the webhook id as user), never the secret in the url. Each post is checked as the
  card's own data (`card_data_invalid` names the path), an identical document is
  not rewritten, and an accepted post is one billed API request.
- A wrong url, a wrong secret, a disabled webhook and any GET answer the same 404;
  only `deliveries` says why. `--signing` also requires `ScreenRig-Signature:
  t=UNIX,v1=HEX`, the HMAC-SHA256 of `t.BODY` under `data.signing_secret`, within
  five minutes. Secrets go to the sender's administrator, never into
  conversation, files or logs.
- A vendor that signs its own posts needs no bearer credential. Create or
  update the webhook with `--verify VENDOR --verify-secret-file FILE`, VENDOR one
  of `github`, `stripe`, `shopify`, `slack`, `linear`, `vercel`, `asana` or
  `generic_hmac` (any HMAC sender; `--help` lists the signature header, encoding
  and timestamp options it needs). A post with the vendor's valid signature is
  accepted without the webhook's own secret, which keeps working beside it. The
  vendor's secret is the one its webhook page shows or takes (Stripe's starts
  `whsec_`): ask the user to save it to a file. It is stored sealed and shown only
  as a hint; `--verify VENDOR` without a file keeps it for the same vendor,
  `--clear-verify` removes it, and `--verify` excludes `--signing`. A refused post
  is the same 404, and `deliveries` says `signature_missing`, `signature_invalid`
  or `timestamp_stale` (the secret was right, the clock was not).
- Handshakes: `--handshake microsoft_graph|monday|trello|azure_event_grid` answers
  the check that vendor makes when a subscription is created; it writes nothing
  and is free. `--verify slack` and `--verify asana` answer their own: Slack's
  signed `url_verification`, and Asana's `X-Hook-Secret` (create the webhook with
  `--verify asana` and no file, then point Asana's webhook at its url: events are
  refused `secret_pending` until Asana's handshake lands). Events from Graph,
  monday.com and Trello carry no header screenRIG verifies, so each must arrive
  with the webhook's own secret: an Event Grid subscription adds it as a static
  bearer-credential delivery header, and for the others a flow tool
  that triggers on the vendor and can set that header (Zapier, Make, Power
  Automate) posts to the webhook instead.

GitHub signs each push with the secret the user sets on its webhook page
(Settings, Webhooks, Add webhook: Payload URL is the printed url, Content type
`application/json`). Save that secret to `gh.secret`; a `text` card shows the
push:

```sh
screenrig kv webhook create --card crd_ID --description "Pushes" --verify github --verify-secret-file gh.secret --map map.json
```

```json
{"title": "{{body.repository.full_name}}", "body": "{{body.head_commit.message}}"}
```

GitHub's `ping` after creation is signed and accepted.

## Overlay triggers

Home Assistant, a sensor hub or an alerting tool shows words on screens with one
HTTP POST: a bar over whatever plays, or a full-screen takeover.

```sh
screenrig triggers create --name "Lobby" --kind overlay --show bar --tag Lobby   # url and secret, shown once
screenrig triggers test trg_ID           # one-minute test; triggers clear trg_ID ends it
screenrig triggers deliveries trg_ID     # why each post was shown, ignored or refused
```

- The sender posts JSON, authenticated with the webhook's secret as a bearer
  credential: `alert_id`, `label`,
  `title`, `message`, `note`, `duration` (`90s`, `10m`, `until_cleared`; default
  10m) and `clear` or a `state` of `off`, `closed`, `resolved`. One `alert_id` is
  one alert; the newest shows; each post holds its alert from now.
- `--map FILE` builds the post from a tool's body (as card webhooks) and runs every
  post through it, so leave it off for a sender that posts the members itself.
  `--style FILE` sets theme and colours, `--signing` adds `ScreenRig-Signature`,
  `triggers update` changes any of it. A wrong url, a wrong secret and any GET
  answer the same 404; only `deliveries` says why. A clear is free. Secrets go
  only to the sender's administrator. `triggers create|update` take the same
  `--verify`, `--verify-secret-file`, `--handshake` and `--clear-verify` as card
  webhooks (above); a post that is only a vendor handshake changes no alert.
- Home Assistant example and the full request: <https://screenrig.ai/docs/cli#overlay-triggers>.

## Per-screen values

Each screen carries its own `fields` (up to 32 lower-case names, values up to
200 characters) and `location` (latitude, longitude, an optional `name` cards
show and an `address`). `screen update` sets them: `--field NAME=VALUE`
(repeatable), `--unset-field NAME`, `--clear-fields`, `--location LAT,LON
[--location-name NAME] [--address TEXT]`, `--clear-location`. Changing them
reissues the screen's manifest.

A card's params read them with tokens that screenRIG fills for each screen:

- Any text param: `{screen.name}`, `{screen.timezone}`, `{screen.field.NAME}`,
  for example `"title": "Store {screen.field.store_number}"`.
- A card's `location` param: the whole value `"{screen.location}"`, so weather,
  air quality, alerts, earthquake, moon, prayer-time, tides, outdoor-safety,
  bike-share and today cards follow each screen. A CAP alert card takes it only
  without `sources`.

`card create` and playlists accept the tokens. `card preview` shows them as
written, so check one screen's screenshot after publishing. A screen without
the field shows empty text; a screen without a location shows the card without
one.

An `iframe` `src` and `fallback_src` take URL tokens in the path, query or
fragment of an `http(s)` address, and an `application` takes optional `params`
(up to 16 names of `[a-z0-9_]{1,32}`, `ticket` and `policy` reserved, values up
to 512 characters, appended to its launch URL so it reads `location.search`):
`{screen.id}` (without `scr_`), `{screen.name}`, `{screen.timezone}`,
`{screen.field.NAME}`, `{screen.location.lat}`, `{screen.location.lon}`,
`{screen.location.name}`, `{screen.location.address}`. Example `src`:
`https://maps.example.com/directory?kiosk={screen.field.kiosk_id}`. The write
stores the template as written; each screen's manifest carries its own address
with every value percent-encoded. A token in the scheme, host, port or
credentials, or in a YouTube, Google or Microsoft document or BI view address,
is `invalid_request`. A screen that lacks a value gets no such iframe or app
(`screen_fact_missing`; a page left empty is dropped), and every write that
reaches it, including `screen update`, returns a `screen_fact_missing` warning
with the tokens and the first 20 screen IDs: set the fields first. Launch
params reach the web Player and the Players that run it (Tizen, BrightSign,
webOS, Vega); the Qt, Android, Apple and Windows Players load apps locally. An app learns its screen from `context.screen_id`
and treats params as untrusted. A template's `url` field may be a whole `src`.

A tag selector's `tag` (and a `tags` entry) may be `{screen.field.NAME}` or
`{screen.id}` (the screen's ID without `scr_`, so a tag). The server fills it per
screen, so one playlist plays each screen's own media: media tagged `Lobby` or
`Garage`, `screen update ID --field zone=Lobby`, and
`{"by": "tag", "tag": "{screen.field.zone}", "one_at_a_time": true}`. A screen
without the field, or whose value is not a tag (1 to 32 letters or digits),
plays no file from that slot (`screen_fact_missing`, `screen_fact_invalid`).
A template cannot be previewed (`selector-preview` takes a concrete tag) or
exported.

## Video walls

A kiosk-installed Linux Player or a Windows Player drives 2 to 12 displays as
one wall. Set it with `screenrig screen wall set SCREEN_ID --outputs
HDMI-A-1,HDMI-A-2 --arrangement row|column|grid [--columns N] [--rotation
0|90|180|270]` (outputs from `screen show`, such as `HDMI-A-1` on Linux or
`DISPLAY1` on Windows, listed left to right, then top to bottom) and remove it
with `screen wall clear SCREEN_ID`; `wall_unsupported` means the Player lacks
wall support. A grid takes `--columns`, an integer of at least 2 that divides
the displays into at least 2 rows (12 displays in 4 columns make 3 rows); a row
or column takes none. Prefer a grid when a row or column would exceed 16384 px
(more than 8 landscape displays in a row), the widest buffer most GPUs
allocate. A wall playlist carries `format` (`displays`, `arrangement`,
`orientation`, and `columns` for a grid), every page canvas is the wall canvas
(a 1920x1080 or portrait 1080x1920 tile times columns and rows: 7680x3240 for
4x3 landscape), and primitives take `displays` (`[2]`, `[1,2]`, or on a 4x3 grid
`[1,2,5,6]`: numbers that fill a rectangle of the wall) or a free `rect`.
Assigning it to a screen whose wall differs is refused
(`playlist_format_mismatch`). Canvas sizes, card layouts and video sizing (wall
aspect ratio within 4K, `content_fit: "fill"`, text off the seams):
[video walls](https://screenrig.ai/docs/players.md#video-walls).

## Strips

A strip is a playlist drawn over the page along one edge of a display: a footer
ticker, a header logo or a side banner. The page keeps playing underneath; the
strip hides what it covers. Make it in three steps:

1. Build the pages with one canvas shaped as the edge, its long side along the
   edge and at least twice the short side: 1920x240 for a landscape footer or
   header, 240x1080 for a landscape side (`playlist init FILES --target-width
   1920 --target-height 240` writes it). A strip holds `image` and `card`
   primitives only, one canvas for every page, and no soundtrack.
2. Create it as a region playlist: `screenrig playlist create ticker.json
   --format-region footer --format-orientation landscape`. `--format-region` is
   `header` (top), `footer` (bottom) or `side` (right edge, full height);
   `--format-orientation` is the orientation of the display it is made for, as
   the viewer sees it. `playlist update ID FILE` takes the same flags, and
   `playlist show` reports the `format`.
3. Show it with a level that covers its region: `screenrig campaign create
   --name Ticker --playlist-id pl_TICKER --tag lobby --covers footer`, or a
   `screen schedule set --file` entry with `"covers": "footer"`. A level that
   covers `header`, `footer` or `side` takes a region playlist of that region;
   `full` and `main` take an ordinary one. A region playlist is never a
   default, a folder default or a takeover.

A strip draws at its canvas aspect along the edge, only on displays of its
orientation and only while it covers at most half the display (its height for a
header or footer, its width for a side). The server refuses a level
(`playlist_format_mismatch`) that fits none of the screens it targets; on a
campaign for a mixed audience, `campaign explain SCREEN_ID` says
`region_not_laid_out` for a screen it does not fit, and `campaign screens ID`
lists it. A format change that moves a playlist into or out of a region is
`resource_conflict` while a screen, folder or campaign uses it. Only Players
that resolve their own stack draw strips; any other Player's row reads
`stack_only`.

## Templates

A template is an ordinary playlist with two additions, built once from the
brand guidelines so staff can fill in the parts that change.

- `locked: true` on a primitive marks fixed brand content (logo, background,
  layout, theme). Only the owner or a member who can approve adds, removes,
  moves or edits it or clears its lock; anyone else is refused with
  `primitive_locked` (under Propose it becomes a review). Copies keep the locks.
- `fields` on the playlist: `[{"name","label","type":"text|media|url",
  "required","max_length"}]`, `name` of 1 to 32 lower case letters, digits or
  underscores. A page reads a field as `{field.NAME}` in a card's `params`
  (text and url fields), as an image or video `selector.media_id` (a media
  field) or as the whole `src` of an iframe (a url field). Every token names a
  declared field of the right type, every field is read, and a locked primitive
  reads none. `playlist validate FILE` checks all of it offline. A template is
  never shown on a screen (`playlist_is_template`); assign the playlists made
  from it. `playlist list --templates` lists them.

Make a playlist from a template with `playlist create --from-template PL_ID
--name NAME --set NAME=VALUE ...` (`--dry-run` checks the values and creates
nothing). A media value is the ID of a ready image or video of the right kind, a
url value an http or https address; the result is checked like any playlist and
is an ordinary one to assign, schedule and revise. `playlist fields PL_ID` shows
a template's fields or a copy's values, and `--set` / `--clear` change them.
Changing values, or `--refresh` alone, builds the copy again from the template's
current revision: that is how a brand change reaches existing copies, and
nothing pushes to them. `playlist instances TEMPLATE_ID` lists the copies and
marks those built from an older revision. Under Propose a values change is a
review. `playlist create --starter urgent-notice` adds the Urgent notice
template, a headline and a message for quick announcements.

## Change one page

`playlist page add PLAYLIST_ID`, `page replace PLAYLIST_ID PAGE_ID` and `page
remove PLAYLIST_ID PAGE_ID` change one page and leave the others as stored; the
kept pages are validated again with the new one. `add --media MEDIA_ID` builds a
full-canvas image or video page on the playlist's canvas (`--seconds`, `--fit`);
`--file PAGE.json` takes any page. `add` puts the page at the end or in front of
`--before PAGE_ID`; `replace --media` swaps the media and keeps the dates, and
with neither `--media` nor `--file` only the dates change. To change the file
itself everywhere a media item plays, use `media replace MEDIA_ID FILE`: the pages
stay as they are.

`--from` and `--until` set the page's `visibility`: `YYYY-MM-DD` or
`YYYY-MM-DDTHH:MM` in each screen's timezone, `--until` exclusive, and a
date-only `--until` covers that whole day. `replace --always` removes the dates
and keeps a switch-off or weekly windows the project set.

Under Propose a page change is a review; your next page change of the same
playlist joins your pending review, which also lets you replace or remove a page
still waiting in it, and approving applies them together. Another proposer's
pending page change makes yours wait (`resource_conflict`) until it is decided.

An uploader changes pages only of its playlists, and its page is an image or
video of its folders only (a stinger transition's logo included);
`outside_upload_scope` carries `upload_scope`, what it may use. Invite one with
`invitations create --kind uploader --folder-id ID --playlist-id ID`.

## Playlist rules that validation will enforce

- A playlist is `name`, optional `audio`, and `pages`. A page has `id`, `canvas`
  (`width`, `height`, `viewport_fit`, `background`), `transition`, `advance`,
  optional `visibility` and `audio_cue`, and flat `primitives` (`id`,
  `primitive`, its own fields, `rect`, `layer`, `content_fit`, optional `enter`
  and `motion`).
- Primitives are `image`, `video`, `stream`, `iframe`, `application`, `card`.
  Text and shapes are not primitives: generate them into an image with
  `media generate`, or show live text with a built-in card.
- `image` and `video` need a `selector` (`by` `id`, `ids`, `all`, `tag`,
  `folder` with a `folder_id` from `media folder list`); `media_id` lives inside it. Others take none. Dynamic selectors
  resolve at each loop; on duration, application and `audio_end` pages they
  need `one_at_a_time: true`. `media_end` is valid only on a page with exactly
  one image or video; an image there needs `dwell_ms`, a video must not loop.
  Use `media selector-preview FILE --primitive image|video [--rect WxH]` to
  inspect a selector.
- Weighted order (share of voice, sponsor rotation): `order: "weighted"` with
  `weights`, both or neither, plus `one_at_a_time: true` or `batch_size: 1`.
  `weights` maps `med_` IDs or `tag:NAME` to 1-1000 (64 keys at most); 50/30/20
  plays exactly 5/3/2 of every 10. An item takes its `med_` key, else its first
  `tag:` key alphabetically (that weight split among the items carrying it), else
  weight 1. Key each sponsor by `tag:` so its share holds however many creatives
  it has. A Player without `selector.weighted` plays random
  (`selector_order_downgraded`); static export drops weights.
- `fit: "aspect"` on a dynamic selector keeps files within 5% of the slot's
  width over height, so a portrait slot never plays a landscape file. Preview
  needs `--rect WxH` with it and lists the rest as `excluded`
  (`aspect_mismatch`); weighted previews give each item's `weight`,
  `share_percent` and the `cycle`.
- `media availability MEDIA_ID --file RULE.json [--expect-rev N]` (or `--clear`)
  sets when `all`, `tag` and `folder` selectors may pick a file; `by` `id`/`ids`,
  cards, soundtracks and ad creatives ignore it. The rule is the schedule's clock
  grammar in each screen's time zone: `from`/`until` (`YYYY-MM-DDTHH:MM`, `until`
  exclusive), `windows` (`[{days, start, end}]`), `monthly` (`{day}` or `{nth,
  weekday}`, optional `start`/`end`), `dates` (`[{date, start, end}]`), `except`
  (dates), at least one member, no `data` or `interaction`. A sponsor's weekend:
  `{"from": "2026-11-27T00:00", "until": "2026-11-30T23:59"}`, plus a
  weekday-evening window if wanted. A file leaves and returns at each screen's
  next loop, within about a minute of the edge, with no playlist or manifest
  revision; an offline Player keeps its last selection. It needs Manage access
  (Propose gets `insufficient_access`). `selector-preview --timezone ZONE` lists
  files outside their rule as `outside_window`.
- `iframe` and `application` use `content_fit: "fill"`; `application` pins a
  `release_id`. A `stream` needs `fallback_media_id` and a `duration` page. Its
  `sources` take an `https` HLS URL or a camera's `rtsp://`/`rtsps://` URL as
  given, login included (`{"url": "…"}` is enough); Android, Amazon and Linux
  Players open RTSP directly, others show the fallback. UniFi Protect: the
  camera's channel RTSP URL from Protect. Apple TV rejects `iframe` and
  `application`.
- An `iframe` takes optional `reload_s` (0, the default, never reloads; else 60
  to 86400 seconds: the screen loads the page again that often while it shows)
  and `fallback_src` (the same forms as `src`): when `src` does not load, the
  screen shows `fallback_src`, and each reload tries `src` first again. Native
  Players also fall back on an HTTP error; the Player web app falls back only
  when `src` is unreachable or silent for 30 s.
- An `iframe` takes an optional `navigation_allowlist`: 1 to 64 addresses the
  page may navigate to, besides `src` and `fallback_src`. Each is
  `[scheme://]host[:port][path]`: `*.example.com` is any subdomain (list
  `example.com` too for the bare name), `*` any host, `:*` any port; a path
  ending in `/` or `/*` covers everything under it, another path only itself;
  no scheme means http or https. Links, scripts and redirects to anything else
  are refused and the page stays; a `src` that redirects off the list counts as
  not loading. Query and fragment never count. Omit it for no restriction.
- For YouTube, put the link the user gave (video, Shorts, live, playlist or
  `youtube.com/channel/UC…/live`) in an `iframe` `src`: the server stores an
  autoplaying, looping embed without YouTube's controls. Every Player plays it
  with sound where the screen's browser allows sound (the Player web app mutes
  it when the browser refuses); `mute=1` in the link mutes everywhere. For a
  page that lasts as long as one video, set the page's advance to
  `{"mode": "duration", "after_ms": N, "until": "video_end"}`: the page ends
  when the video does, and `after_ms` is how long it shows when the screen
  cannot read the video's length. A page with a playlist, a live stream or more
  than one YouTube video rejects `until` at `advance.until`.
  A channel handle (`@name`) is rejected: ask for a video or channel-ID link.
- For a Google Slides, Docs or Sheets file, or a PowerPoint, Word or Excel file
  on OneDrive or SharePoint, put the share link, Publish to web link or Embed
  code the user gave in an `iframe` `src`; `playlist init` also takes the
  `<iframe …>` code as an input. The server stores the embed address. Slides loop
  and advance on the link's `delayms` (10 s by default, held to the page's
  `after_ms`, so give the page the time of the whole deck); Docs, Sheets, Word
  and Excel reload every 5 minutes. Google needs Share → Anyone with the link, or
  File → Share → Publish to web. Microsoft needs File → Share → Embed on a file
  its admin lets share with Anyone links; `1drv.ms` and sharing links are
  rejected. A file that asks viewers to sign in fails with `document_not_shared`
  naming the setting to change. The screen needs Google or Microsoft on the
  internet.
- `visibility` times are civil (no zone); keep at least one page without it, and
  set the screen timezone before assigning a scheduled playlist. A
  `visibility.data` condition keys off card data. Its key `{screen.weather}`
  keys off the weather where each screen is (give the screen a location first,
  `screen update --location`): `{"key":"{screen.weather}","path":"/condition","equals":"rain"}`.
  `/condition` is clear, cloud, fog, rain, snow, storm or wind; `/band` is
  freezing (below 0 °C), cold (0-9), mild (10-17), warm (18-24) or hot (25+);
  `/temperatureC` is whole degrees; `/isDay` is true or false. It is the
  current weather at the screen, refreshed about hourly, not a forecast; a
  screen without a location never shows the page.
- A soundtrack is `audio: {tracks, loop, volume, cued}` (1 to 128 uploaded
  tracks); pages bind with `audio_cue` or `advance: {"mode": "audio_end"}`.
  `playlist update` replaces the whole document, so omitting `audio` removes it.
  Details: [soundtracks](https://screenrig.ai/docs/compose.md#add-a-soundtrack).
- An ad break is an `adslot` page (`id`, `type`, `adslot_id`, optional
  `visibility`), not a primitive; keep an ordinary fallback page.
- `playlist export|import` moves image/video media, soundtrack audio and iframe
  URLs as a bundle. Cards, streams and adslot pages stop export. Applications
  stop it by default; `--skip-applications` drops them and empty or
  application-controlled pages, and requires at least one remaining page.
  For an editable document retaining card/application references in the same
  project, use `playlist show ID --output playlist.json`; referenced resources
  stay in that project.
  `playlist patch` and `rename` change only supplied fields.
