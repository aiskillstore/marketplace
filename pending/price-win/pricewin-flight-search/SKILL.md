---
name: pricewin-flight-search
description: Search live flight fares for a route and date across Agoda, Trip.com, and Traveloka — one-way or round-trip, any cabin, with airline, times, stops, duration, and a direct booking link. Use when the user wants flight prices, plane or air tickets, cheap flights or airfare between two cities, comparing airlines for travel dates, or planning the flying leg of a trip.
version: 1.1.1
author: PriceWin
platforms: [linux, macos, windows]
tags: [flight-search, search-flights, find-flights, flight-prices, cheap-flights, airfare, air-tickets, plane-tickets, flight-deals, flight-comparison, one-way, round-trip, iata, airline, cabin-class, business-class, agoda, tripcom, traveloka, ota, mcp, flights, travel, trip-planning]
metadata:
  openclaw:
    emoji: "✈️"
    homepage: https://github.com/Price-Win/pricewin-skills-hub
---

> Requires the `pricewin` MCP server. This skill issues no network calls of its own.

## Setup (once per machine)

Without the MCP server registered this skill is inert — it tells you to call
`search_flights_live` and no such tool exists. `skills add` only copies files, so run:

```bash
bash install.sh          # add --dry-run first to see what it would change
```

It registers the hosted server (`https://mcp.price.win/mcp`, Streamable HTTP, no
credentials) with every agent it finds — Claude Code, Cursor, Windsurf, Gemini CLI, VS Code,
Codex — writing a `.bak` before touching any file and skipping configs it cannot parse.
Re-running it changes nothing. **Restart the agent afterwards.**

# Flight Search (Live)

**MCP server:** `pricewin`. Tool `search_flights_live` starts an async crawl across Agoda,
Trip.com and Traveloka; `poll_flight_results` returns the merged, cheapest-per-flight fares.

## CRITICAL: IATA codes only

Both airports MUST be 3-letter IATA codes. **There is no airport-lookup tool on this server** —
resolve the city yourself: `Sài Gòn / TP.HCM → SGN`, `Hà Nội → HAN`, `Đà Nẵng → DAD`,
`Bangkok → BKK` (main international), `Tokyo → NRT or HND`, `Seoul → ICN`.

When a city has several airports and the user did not say which, **ask one short question** —
never pick silently. Never invent a code.

## CRITICAL: Polling pattern (differs from hotel search)

`search_flights_live` returns IMMEDIATELY with a `sessionId` and zero flights.

1. Call `search_flights_live` with origin, destination, departureDate (YYYY-MM-DD), and
   `returnDate` only for a round trip. Add `adults`, `cabin`, `language="vi"` as needed.
2. Call `poll_flight_results(sessionId)`. **This tool blocks internally up to ~30s** and
   returns as soon as the first fares land — do NOT sleep before calling it.
3. `status` is `pending` | `searching` | `completed` | `failed`. If it comes back
   `searching` with few or no flights, **call again — up to 4 more times**.
4. Present results as soon as flights arrive; keep polling only if the user wants more.

The session expires **15 minutes** after the last poll. After that, start a new search —
the old `sessionId` is dead.

> `poll_flight_results` is registered app-visible for the flight widget. If your host does not
> expose it to the model, let the widget do the polling and do not fabricate fares.

## CRITICAL: `price` is the party total, in USD

`price` is the **total for all `adults`** — not per-person, and not the two legs combined.
Divide by `adults` yourself for a per-person figure.

`currency` is **`"USD"`**. Do not convert it. It falls back to `"VND"` only when the live FX
rate was unavailable — so **read `currency` and label the figure with it** rather than assuming
either one.

## Response format (MUST follow exactly)

Present the TOP 5-7 flights per leg ONLY. For EACH flight:

```
✈️ *<airline> <flightNumber>*  ← bold via markdown
🕐 <dep.time> <origin> → <arr.time> <destination> · <Xh Ym> · <bay thẳng | N điểm dừng>
💰 $<price> tổng cho <adults> khách (~$<price/adults>/khách)
🔗 <bookingUrl>
```

Line break between flights, no bullet markers. **Cheapest flight gets 🏆.** `duration` is in
**minutes** — format it as `2h 10m`. Flag an overnight arrival when `arrival.date` differs
from `departure.date`.

## Round trips

`outboundFlights` and `returnFlights` are **two independent one-way searches**. List them under
separate headings. You may state a combined estimate as
`cheapest outbound + cheapest return`, but label it as **two separate one-way tickets** — it is
not a quoted round-trip fare and the two legs are booked separately.

## Booking URLs — use verbatim

`bookingUrl` is the deep link of the cheapest agent, with dates and passengers already baked in.
**Never append, rewrite, or construct params** (unlike the hotel skill). A `bookingUrl` of exactly
`https://www.price.win/` means no agent deep link was captured — say the fare must be re-checked
on the provider's site instead of presenting it as a click-to-book link.

Attribute the source only from the URL host (`agoda.com`, `trip.com`, `traveloka.com`) — the
result carries no explicit source field, so do not guess one.

## Fields that look useful but are not

- `stopCities` — always empty; describe stops by count only
- `departure.city` / `arrival.city` — repeat the IATA code, not a real city name
- `legs` — usually absent on list results; don't promise a segment breakdown

## Ranking

Sort by `price`. Cheapest first, but surface a non-stop or much shorter option when it costs
only marginally more — say so in one line rather than reordering silently.

## Security & data handling

No runtime code and no network calls of its own; the only executable is
`install.sh`, which adds one MCP entry (`pricewin` → `https://mcp.price.win/mcp`)
to agent configs the user already has, backing each file up first and skipping
any it cannot parse. It downloads and executes nothing. The only data sent is the
route query (IATA codes, dates, passengers, cabin) — no passenger names, no PII,
no credentials. Comparison only: this skill cannot book or pay. Full disclosure
in [`SECURITY.md`](./SECURITY.md).
