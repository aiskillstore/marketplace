# Hotspot HTML Template Variables — Full Reference

RouterOS substitutes `$(name)` placeholders **server-side** before serving any file from `html-directory-override`. Substitution happens in HTML, JS embedded in HTML, and `errors.txt`. The browser never sees the `$(...)` tokens.

Source: <https://help.mikrotik.com/docs/spaces/ROS/pages/87162881/Hotspot+customisation>

---

## Servlet Pages

RouterOS serves these filenames from the html-directory. All accept template variables.

| File | When served |
|------|-------------|
| `login.html` | Authentication form (unauthenticated client requests any URL) |
| `flogin.html` | Login page after a failed attempt — falls back to `login.html` if missing |
| `alogin.html` | Shown immediately after a successful login (popup/redirect handler) |
| `status.html` | Authenticated status page (session stats, logout button) |
| `rstatus.html` | Status redirect when client requests `/status` while logged in |
| `fstatus.html` | Status request from unauthenticated client |
| `logout.html` | Post-logout confirmation |
| `flogout.html` | Logout request from unauthenticated client |
| `rlogin.html` | Login redirect when client hits a restricted URL |
| `redirect.html` | Generic URL redirector |
| `error.html` | Fatal error page |
| `radvert.html` | Advertisement redirector (when `advertise=yes` profile flag set) |
| `md5.js` | Client-side MD5 helper for CHAP login |
| `errors.txt` | Localized error message strings |

External captive portal typically only customizes `login.html` + `alogin.html` + `status.html`. The rest can stay default.

---

## POST Form Fields

Fields RouterOS expects when the browser submits to `$(link-login-only)`:

| Field | Purpose |
|-------|---------|
| `username` | Username (or MAC for mac-auth) |
| `password` | Plaintext (HTTP-PAP) or `response` after CHAP hashing |
| `domain` | Optional domain suffix — combined per `radius-default-domain` / `split-user-domain` |
| `dst` | Original URL to redirect to after login |
| `popup` | `true` to open status page as popup |
| `session-id` | CHAP session id (echoed from `$(chap-id)`) |
| `var` | Free-form custom variable, accessible as `$(var)` in templates |
| `erase-cookie` | `on`/`true` on logout — drops the auth cookie so auto-login won't trigger |
| `target` | Subdirectory selector for multi-language templates (`target=de` → `/de/login.html`) |

---

## Common Server Variables

| Variable | Description |
|---|---|
| `$(hostname)` | DNS name (or IP if no DNS) of the hotspot servlet |
| `$(identity)` | RouterOS `/system/identity` value |
| `$(server-name)` | Hotspot instance name |
| `$(server-address)` | Hotspot servlet IP:port |
| `$(login-by)` | Auth method actually used (`cookie`, `http-chap`, `http-pap`, `https`, `mac`, `mac-cookie`, `trial`) |
| `$(plain-passwd)` | `yes` if HTTP-PAP enabled in profile, else `no` |
| `$(ssl-login)` | `yes` if current connection is HTTPS, else `no` |

## Link Variables

| Variable | Description |
|---|---|
| `$(link-login)` | Full login URL **including** `?dst=<orig>` redirect |
| `$(link-login-only)` | Login URL **without** `dst` — preferred for external auth (avoids double-encoding) |
| `$(link-logout)` | Logout URL |
| `$(link-status)` | Status page URL |
| `$(link-orig)` | Original URL the client requested |
| `$(link-orig-esc)` | URL-escaped variant — **use this** when embedding `link-orig` into another URL/query string |
| `$(link-redirect)` | Custom redirect target |

**Security:** Always pick the `-esc` variant when interpolating into another URL, query string, or attribute value. The non-escaped variants can break URL parsing or open injection paths if the original URL contains `&`, `=`, `?`, or `#`.

## Client Variables

| Variable | Description |
|---|---|
| `$(username)` / `$(username-esc)` | Authenticated username (raw / URL-escaped) |
| `$(domain)` | Domain part if `split-user-domain=yes` |
| `$(ip)` | Client IP address |
| `$(mac)` / `$(mac-esc)` | Client MAC (raw `XX:XX:XX:XX:XX:XX` / URL-escaped) |
| `$(host-ip)` | IP from `/ip/hotspot/host` table — differs from `$(ip)` when one-to-one NAT applies |
| `$(interface-name)` | Physical hotspot interface (or bridge) the client is on |
| `$(vlan-id)` | VLAN ID if client is on a tagged interface |
| `$(logged-in)` | `yes` / `no` |
| `$(trial)` | `yes` if trial access still available for this MAC |
| `$(user-agent)` | Browser User-Agent string (shortcut for `$(http-header-User-Agent)`) |
| `$(http-header-<Name>)` | Read any incoming HTTP request header — e.g. `$(http-header-Accept-Language)`, `$(http-header-Referer)`. Header name is case-sensitive as sent by the client. |

## Session / Limit Variables

Available on `status.html` (and any post-login page).

| Variable | Description |
|---|---|
| `$(session-timeout)` | Remaining session time, formatted (`5h30m`) |
| `$(session-timeout-secs)` | Same, in seconds |
| `$(session-time-left)` / `$(session-time-left-secs)` | Time left until forced logout |
| `$(idle-timeout)` / `$(idle-timeout-secs)` | Idle disconnect timer |
| `$(refresh-timeout)` / `$(refresh-timeout-secs)` | Status page auto-refresh interval |
| `$(uptime)` / `$(uptime-secs)` | Current session duration |
| `$(bytes-in)` / `$(bytes-in-nice)` | Bytes received from user (raw / human-readable) |
| `$(bytes-out)` / `$(bytes-out-nice)` | Bytes sent to user |
| `$(packets-in)` / `$(packets-out)` | Packet counters |
| `$(limit-bytes-in)` / `$(limit-bytes-out)` | Quota limits from profile/RADIUS |
| `$(remain-bytes-in)` / `$(remain-bytes-out)` | Quota remaining |

## Auth / Error Variables

| Variable | Description |
|---|---|
| `$(error)` | Localized error message (looked up in `errors.txt`) |
| `$(error-orig)` | Untranslated raw error string — stable for programmatic matching |
| `$(chap-id)` | CHAP challenge ID (login.html only) |
| `$(chap-challenge)` | CHAP challenge value (login.html only) |
| `$(popup)` | `true` / `false` — was login popup-mode |
| `$(advert-pending)` | `yes` if a forced advertisement popup is queued |

## RADIUS Pass-Through

Direct access to attributes from the RADIUS Access-Accept reply:

| Variable | Description |
|---|---|
| `$(radius<id>)` | Attribute `<id>` as text string (e.g. `$(radius27)` for Session-Timeout) |
| `$(radius<id>u)` | Attribute as unsigned integer |
| `$(radius<id>-<vnd-id>)` | Vendor-specific attribute (text) |
| `$(radius<id>-<vnd-id>u)` | Vendor-specific attribute (unsigned) |

Empty string (text variants) or `"0"` (unsigned variants) when local-DB auth (no `use-radius=yes`).

## HTTP Request / Response Control

**Reading request headers:** use `$(http-header-<HeaderName>)` — direct substitution, no conditional needed. Header name is case-sensitive as sent by the client. Examples:

```
Detected language: $(http-header-Accept-Language)
$(if http-header-User-Agent == "MyKioskApp/1.0")
  ...kiosk-specific markup...
$(endif)
```

**Setting response status / headers:** use the `$(if ...)` form — note that `http-status` and `http-header` (without dash + name) are **special tokens** the substitution engine recognizes:

```
$(if http-status == 302)Found$(endif)
$(if http-header == Location)https://example.com/welcome$(endif)
```

First produces `HTTP/1.0 302 Found`; second adds `Location: https://example.com/welcome`. Useful for `redirect.html` / `alogin.html` programmatic redirects without HTML/JS.

The two patterns coexist: `$(http-header-User-Agent)` reads, `$(if http-header == Location)...$(endif)` writes.

---

## Conditional Syntax

```
$(if VAR)
  shown when VAR is non-empty
$(elif VAR == "value")
  shown when VAR equals "value"
$(elif VAR != "other")
  shown when VAR not equal "other"
$(else)
  fallback
$(endif)
```

Comparisons supported: presence (non-empty), `==`, `!=`. No arithmetic, no string concat, no nested complex expressions documented. Strings may be quoted or bare.

Common patterns:

```html
$(if error)
  <div class="error">$(error)</div>
$(endif)

$(if logged-in == "yes")
  <a href="$(link-logout)">Logout</a>
$(else)
  <form action="$(link-login-only)" method="post">...</form>
$(endif)

$(if trial == "yes")
  <button name="trial" value="yes">Free 30 minutes</button>
$(endif)
```

---

## Multi-Language Templates

1. Create subdirectories per language: `hotspot-files/de/`, `hotspot-files/fr/`, etc.
2. Drop translated `login.html`, `errors.txt`, etc. into each.
3. Pass `target=de` as a POST/GET parameter — RouterOS prefixes the path with that subdirectory for subsequent requests.

Selector pattern in `login.html`:

```html
<form action="$(link-login-only)" method="post">
  <input type="hidden" name="target" value="de">
  ...
</form>
```

---

## Escaping Rules

| Suffix | What it does |
|---|---|
| `-esc` | URL-encodes the value (`&` → `%26`, `=` → `%3D`, space → `%20`, etc.) |
| `-nice` | "User-friendly" formatting of a numeric value. Upstream docs do not specify the exact format (separators vs. unit-conversion); treat as opaque display string and don't parse programmatically — use the raw counter (e.g. `$(bytes-in)`) when you need an integer |

There is **no HTML-escape variant**. If a variable can contain user-controlled data (e.g. `$(username)`, `$(error-orig)` reflecting form input), do not interpolate it directly into HTML attributes or `<script>` blocks without your own escaping. Safe spots: text nodes inside elements that don't allow HTML.

---

## External Captive Portal Flow

```
1. Unauth client requests any URL
   → RouterOS serves login.html with $(link-login-only), $(mac), $(link-orig-esc)
2. login.html JS posts client info to external auth provider (auth.example.com)
3. External provider authenticates user, stores session
4. External provider returns a page or redirect target that submits an HTTPS POST to:
     $(link-login-only)
     with `username`, `password`, and `dst=$(link-orig-esc)` form fields
5. RouterOS validates credentials (local DB or RADIUS), issues cookie, and redirects to `dst`
6. Subsequent requests pass via cookie auth (login-by=cookie)
```

Walled-garden must allow `auth.example.com` (and any CDN/asset hosts) **before** the client authenticates — otherwise step 2 cannot reach the external provider.

---

## See Also

- Captive portal overview: <https://help.mikrotik.com/docs/spaces/ROS/pages/56459266/HotSpot+-+Captive+portal>
- Customisation reference: <https://help.mikrotik.com/docs/spaces/ROS/pages/87162881/Hotspot+customisation>
