---
name: pricewin-price-comparison
description: Compare live hotel room rates across Booking.com, Agoda, Traveloka, and OpenTravel for specific dates — which OTA is cheapest for the same property, per-room prices, and free-cancellation terms. Use when comparing hotel prices, checking room rates for a named hotel, asking which site is cheaper, or finding the best rate for given check-in/check-out dates.
version: 1.0.3
author: PriceWin
platforms: [linux, macos, windows]
tags: [price-comparison, compare-hotel-prices, hotel-price-comparison, room-rates, cheapest-hotel, best-hotel-rates, booking-vs-agoda, ota-comparison, cancellation-policy, free-cancellation, agoda, booking-com, traveloka, opentravel, mcp, hotel, travel]
metadata:
  openclaw:
    emoji: "⚖️"
    homepage: https://github.com/Price-Win/pricewin-skills-hub
---

> Requires the `pricewin` MCP server. This skill issues no network calls of its own.

# Price Comparison

**MCP server:** `pricewin`. Compares live rates across **Booking.com, Agoda, Traveloka** (crawled) plus **OpenTravel** (direct API).

Comparison is something you do **over the returned sources** — there is no server-side
compare call. Pick the entry point by what the user gave you:

| User gave you | Tool |
|---|---|
| A **city** — "compare hotel prices in Da Nang" | `search_hotels_live` → `poll_search_results` |
| A **named hotel** — "is Mercure Danang cheaper on Agoda or Booking?" | `get_ota_hotel_detail` |
| A hotel already known to be **OpenTravel direct** (`source: "OPENTRAVEL_DIRECT"`, has `propertyId`) | `get_hotel_detail` |

## City-wide comparison

`search_hotels_live` returns IMMEDIATELY with a `sessionId` — it does **not** return hotels.

1. `search_hotels_live` — required: `city`, `checkIn`, `checkOut` (YYYY-MM-DD). Optional: `adults` (default 2), `rooms`, `area`, `hotelName`, `priceMin`, `priceMax`, `language`
2. Wait 5s → `poll_search_results(sessionId, nights)`
3. While `status` is `pending` or `partial`: wait 5s and poll again — up to 18 times (90s)
4. Present as soon as `status == "partial"` with hotels; keep polling silently and refine

Then compare per hotel across its sources. See [`pricewin-hotel-search`](../pricewin-hotel-search/SKILL.md)
for the full dedupe + presentation contract — do not restate it differently here.

## Single named hotel

`get_ota_hotel_detail` — for one specific Booking.com/Agoda hotel the user named.

- Required: `checkIn`, `checkOut`. Pass `hotelName` + `city` + `queryText` (verbatim user text) whenever known
- **Do NOT call `search_hotels_live` for a named hotel** — that returns a whole-city list
- Live crawl, **~20–60s**. Say nothing about "loading" until it actually returns
- Speed-up: if a prior search already gave you `prices.booking.url`, pass it as `propertyUrl` to skip name resolution
- If it returns not-found under load, retry **once**

Returns rooms, prices, facilities, photos, reviews for that property.

## OpenTravel direct properties

`get_hotel_detail` — only for results with `source: "OPENTRAVEL_DIRECT"`.

- Pass `propertyId` (UUID from `opentravelResults[].propertyId`) when available
- `hotelName` + `city` is a fallback **only** for a property already confirmed as OpenTravel direct
- Required: `checkIn`, `checkOut`. Optional: `adults`, `children`, `language`
- Returns room types with `roomTypeId` and `ratePlanId` — these are what make a property bookable

⚠️ Router rule: **have a `propertyId` → `get_hotel_detail`. Name only → `get_ota_hotel_detail`.**

## Cancellation terms

For OpenTravel rate plans only: `get_cancellation_policy(propertyId, ratePlanId, checkInDate)`
→ non-refundable flag, free-cancellation window, refund %, and the computed deadline.

`ratePlanId` comes from `get_hotel_detail` → `roomTypes[].ratePlanId`. Pass `checkInDate`
or you get no deadline. OTA hotels have no structured policy — quote whatever the crawl returned.

## Presenting a comparison

- Rank **purely by price**. No source gets priority, OpenTravel included
- Show the cheapest source first, then the others underneath:
  `Agoda $X · Booking $Y · OpenTravel $Z`
- Savings vs the next-cheapest source: `(next - cheapest) / next * 100` → "Save Z%"
- When the gap is small, prefer the free-cancellation option and say why
- All prices USD unless the tool says otherwise. No conversion

Tool inputs and response fields: [reference.md](reference.md).

## Security & data handling

Documentation only — no code, no dependencies, no network calls of its own. The
only data sent is the comparison query (city or hotel name, dates, guests, plus
`queryText` — the user's message verbatim), to PriceWin's hosted MCP server
`https://mcp.price.win/mcp` (no credentials, no account). No PII, and this skill
cannot book or pay for anything. Full disclosure — operator, backend provenance,
exact fields per tool — in [`SECURITY.md`](./SECURITY.md).
