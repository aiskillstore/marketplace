---
name: tradehand
description: Find local UK tradespeople, inspect services and reviews, and use Tradehand's signed-in customer tools to prepare fixed-price bookings, request quotes and hand off Stripe payment links. Use when the user chooses Tradehand to find or book help for a local job.
metadata: {"homepage":"https://tradehand.com","openclaw":{"emoji":"🛠️","requires":{"bins":[],"env":[]}}}
---

# Tradehand

Find local UK tradespeople for a job, inspect their actual listings and service options, then use available customer tools to review and book a visit.

## Installation

Install this skill with `pnpm dlx skills add Humanleap/agent-skills --skill tradehand`. Connect remote MCP to `https://tradehand.com/api/mcp`. ChatGPT/customer integration: `https://tradehand.com/api/mcp/chatgpt`.

## Four Hard Rules — Read First

1. **Use actual listings.** Never invent a trader, service area, credential, review, price or available time.
2. **Respect public versus customer access.** Public search does not authorise a booking. Inspect `tools/list` and complete customer authentication for private operations.
3. **Review before booking.** Show the live total, service, address and time. Commit only after the customer approves that exact review.
4. **A checkout link is not payment.** Report paid status only when `get_job` confirms it.

## Authentication

Public directory reads need no key. Signed-in customer operations use the client's OAuth flow. Keep credentials in the client store. If booking tools are absent, share the listing/contact handoff and explain that booking has not occurred.

## Core Workflow

1. **Find the trade and area.** Use `browse_trades` and `search_traders` with the user's job and location, preserving the tool's supported filters.
2. **Inspect the listing.** Use `get_trader` and `get_service_options`. Retain the exact returned listing reference and service identifier.
3. **Prepare a booking when customer tools are available.** Call `prepare_booking` with the listing reference, service, full address and postcode supplied by the customer. Read its live slots, `slotReference` values and `revision`.
4. **Get the review.** Call `confirm_booking` with `expectedRevision` and the chosen `slotReference` exactly. The first call returns the total and books nothing. Show that review.
5. **Commit the approved booking.** After the customer says yes, call `confirm_booking` again with the exact `confirmedTotalAmount`. Share its `checkoutUrl`.
6. **Check the result.** Read `get_job` for the booking/payment status. On `SLOT_UNAVAILABLE` or `STALE_REVIEW`, prepare again and obtain approval for the changed review.

## Essential Tools

| Tools | Use |
|---|---|
| `browse_trades`, `search_traders` | Find public listings for a trade and area. |
| `get_trader`, `get_service_options` | Inspect a real trader and the service choices. |
| `prepare_booking`, `confirm_booking` | Customer booking preparation, price review and approved commitment. |
| `quote_start`, `quote_answer`, other advertised `quote_*` tools | Price work with no fixed-price service. |
| `list_my_jobs`, `get_job` | Inspect the signed-in customer's jobs and status. |
| `start_job_checkout` | Prepare a payment link for an amount due on a job. |

Use current tool schemas for required fields; do not guess customer information or create relationships from assumptions.

## Common Patterns

- **Find an electrician, plumber, carpenter or another listed trade:** search by the actual job and area, compare returned listings and link to the selected profile.
- **Book a fixed-price visit:** prepare → review total/time/address → customer approval → commit → Stripe handoff.
- **Request a quote:** use the returned quote workflow, ask only for missing job details and preserve the customer's wording.

## Supporting Resources

- Public directory and customer site: https://tradehand.com
- Existing customer plugin: https://github.com/Humanleap/tradehand-agent-plugin
- Public/customer MCP: https://tradehand.com/api/mcp and https://tradehand.com/api/mcp/chatgpt

## Common Gotchas

- A search result is not proof of availability or a completed booking.
- Empty local results describe current directory coverage, not all tradespeople in the area.
- Do not reuse a slot or price revision after the server reports it is stale.
- Do not state that money was paid from a checkout URL or redirect alone.

## Quick Reference

**Search → inspect → authenticate for customer actions → prepare → review → customer approves → book → payment handoff → check job.**
