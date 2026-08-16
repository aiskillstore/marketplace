# Price Comparison – Tool reference

Inputs below are the exact `pricewin` MCP tool contracts. Response fields are those
the tool contracts guarantee; anything else a crawl returns is best-effort.

## `search_hotels_live`

**Required:** `city`, `checkIn` (YYYY-MM-DD), `checkOut`
**Optional:** `adults` (1–20, default 2), `rooms` (1–20, default 1), `area`, `hotelName`,
`priceMin`, `priceMax`, `language` (`en|vi|de|ja|ko|zh`), `queryText`

Returns a **`sessionId` only** — crawling continues in the background.
Use `hotelName` / `area` / price bounds only when the user actually asked for them.

## `poll_search_results`

**Required:** `sessionId`, `nights` (1–365)
**Optional:** `limit` (0–100, default 50; `0` = all), `offset`, and overrides for
`area` / `hotelName` / `priceMin` / `priceMax`

**Returns:** `status` (`pending` | `partial` | `completed`) + hotel listings.
OpenTravel direct listings arrive in `opentravelResults[]`, each carrying a
`propertyId` UUID for `get_hotel_detail`. Booking.com URLs appear at
`hotel.prices.booking.url`.

Per-hotel fields used for comparison: `name`, `price`, `stars`, `rating` (0–10),
`reviewCount`, `url`, `source`.

## `get_ota_hotel_detail`

For ONE specific NAMED Booking.com/Agoda hotel with **no** `propertyId`.

**Required:** `checkIn`, `checkOut`
**Strongly recommended:** `hotelName`, `city`, `queryText` (user's original text, verbatim)
**Optional:** `adults` (default 2), `rooms` (default 1), `language`, `propertyUrl`

`hotelName` is required unless `propertyUrl` is given. Live crawl, ~20–60s.
Returns rooms, prices, facilities, photos, reviews.

## `get_hotel_detail`

For OpenTravel direct listings (`source: "OPENTRAVEL_DIRECT"`) only.

**Required:** `checkIn`, `checkOut`
**Preferred:** `propertyId` (UUID from `opentravelResults[].propertyId`)
**Fallback:** `hotelName` + `city` — only for a confirmed OpenTravel direct property
**Optional:** `adults` (default 2), `children` (default 0), `language`, `queryText`

**Returns:** markdown summary + structured detail — photo gallery, amenities,
availability, and `roomTypes[]` carrying **`roomTypeId`** and **`ratePlanId`**.

## `get_cancellation_policy`

**Required:** `propertyId` (UUID), `ratePlanId` (UUID, from `get_hotel_detail`
→ `roomTypes[].ratePlanId`)
**Optional but important:** `checkInDate` (YYYY-MM-DD) — without it there is no
computed free-cancel deadline

**Returns:** non-refundable flag, free-cancellation window, refund percentage,
human-readable summary, computed deadline.

## Router

| Situation | Tool |
|---|---|
| Have `propertyId` (UUID) | `get_hotel_detail` |
| Hotel named, no `propertyId` | `get_ota_hotel_detail` |
| Only a city | `search_hotels_live` → `poll_search_results` |

## Notes

- **No `slug` parameter exists** on any tool. Properties are addressed by
  `propertyId` (OpenTravel) or by `hotelName` + `city` (OTA)
- There is **no** `compare_hotel_prices`, `get_hotel_prices`, `search_hotels`,
  `autocomplete_city`, `get_popular_hotels`, or `get_hotel_details` tool —
  comparison is done client-side over `poll_search_results` output
- Currency: USD default, presented as-is, no conversion
