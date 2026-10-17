---
name: appie-linkedin-growth
description: Track LinkedIn profiles and list leads via Appie.run. Use when the user asks to track or stop tracking a LinkedIn profile, see which profiles are tracked, or list LinkedIn leads with their email or phone. Triggers include track this LinkedIn profile, LinkedIn leads, show my tracked profiles, stop tracking, lead emails, LinkedIn growth.
license: MIT
---

# Appie LinkedIn Growth

## Overview

Manage the LinkedIn profiles the current Appie project tracks and list the leads, with email and phone when a lookup has found them.

- Listing profiles, saving a profile and listing leads are free.
- The existing schedule runs profile scans, which cost 30 credits each.
- The lookup that fills a lead's email and phone costs 5 credits per lead.
- Never invent profiles, leads, emails or phone numbers — only return API results.

## Prerequisites (always run first)

This skill needs the Appie.run MCP server connected to your agent.

1. Check whether the Appie tools (e.g. `get_linkedin_profiles`, `list_linkedin_leads`) are already available. If they are, continue.
2. If not, ask the user to connect the Appie MCP server:
   - URL: `https://appie.run/mcp` (transport: streamable HTTP)
   - Header: `Authorization: Bearer <esk_...>` (your Appie.run project API key, starting with `esk_`)
   - Setup docs for each client: https://appie.run/docs/mcp
3. New Appie.run accounts get 500 free credits. Never ask the user to paste their key into chat, and never invent one.
   Stop and wait until the tools are available before continuing.

## Tool Reference

| Action              | Tool name                 | Cost | Notes |
|---------------------|---------------------------|------|-------|
| List profiles       | `get_linkedin_profiles`   | free | profiles this project tracks |
| Add/update profile  | `set_linkedin_profile`    | free to save | scheduled scans cost 30 |
| List leads          | `list_linkedin_leads`     | free to list | lookups cost 5 per lead |

### set_linkedin_profile parameters
- `profile_url` (required) — the LinkedIn profile URL
- `tracking_enabled` (optional, default true) — set false to stop tracking

### list_linkedin_leads parameters
- `limit` (optional, default 20, maximum 50)
- `tracked_profile_id` (optional) — only leads for one tracked profile
- Leads include `email` and `phone` when a lookup has found them.

## Full Workflow

### 1. See what's tracked
1. Call get_linkedin_profiles.
2. Show the profiles exactly as returned.

### 2. Add, update or pause a profile
1. Get the LinkedIn profile URL from the user. If it doesn't look like a LinkedIn profile URL, ask for the correct one.
2. Call set_linkedin_profile with `profile_url` (and `tracking_enabled: false` to pause).
3. Tell the user saving is free, and that the existing schedule runs the scan, which costs 30 credits.

### 3. List leads
1. Call list_linkedin_leads, optionally with `limit` and `tracked_profile_id`.
2. Present the leads in a compact table. Show `email` and `phone` only when the result includes them.
3. Mention that the lookup that fills email and phone costs 5 credits per lead.

## Error Handling & Edge Cases

- No profiles tracked yet → offer to add one with set_linkedin_profile.
- No leads yet → say so; scans run on the existing schedule, so leads may appear later.
- `insufficient_credits` → report the costs (30 per scan, 5 per lookup) and stop. Do not retry.
- `app_not_allowed` → the key's owner can't use the LinkedIn app; ask a project owner or admin.
- Missing email or phone → leave it blank. Never guess or construct contact details.
- Multiple profiles → list them with ids and ask which one to filter by if ambiguous.

## Cross-skill Integration

- Brand context from get_brain (ideal customer, competitors) can help the user decide which profiles to track.
- Use appie-url-shortener to make trackable links for outreach to the leads.

## Response Style

- Be concise. Lead with the profiles or leads.
- Mention credit costs the first time a scan or lookup is relevant.
- Keep profile and lead ids so the user can filter or update later.
- Do not add marketing fluff or extra suggestions unless the user asks.
