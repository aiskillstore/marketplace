---
name: sent-templates
description: Lists, finds by name or ID, inspects, or deletes existing Sent templates with the Sent MCP tools. Use when a user asks to browse templates, find an approved template, check template language, channel, category, or status, retrieve a template record, or delete a template. Use waba-template-author to write WhatsApp content and template-builder-ui to design template interfaces.
---

# Sent Templates

Operate existing template records with `templates.list`, `templates.get`, `templates.get_by_name`, and `templates.delete`.

## Establish connection and scope

Use client-managed OAuth 2.1/PKCE and never request or expose credentials. Surface the active organization and Sender Profile before deletion; use `sent-account-readiness` if the connection context does not expose both. Reauthorize in the client to change scope.

Avoid repeating template body text or sample data unnecessarily. Prefer template identifiers, names, languages, channels, categories, and statuses in summaries.

## Find and inspect templates

- Use `templates.list` for filtered discovery and pagination.
- Use `templates.get` for an exact template identifier.
- Use `templates.get_by_name` when the user supplies a name. If a name can match more than one language, channel, or scope, present the candidates and resolve one exact record before continuing.

These tools inspect existing records. For authoring or classification, hand off to `waba-template-author`; for a tenant-facing creation experience, hand off to `template-builder-ui`.

## Delete a template

1. Resolve the request to one exact template.
2. Fetch that target first with `templates.get` or `templates.get_by_name`. Never delete from a guessed identifier, broad filter, or stale list result.
3. Show a delete preview with the selected organization, Sender Profile, exact template identifier, name, language, channel, category, and status. State that deletion is destructive; do not repeat its body.
4. Ask for explicit confirmation to delete this exact target. Earlier or general approval is not sufficient.
5. Call `templates.delete` immediately after confirmation. A change to target, scope, or record invalidates confirmation.

Never call `templates.delete` without fetching the target and obtaining explicit confirmation immediately before the call. Treat every retry as a new mutation: refetch the target, show a fresh preview, and obtain new explicit confirmation.

If the result is ambiguous, re-read the target when possible. Report uncertainty and do not retry automatically.
