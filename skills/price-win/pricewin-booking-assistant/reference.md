# Booking Assistant – Tool reference

Inputs below are the exact `pricewin` MCP tool contracts.

## Discovery

**`search_hotels_live`** — required `city`, `checkIn`, `checkOut`; optional `adults`
(default 2), `rooms`, `area`, `hotelName`, `priceMin`, `priceMax`, `language`, `queryText`.
Returns a `sessionId` only.

**`poll_search_results`** — required `sessionId`, `nights`; optional `limit` (default 50,
`0` = all), `offset`, filter overrides. Returns `status`
(`pending` | `partial` | `completed`) + listings. OpenTravel direct properties arrive in
`opentravelResults[]` with a `propertyId` UUID.

Per-hotel fields used for ranking: `name`, `price`, `stars`, `rating` (0–10),
`reviewCount`, `url`, `source`.

## Detail

**`get_hotel_detail`** (OpenTravel direct only) — required `checkIn`, `checkOut`;
preferred `propertyId`; fallback `hotelName` + `city`; optional `adults`, `children`,
`language`, `queryText`.
Returns gallery, amenities, availability, and **`roomTypes[]` with `roomTypeId` and
`ratePlanId`** — the inputs booking depends on.

**`get_ota_hotel_detail`** (named Booking.com/Agoda hotel, no `propertyId`) — required
`checkIn`, `checkOut`; pass `hotelName` + `city` + `queryText`; optional `adults`,
`rooms`, `language`, `propertyUrl`. Live crawl ~20–60s; retry once on not-found.

**`get_cancellation_policy`** — required `propertyId`, `ratePlanId`; pass `checkInDate`
to get the computed free-cancel deadline. Returns non-refundable flag, window,
refund %, summary, deadline.

## Booking

**`create_booking`** — required: `propertyId`, `roomTypeId`, `checkIn`, `checkOut`,
`adults`, `guestName`, `guestPhone`, `guestEmail`, `paymentMethod`, `totalAmount`,
`currency` (ISO 4217, 3 chars). Optional: `children` (default 0), `language`, `queryText`.

- `paymentMethod` ∈ `SEPAY` (Vietnam bank QR) | `POLAR` (international card) | `PAYPAL`
- `totalAmount` is in the property's base currency
- `guestEmail` must be explicitly typed by the user in chat — never inferred from a profile
- Returns `structuredContent` with a **`confirmationCode`** (8 chars, e.g. `K7X9M2P4`)
  plus the payment link

**`check_booking_status`** — required `confirmationCode`; optional `language` (`en|vi`).

**`recreate_payment_link`** — required `confirmationCode`; optional `language`.
Reuses the same booking; re-checks availability. On 409 the room is gone — tell the user
to pick another room.

## Cancellation — two steps

**`request_cancel_token`** — required `confirmationCode`, `guestEmail` (must match the
booking's primary guest). Emails a single-use magic link.

**`cancel_booking`** — required `confirmationCode`, `cancelToken` (pasted by the guest
from that email), `reason` (≥ 3 chars).

## Ranking

`score = rating × log(reviewCount + 1)`. Strong candidates: `rating ≥ 8.0` and
`reviewCount ≥ 100`.

## Notes

- Booking links for OTA hotels are **only** the `url` values the tools returned — never
  construct one
- There is no `search_hotels`, `compare_hotel_prices`, `get_hotel_details`,
  `get_popular_hotels`, or `autocomplete_city` tool
- Currency: USD default, presented as-is, no conversion
