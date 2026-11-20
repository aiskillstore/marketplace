---
name: approve-work
description: Approve an exact price, up to the maximum the person set. This starts paid work.
---

# Approve a price

SpecStream is the live web data engine for teams and agents. Use the configured MCP server at `https://api.specstream.ai/mcp`.

`authorize_capacity_work` starts paid work, so treat it as a write. It needs the reviewed `quote_id` and `quote_hash`, the approved maximum as an integer in `confirm_max_cents`, and a stable `idempotency_key`. A standing project or agent authority must cover this exact scope and limit. A funded account is not enough.

Save the same key before you send the call. If the response is unclear, recover the same work with `get_capacity_request` or `get_capacity_quote`. Never create a new key, price or run just to recover a lost response. A price that expired or changed needs a new approval.

Do not top up, subscribe, add a seat or open a payment page. If the balance or the authority is missing, say exactly what is missing and keep the request.

Use `get_find` for progress. Rows appear while the run works, and a run can be stopped and keeps what it found. Only delivered matches are charged. Unsure results stay unsure.
