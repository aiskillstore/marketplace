---
name: routeros-hotspot
description: "RouterOS hotspot captive portal for wired/wireless access control. Use when: configuring hotspot on RouterOS, setting up captive portal, writing hotspot profiles or instances, configuring walled garden, setting DHCP option 114 (RFC 8910 captive portal URI), integrating RADIUS with hotspot, or when the user mentions /ip/hotspot, walled-garden, hotspot profile, or captive portal on MikroTik."
---

# RouterOS Hotspot

## How Hotspot Chains Work

Hotspot traffic intercept runs **before** the regular firewall input/forward chains. This is the single most important fact to internalize:

- `/ip/hotspot` binds to a bridge or interface — all traffic on that interface enters the hotspot chain first
- Firewall rules blocking TCP 80/443 from the hotspot interface do **NOT** block the captive portal login page — hotspot handles it before the firewall sees it
- RouterOS automatically injects dynamic firewall rules (`hs-unauth`, `hs-auth` chains) — do not manually create, remove, or interfere with these hotspot-managed rules

**Common mistake:** Adding a DROP rule for port 443 from bridge-hotspot to "fix a security gap" — this breaks the HTTPS login page silently.

## Hotspot Profile

```routeros
/ip/hotspot/profile/add \
  name=my-profile \
  hotspot-address=10.20.0.1 \
  login-by=https,mac,http-pap \
  mac-auth-mode=mac-as-username-and-password \
  dns-name=login.example.com \
  ssl-certificate=login.example.com.crt_0 \
  nas-port-type=ethernet \
  use-radius=yes \
  radius-accounting=yes \
  html-directory-override=hotspot-files
```

Key properties:
- `ssl-certificate=` — reference the name after import (RouterOS appends `_0` to imported certificate names)
- `nas-port-type=` — use `ethernet` for wired hotspots and `wireless-ieee-802-11-g` for wireless hotspots
- `html-directory-override=` — must match the exact folder name on the router's filesystem
- `login-by=https` — serves the login page over HTTPS; requires `www-ssl` service enabled with the same certificate
- `use-radius=yes` — when set, **local `/ip/hotspot/user` entries are bypassed**; adding them has no effect

## Hotspot Instance

```routeros
/ip/hotspot/add \
  name=hotspot1 \
  interface=bridge-hotspot \
  profile=my-profile \
  address-pool=pool-hotspot \
  addresses-per-mac=2 \
  idle-timeout=5m \
  keepalive-timeout=none \
  disabled=no
```

**Note:** `keepalive-timeout=none` disables the keepalive. `keepalive-timeout=0` is NOT valid — it is ignored.

**Note:** RouterOS hotspot relies on NAT and is **IPv4-only**. IPv6 clients are not supported by the hotspot subsystem.

## DHCP Option 114 — Captive Portal API (RFC 8910)

Option 114 (standardized 2020, RFC 8910) signals the captive portal URI to clients. It is underrepresented in LLM training data.

```routeros
# force=yes is REQUIRED — without it, clients whose DHCP Parameter Request
# List does not include code 114 (e.g. iOS, Android) silently skip the option
/ip/dhcp-server/option/add \
  name=captive-portal \
  code=114 \
  force=yes \
  value="'https://login.example.com/api'"

/ip/dhcp-server/option/sets/add \
  name=captive-portal-set \
  options=captive-portal

/ip/dhcp-server/set my-dhcp-server dhcp-option-set=captive-portal-set
```

**Option value syntax:** outer double quotes, inner single quotes — `"'https://...'"`. Missing inner quotes cause the option to be sent as a binary blob, not a string URI.

**api.json timing:** RouterOS creates `hotspot/api.json` only after the **first client CAPPORT probe** — not at hotspot enable time. Move it to the html-directory-override folder after first client connects:

```routeros
# Handles both flash/ and non-flash storage layouts
:local srcPath "hotspot/api.json"
:local dstPath "hotspot-files/api.json"
:if ([:len [/file find name="flash"]] > 0) do={
  :set srcPath "flash/hotspot/api.json"
  :set dstPath "flash/hotspot-files/api.json"
}
:if ([:len [/file find name=$srcPath]] > 0) do={
  /file set [find name=$srcPath] name=$dstPath
} else={
  :log warning "api.json not yet created — run after first client CAPPORT probe"
}
```

## Walled Garden

Use a consistent `comment=` tag for idempotent add/remove. Without it, repeated script runs accumulate duplicate entries.

```routeros
# Remove only our entries, not manually-added ones
/ip/hotspot/walled-garden/ip/remove [find comment="my-wg"]

/ip/hotspot/walled-garden/ip/add dst-host=example.com   action=accept comment="my-wg"
/ip/hotspot/walled-garden/ip/add dst-host=*.example.com action=accept comment="my-wg"
```

**IP vs HTTP walled garden:**
- `/ip/hotspot/walled-garden/ip` — layer 3 match by destination host, applied BEFORE authentication. Use for HTTPS destinations.
- `/ip/hotspot/walled-garden` — layer 7 URL pattern match, requires HTTP. Does NOT work for HTTPS.

## SSL Certificate Note

The hotspot profile references `ssl-certificate=name.crt_0` (RouterOS appends `_0` on import). Enable `www-ssl` with the same certificate:

```routeros
/ip/service/set www-ssl disabled=no certificate=login.example.com.crt_0 tls-version=only-1.2
```

Quick import pattern:
```routeros
/certificate import file-name=login.example.com.crt passphrase=""
/certificate import file-name=login.example.com.key passphrase=""
# After import, the certificate appears as login.example.com.crt_0
```

## External Captive Portal — HTML Template Variables

RouterOS substitutes `$(variable)` server-side in any file under `html-directory-override` before serving it. These are **not** JavaScript variables — they are filled before the browser receives the page.

**Servlet pages RouterOS serves** (drop your own to override):
`login.html`, `flogin.html` (failed-login), `alogin.html` (post-success), `status.html`, `logout.html`, `error.html`, `redirect.html`, `rlogin.html`, `rstatus.html`, `fstatus.html`, `flogout.html`, `radvert.html`, `md5.js`, `errors.txt`. Most external-CP setups only need `login.html` + `alogin.html` + `status.html`.

**Most-used variables for external CP:**

| Variable | Description |
|---|---|
| `$(link-login-only)` | Login POST endpoint **without** `?dst=` — preferred for external auth (avoids double-encoding) |
| `$(link-login)` | Login URL **with** `?dst=` redirect appended |
| `$(link-orig)` / `$(link-orig-esc)` | Original URL the client requested. **Use `-esc` when interpolating into another URL** |
| `$(server-name)` | Hotspot instance name |
| `$(mac)` / `$(mac-esc)` | Client MAC (raw / URL-escaped) |
| `$(ip)` | Client IP |
| `$(host-ip)` | IP from hotspot host table (differs from `$(ip)` under one-to-one NAT) |
| `$(interface-name)`, `$(vlan-id)` | Useful for tenant-aware external auth |
| `$(error)` / `$(error-orig)` | Localized vs raw error from previous auth attempt |
| `$(logged-in)` | `yes` if client is already authenticated |
| `$(trial)` | `yes` if trial access still available for this MAC |
| `$(username)` / `$(username-esc)` | Authenticated username (status page) |
| `$(bytes-in[-nice])`, `$(bytes-out[-nice])`, `$(uptime[-secs])`, `$(session-time-left[-secs])` | Status-page counters |
| `$(radius<id>[u])`, `$(radius<id>-<vnd-id>[u])` | Pass-through of RADIUS Access-Accept attributes — text or unsigned int. Empty / `"0"` when local-DB auth (`use-radius=no`) |
| `$(http-header-<Name>)` | **Read** an incoming request header — e.g. `$(http-header-User-Agent)`, `$(http-header-Accept-Language)` |
| `$(if http-status == XYZ)MSG$(endif)` | **Set** the HTTP response status code |
| `$(if http-header == NAME)VALUE$(endif)` | **Set** a custom response header (different syntax from the read pattern above) |

**Always pick the `-esc` variant** (`$(link-orig-esc)`, `$(mac-esc)`, `$(username-esc)`) when embedding a value into a URL or query string. The non-escaped variants will break parsing or open injection paths if the value contains `&`, `=`, `?`, `#`.

**POST form fields** RouterOS accepts at `$(link-login-only)`:
`username`, `password`, `domain`, `dst`, `popup`, `session-id`, `var`, `erase-cookie`, `target` (multi-language subdir).

**Conditional syntax** (server-side, not JavaScript):

```
$(if logged-in == "yes")
  <a href="$(link-logout)">Logout</a>
$(else)
  <form action="$(link-login-only)" method="post">...</form>
$(endif)
```

Operators: presence (`$(if VAR)`), `==`, `!=`. Also `$(elif ...)`. No nested arithmetic / string ops.

Generic `login.html` pattern for external captive portal:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="pragma" content="no-cache">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- External auth provider loads redirect logic -->
  <script src='https://auth.example.com/snippets/router-os/redirect'></script>
</head>
<body>
  <div id="entryPoint">Redirecting...</div>
  <script>
    window.addEventListener('load', function () {
      ExternalAuth_redirect(
        '$(server-name)', '$(mac-esc)', '$(link-login-only)',
        '$(link-orig-esc)', '$(error-orig)', '$(logged-in)', '$(ip)'
      );
    });
  </script>
</body>
</html>
```

The external provider authenticates the user and redirects the browser back to `$(link-login-only)` with `username` + `password` + `dst` POST fields. RouterOS validates (local DB or RADIUS), issues the auth cookie, and redirects to `dst`.

**Walled-garden must include the external auth host (and any CDN/asset hosts)** — otherwise the unauthenticated browser cannot reach the redirect script in step 2.

Full variable reference, all servlet pages, RADIUS pass-through patterns, multi-language `target=` mechanics, and HTTP response control: see [references/template-variables.md](./references/template-variables.md).

## Common LLM Mistakes

| Mistake | Correct behavior |
|---------|-----------------|
| DROP TCP 443 from hotspot interface | Hotspot chain runs before firewall — breaks the HTTPS login page |
| `keepalive-timeout=0` to disable keepalive | Use `keepalive-timeout=none` |
| Option 114 `value=` without inner single quotes | Must be `"'https://...'"` — outer double, inner single |
| Option 114 without `force=yes` | iOS/Android silently skip option if not in their DHCP PRL |
| Adding `/ip/hotspot/user` when `use-radius=yes` | Local users are bypassed when RADIUS is active |
| Wildcard HTTPS domains in `/ip/hotspot/walled-garden` | Use `/ip/hotspot/walled-garden/ip` for HTTPS (layer 3 match) |
| Hotspot on dual-stack network with IPv6 | Hotspot is IPv4-only — IPv6 not supported |
| `$(link-login)` treated as JavaScript variable | It is RouterOS server-side substitution, not JS |
| Embedding `$(link-orig)` / `$(mac)` / `$(username)` into another URL | Use the `-esc` variant — non-esc breaks parsing on `&`, `=`, `?` and may enable injection |
| Hotspot with PCC / multiple routing tables | Hotspot uses only the default routing table — split-WAN setups need explicit `/ip route rule` for hotspot traffic |

## Additional Resources

**Related skills:**
- `routeros-fundamentals` — RouterOS CLI syntax, REST API, scripting basics
- `routeros-certificates` (in backlog) — for the full certificate chain handling pattern

**MCP tools:**
- `rosetta` MCP server — `/tool/ping`, `/ip/hotspot` command tree inspection (`routeros_search`, `routeros_get_page`)

**MikroTik docs:**
- [HotSpot](https://help.mikrotik.com/docs/display/ROS/HotSpot) — official reference
- [DHCP Server](https://help.mikrotik.com/docs/display/ROS/DHCP) — option 114 configuration

## RADIUS Integration

See [references/radius-client.md](./references/radius-client.md) for RADIUS client configuration patterns.
