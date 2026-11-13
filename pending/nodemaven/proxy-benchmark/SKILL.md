---
name: proxy-benchmark
description: Measure proxies and scraping browsers with the open-source proxy-benchmark harness - success rate on real targets (Google, Bing, DuckDuckGo, Amazon), bytes per page, exit yield, and side-by-side comparison of providers or automation engines (Playwright, Patchright, Camoufox, zendriver, SeleniumBase and others). Use when the user wants to test or compare proxy providers, check which browser gets past a target, estimate traffic cost, or reproduce a published number.
license: MIT
---

# proxy-benchmark

Open source, MIT: [github.com/nodemaven/proxy-benchmark](https://github.com/nodemaven/proxy-benchmark).
Every attempt is one JSONL row under `data/runs/`; a number is only as good as
the run file it came from. Python 3.11+, run from a checkout.

## First run, no proxy and no browser

```bash
git clone https://github.com/nodemaven/proxy-benchmark && cd proxy-benchmark
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-core.txt
python scripts/benchmark.py --engines http --targets ddg_serp --queries 5 --direct --preset none
```

It prints the plan and its cost before sending anything. Then
`python scripts/analysis/report.py` reads the result.

## Full setup

```bash
pip install -r requirements-dev.txt
python -m patchright install chromium          # and the other engines' browsers, see the README
cp .env.example .env
make check                                      # ruff plus the offline suite
python scripts/benchmark.py --dry-run           # plan, cost, engines unavailable on this machine
```

Run `--dry-run` before every new matrix. A missing engine reports itself and the
rest still runs.

## Proxies

`.env` takes `<PROVIDER>_LOGIN` and `<PROVIDER>_PASSWORD`, where the prefix is the
provider file's id: `NODEMAVEN_LOGIN`, `OXYLABS_LOGIN`, ... Any other proxy:

```
CUSTOM_HOST=1.2.3.4
CUSTOM_PORT=8000
CUSTOM_LOGIN=your_login
CUSTOM_PASSWORD=your_password
```

Check a gateway before spending on it - ten CONNECTs, a few hundred bytes:

```bash
python -m nmbench gateway-health --provider custom
```

A provider that encodes country or sticky session in the username gets its own
file: copy `data/providers/_template.toml` to `data/providers/<id>.toml` and
describe the username format there. No code changes.

## Common runs

```bash
# compare two providers in the same time window (interleaved, not one after the other)
python scripts/benchmark.py --providers nodemaven,custom --engines patchright \
  --targets google_serp --queries 40 --batch 10

# compare engines; :direct runs the same browser without the proxy in the same window
python scripts/benchmark.py --engines patchright,chromium,chromium:direct \
  --targets google_serp --queries 40 --batch 10 --headful

# compare a gateway setting
python scripts/benchmark.py --arm filter=medium --arm filter=high --engines http \n  --targets bing_serp --preset none
```

| flag | meaning |
|---|---|
| `--engines` | `http`, `curlcffi`, `chromium`, `patchright`, `rebrowser`, `cloak`, `camoufox`, `obscura`, `seleniumbase`, `zendriver`, `botasaurus`; `:direct` suffix for no proxy |
| `--targets` | `google_serp`, `bing_serp`, `ddg_serp`, `amazon_search`, `ipinfo` (cheap: only the exit IP) |
| `--queries`, `--batch` | how many queries, and queries per browser session (one exit) |
| `--countries` | default `us`; `any` serves more on Google, pass both if country is the question |
| `--preset` | resource blocking `none`, `light` (default), `aggressive`; an engine without blocking, such as `http`, needs `none` |
| `--resume` | continue an interrupted run without re-asking targets |
| `--breaker` | consecutive sessions with nothing served that stop a cell (default 3) |

Reading results: `report.py` for one run or `--all`, `peek.py <file>` line by
line, `calibrate.py` for what a run really cost.

## Rules

- Interleave what you compare. Provider A at 10:00 and provider B at 14:00
  measures the afternoon too; `--providers` and `--arm` interleave for you.
- A single run is an anecdote. Quote a number with its run file and the date.
- The breaker is not an error handler: retrying an exit a target refused rarely
  works and burns the pool. On the published runs, an attempt succeeds 75% of
  the time with no failures before it in its cell, 5.8% after five, 1.6% from the
  sixth on.
- Pause 3-5 s between requests at least, and estimate anything above about 100
  requests with `--dry-run` first.
- `.env` and raw response bodies stay local; committed run rows mask exit IPs to
  /24 and the username to `<login>`.
