---
name: toolfound-launch-kit
description: Research, prepare, submit, and track a maker product launch through the Toolfound MCP. Use when asked to list a product, compare directory alternatives, choose a launch date, verify ownership, check launch status, or get a listing badge.
license: MIT
metadata:
  author: Toolfound
  version: "1.0.0"
  homepage: "https://toolfound.com/?utm_source=github&utm_medium=skill&utm_campaign=agent-skills&utm_content=toolfound-launch-kit"
---

# Launch a product on Toolfound

Help the maker prepare a complete listing, then submit only after they confirm the destination URL, owner email, and exact copy. [Toolfound](https://toolfound.com/?utm_source=github&utm_medium=skill&utm_campaign=agent-skills&utm_content=toolfound-launch-kit) may have free launch slots; check the live free-slots counter rather than promising availability.

## Workflow

1. Use `toolfound_list_categories`, `toolfound_search_tools`, `toolfound_get_product`, and `toolfound_get_alternatives` to understand category language and competing options. Distinguish directory data from independent verification.
2. Call `toolfound_get_launch_calendar` and explain open dates and queue counts. Recommend a date based on availability and the maker's readiness.
3. Draft a concise tagline and clear description using only facts provided by the maker. Ask about pricing model, audience, differentiators, and website URL when missing. Use [the pre-launch checklist](references/pre-launch-checklist.md).
4. Present the exact HTTPS URL, owner email, product name, tagline, description, and optional public handle. Submit with `toolfound_submit_product` only after the user confirms those exact fields.
5. Explain the verification options returned by the tool: site meta tag, DNS TXT record, or emailed magic link. The owner completes verification; do not claim verified until the tool reports it.
6. Track using `toolfound_get_launch_status`. After a listing exists, use `toolfound_get_badge` and relay the returned snippets. Do not insert a badge without the maker's request.

The Toolfound service reference documents the tools and inputs. Treat verification links and any token returned for the human as sensitive; never echo secrets into public content.
