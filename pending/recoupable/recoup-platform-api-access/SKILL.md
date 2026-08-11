---
name: recoup-platform-api-access
description: Call the Recoup API and external connectors directly — fetch any platform resource (artists, socials, organizations, research, documents) and run connector actions (Google Docs/Sheets/Drive edits, Gmail, TikTok, Instagram). Use whenever you need raw Recoup data, a platform resource, to write curl against api.recoupable.dev, or to read/write something outside Recoup like a Google Doc URL or a spreadsheet. The plumbing every other skill rides on. To onboard or operate on an artist use the recoup-roster-* skills; for first-run connection use recoup-platform-connect-account.
---

# Recoup — API Access

The platform access layer: authenticate, talk to the Recoup REST API, and
invoke external connectors. Base `https://api.recoupable.dev/api`; docs
`https://docs.recoupable.dev` (`/llms.txt`, `/llms-full.txt`, OpenAPI JSONs).

## Auth — one Bearer header, inline

Every call uses the same header, dropped straight into the `curl` (no setup step):
the sandbox sets one of the two vars, and the API accepts a `recoup_sk_` key or a
Privy JWT over `Bearer`.

```bash
curl -sS -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  "https://api.recoupable.dev/api/artists/{id}/socials"
```

If neither var is set, ask the user to authenticate — don't retry blindly.

## Pick the artist mode first (guessing here fabricates artists)

- **A — any-artist research** (a name; no roster lookup) → Research endpoints.
- **B — browse my roster** → Roster discovery (below).
- **C — a specific roster artist** → Roster discovery, match the name, capture
  `account_id` + row `id`.
- **D — add an artist** → use recoup-roster-add-artist.

**Roster discovery:** `GET /accounts/id` → `GET /artists` (your roster; `org_id`
optional — orgs are often empty, so don't stop when `organizations` is `[]`).

> **Use `account_id`, not the list `id`, for every `/artists/{id}/*` sub-resource**
> (socials/posts/fans key on `account_id`; the list's top-level `id` 404s). And
> **socials are embedded** in the `/artists` response as `account_socials`
> (`username`, `followerCount`, `profile_url`) — read them there before calling
> `/artists/{account_id}/socials` at all.

**Stop rule — never invent a roster:** if `GET /accounts/id` resolves to an
`agent+…@recoupable.com` email, or `organizations` and `artists` both return `[]`,
it's a throwaway key — say so and ask for a real-account key (or
recoup-platform-connect-account). Don't fabricate an artist/roster to keep moving.

**Stop rule — never invent metrics/data:** report only figures you retrieved from a
successful call this run. If a call errors or returns empty, or no connector exists
for a metric (`GET /connectors/actions` → check `isConnected`), **say so and omit
it** — never estimate, use "industry averages", or fill gaps with
sample/placeholder numbers. A short accurate report beats a padded, invented one.

**Before you give up on missing data — get it, or hand back a connect link.** When a
metric's source isn't connected, work down this list before omitting:
1. **Scrape the public data you can get** — `POST /api/socials/{social_id}/scrape`
   (one profile) or `POST /api/artist/socials/scrape` (all of an artist's). Works
   for TikTok / Instagram / X / YouTube / Threads / Facebook. Report those real
   public numbers.
2. **Check connection status** — `GET /api/connectors` → each connector's
   `isConnected`.
3. **Mint a connect link** — `POST /api/connectors {"connector":"youtube"}` returns
   `{ redirectUrl }` (a Composio OAuth URL). Surface it to the caller so the user can
   self-connect: *"CPM/revenue needs YouTube Analytics — connect here: {redirectUrl}"*.

Return the real public data **plus** the connect link — that beats both a fabricated
report and an empty/omitted one.

## Docs map (pull the section you need; don't guess paths)

Account & Identity · Artists & Content · Research (Songstats + Web) · Social
Integrations · Chat & Agents · Developer/Infra. Find the exact path/params by
grepping `llms-full.txt` or pulling the OpenAPI JSON for the area, e.g.:

```bash
curl -s https://docs.recoupable.dev/llms-full.txt | grep -A 30 -i "similar artists"
curl -s https://docs.recoupable.dev/api-reference/openapi/research.json | jq '.paths | keys'
```

Geography comes from `audience`; discovery from `similar` + `web`.

## Connector actions (Google Docs/Sheets/Drive, Gmail, TikTok, Instagram)

For reads/writes **outside** Recoup:
- `GET /connectors/actions` — catalog (each action's `slug`, `parameters`
  schema, `connectorSlug`, `isConnected`).
- `POST /connectors/actions` `{actionSlug, parameters}` — execute one.

Slugs are `UPPERCASE_SNAKE_CASE` (e.g. `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`,
`GMAIL_FETCH_EMAILS`). **Always pull the parameters schema from the catalog before
executing** — shapes vary per action. Trigger heuristic: a pasted
`docs.google.com`/`drive.google.com`/`sheets.google.com` URL, or "edit this doc",
"send an email", "post on TikTok".

## Send an email (from Recoup)

`POST /api/emails` sends an email from `Agent by Recoup <agent@recoupable.com>` via
Recoup — works headless with your API key, no Gmail connector needed. Use it for
reports, alerts, and scheduled-task output.

Run it with `bash` (not `web_fetch` — that hides the response and you can't confirm
the recipient):

```bash
curl -sS -X POST -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"to":["someone@example.com"],"subject":"Weekly report","text":"# Summary\n…"}' \
  "https://api.recoupable.dev/api/emails"
# → {"success":true,"message":"Email sent successfully … to someone@example.com.","id":"<resend-id>"}
```

`to` is a JSON array of email strings (`["a@b.com"]` — not a bare string, not
`[{"email":…}]`). The only keys are `to`, `cc`, `subject`, `text`, `html`,
`chat_id`, `account_id`; an unknown key (e.g. `recipients`) is dropped, and `to`
then defaults to your own account email — silently misrouting the message. `subject`
is optional. Read the response and check `message` names the recipient you intended.
No payment method on file → `to`/`cc` are limited to the account's own email (403).
To send as the user from their own Gmail instead, use `GMAIL_SEND_EMAIL`.

## Troubleshooting

401 = token missing/expired (check the credential). 403 = no access to the
org/artist. 404 = re-check the Docs map (endpoint moved/renamed). 5xx = retry once,
then surface the status.

## When NOT to use

- Files inside the sandbox → filesystem tools.
- Onboarding/operating an artist's workspace → the recoup-roster-* skills.
- A domain task (research/content/release/deal/song) → that domain skill, which
  makes its own calls.
