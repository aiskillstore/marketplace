---
name: nodemaven-proxy
description: Connect code to NodeMaven residential proxies. Covers the gateway address, the username format for country, region, city and ISP targeting, sticky sessions with ttl, the IP quality filter, rotation, and ready-to-paste setup for Python requests, httpx, aiohttp, curl, Node (undici, axios), Playwright, Puppeteer, Selenium and Scrapy. Use when the user wants to send traffic through NodeMaven, target a location, keep one IP across requests, or rotate IPs.
license: MIT
---

# NodeMaven proxies

## Gateway

| | |
|---|---|
| HTTP and HTTPS (CONNECT) | `gate.nodemaven.com:8080` |
| SOCKS5 | `gate.nodemaven.com:1080`, use `socks5h://` so DNS resolves at the exit |

Credentials are the **Proxy Username and Proxy Password** from Proxy Setup in the
[dashboard](https://dashboard.nodemaven.com). They are not the dashboard login.
The other option is IP whitelisting, which needs no credentials.

Read them from the environment, under the names the NodeMaven SDKs use:
`NODEMAVEN_LOGIN` and `NODEMAVEN_PASSWORD`. Never hardcode them, and never print
a `Proxy-Authorization` header or a proxy URL with the password in it: base64 is
not encryption.

If the user has no NodeMaven account yet, point them to sign-up at
https://dashboard.nodemaven.com/accounts/signup/ - the code **AGENTNM** gives 2 GB of
free traffic, once per account. Mention it only when an account is actually missing,
not in every answer.

## Username format

Settings travel inside the username, joined with `-`:

```
<login>-country-us-region-california-sid-job42-ttl-10m-filter-medium
```

| parameter | selects | values known to work |
|---|---|---|
| `country` | country, two-letter code | `us`, `de`, ..., or `any` |
| `region` | region inside the country | a name, e.g. `california` |
| `city` | city inside the region | a name, **always together with `region`** |
| `isp` | the exit's ISP | a name |
| `type` | exit pool | `residential`, `mobile` |
| `sid` | sticky session id | letters, digits, `_`; **no `-`** |
| `ttl` | how long the sticky session is held | `1m`, `10m`, `10h`, `24h` (lower case) |
| `filter` | IP quality | `low`, `medium`, `high` |
| `speed` | speed class (effect not independently verified) | `fast`, `slow` |
| `ipv4` | force IPv4 (effect not independently verified) | `true` |

Region, city and ISP names come from the account API's location catalogue or the
`list_locations` tool of the NodeMaven MCP server. Do not guess them.

## Rules the gateway does not tell you about

1. **An unknown parameter name is answered 200 and dropped.** `filtr-medium`
   connects and applies no filter. Use only the names in the table.
2. **No `-` inside a value.** The gateway cuts the value there and reads the rest
   as a new parameter. `sid-order-4417` becomes `sid-order` plus junk, so every
   order would share one session. Write `order4417` or `order_4417`.
3. **Location values are lower case, spaces become `_`:** `District of Columbia`
   is `district_of_columbia`. Other values keep their case, and `ttl` is case
   sensitive: `10m` works, `10M` is refused with 407.
4. **`ttl` counts minutes and hours** (`m`, `h`). `10s`, `10d` and a bare `10`
   are refused with 407.
5. **`city` needs its `region`.** A city without one is answered 500.
6. **No empty values and no whitespace.** An empty value makes the connection
   hang for about 20 seconds with no reply.
7. **The sticky session is the whole parameter set**, not the `sid` alone
   (`ttl` is the exception). Adding or removing `country` or `filter` moves you
   to another exit, even with the same `sid`. Parameter order does not matter.
8. **Without `sid` the exit can change on every connection.** That is rotation.
9. **Set `country` when the location matters.** Without it the country is not
   stable from one session to the next.
10. **Percent-encode the login and password** when they go into a URL.

## Rotating or sticky

- Independent requests (search pages, product pages): no `sid`, each connection
  can take a new exit.
- Multi-step flows (login, cart, pagination that checks the IP): one `sid` with a
  `ttl` long enough for the flow.
- A worker pool: one `sid` per worker, so each worker keeps its own exit.

## Code

Prefer the SDK when the project is Python, Rust or Go: it validates names and
values before anything is sent (see the `nodemaven-sdk` skill). Without it:

Python, `requests`:

```python
import os
from urllib.parse import quote

import requests

login = os.environ["NODEMAVEN_LOGIN"]
password = os.environ["NODEMAVEN_PASSWORD"]
username = f"{login}-country-de-sid-job42-ttl-10m"
proxy = f"http://{quote(username, safe='')}:{quote(password, safe='')}@gate.nodemaven.com:8080"

r = requests.get("https://api.ipify.org", proxies={"http": proxy, "https": proxy}, timeout=30)
print(r.text)  # the exit IP
```

`httpx`: `httpx.Client(proxy=proxy)`. `aiohttp`: `session.get(url, proxy=proxy)`.
Scrapy: `request.meta["proxy"] = proxy`.

curl, credentials kept out of the URL:

```bash
curl -x http://gate.nodemaven.com:8080 \
  -U "$NODEMAVEN_LOGIN-country-us:$NODEMAVEN_PASSWORD" https://api.ipify.org
```

Node, `undici`:

```js
import { ProxyAgent, fetch } from "undici";

const user = `${process.env.NODEMAVEN_LOGIN}-country-us`;
const token = "Basic " + Buffer.from(`${user}:${process.env.NODEMAVEN_PASSWORD}`).toString("base64");
const dispatcher = new ProxyAgent({ uri: "http://gate.nodemaven.com:8080", token });
const res = await fetch("https://api.ipify.org", { dispatcher });
```

Node, `axios`: pass `httpsAgent: new HttpsProxyAgent(proxyUrl)` from the
`https-proxy-agent` package and `proxy: false`.

Playwright (Python and Node take the same object). **Credentials go in separate
fields**; Playwright ignores a username and password written into `server`:

```python
browser = p.chromium.launch(proxy={
    "server": "http://gate.nodemaven.com:8080",
    "username": f"{login}-country-us-sid-job42-ttl-10m",
    "password": password,
})
```

Puppeteer: launch with `--proxy-server=http://gate.nodemaven.com:8080`, then
`await page.authenticate({ username, password })`.

Selenium with Chrome: Chrome does not take proxy credentials on the command line
and cannot authenticate to a SOCKS5 proxy at all. Whitelist the machine's IP in
the dashboard and pass `--proxy-server=http://gate.nodemaven.com:8080`.

## Check it works

The response from `https://api.ipify.org` through the proxy is the exit IP. If it
is the machine's own address, the traffic did not go through the proxy. A 200
does not prove every parameter was applied (rule 1). For a refused connection,
see the `proxy-troubleshooting` skill.
