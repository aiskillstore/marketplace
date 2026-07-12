---
name: use-form-5500-mcp
description: Connect and use the PlanProvider.Pro Form 5500 MCP from Claude, Codex, Cursor, or another MCP-compatible agent. Use when a user wants to find a company retirement plan, search retirement plan providers, retrieve a provider profile, identify a plan's service providers, or ground Form 5500 research in PlanProvider.Pro source records.
---

# Use the PlanProvider.Pro Form 5500 MCP

Connect an MCP-compatible agent to PlanProvider.Pro for authenticated Form 5500 plan and retirement provider research.

## Connect

Add this remote MCP server in the client's MCP connections or integrations settings:

```
https://swhejpcukgzywbwacfdv.supabase.co/functions/v1/mcp
```

Complete the PlanProvider.Pro OAuth flow when the client opens it. The server address is public; OAuth and the signed-in account tier control access.

## Choose the right tool

- `lookup_company_plan`: Search indexed Form 5500 plan records by company or sponsor name. Returns the sponsor, plan name, EIN, plan number, participants, assets, and canonical plan URL.
- `search_providers`: Search auditors, advisors, administrators, insurers, and ERISA attorneys by firm name, provider type, or state.
- `get_provider`: Retrieve a provider profile by its PlanProvider.Pro URL slug.

## Workflow

1. Restate the company, plan, provider type, or geography being researched.
2. Call the narrowest matching MCP tool.
3. If `lookup_company_plan` returns multiple plans, distinguish them by plan name, EIN, plan number, participants, and assets before choosing one.
4. Follow the canonical PlanProvider.Pro URL when the question needs fields beyond the MCP result, such as the plan's listed advisor, auditor, recordkeeper, or administrator. Request the page with `Accept: text/markdown` when the client supports web retrieval.
5. Use `get_provider` after a provider slug is known and the user needs the provider's profile details.
6. Answer with the filing context and canonical source links.

### Example

For “Who is the advisor for Dave's Produce 401(k)?”:

1. Call `lookup_company_plan` with `company: "Dave's Produce"`.
2. Select the matching plan from the returned sponsor and plan details.
3. Open the returned canonical plan URL and inspect its listed service providers.
4. Report the advisor only if it appears on that source record, and include the plan URL.

## Account access

- Free users receive up to 10 Form 5500 plan rows without signer details, matching the browser database allowance.
- Individual Access includes up to 50 Form 5500 rows; Access+ includes unlimited rows and signer details.
- Verified providers receive up to 10 plan rows; Basic providers receive up to 50; Premium providers receive unlimited access and signer details.

## Grounding rules

- Never invent a company, plan, provider relationship, EIN, asset value, participant count, or credential.
- Treat Form 5500 data as filing-derived research with an as-of period, not a statement of a provider relationship today.
- When no record matches, say so and ask for an alternate sponsor name, state, or EIN.
- Include canonical PlanProvider.Pro URLs in the answer.
- Distinguish MCP-returned fields from details found by following the linked PlanProvider.Pro record.
