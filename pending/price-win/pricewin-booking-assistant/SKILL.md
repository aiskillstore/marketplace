---
name: pricewin-booking-assistant
description: Recommend hotel rooms and complete a real booking end to end — reserve an OpenTravel direct property with a payment link (bank QR, card, or PayPal), check payment status, resend an expired link, or cancel a booking. Falls back to direct Booking.com/Agoda/Traveloka links for OTA-only hotels. Use when booking or reserving a hotel, getting room recommendations, paying for a stay, checking a confirmation code, or cancelling a reservation.
version: 1.0.3
author: PriceWin
platforms: [linux, macos, windows]
tags: [hotel-booking, book-hotel, reserve-hotel, room-recommendation, booking-links, payment-link, booking-management, check-booking, cancel-booking, cancellation, opentravel, agoda, booking-com, mcp, hotel, travel, accommodation]
metadata:
  openclaw:
    emoji: "🛎️"
    homepage: https://github.com/Price-Win/pricewin-skills-hub
---

> Requires the `pricewin` MCP server. Handles real money: it creates bookings and
> payment links. Read the confirmation rules below before use.

# Booking Assistant

**MCP server:** `pricewin`. Orchestrates discover → detail → recommend → **book → pay → manage**.

## What is actually bookable

| Source | Can you book it here? |
|---|---|
| `source: "OPENTRAVEL_DIRECT"` (has `propertyId`) | ✅ **Yes** — full booking + payment via `create_booking` |
| Booking.com / Agoda / Traveloka | ❌ No — comparison only. Hand the user the OTA `url` |

Only OpenTravel direct properties yield the `propertyId` + `roomTypeId` that
`create_booking` requires. Never imply an OTA hotel can be reserved through this skill.

## Recommendation flow

1. **Discover** — `search_hotels_live(city, checkIn, checkOut, adults, …)` → `sessionId`,
   then poll `poll_search_results(sessionId, nights)` every 5s while `status` is
   `pending`/`partial` (up to 18 polls / 90s)
2. **Score** — `rating × log(reviewCount + 1)` — balances quality against credibility.
   Strong candidates: `rating ≥ 8.0` and `reviewCount ≥ 100`
3. **Rank** — top 3–5 by score
4. **Detail** — `get_hotel_detail(propertyId, checkIn, checkOut, adults)` for OpenTravel
   picks; `get_ota_hotel_detail(hotelName, city, checkIn, checkOut, queryText)` for a
   named OTA hotel (~20–60s)
5. **Recommend** — filter rooms by guest capacity, then pick best value

## Booking link rules (OTA hotels)

- **NEVER invent URLs** — only use a `url` the tool returned
- Always name the OTA next to the link; if several have the same room, show all with prices
- Append the user's dates to the raw URL — see [`pricewin-hotel-search`](../pricewin-hotel-search/SKILL.md)

## Booking flow (OpenTravel direct)

### 1. Get the room first — mandatory

Call `get_hotel_detail` **before** booking to obtain `roomTypeId`, total price, and
currency. Do not guess any of the three.

Optionally call `get_cancellation_policy(propertyId, ratePlanId, checkInDate)` and show
the refund terms before taking payment.

### 2. Ask for all four things in ONE message

In your **first** request for guest info, ask for **all of these together** — never split
across turns, and always in the user's language:

1. Full name
2. Phone number
3. **Email** — the confirmation email goes here
4. Payment method

⚠️ **Never auto-fill the email** from the account/profile. The guest is often not the
account owner. It must come from what the user typed in this chat. If it is missing, ask.

Present the three payment methods as **equal choices, no default, no recommended order**:

- Bank transfer via QR (SePay) → `SEPAY`
- International card via Polar → `POLAR`
- PayPal → `PAYPAL`

If the user already signalled a preference, **infer it and skip re-asking**:

| They said | Method |
|---|---|
| "scan QR", "quét mã", "chuyển khoản", "bank transfer", "VietQR" | `SEPAY` |
| "card", "thẻ", "credit/debit card", "visa", "mastercard" | `POLAR` |
| "PayPal" | `PAYPAL` |

If anything is still missing after their reply, ask again for just the missing item(s).

### 3. Confirm before charging

Summarise back **everything** — hotel, room type, check-in/check-out, guests,
**TOTAL price** (full amount, not a deposit), guest name, **email address**
(emphasise it — a typo means the confirmation never arrives), phone, payment method
— then explicitly ask the user to confirm it is all correct.

### 4. Only then call `create_booking`

Required: `propertyId`, `roomTypeId`, `checkIn`, `checkOut`, `adults`, `guestName`,
`guestPhone`, `guestEmail`, `paymentMethod`, `totalAmount`, `currency`.
Also pass `queryText` (user's original text, verbatim).

Returns a payment link and a `confirmationCode` (e.g. `K7X9M2P4`) — surface both.

## After booking

| User says | Tool |
|---|---|
| "I paid" / "check my booking" | `check_booking_status(confirmationCode)` |
| "the payment link expired" | `recreate_payment_link(confirmationCode)` |
| "cancel my booking" | `request_cancel_token` → then `cancel_booking` |

🚨 **Never call `create_booking` twice for the same stay.** An expired payment link is
fixed with `recreate_payment_link` — it reuses the same confirmation code. Calling
`create_booking` again creates a **duplicate booking** and a duplicate confirmation email.

### Cancelling — two steps, by design

1. `request_cancel_token(confirmationCode, guestEmail)` — email must match the booking's
   primary guest. This emails the guest a magic link
2. The guest pastes the token back → `cancel_booking(confirmationCode, cancelToken, reason)`
   (`reason` ≥ 3 chars)

You cannot cancel without the guest fetching that token from their inbox. Tell them to
check their email rather than retrying step 1.

## Output format

```
### Hotel Name ★★★★☆
- Rating: 8.5/10 (1,234 reviews)
- Best room: Deluxe Double — $85/night
- Free cancellation: until 2026-08-10
- Book: [Reserve now](payment-link)          ← OpenTravel direct
- Or compare: [Agoda](url) | [Booking.com](url)
```

Tool inputs and response fields: [reference.md](reference.md).

## Security & data handling

This skill has **real transaction authority** and transmits **guest PII** (name,
phone, email) to PriceWin's hosted MCP server `https://mcp.price.win/mcp` — that
is inherent to making a reservation, and it is why booking is a separate skill
from search. It ships no code and makes no network calls of its own.

**Card numbers, CVV and bank credentials never pass through the skill or the
agent** — `create_booking` returns a payment *link* and the user pays on the
provider's own page. Never ask for card details; refuse if offered.

Confirm the full summary and total price with the user before every
`create_booking`. Full disclosure — operator, exact PII fields per tool, payment
boundary, cancellation model — in [`SECURITY.md`](./SECURITY.md).
