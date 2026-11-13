---
name: nodemaven-sdk
description: Write code with the official NodeMaven SDKs - `nodemaven` for Python (PyPI), Rust (crates.io) and Go (github.com/nodemaven/nodemaven-go). Build validated proxy usernames and URLs, sticky sessions, per-worker session pools, check a proxy with one CONNECT, and call the account API client. Use when the user's project is in Python, Rust or Go and needs NodeMaven proxies or account data, or asks which SDK call does something.
license: MIT
---

# NodeMaven SDKs

Three SDKs with the same behaviour. Each builds the proxy username, **refuses
input the gateway would silently drop** (an unknown parameter name, a `-` inside
a value, whitespace, an empty value), and hands back a URL or a browser proxy
object for the HTTP client the project already uses. Building a proxy opens no
socket; only `check` and the account API client touch the network.

Credentials come from `NODEMAVEN_LOGIN` and `NODEMAVEN_PASSWORD` (proxy
username and password from Proxy Setup in the dashboard) when not passed in. The
account API client reads `NODEMAVEN_APIKEY`, a different secret.

Parameters and gateway rules are in the `nodemaven-proxy` skill. The names
accepted are `country`, `region`, `city`, `isp`, `type`, `sid`, `ttl`, `filter`,
`speed`, `ipv4`. `country`, `region`, `city`, `isp` and `type` are folded for
you (`"District of Columbia"` becomes `district_of_columbia`); the others are
sent as given, so pass them in lower case.

## Python

```bash
pip install nodemaven               # add [requests] if the code uses requests
```

```python
from nodemaven import Proxy

proxy = Proxy(country="us", filter="medium")       # credentials from the environment

proxy.url()          # http://user:pass@gate.nodemaven.com:8080, encoded
proxy.requests()     # {"http": ..., "https": ...}
proxy.httpx()        # {"http://": ..., "https://": ...}
proxy.playwright()   # {"server", "username", "password"}
proxy.username       # the username alone

held = proxy.session("order4417")                  # sticky; no "-" in the id
germany = proxy.replace(country="de")              # new object, new exit
pool = list(proxy.sessions(50))                    # 50 random ids, one per worker

print(proxy.check())                               # one CONNECT, status and exit IP
```

Errors: `ParamError` (bad name or value, raised before sending),
`CredentialsError`, `CheckError` (no answer at all), `ApiError` and its
subclasses `AuthError`, `NotFoundError`, `RateLimitError`. All inherit
`NodeMavenError`. `check()` returns a refusal as a value, not an exception.

## Rust

```bash
cargo add nodemaven
```

```rust
use nodemaven::Proxy;

let proxy = Proxy::builder()
    .param("country", "us")
    .param("filter", "medium")
    .build()?;                                     // credentials from the environment

let client = reqwest::Client::builder()
    .proxy(reqwest::Proxy::all(proxy.url())?)
    .build()?;

let held = proxy.session("order4417")?;
let germany = proxy.with_param("country", "de")?;
let plain = proxy.without_param("filter")?;
let pool = proxy.sessions(50)?;
println!("{}", proxy.check()?);                    // a refusal is Ok(Check), not Err
```

`proxy.browser()` gives server, username and password unencoded, for a browser
driver.

## Go

```bash
go get github.com/nodemaven/nodemaven-go
```

```go
proxy, err := nodemaven.New(
	nodemaven.WithParam("country", "us"),
	nodemaven.WithParam("sid", "order4417"),
) // credentials from NODEMAVEN_LOGIN and NODEMAVEN_PASSWORD
if err != nil {
	log.Fatal(err)
}
client := &http.Client{Transport: &http.Transport{Proxy: proxy.HTTPProxy()}}

germany, err := proxy.With("country", "de")
plain, err := proxy.Without("filter")
pool, err := proxy.Sessions(50)                    // []*nodemaven.Proxy, one exit each
check, err := proxy.Check(ctx)                     // err only when there was no answer
```

`proxy.Browser()` returns the three fields for Playwright, chromedp or Rod.
Errors are tested with `errors.Is` against `ErrParam`, `ErrCredentials`,
`ErrCheck`, `ErrAPI`, `ErrAuth`, `ErrNotFound`, `ErrRateLimit`. Printing a
`Proxy` shows the password as `***`.

## Account API client

The same in all three: `Client` (Python), `Client::builder().build()?` (Rust),
`nodemaven.NewClient()` (Go). Methods cover the account, location catalogue,
statistics, sub-users and whitelisted IPs - see the `nodemaven-account-api`
skill for what each endpoint returns and its quirks.

```python
from nodemaven import Client

client = Client()                                  # NODEMAVEN_APIKEY
problems = client.validate(proxy)                  # country/city checked against the catalogue
for city in client.iterate(client.cities(country__code="us")):
    ...
```

**`me()` and the sub-user calls return proxy passwords in clear text.** Never
print, log or paste their results; pick the fields you need.

## Picking a call

| the user wants | Python | Rust | Go |
|---|---|---|---|
| a proxy URL | `proxy.url()` | `proxy.url()` | `proxy.URL()` |
| the same IP for a flow | `proxy.session(id)` | `proxy.session(id)?` | `proxy.Session(id)` |
| N workers, N exits | `proxy.sessions(n)` | `proxy.sessions(n)?` | `proxy.Sessions(n)` |
| does it connect, where does it exit | `proxy.check()` | `proxy.check()?` | `proxy.Check(ctx)` |
| traffic left | `client.me()["data"]` | `client.me()?["data"]` | `client.Me(ctx)` |

Docs: [Python](https://github.com/nodemaven/nodemaven-python),
[Rust](https://docs.rs/nodemaven), [Go](https://github.com/nodemaven/nodemaven-go).
