---
name: review-work
description: Get the real price for the exact request. Nothing runs.
---

# See the price

SpecStream is the live web data engine for teams and agents. Use the configured MCP server at `https://api.specstream.ai/mcp`.

Call `quote_capacity_work` with the `ast_hash` from `compile`, the operation, the number of results wanted, the useful minimum, and the original `parent_find_id`, `project_id` or `revision_id` when one applies. Asking for more uses `extend`, adding facts uses `add_facts` and rechecking uses `refresh`.

Say the scope, the conditions, the maximum price and the expiry in text. Results cost 5 cents, 15 cents or $1 each, plus 5 cents for a person's email and 15 cents for a phone, and nothing when nothing matches. A price lasts 30 minutes. The price does not spend any balance and does not start a job.

Use `get_capacity_balance` to read the balance. A balance is not permission to spend. Do not copy the maximum into an approval unless the person said to, or an existing bounded task already allows it. Plans and top-ups live in the person's account, not in chat.
