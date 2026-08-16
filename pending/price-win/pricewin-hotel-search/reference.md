# Hotel Search – Tool reference

This skill uses exactly two `pricewin` MCP tools.

## `search_hotels_live`

**Required:** `city`, `checkIn` (YYYY-MM-DD), `checkOut` (YYYY-MM-DD)
**Optional:** `adults` (1–20, default 2), `rooms` (1–20, default 1), `area`,
`hotelName`, `priceMin`, `priceMax`, `language` (`en|vi|de|ja|ko|zh`), `queryText`

Returns a **`sessionId` only** — no hotels. Crawling continues in the background across
Agoda, Booking.com, and Traveloka, plus direct OpenTravel listings.

Use `hotelName`, `area`, and price bounds **only** when they appear in the user's request.
Prefer `language` over `queryText` when you already know the locale.

## `poll_search_results`

**Required:** `sessionId`, `nights` (1–365)
**Optional:** `limit` (0–100, default 50; `0` = all), `offset` (pagination),
and overrides for `area` / `hotelName` / `priceMin` / `priceMax`

**Returns:** `status` — `pending` | `partial` | `completed` — plus hotel listings.
Call again every few seconds until `completed`.

### Per-hotel fields

`name`, `price`, `stars`, `rating` (0–10), `reviewCount`, `url`, `source`

- `source` identifies the OTA; `"OPENTRAVEL_DIRECT"` marks a direct listing
- Booking.com URLs are at `hotel.prices.booking.url`
- OpenTravel direct results arrive in `opentravelResults[]`, each with a `propertyId`
  UUID — pass it to `get_hotel_detail` (see `pricewin-price-comparison`) for rooms,
  photos, and availability

## Notes

- `url` is the raw OTA hotel page **without dates** — append the user's dates before
  showing it (see SKILL.md). Traveloka URLs already carry dates in `spec=`
- There is no `autocomplete_city`, `search_hotels`, or city/region-listing tool on this
  server — pass the city as free text to `search_hotels_live`
- Currency: USD, presented as-is, no conversion
