# Flight Search – Tool reference

This skill uses exactly two `pricewin` MCP tools. Register the server first with
`bash install.sh` (see SKILL.md) — the hosted endpoint is
`https://mcp.price.win/mcp`, Streamable HTTP, anonymous.

Probing it by hand needs `mcp-protocol-version: 2025-06-18` on every request; without
that header the server answers `400 Bad Request`, which looks like an outage but is not.

## `search_flights_live`

**Required:** `origin` (IATA, 3 letters), `destination` (IATA), `departureDate` (YYYY-MM-DD)
**Optional:** `returnDate` (YYYY-MM-DD — omit for one-way), `adults` (1–20, default 1),
`cabin` (`economy` | `premium_economy` | `business` | `first`, default `economy`),
`language` (`en|vi|de|ja|ko|zh`), `queryText`

Returns a **`sessionId` only** — `outboundFlights` / `returnFlights` come back empty with
`status: "pending"`. A round trip fires **two separate one-way crawls** (A→B and B→A).

Prefer `language` over `queryText` when you already know the locale. Never put unrelated
conversation or personal data in `queryText`.

**Fails when:** `returnDate` precedes `departureDate`; the airport code is not 3 letters; the
upstream crawl is unavailable. All three surface as an error message, not an empty result.

## `poll_flight_results`

**Required:** `sessionId` (UUID from `search_flights_live`)

Blocks internally: polls upstream up to 15 times at 2s intervals (~30s) and returns early once
the outbound leg has flights — and, for a round trip, the return leg too. So call it directly,
without sleeping first.

**Returns:** `status` — `pending` | `searching` | `completed` | `failed` — plus
`origin`, `destination`, `departureDate`, `returnDate`, `adults`, `cabin`,
`tripType` (`one_way` | `round_trip`), `cached`, `outboundFlights[]`, `returnFlights[]`,
`totalOutbound`, `totalReturn`.

`cached` means the fares came from a warm cache rather than a fresh crawl — still time-sensitive.

### Per-flight fields

`airline`, `airlineCode`, `flightNumber`, `duration`, `stops`, `stopCities`, `price`,
`currency`, `cabin`, `bookingUrl`, `departure{airport,city,time,date}`,
`arrival{airport,city,time,date}`, `legs?`

- **`price`** — the **party total** (per-person fare × `adults`), in **USD**. The service
  normalizes every OTA to VND for display and returns the exact `fxRate` it used; the MCP
  server divides by that rate, so no rate is ever guessed. `currency` reads `"USD"`, falling
  back to `"VND"` only when no plausible rate was available — read the field, don't assume.
- **`duration`** — minutes. Format as `Xh Ym`.
- **`stops`** — count only. `stopCities` is always `[]` on list results.
- **`departure.city` / `arrival.city`** — mirror the IATA code, not a city name.
- **`arrival.date`** — computed from departure + duration; when it differs from
  `departure.date` the flight arrives the next day.
- **`bookingUrl`** — deep link of the cheapest agent, already carrying dates and passenger
  count. The literal `https://www.price.win/` is the **no-deep-link fallback**.
- **`legs`** — optional segment breakdown; not populated by the list crawl.

There is **no source / OTA field**. The three agents behind a fare are Agoda, Trip.com and
Traveloka; only the cheapest survives the merge, so infer attribution from the `bookingUrl`
host or omit it.

## Session lifetime

15 minutes, refreshed on every poll. An expired or unknown `sessionId` returns
"Unable to retrieve this flight search" — start a new search rather than retrying.

## Common IATA codes

| City | Code | Note |
|---|---|---|
| TP.HCM / Sài Gòn | SGN | |
| Hà Nội | HAN | |
| Đà Nẵng | DAD | |
| Nha Trang | CXR | Cam Ranh |
| Phú Quốc | PQC | |
| Bangkok | BKK / DMK | DMK = low-cost carriers |
| Singapore | SIN | |
| Seoul | ICN | GMP = domestic/short-haul |
| Tokyo | NRT / HND | HND closer to the city |
| Kuala Lumpur | KUL | |

When two codes are plausible and the user did not choose, ask — do not default.

## Notes

- No airport autocomplete or city-lookup tool exists on this server
- Flights are **comparison-only** — the booking tools (`create_booking` etc.) are hotel-only
- Currency USD, same as the hotel tools — but a flight `price` is a party total for the whole
  leg, while a hotel price is per night, so never add the two without saying what each covers
