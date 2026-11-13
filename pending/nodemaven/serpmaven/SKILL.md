---
name: serpmaven
description: Scrape Google search results (SERP) to JSON with SERP Maven (serpmaven) - a real Chrome browser on a residential proxy with sticky sessions. Run it as a CLI, a Python library, a local HTTP search API (`serve`), an MCP server or a Docker image; set the proxy login, workers, pages and cost tracking. Use when the user wants Google results, rank tracking, a self-hosted SERP API, or live Google search for an AI agent.
license: MIT
---

# SERP Maven (serpmaven)

Open source, MIT: [github.com/nodemaven/serpmaven](https://github.com/nodemaven/serpmaven).
It warms a sticky proxy session with ordinary browsing, opens Google's results page
for each query in a real Chrome browser, checks whether Google served results or
refused, and writes one JSON record per results page. Captchas and blocks come back
labelled, never as empty results. Formerly `gserp` and `google-browser-scraper`; both
names still install it.

## Install and first run

```bash
pip install serpmaven          # Python 3.10+, inside a venv on macOS and Linux
serpmaven login                # saves the proxy login once
serpmaven search "best running shoes" --country us -o results.jsonl
```

Or with uv, no Python needed: `uv tool install serpmaven`, and `uvx serpmaven ...` to try
it without installing. The first search offers to download its browser (about 150 MB,
once per machine); `serpmaven install` does it ahead of time and `serpmaven doctor`
checks the setup. On a Linux server without a screen: `sudo apt install xvfb`,
`serpmaven install --with-deps`, `export SERPMAVEN_BROWSER_ARGS=--enable-unsafe-swiftshader`,
then start every command with `xvfb-run -a`.

## Proxy

It needs a residential proxy **with sticky sessions**. `serpmaven login` asks for the
NodeMaven Proxy Username and Proxy Password from the dashboard; for any other provider,
save its URL with `{session}` where the session id goes in the username:

```bash
serpmaven login --proxy "http://USER-session-{session}:PASS@gate.example.com:7000"
```

`--proxy`, `--nodemaven`, `SERPMAVEN_PROXY` and `NODEMAVEN_LOGIN` / `NODEMAVEN_PASSWORD`
win over the saved login; `serpmaven logout` deletes it. `--country` applies to NodeMaven
only. No NodeMaven account yet: 2 GB free with the code GOOGLENM.

To cap spend, `--nodemaven-demo --traffic-limit-mb 300` creates a sub-user with a traffic
limit from the dashboard API key in **`NODEMAVEN_API_KEY`** (this tool's name; the SDK's is
`NODEMAVEN_APIKEY`) and deletes it when the run ends. A fresh warm-up alone is about 60 MB,
so keep the cap well above that.

`--no-proxy` uses the machine's own connection: fine for a try, captchas come sooner.
SOCKS5 needs an IP-whitelisted endpoint, because Chrome cannot send a SOCKS5 username and
password.

## Expectations to set

- The first query takes minutes: a new proxy IP is warmed up first. Later queries take
  seconds, and new proxy IPs start from the first one's cookies.
- The terminal shows each step; the run ends with pages served, traffic used and proxy
  IPs used. `--price-per-gb` adds the cost per 1000 pages.
- A run where Google refuses proxy IP after proxy IP stops instead of spending more.

## Ways to run it

A file of queries: `serpmaven search -f queries.txt -o results.jsonl`;
`--workers 2` runs two browsers on two proxy IPs from one list.

HTTP API, same record format:

```bash
serpmaven serve --country us --prewarm
curl "http://127.0.0.1:8000/search.json?q=best+running+shoes"
```

`pages=N`, `hl` and `gl` per request. `/health` answers 503 `warming` until the prewarm is
done. Set `SERPMAVEN_API_KEY` to require a key; without one it listens on localhost only.

MCP server for an AI client (one tool, `google_search(query, pages, hl, gl)`), using the
saved login:

```json
{
  "mcpServers": {
    "google-search": {
      "command": "uvx",
      "args": ["serpmaven", "mcp", "--country", "us", "--prewarm"]
    }
  }
}
```

Python:

```python
from serpmaven import NodeMavenSource, Scraper

scraper = Scraper(NodeMavenSource(country="us"))
for page in scraper.run(["best running shoes"]):
    for result in page.get("organic_results", []):
        print(result["position"], result["title"], result["link"])
```

Docker: `ghcr.io/nodemaven/serpmaven`, e.g.
`docker run --rm -p 8000:8000 -e SERPMAVEN_API_KEY=... -e SERPMAVEN_PROXY='http://USER-session-{session}:PASS@host:port' ghcr.io/nodemaven/serpmaven serve --host 0.0.0.0`.

## Output

One JSON object per results page: `search_metadata` (`status`, `page_verdict`, `timings`),
`search_parameters`, `organic_results` (`position`, `title`, `link`, `snippet`), `ads`,
`related_questions`, `related_searches`, `ai_overview`, `local_results`, `pagination`, and an
`exit` block with the proxy session and bytes. Knowledge panels, shopping and images are not
parsed. A failed query is a record with an `error`. `--format csv` writes organic results
as a table.

## Options worth knowing

| option | default | |
|---|---|---|
| `--workers N` | 1 | N browsers on N proxy IPs from one query list |
| `--pages N` | 1 | result pages per query |
| `--country CC` | | with NodeMaven |
| `--hl`, `--gl` | `en`, unset | language and country of the results |
| `--max-per-exit N` | 300 | queries before a served proxy IP is retired |
| `--gap LOW,HIGH` | 2,5 | seconds between queries on one proxy IP |
| `--no-resolve-links` | | keep Google's `/goto` redirect links |
| `--save-html DIR` | | keep page HTML, for reporting a parsing problem |

`serpmaven search --help` lists the rest. Use within Google's terms and the law where it
runs.
