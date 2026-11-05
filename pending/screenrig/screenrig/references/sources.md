# Data sources: cards that stay live from an outside address

A data source reads an address on a schedule and writes the result to one
card's dynamic properties, so the card stays current without republishing and
screens refetch it when it changes. One source writes one card. Use it when the
data already lives somewhere you can name (a calendar, a Google Sheet, a CSV,
JSON or XML address, a Slack channel, social posts, reviews, room calendars, a
venue's booking system, a Square, Shopify or Toast till); use `card data put`
for data you hold, and `kv webhook` for a system that pushes ([keep cards
current](#keep-cards-current) chooses between them).

Commands go through the helper (`SKILL.md`, "Install and call the CLI").
The help for `source create` lists the kinds; settings, status codes and
privacy rules per kind are at https://screenrig.ai/docs/sources. Changing
sources needs Manage access; `source list|show` needs Read only.

## Presets

A preset is a tested source for one service: it builds the address, request and
mapping from a few fields, so you give a card, the fields and a credential.
`source presets` lists them; `source presets NAME` shows one's fields, the cards
it fills and how the customer gets its credential. Every preset runs as a `json`
source with its own refresh and stale period, so the workflow below applies
unchanged.

| Preset | Fills | Credential |
| --- | --- | --- |
| `slack-channel` | `workplace-posts`, `message-wall` | `token`: the bot token of an internal Slack app (`channels:history`, plus `groups:history` for a private channel) that is added to the channel |
| `bonusly` | `kudos` | `token`: a Bonusly access token with `recognition:read` |
| `facebook-page` | `social-wall` | `access_token`: a Page access token |
| `instagram-business` | `social-wall` | `access_token`: the linked Page's access token |
| `google-reviews` | `reviews` | `api_key`: a Google Cloud key with the Places API (New) |
| `google-travel-times` | `travel-times` | `api_key`: a key with the Routes API |
| `greenhouse-jobs`, `lever-jobs`, `ashby-jobs` | `now-hiring` | none: the job board is public |
| `github-actions` | `build-board` | `token`: a fine-grained token with read-only Actions access to the repository |
| `api-football-scores`, `api-football-standings` | `scores`, `standings` | `api_key`: an API-Sports key (football) |
| `api-sports-scores`, `api-sports-standings` | `scores`, `standings` | `api_key`: the same API-Sports key, with `sport` basketball, hockey, baseball or american-football |

```sh
screenrig source presets slack-channel
screenrig source test --preset slack-channel --card crd_ID --set channel=C0123456789 --secret token=@slack.token
screenrig source create --preset slack-channel --card crd_ID --name "Announcements" --set channel=C0123456789 --secret token=@slack.token
```

`--preset` takes the place of `--kind` and `--settings`. `--set FIELD=VALUE`
names the preset's fields (a list field such as `destinations` takes JSON; if the
preview says an all-digit ID is not text, give it as a JSON string, `--set
'page_id="104512381823456"'`), and `source update ID --set FIELD=VALUE` changes
one. A card the preset does not fill is `source_target_unsupported`, and its
detail lists the cards it does; a missing credential is
`source_secret_required`. Ask the user to save each credential to a file: never
take it as an argument or print it.

- `slack-channel`: Slack answers 200 with `ok: false` when the app is not in the
  channel, the token is wrong or a scope is missing, so the source fails
  `mapping_failed` at `rows_path` and the card keeps its messages. People's own
  messages show; joins, bot and app posts are left out. Keep the app internal:
  Slack limits an app distributed outside its Marketplace to one history request
  a minute.
- `facebook-page`, `instagram-business`: make the Page token from a long-lived
  user token (or a system user) so it does not expire; Meta answers an expired
  token with HTTP 400 (`http_status`). The wall shows each post's words (an
  Instagram post's caption): the card takes pictures only as media, so a post
  without words is left out.
- `google-reviews` reads the place every 6 hours and `google-travel-times` every
  15 minutes (one billed route element per destination per refresh), both on the
  customer's own Google key: leave the interval alone. The reviews card shows the
  Google mark and each reviewer's name, as Google requires, and its data leaves
  the screen after 24 hours without a refresh.
- The job boards show up to 8 roles and a QR code to the board; `github-actions`
  shows one repository and branch, the latest run of each workflow.
- API-Sports presets take a league ID and season (`source presets NAME` shows
  examples) and a required `timezone`. Scores refresh every 20 minutes and
  standings every 6 hours, 76 of the free plan's 100 requests a day for one
  sport; every source on one key shares the allowance, so leave the intervals
  alone on a free key. A spent quota or a season the plan lacks fails the run,
  and the card keeps its data. The data is the customer's to show on their own
  screens under API-Sports' terms.

## The workflow

1. **Create the card** the data will fill, with `card create --type TYPE --file
   PARAMS.json`. A calendar fills an `events` card (an agenda of every calendar,
   merged) or a `study-rooms` card (one room per calendar). Place it on a page as
   usual; the source never needs a republish.
2. **Preview.** `source test --kind ics --card crd_ID --set
   'calendars=[{"key":"lobby"}]' --secret calendar_url.lobby=@lobby.url`
   fetches, shapes and validates against the card and writes nothing. Read
   `data.valid`, `data.warnings` (a time zone it could not place, events cut at
   a limit) and `data.document`. If `valid` is false the warning names the path
   the card refuses.
3. **Create** with the same options plus `--name`: `source create --kind ics
   --card crd_ID --name "Lobby calendar" ...`. It runs within seconds.
4. **Check.** `source show src_ID` (or `source refresh src_ID`, which syncs now
   and shows the result): `status.state` ok, `last_success_at` moving, and
   `card data get crd_ID` holds the events. Report what you saw.

`--settings JSON|@FILE|-` gives the whole config; `--set KEY=VALUE` changes one
top-level member (JSON when it parses, else text). `--config` is the CLI's
credential-file option, not the source's. `source update src_ID --set days=14`
edits the saved config; `--disable` stops the schedule and the card keeps its
last document; `source delete src_ID` does the same for good.

## Secrets

A calendar address is a credential: anyone holding a private feed address reads
the calendar. Give it with `--secret calendar_url.KEY=@FILE` (the file holds the
address) or `=-` to read stdin, so it stays out of shell history and process
lists; at most one option reads stdin. It is stored sealed and every read shows
only the scheme and host. Never paste an address into a note, a card, a message
or a playlist. A secret is entered for the address it was entered for: if
`source update` points a source elsewhere, `source_secret_required` asks for it
again. Tokens, passwords and API keys take the same forms (`token`, `password`,
`client_secret`, `header.NAME`, `query.NAME` or a preset's own names).

## Reading status

`status.state`: `pending` (not run yet), `ok`, `error` (the card keeps its last
good document; `status.error.code` and `.message` say why) or `disabled`.
`ok` means the last fetch worked and the card accepted the document; it does
not say the upstream data is right or current, or that a screen shows the card.
Failures back off by themselves; `source refresh` retries now. A source keeps its
last good data on the card for `stale_after_seconds` (`--stale-after`, 1m to 7d,
`none` keeps it until the next refresh); a failing source past that has
`status.stale` true, its documents have expired on every screen, and pages that
depend on the data have fallen back. `data_expires_at` says when. A
notification on `source_failed` and `source_stale` says when a feed breaks and
when its data goes stale (`notifications create --conditions source_failed,source_stale`). Common codes:
`parse_failed` (the address returned a web page: use the calendar's ICS
address), `unreachable` (public http(s) on port 80 or 443 only), `auth_failed`,
`http_status`, `card_data_invalid`. Problems on create: `source_target_taken`
(the card has a source), `source_target_unsupported` (the detail names the card
types the kind fills), `source_secret_required`, `source_limit_reached` (200).

## Calendars (`ics`)

`config`: `calendars` (1 to 60, each `{key, name?, floor?, capacity?}` with a
key of lower-case letters, digits, `-` and `_`), `days` (1 to 31, default 7),
`time_zone` (IANA, for floating times and the day boundary), `private_title`
(default `Private`). One secret per calendar: `calendar_url.KEY`. Google,
Outlook, iCloud and Nextcloud addresses, and `webcal://`, work. Set
`time_zone` when the feed names none (the warning says so). Recurrences,
exceptions and time zones are expanded on the server; events marked private or
confidential show their times only. Free (transparent) events are left out of a
`study-rooms` card. A `study-rooms` card takes one calendar per room.

`include` and `exclude` (also on `microsoft365`, `google_calendar` and
`momentus`) filter events by title: each is a list of 1 to 20 keywords of up to
100 characters, matched as a substring without regard to case or accents (`café`
matches `CAFE`). An event stays when it matches an `include` keyword (when
`include` is set) and no `exclude` keyword: `--set 'include=["Board","Council"]'
--set 'exclude=["Setup"]'`. Only the title is matched, never the location,
organizer or description, and a private event is matched on its real title but
still shows the private title (`exclude: ["private"]` removes nothing).
`source test` counts the events removed in `data.stats.filtered`; when the
keywords leave none of the window's events, a warning says to check them.


## Sheets, CSV and JSON (`sheets`, `csv`, `json`)

These fill any card. The settings carry a `mapping`, a JSON template that builds
the card's data from what was read; the card's own schema decides whether the
result is accepted, so `source test` is the loop: edit the mapping until
`data.valid` is true.

- `sheets`: `{url, sheet?, header_row, key_column?, mapping}`, no secret. The
  sheet must be shared (Share, General access, Anyone with the link, Viewer) or
  published to the web, else the status is `not_shared`: ask its owner, never
  sign in for them. `url` is the link they copy; `sheet` names a tab.
- `csv`: `{url, delimiter?, header_row, key_column?, auth, header_name?, mapping}`.
  `json`: `{url, auth, header_name?, rows_path?, key_field?, mapping}`. Both also
  take the request settings below.
- `auth` is `none`, `bearer` or `header` (with `header_name`, such as
  `X-API-Key`), or one of the kinds below. The token is `--secret token=@FILE`,
  sent only to the address's own origin: pointing the source at another site asks
  for it again.

Mapping roots. Tables: `rows` (objects by column key), `columns` (`[{key,
name}]`) and, with `key_column`, `by_key`. JSON: `body` and, with `rows_path`
plus `key_field`, `by_key`. A header becomes a key in lower case with `_` for
anything else (`Sold out` is `sold_out`). Prefer `by_key` to positions: a key
keeps pointing at its row when someone sorts the sheet. Cells are text:
`{"$number": "{{item.price}}"}` reads `$4.50` or `3,50` (with `"$decimal": ","`),
`{"$bool": "{{item.sold_out}}"}` reads yes, x or 1. `{"$each": "{{rows}}",
"$template": T}` maps a list; `{"$group": "{{rows}}", "$by": "{{item.section}}",
"$template": T}` groups, with `group.key` and `group.items` inside. A missing
column leaves its member out, and the card then names what it lacks.

A `menu` sheet with columns Section, Item, Price:

    {"sections": {"$group": "{{rows}}", "$by": "{{item.section}}", "$template": {
      "name": "{{group.key}}",
      "items": {"$each": "{{group.items}}", "$template": {
        "name": "{{item.item}}", "price": {"$number": "{{item.price}}"}}}}}}

A `kpi` sheet with columns Metric, Value and `key_column` Metric:

    {"tiles": [{"label": "Revenue", "value": {"$number": "{{by_key.Revenue.value}}"}}]}

To see what a source reads, test with the mapping `{"columns": "{{columns}}",
"rows": "{{rows}}"}`: the card refuses it, and `data.document` shows every key
and row. `parse_failed` means the address returned a web page or a file that is
not CSV text or JSON; `not_shared` names the sharing setting to change.
Warnings count repeated keys and cut rows (10,000 rows, 200 columns) without
quoting the data.

### HTTP requests

`csv` and `json` sources make the call an API expects, through `--settings` or
`--set`:

- `method` is `GET`, or `POST` with a `body`: a JSON object or array, or text sent
  as written (`"body_format": "form"` URL-encodes fields). `graphql: {query,
  variables}` is a POST too. A body is at most 16 KiB.
- `headers` holds up to 8 more headers that are not credentials. Credentials are
  `auth`: `bearer` or `header` (secret `token`), `basic` (`username`, secret
  `password`), `oauth2` for client credentials (`token_url`, `client_id`,
  `scope?`, `audience?`, secret `client_secret`) or `token_request`, a login whose
  answer holds the token (`token_url`, `token_body` reading `{{secrets.NAME}}`,
  `token_path`). A second credential header, or a key in the address, is a secret
  named `header.NAME` or `query.NAME` (up to 8 each): `--secret
  header.X-Api-Key=@FILE`. Secrets go only to the address's origin.
- Date placeholders `{{now}}`, `{{today}}` and `{{unix}}`, with an offset
  (`{{now-90m}}`, `{{today+7d}}`), fill the address, `body` and `headers` on every
  run, in `time_zone` (IANA, else UTC).
- `pagination` reads more pages: `link_header`, `next_url`, `cursor` or `page`, up
  to `max_pages` (5, at most 20). A next address must stay on the source's origin.
- `format` is `auto`, `json`, `csv` or `xml`. An XML answer becomes a tree, and an
  RSS or Atom feed also gives `body.items` (`title`, `link`, `published`,
  `summary`, `image`).

`source test` shows `request`, the first call as it went out (method, address
with query secrets masked, header names, the first 1 KiB of the body), beside the
document. A POST with a JSON body and an `X-Api-Key` header secret, counting open
orders on a `kpi` card:

```sh
screenrig source test --kind json --card crd_ID --settings @orders.json --secret header.X-Api-Key=@orders.key
```

```json
{"url": "https://api.example.com/v2/orders/search",
 "method": "POST",
 "body": {"status": "open", "since": "{{today-7d}}"},
 "time_zone": "America/Vancouver",
 "mapping": {"tiles": [{"label": "Open orders", "value": {"$count": "{{body.orders}}"}}]}}
```

An API that wants OAuth 2 client credentials, with `--secret
client_secret=@client.secret`:

```json
{"url": "https://api.example.com/v1/summary",
 "auth": "oauth2",
 "token_url": "https://login.example.com/oauth2/token",
 "client_id": "signage",
 "scope": "metrics.read",
 "mapping": {"tiles": [{"label": "Active users", "value": {"$number": "{{body.active_users}}"}}]}}
```

The source asks the token address for a token whenever the last one expires and
never stores it; `"token_auth": "basic"` sends the client id and secret as a
Basic header instead of in the form.

### Computed values

A mapping also computes numbers and true or false on the server. A page
condition tests equality only (`visibility.data {key, path, equals}`), so compute
the comparison and the page follows a number with no Player change:

- `$gt`, `$gte`, `$lt`, `$lte`, `$between`, `$eq`, `$ne`, `$contains` and `$in`
  give true or false (`{"$lt": ["{{body.stock}}", 5]}`); `$and`, `$or` and `$not`
  combine them.
- `$sum`, `$avg`, `$min` and `$max` give one number from an array (`{"$sum":
  "{{rows}}", "$of": "{{item.amount}}"}`) and `$count` the number of elements,
  with `$where` to count those a condition holds for. Numbers read as `$number`
  reads them (`"$decimal": ","` for `3,50`); empty cells are skipped and counted
  in a warning.
- A comparison that cannot be made is false with a warning, so missing data never
  switches a page on.
- The result must be a property the card has: `cards show TYPE` lists them, and
  `card_data_invalid` names any other member.

A `badge` that shows only while some product is below its own reorder level
(`active: false` lowers the card), from a sheet with columns Stock and Reorder at:

```json
{"text": "LOW STOCK", "tone": "danger",
 "active": {"$gt": [{"$count": "{{rows}}", "$where": {"$lt": ["{{item.stock}}", "{{item.reorder_at}}"]}}, 0]}}
```

A page that plays only then takes this `visibility`, with an ordinary page after
it:

```json
{"enabled": true, "data": {"key": "crd_ID", "path": "/active", "equals": true}}
```

A `kpi` tile that totals a sheet column written with decimal commas:

```json
{"tiles": [{"label": "Sales", "value": {"$sum": "{{rows}}", "$of": "{{item.amount}}", "$decimal": ","}, "unit": "EUR"}]}
```

Two tips:

- A CSV on OneDrive or SharePoint shared with Anyone with the link: use its share
  link plus `?download=1` (`&download=1` when the link already has a query) as the
  `csv` `url`, which returns the raw file. Without it the link answers a web page
  (`parse_failed`), and the file must be CSV text in UTF-8, not a spreadsheet.
- Read a value by its row's key, not its position: with `key_column` set to
  Metric, `{{by_key.Revenue.value}}` stays on the Revenue row after someone sorts
  the sheet or inserts a row above it, while `{{rows[0].value}}` follows whatever
  row is first.


## Meeting rooms (`microsoft365`, `google_calendar`)

A room's calendar fills a `room` card (the door sign of exactly one room) or a
`room-board` card (a building's rooms, up to 60). Create the card first
(`card create --type room ...` with `room`, `capacity`, `showOrganizer`;
`--type room-board` with `showTitles`). The cards take no input and the
sources only read, so nothing is booked, ended or checked in from a screen; the
card works out free, in use and next on the screen every second, so a sign
stays right while its screen is offline. An `ics` calendar fills the same
cards.

- **`microsoft365`** reads Exchange Online room mailboxes with the customer's
  own Microsoft Entra app. Config: `tenant` (directory id or verified domain,
  never `common`, `organizations` or `consumers`), `client_id`, `rooms`
  (`[{key, email, name?, floor?, capacity?}]`), `days`, `time_zone`,
  `private_title`. Secret `client_secret` (the secret's Value):
  `--secret client_secret=@secret.txt`. The app needs the Microsoft Graph
  application permission `Calendars.Read` with admin consent.
- **`google_calendar`** reads resource calendars as the customer's service
  account. Config: `rooms` (`[{key, calendar_id, name?, floor?, capacity?}]`),
  `subject?` (domain-wide delegation), `days`, `time_zone`, `private_title`.
  Secret `service_account_key`: the JSON key file as Google issues it,
  `--secret service_account_key=@key.json`; the secret's hint is the account's
  address, which each room calendar is shared with (See all event details).

The customer's administrator does the setup on their side; ask for no admin
credentials. Give them the Exchange commands that scope the app to the room
mailboxes (`New-ApplicationAccessPolicy -AppId CLIENT_ID -PolicyScopeGroupId
GROUP -AccessRight RestrictAccess`, checked with `Test-ApplicationAccessPolicy
-AppId CLIENT_ID -Identity ROOM`) and, for meeting titles to show,
`Set-CalendarProcessing -Identity ROOM -DeleteSubject $false
-AddOrganizerToSubject $false`. Both secrets go in only as `@FILE` or `-`.

A **connection** holds the access once: every room source, a Power BI
connection ([dashboards](dashboards.md#power-bi)) and a SharePoint sync account
([media sync](media-sync.md)) reuses it by `connection_id` instead of carrying a
tenant, client id and secret of its own (`--set connection_id=pcn_ID`; inline
settings keep working, and the two cannot be mixed). `connection create
microsoft` or `connection create google` makes one, with `--mode` set to
screenrig_app or own_app. The simple route is screenrig_app, screenRIG's own
application, which the customer approves once, so you never handle a secret.
The answer carries a `consent_url`; give it only to the customer's administrator
(for Google, a person whose account sees every room calendar), then `connection
show pcn_ID` reads `pending_consent` until they approve and `ready` after. The
customer still limits the app to the room mailboxes with the Exchange commands
above. A Google source on a screenrig_app connection reads what the approving
account can see and takes no `subject`. Mode own_app keeps the customer's own
Entra app or service account key. `connection test pcn_ID` signs in and, for
Microsoft, lists the permissions the token carries; `connection connect pcn_ID`
makes a new consent link; `connection delete` is refused while a source, BI
connection or sync account uses it.

Preview with `source test` and read `data.stats`: `rooms`, `events`, one
`events_KEY` per room (compare with what the customer sees in their calendar)
and, for Microsoft 365 when the app also holds `Place.Read.All`, `places_rooms`.
Set `time_zone` (otherwise days start at UTC midnight and a warning says so).
Free time is not a booking, tentative counts as busy, private and confidential
meetings carry `private_title` and no organizer. The document carries titles
and organizers; a `room` card draws organizers only with `showOrganizer` and a
`room-board` titles only with `showTitles`.

Errors quote Microsoft's or Google's own text. `auth_failed` with an `AADSTS`
code or `invalid_grant` is a wrong secret, tenant or key, or a missing consent
or delegation: the customer fixes it on their side, then `source refresh`.
`config_invalid` names the room's address when no calendar can be found or
seen. One room failing fails the sync and names the room (`Room KEY: ...`);
the card keeps its last good document.


## A venue's booking system (`momentus`)

Reads the functions (each use of a room, with its dates and times) and spaces of
a Momentus Enterprise installation (formerly Ungerboeck, EBMS) with an API user
the venue's administrator creates in Momentus (Main Menu, Api Users). Ask for no
admin login: they give you the server address, the organization code, the API
user's id, one Key GUID and the Secret GUID, and you enter the two GUIDs as
`--secret api_key=@FILE` and `--secret api_secret=@FILE`.

Config: `base_url` (the https address of the Momentus web server, such as
`https://momentus.example.com/prod`), `organization`, `api_user`, `time_zone`
(set it: Momentus keeps local dates and times), `days`, and either `rooms`
(`[{key, space, name?, floor?, capacity?, area?}]`, `space` is the Momentus
space code) or nothing, which makes every space Momentus lists a room (key =
the code in lower case; `space_filter` narrows it). `exclude_status_codes` lists
the function status codes that are cancelled or not to be shown; Momentus status
codes are the venue's own, so ask. It fills an `events` card (the event
directory), a `room-board` card, or a `room` card for exactly one room.

One source can also keep each screen to its own room. Set `room_key_prefix`
(for example `momentus-room-`) and the source writes a `room` document per room
under that prefix plus the room's key. Give each room's screen the field:
`screen update SCR --field room=ballroom-a`. Use the inline catalogue type
`room` in this playlist primitive:

```json
{"id":"door","primitive":"card","card":"room","layout":"full","content_fit":"fill","params":{"room":"{screen.field.room}"},"data":"momentus-room-{screen.field.room}"}
```

A `crd_` instance placement omits `params` and `major`: those belong
to the instance. Its optional `data` selects a concrete key or a
`{screen.field.NAME}` template; omitting it uses the instance document.
The source's `--card crd_ID` still names its sync target;
the keyed playlist placement above names the catalogue type. `area_key_prefix` does
the same for a hallway display, a `room-board` of the rooms sharing an `area`
(set on each room, or by `area_field`'s screens). `source rooms src_ID` is the
check: rooms no screen shows, and screens with no room field or a value that
names no room (it suggests the room it probably meant). Fix with `screen update
SCR --field room=KEY`. Set the page's `visibility.data.key` to the same
template and keep an ordinary page without visibility as the fallback. The
conditional page falls back when its room's data has expired.

It refreshes every minute (30s floor), so a room change shows within about a
minute. `stale_after_seconds` defaults to 30 minutes. `source test` shows the
rooms and events read and `data.stats` (`functions`, `functions_other_spaces`,
`events_KEY`). The status never quotes Momentus's own text: `auth_failed`
means the API user, key or secret is wrong or may not read functions and spaces;
a 400 means `function_filter` or `space_filter` is not a valid Momentus search.


## Menus from a till (`square`, `shopify`, `toast`)

Fills a `menu` card or a `price-matrix` card from the business's own catalogue.
Create the card first (`card create --type menu --file PARAMS.json`; the first
sync replaces its `sections`), then preview and create as above. The document
cannot carry the currency symbol: set the card's `currency` (`€`); `source test`
warns while it still shows `$` over other prices.

- `square`: `--secret access_token=@FILE`, the Production access token from the
  Square Developer Dashboard (`--set environment=sandbox` with the Sandbox
  token). It reads only, and only from Square, but a Square token cannot be
  narrowed: keep it in a file. With several locations set `--set location_id=ID`;
  the failed `source test` lists them.
- `shopify`: `--set shop=NAME` (the `.myshopify.com` name; a custom domain is
  refused) and either `--secret access_token=@FILE` (a custom app with
  `read_products` only) or `--set client_id=ID --secret client_secret=@FILE` (a
  Dev Dashboard app). `--set 'collections=["hot-drinks","pastries"]'` makes those
  collections the sections, in order; `--set tag=menu` keeps tagged products.
- `toast`: `--set restaurant=GUID --set client_id=ID --secret
  client_secret=@FILE` (`--set environment=sandbox` only for credentials Toast
  issues to integration partners). The restaurant creates read-only API access in
  Toast Web (Integrations, Toast API access, Manage credentials) with the scopes
  `menus:read` and `stock:read`, and Toast emails the location's GUID. A menu
  shows while its own schedule allows, on the restaurant's clock; `--set
  'menus=["Dinner"]'` names the menus to show, and a board that follows day-parts
  takes a source per menu. Sold out follows Toast's stock status. The answer
  carries no currency: set the card's `currency`.

All three take `include_sections` and `exclude_sections` (section names, as lists),
`hide_sold_out` (default false: sold-out rows show as sold out) and, for `menu`
cards, `variations` (`rows`: a row for each size, or `first`). A `price-matrix`
card shows sizes as up to 6 columns and refuses `variations`. A `menu` card holds
8 sections of 24 rows, a `price-matrix` 12 of 40: a cut is a `data.warnings`
entry, so read it. Sold out is the till's own mark or availability, not stock
counts. A catalogue past 30 Square pages or 500 Shopify products fails with
`too_large`; name collections or sections. A credential belongs to the
environment, store or restaurant it was entered for; `source_secret_required`
asks again.

## Keep cards current

screenRIG reads addresses on a schedule and accepts pushes; for everything else
you are the automation. Pick the lane by how each card's data moves.

| The data | Lane |
| --- | --- |
| Must stay live with nobody running anything: a calendar, a sheet, a JSON, CSV or XML address, Slack, social posts, reviews | A source: a preset when one exists (`source presets`), else the generic HTTP source ([sources](sources.md)) |
| Changes hourly or daily and you can read it with your own tools: a web page, a file, a database, a connector in your runtime | Your own schedule: read it, then `card data put` with `--ttl` |
| A system that pushes: a CMS, a till, GitHub, Stripe, Slack events | A card webhook, with the vendor's signature where it signs ([card webhooks](playlists.md#card-webhooks)) |

Take the first lane that fits. A source runs on screenRIG's schedule, outlives
your session and reports its own failures (`source_failed`, `source_stale`).

### Your own schedule

```sh
screenrig card data put crd_ID --file data.json --ttl 3h
```

1. Read the data with your own tools and write the card's whole document.
   `cards show TYPE` lists its dynamic properties; `card preview crd_ID` draws it.
2. Run the write from a recurring task in your runtime (a scheduled task, a
   routine, a cron job) at the data's own pace: hourly data hourly, a daily menu
   daily. A schedule that lives only in a conversation ends with it, so run it
   where it outlives the session, and tell the user where it runs and how to
   stop it.
3. Size `--ttl` to the schedule: longer than the gap between runs, so a late run
   does not blank the card, and short enough that stale data is not worth
   showing (`3h` for an hourly job, `36h` for a daily one). When it elapses with
   no new write the card goes blank on every screen, offline ones included, and
   a page that depends on it through `visibility.data` falls back. Write on every
   run, changed or not: the write renews the expiry.
4. Once per project, so a stopped schedule is noticed:
   `screenrig notifications create --email owner --conditions card_data_stale`
   ([notifications](notifications.md#card_data_stale-a-scheduled-write-stops)).
5. A write that answers `rate_limited` waits `error.retry_after_seconds`; never
   write faster than the data moves.

### Systems that push

`kv webhook create --card crd_ID --map FILE` prints the sender's url and secret.
A vendor that signs its posts (GitHub, Stripe, Shopify, Slack, Linear, Vercel,
Asana, any HMAC sender) needs no header: `--verify VENDOR --verify-secret-file
FILE` lets its own signature open the webhook. Webhook data stays until the next
post, so a quiet sender keeps its last value on glass.

### Recipes

**Stock quotes.** `feeds` carries no stock quotes. Use TradingView's free widget
(ticker tape, market overview or symbol overview): on TradingView's widget page
choose the symbols, the dark theme and the size, copy the snippet, save it as one
HTML page on a host the customer controls, and play that page in an `iframe`
primitive with `content_fit: "fill"` ([dashboards](dashboards.md) shows the
primitive). The widget is a script that draws its own iframe, so it needs the
page and the screen's internet access, and Apple TV cannot show it. Leave the
TradingView link the snippet puts under the widget: it is TradingView's
attribution, and changing it is TradingView's to allow.

**Slack, Bonusly, Facebook, Instagram, Google reviews.** Each is a preset
([sources](#presets)). Create the card the preset fills, ask the
customer to save the credential to a file, preview, then create:

```sh
screenrig card create --type workplace-posts --file posts.json
screenrig source test --preset slack-channel --card crd_ID --set channel=C0123456789 --secret token=@slack.token
screenrig source create --preset slack-channel --card crd_ID --name "Announcements" --set channel=C0123456789 --secret token=@slack.token
```

`bonusly` fills `kudos`, `facebook-page` and `instagram-business` fill
`social-wall`, `google-reviews` fills `reviews`; `source presets NAME` lists the
fields and how the customer gets the credential. A preset keeps the last good
data for its stale period, and `source_failed` and `source_stale` notifications
say when it breaks.

**Microsoft Teams posts.** A card webhook created with `--handshake
microsoft_graph` answers Graph's validation request, but Graph's notifications
carry no header screenRIG verifies and name a post without its text, so a
subscription cannot fill a posts card alone. Fill a `workplace-posts` card from
something that has the text and can set a header (a Power Automate flow on "When
a new channel message is added" that posts to the webhook with the webhook's secret
as a bearer credential), or read the channel with your own Graph access on a schedule and
`card data put` the posts with `--ttl`.
