---
name: proxy-troubleshooting
description: Diagnose residential proxy failures, with NodeMaven's gateway as the reference - 407 with correct credentials, 406, 410, 500, a connection that hangs, ERR_TUNNEL_CONNECTION_FAILED in a browser, Playwright or Puppeteer ignoring proxy credentials, a sticky session that changes IP, geo-targeting that is silently ignored, passwords with special characters, and unexpected traffic from headless Chrome. Use when a proxy connection fails, returns the wrong location, or costs more traffic than expected.
license: MIT
---

# Proxy troubleshooting

Start by getting the gateway's own status code. A browser hides it behind
`ERR_TUNNEL_CONNECTION_FAILED` or `ERR_PROXY_CONNECTION_FAILED`, and most HTTP
clients turn it into a generic exception. One CONNECT shows it:

```bash
curl -sv -o /dev/null -x http://gate.nodemaven.com:8080 \
  -U "$NODEMAVEN_LOGIN-country-us:$NODEMAVEN_PASSWORD" https://api.ipify.org 2>&1 \
  | grep -E "^< HTTP|CONNECT phase"
```

Or `proxy.check()` in the NodeMaven SDKs, which also prints what the code means.
Do not paste the full `-v` output anywhere: it contains the
`Proxy-Authorization` header, which is the password in base64.

## What the NodeMaven gateway's status codes mean

| answer | most likely cause |
|---|---|
| **407** | **usually a bad value, not bad credentials.** A value the gateway will not take on `country`, `filter`, `ttl`, `type` or `speed` answers 407, exactly like a wrong password. Check values first: `ttl` must be lower case with `m` or `h` (`10m`, not `10M`, `10s` or `10`); `country` a two-letter code or `any` |
| **406** | `region`, `city` or `isp` names something unknown or unavailable to the account. The code does not say which of the three |
| **410** | `isp` names a network the gateway knows but will not give this account |
| **500** | measured cause: `city` sent without its `region`. Add the region the location catalogue files the city under |
| **no reply, ~20 s, then timeout** | an empty value somewhere in the username, e.g. `country-` or `sid--ttl` from an unset variable |
| **200 but the setting is not applied** | a misspelt parameter name (`contry`, `filtr`) is answered 200 and dropped |

Look up valid region, city and ISP names in the account API location catalogue
(`locations/regions/`, `cities/`, `isps/` with `country__code`) or the MCP
server's `list_locations`, instead of guessing.

## Symptom checklist

**407 in Playwright with credentials that work in curl.** Playwright ignores a
username and password written into `proxy.server`. Pass them separately:
`{"server": "http://gate.nodemaven.com:8080", "username": ..., "password": ...}`.

**Chrome or Selenium cannot authenticate.** Chrome takes no credentials in
`--proxy-server` and cannot authenticate to SOCKS5 at all. Use the driver's own
proxy auth (Playwright `proxy`, Puppeteer `page.authenticate`), or whitelist the
machine's IP in the dashboard and drop the credentials.

**Works in one tool, 407 or a parse error in another, password has `#`, `/`,
`?`, `%`, `@` or `:`.** The credentials were put into a URL unencoded. Encode
both parts (`urllib.parse.quote(value, safe="")`, `encodeURIComponent`), or pass
username and password as separate fields.

**The exit IP is the machine's own address.** The proxy was never applied:
wrong `proxies` key (`https` missing), a client that ignores environment
variables (`trust_env=False`) or reads them when you did not expect it, or a
browser launched without the proxy argument. Check with `https://api.ipify.org`.

**The sticky session changes IP.** In order of likelihood:
1. Another parameter changed. The session is keyed on the whole parameter set,
   so adding `filter` or changing `country` is a new session even with the same
   `sid`.
2. The `sid` contains `-`. The gateway cuts the value there, so `order-1` and
   `order-2` are the same session `order`, and the tail is read as a parameter.
3. `ttl` ran out, or the exit went offline. Residential exits are people's
   connections; plan for an exit to disappear and move to a new `sid`.

**Geo-targeting is ignored.** A misspelt parameter name (200 and dropped), a
location value with spaces instead of `_`, or no `country` at all, in which case
the country is not stable.

**The exit IP header is missing.** Some gateway back ends send the exit address
on the CONNECT reply and some do not. Read the IP through the tunnel from an echo
service when you need it every time.

**Retrying a refused exit.** If a target refused an exit (captcha, block), move
to a new `sid` rather than retrying the same one. On the published
proxy-benchmark runs, an attempt succeeded 75% of the time with no failures
before it in its cell, and 1.6% from the sixth failure on. Stop after a few
consecutive failures instead of looping.

## Unexpected traffic from Chrome

**A fresh Chrome profile downloads an on-device model from
`optimizationguide-pa.googleapis.com` while idle**: 24 to 45 MB per fresh
profile measured through a proxy with several automation libraries, billed as
proxy traffic. `--disable-features=OptimizationHints` stops it. It is
probabilistic, so one quiet run proves nothing. One report linked this flag to a
startup crash on an early unbranded Chromium 151 build; test it on your build.

**Chrome honours only the last `--disable-features` switch** and discards
earlier ones whole. A library that emits its own and then appends yours (or the
reverse) silently loses one list, including Playwright's defaults, which already
contain `OptimizationHints`. Merge everything into one switch:
`--disable-features=OptimizationHints,Translate,YourFeature`. Check the real
command line at `chrome://version`.
