# Live dashboards on screens

A Grafana dashboard or panel, a Power BI report or a Tableau view plays as an
`iframe` primitive ([Power BI](#power-bi) and [Tableau](#tableau) below), and a
page behind any other sign-in plays as an image ([signed-in
pages](#signed-in-pages)). A Grafana view: the server draws it
as a PNG through Grafana's image renderer on a cadence and shares each render
among screens of the same size; a screen never talks to Grafana and keeps the
last image if Grafana fails. A connection's token stays on the server, sealed,
and no playlist holds a credential.

## What the user does in Grafana

1. Install the **Grafana Image Renderer**, as the plugin or as the remote
   rendering service. Without it nothing renders.
2. Create a **service account** with the **Viewer** role and add a token. Ask
   the user to save the token to a file for you; never take it as an argument
   or print it.
3. For a **public dashboard** (no connection needed), the user sets
   `allow_embedding` in Grafana's settings, because that page plays live from
   Grafana.

Grafana must be reachable from the public Internet: a private or reserved
address is refused.

## The flow

```sh
screenrig bi connection create grafana --url https://grafana.example.com --token-file token.txt
screenrig bi connection test bic_ID
screenrig bi connection browse bic_ID --query lobby      # dashboards and uids
screenrig bi connection browse bic_ID --dashboard UID    # its panels
screenrig bi view create --connection-id bic_ID --dashboard UID --panel 4 --from now-6h --var host=web1 --refresh 5m
screenrig bi view test biv_ID --output check.png         # open the image before publishing
```

`--url` accepts a dashboard address copied from the browser (quote it:
`--url 'https://grafana.example.com/d/UID/name?viewPanel=4&var-host=web1'`) and
reads the panel, time range, variables and theme from it. A public dashboard is
`bi view create --public-url URL` with no connection. `--refresh` is 30s to 24h
(default 5m); `--fit contain|cover|fill` sets how the image fills the screen.

`bi view create` prints `embed_url`. Put it in an `iframe` primitive:

```json
{"id": "kpis", "primitive": "iframe", "src": "EMBED_URL", "title": "Ops dashboard", "rect": {"x": 0, "y": 0, "width": 1920, "height": 1080}, "layer": 0, "content_fit": "fill"}
```

Then publish as usual (`playlist create`, `screen assign`). Edit a view with
`bi view update`: screens pick up a new target at their next refresh without a
republish.

## Rules and errors

- `bi connection test` checks the token and lists the Image Renderer plugin; a
  plugin that is not listed only warns, because a remote renderer does not show
  as one. `bi view test` renders for real and is the check that counts.
- `bi_upstream_refused` (exit 5): Grafana refused the token; fix it with
  `bi connection update ID --token-file FILE`. `bi_upstream_unavailable`
  (exit 9): Grafana is unreachable, not public, timed out or has no renderer; the
  detail says which.
- `bi connection update ID --url ADDRESS` on another host, scheme or port
  needs `--token-file` (Grafana) or `--secret-file` (Tableau) in the same
  command: a stored secret is sent only to the address it was saved for.
- A view plays only on screens of its own project. A playlist exported to
  another project shows `forbidden` there: create a view in that project.
- Deleting a view leaves screens showing it with `not_found` until their
  playlist changes. A connection that views use cannot be deleted.
- The page on glass shows no text except an error code, or the time of a stale
  image in a corner: read `bi view show ID` for `status.last_error`.

## Power BI

A report plays as an `iframe` primitive that embeds it with a view-only token
the server generates (Power BI "app owns data") and renews before it expires. A
screen never holds the client secret, and the report needs no Power BI sign-in.

### What the user does in Microsoft, once

1. In Microsoft Entra, register an app (single tenant, no redirect URI, **no API
   permissions**) and add a **client secret**. Ask the user to save the secret's
   **Value** (not its ID) to a file for you; never take it as an argument or print
   it. Note the app's **Application (client) ID** and the **Directory (tenant)
   ID**.
2. A Power BI admin opens the admin portal, Tenant settings, Developer settings,
   and turns on **Embed content in apps** and **Service principals can call
   Fabric public APIs** (older portals call the second one "Allow service
   principals to use Power BI APIs" or "Service principals can use Fabric APIs")
   for the organization or a security group that holds the app.
3. In each workspace to show: Workspace access, add the app as **Member** or
   **Admin**. My workspace is not available to an app.
4. For production the workspace must sit on a **Fabric (F), Power BI Embedded
   (A) or Premium (P/EM)** capacity. Commercial cloud only.

### The flow

```sh
screenrig bi connection create powerbi --tenant-id TENANT --client-id APP_ID --secret-file secret.txt
screenrig bi connection test bic_ID                       # counts the workspaces the app sees
screenrig bi connection browse bic_ID                     # workspaces and their ids
screenrig bi connection browse bic_ID --workspace WS_ID   # that workspace's reports
screenrig bi view create --connection-id bic_ID --workspace WS_ID --report REPORT_ID --refresh 5m
screenrig bi view test biv_ID                             # generates a real embed token
```

`--url` takes a report address copied from Power BI
(`https://app.powerbi.com/groups/WS/reports/REPORT`, optionally ending in a
`/ReportSection...` page). `--page NAME` (repeat it, by page name or display
name) picks pages and `--all-pages` takes every visible one; two or more pages
need `--rotate 10s..1h`, and `--rotate` needs two or more pages. `--refresh` is
60s to 24h (default 5m), or `0` for a report that updates itself (DirectQuery,
automatic page refresh). Put `embed_url` in an `iframe` primitive as above.

A Microsoft connection in mode own_app can supply the app instead:
`bi connection create powerbi --connection-id pcn_ID` replaces `--tenant-id`,
`--client-id` and `--secret-file`, and the same connection serves the project's
room calendars and SharePoint sync
([connections](sources.md#meeting-rooms-microsoft365-google_calendar)). Power BI
refuses a screenrig_app connection: embedding needs the customer's own app,
registered without permissions.

A **Publish to web** link, `bi view create --public-url 'https://app.powerbi.com/view?r=KEY'`,
needs no connection and plays as Power BI serves it, reloaded every `--refresh`,
without page rotation. Publish to web makes the report public to anyone with the
link: tell the user before using it.

### Power BI errors

- `bi_upstream_refused` on the connection test or `bi view test`: the detail
  names the cause. 401 or 403 is the Developer tenant settings or the app's role
  in the workspace. An `AADSTS7000215` code is a secret ID given instead of its
  Value; `AADSTS700016` or `AADSTS90002` is a wrong client or tenant ID. Fix with
  `bi connection update ID --secret-file FILE` (or `--client-id`, `--tenant-id`).
- A test that sees no workspaces fails: add the app to a workspace.
- A dataset with row-level security cannot be shown: Power BI refuses its embed
  token, and the test shows its message.
- A test does not judge capacity or what the report shows; look at the screen.

## Tableau

A Tableau Cloud or Tableau Server view plays as an `iframe` primitive that embeds
it with the Tableau Embedding API and a five-minute token the server signs with a
connected app (embed scope only) each time the page loads. A screen never holds
the connected app's secret. A Tableau Public viz needs no connection.

### What the user does in Tableau, once

1. Settings, Connected Apps, **New Connected App**, **Direct trust**. Copy its
   **Client ID**, generate a secret, enable the app and the secret, and copy the
   **Secret ID** and the secret **Value**. Ask the user to save the Value (not the
   ID) to a file for you; never take it as an argument or print it.
2. Pick or create the Tableau **user** the screens show, and give it access to only
   the views screens show: anyone holding a screen's ticket can embed any view that
   user can see.
3. After `bi connection create`, run `bi connection show ID` and add its
   `embed_origin` host to the connected app's **domain allowlist** (Only specific
   domains). Only a screen loading the view proves this step.
4. Tableau Cloud, or Tableau Server 2023.3 or later. The screens must reach the
   Tableau host and accept its third-party cookies.

### The flow

```sh
screenrig bi connection create tableau --url https://10ay.online.tableau.com --site SITE \
  --client-id CLIENT_ID --secret-id SECRET_ID --username USER --secret-file secret.txt
screenrig bi connection test bic_ID                       # signs in as the user
screenrig bi connection browse bic_ID --query sales       # views as Workbook/View
screenrig bi view create --connection-id bic_ID --view Sales/Overview --refresh 5m
screenrig bi view test biv_ID                             # looks the view up as the user
```

`--url` is the server's address, or your Tableau Cloud **pod** (`10ay.online...`,
not `online.tableau.com`); leave `--site` out for Tableau Server's default site.
`bi view create --url` takes an address copied from Tableau (`/t/SITE/views/W/V`,
Tableau Cloud's `#/site/SITE/views/W/V`) or `Workbook/View`. `--rotate-sheets
--rotate 10s..1h` turns the workbook's published sheets; `--refresh` is 60s to
24h (default 5m) or `0`. Put `embed_url` in an `iframe` primitive as above. A
dashboard with a fixed size draws at that size: publish it with Automatic sizing
to fill a screen.

A **Tableau Public** viz, `bi view create --public-url
https://public.tableau.com/app/profile/USER/viz/WORKBOOK/VIEW`, needs no connection
or token; Tableau Public draws its own toolbar.

### Tableau errors

- `bi_upstream_refused` on the test: the detail is Tableau's own words, such as an
  unknown secret ID, a disabled app or secret, or a user the site does not know.
  Fix with `bi connection update ID --secret-id ID`, `--username`, `--site` or
  `--secret-file FILE`.
- A `bi view test` that does not find the view: names are case-sensitive; copy the
  path from `bi connection browse`, and check that the user can open the view.
- Neither test judges the domain allowlist or the embed permission: if the screen
  shows `tableau_auth_failed`, check the allowlist and that the secret is enabled.

## Signed-in pages

A page behind any other sign-in (Salesforce, Looker Studio, Datadog, HubSpot)
plays as an image. A web connection is a service account of the site and a web
view is one page of it: a server-side browser signs in as that account, opens the
page and draws it, and each image is shared among screens of the same size, as for
Grafana. A screen never sees the credentials, and a view draws only while a
screen's playlist names it. The kind needs the same plan feature as the other
dashboards.

What the user does: create a **read-only service account** for screenRIG on the
site (never a person's own login) and save its password to a file; when it uses
an authenticator app, save the base32 key the site shows during setup (or its
`otpauth://` address) to a file too.

```sh
screenrig bi connection create web --login-mode auto --login-url https://app.example.com/login \
  --username signage@example.com --password-file password.txt --totp-file totp.txt
screenrig bi connection test bic_ID
screenrig bi view create --connection-id bic_ID --url https://app.example.com/dashboards/sales \
  --wait-for '#sales-total' --refresh 5m
screenrig bi view test biv_ID --output check.png         # open the image before publishing
```

Put `embed_url` in an `iframe` primitive as above.

- `--login-mode`: `auto` fills the form at `--login-url` with the username, the
  password and, when a seed is stored, the code. `steps` runs `--steps FILE` for
  any other login: a JSON array of steps `{action, selector, value, url, ms}`
  with `action` `goto`, `fill`, `click`, `press`, `wait_for` or `wait_ms`, and
  values that may read `{{username}}`, `{{password}}` and `{{otp}}` (each needs
  its secret). `none` does no sign-in: the view shows pages with the cookies it
  holds.
- A site that approves sign-ins on a phone (push MFA), checks devices or shows a
  CAPTCHA cannot be scripted. Sign in once in a browser the user controls, export
  its cookies for the site to a JSON file (name, value, domain, path, expires,
  httpOnly, secure, sameSite; at most 100 cookies and 48 KiB) and create the
  connection with `--login-mode none --cookies-file FILE`, or ask the site's
  administrator for a service account it exempts from those checks. The
  connection keeps its cookie jar current from each image; when the site ends the
  session (`bi_web_session_expired`), cookies alone need a new export.
- `--wait-for CSS` names an element that exists only when signed in, so a sign-in
  page times out instead of being drawn; `--wait-ms N` waits N milliseconds
  first; `--clip CSS` crops the image to one element. A site that keeps its
  session outside cookies signs in for every image: give its view a long
  `--refresh`.
- The password goes only to `--login-url` and the `goto` steps; adding another
  address to them needs the password in the same command, so a member who cannot
  read the password cannot point it elsewhere.
- Protect the account: a refused sign-in waits 5 minutes, then 15, 60 and 120, and
  the fifth in a row stops the connection until its credentials or sign-in
  settings change (`bi connection update`). Fix the cause; never retry in a loop.
- Errors, with the last good image kept on glass: `bi_web_login_failed` (fix the
  username, password, seed, login URL or steps), `bi_web_otp_required`,
  `bi_web_session_expired`, `bi_web_login_paused` (waiting out a refusal, stopped,
  or another capture is signing in), `bi_web_timeout` (raise `--wait-for` or
  `--wait-ms`), `bi_web_navigation_failed`, `bi_web_blocked` (a bot check or
  CAPTCHA: use a cookie jar) and `bi_upstream_unavailable`. `bi view show ID`
  reads `status.last_error`.
