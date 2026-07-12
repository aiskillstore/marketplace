---
name: plan-prospecting
description: Build a sourced retirement-plan prospecting brief with PlanProvider.Pro MCP data. Use when a user wants to research target employers, identify their current retirement-plan providers, or prioritize outreach based on Form 5500-derived plan signals.
---

# Prospect retirement-plan accounts with PlanProvider.Pro

Use the PlanProvider.Pro MCP to enrich a user-supplied target list with Form 5500-derived plan and provider context. The MCP is a research tool: it does not replace a CRM, a current contact database, or legal and fiduciary advice.

## Connect

Add this remote MCP server in the client's MCP connections or integrations settings:

https://swhejpcukgzywbwacfdv.supabase.co/functions/v1/mcp

Complete the PlanProvider.Pro OAuth flow when prompted. The endpoint is public by design; account tier controls the accessible Form 5500 rows and fields.

## MCP tools

- lookup_company_plan: search indexed Form 5500 plan records by company or sponsor name.
- search_providers: find auditors, advisors, administrators, insurers, and ERISA attorneys by name, provider type, or state.
- get_provider: retrieve a provider profile after a provider slug is known.

## Recommended workflow

1. Clarify the target market: geography, industry, plan type, approximate participants or assets, and the provider service being sold.
2. Start with the user's target employers or a narrow, named candidate list. The MCP does not provide an unrestricted bulk company export, so do not claim to have searched every employer in a market.
3. Call lookup_company_plan for each target sponsor name. Try the legal name, operating name, and a likely alternate name when the first lookup is empty.
4. Confirm the match using the returned sponsor, plan name, EIN, plan number, participants, assets, filing year, and canonical PlanProvider.Pro URL.
5. Identify current plan providers from the linked plan record. Use search_providers or get_provider when the user needs provider context, credentials, geography, or a profile link.
6. Prioritize outreach using explicit, filing-derived signals such as plan size, plan type complexity, recent provider changes shown on the source record, and a provider-service gap. Label every inference as an inference.
7. Return a concise prospecting table with the target company, plan, filing as-of year, participants, assets, current providers, signal, rationale, and canonical source URL.

## Source verification

When a result needs fields beyond the MCP response, fetch its canonical PlanProvider.Pro URL with:

GET https://planprovider.pro/<path>
Accept: text/markdown

Do not invent a provider relationship, current contact, intent signal, plan size, fee, credential, or reason to switch. Form 5500 data can lag, be amended, or reflect a filing period rather than a relationship today.

## Example prompts

- "Use the PlanProvider.Pro MCP to research these five Colorado employers for a 401(k) audit-services brief. Keep only confirmed plan matches, show the filing year and current auditor, and include a source URL for every row."
- "For these target sponsors, look up the matching retirement plan, identify the listed advisor and recordkeeper, and flag only evidence-backed reasons an RFP might be timely. Separate facts from inferences."
- "Build a sourced shortlist of plan-advisor prospects from this named employer list. Use MCP lookups first, then fetch the canonical plan pages as markdown when you need more detail."

## Output format

Return a markdown table or a short ranked list. Include: target company, matching plan, filing as-of year, participants, total assets, current providers, evidence-backed signal, clearly labeled inference, and the canonical PlanProvider.Pro URL.
