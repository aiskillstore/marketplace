---
name: using-email-templates
description: >-
  Use when creating or sending Mailtrap-hosted email templates, Handlebars
  personalization, template UUID in API payloads, or debugging variables and
  preview. Use when separating email design from application code for
  transactional or bulk sends.
---

# Using Mailtrap email templates

## Overview

Templates are edited in the Mailtrap **UI**, referenced by **UUID** from your app, and filled with **Handlebars** data at send time. The same template can be used with **transactional** and **bulk (promotional)** streams; pick the stream when you integrate.

**Before generating SDK code:** read the README of the relevant SDK repository linked below for current method signatures. Do not rely on memory.

**Before generating API request bodies:** use the official docs and examples below—request shapes belong in the API reference, not in guesses (including when using AI-assisted coding).

**Template management via API** (create/update/list outside the UI): [Templates API](https://docs.mailtrap.io/developers/templates/templates.md).

**Related skills:** `authorizing-api-requests` (tokens, env vars, auth headers), `sending-emails` (bases and streams), `testing-with-sandbox` (preview sends without live delivery).

## When to use

- When sending or testing emails with Mailtrap-hosted templates (UUID in the send payload)
- Creating or editing templates in the **UI**
- Templates CRUD via [Templates API](https://docs.mailtrap.io/developers/templates/templates.md) (automations, provisioning)
- API body using `template_uuid` and `template_variables`
- Handlebars conditionals, loops, escaped vs unescaped HTML

## Quick reference

### API operations

In the developer docs, open:

- [Transactional – Send email (including template)](https://docs.mailtrap.io/developers/email-sending/transactional.md) (`https://send.api.mailtrap.io`)
- [Bulk – Send email (including template)](https://docs.mailtrap.io/developers/email-sending/bulk.md) (`https://bulk.api.mailtrap.io`)

Request body variant is typically **`EmailFromTemplate`** in the interactive reference.

### Authorization

Send with `Authorization: Bearer $MAILTRAP_API_TOKEN` on the matching stream host (`send.api.mailtrap.io` or `bulk.api.mailtrap.io`). Token scope, storage, and the alternative `Api-Token` header are covered in skill `authorizing-api-requests`.

### Example (`curl`) — template send

```bash
curl -X POST https://send.api.mailtrap.io/api/send \
  -H "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": {"email": "hello@yourdomain.com", "name": "Your App"},
    "to": [{"email": "user@example.com"}],
    "template_uuid": "your-uuid",
    "template_variables": {"user_name": "Jane"}
  }'
```

### Payload shape

Replace literal `text`/`html` with template fields, for example:

- `template_uuid` (from the template **Integration** tab)
- `template_variables` (object whose keys match Handlebars variables)

Exact required fields (e.g. `from`, `to`) follow the same rules as non-template sends for that stream.

### Handlebars (supported patterns)

- `{{name}}` — escaped output; `{{{html}}}` — raw HTML
- `{{#if}}` / `{{#unless}}`, `{{#each}}`, `{{#with}}`
- Nested paths such as `{{order.id}}`
- Falsy values that suppress blocks include empty string, `0`, `false`, empty collections (see product docs)

Full syntax and examples: [Using Handlebars with Email Templates](https://docs.mailtrap.io/email-api-smtp/email-templates/handlebars.md). Testing workflow: [Testing templates with Handlebars](https://docs.mailtrap.io/email-api-smtp/email-templates/handlebars.md#testing-templates-with-handlebars). Sandbox preview sends: [Send test emails (sandbox)](https://docs.mailtrap.io/developers/email-sandbox/send-test-emails.md).

### Where templates live

**Templates** in the app sidebar. UUID and stream-specific integration snippets are under each template's **Integration** tab.

### Generating template HTML

Proactively offer to generate the template HTML when the user is creating a new template — don't wait to be asked. The output must be a real **email template** — not arbitrary web HTML — and must be **mobile-compatible** (responsive, renders well across email clients and screen sizes).

### SDKs

- [Node.js](https://github.com/mailtrap/mailtrap-nodejs)
- [Python](https://github.com/mailtrap/mailtrap-python)
- [PHP](https://github.com/mailtrap/mailtrap-php)
- [Ruby](https://github.com/mailtrap/mailtrap-ruby)
- [Java](https://github.com/mailtrap/mailtrap-java)
- [.NET](https://github.com/mailtrap/mailtrap-dotnet)
- [CLI](https://github.com/mailtrap/mailtrap-cli)

## Common mistakes

| Mistake                                   | Fix                                                                                                                                                                   |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mixing `text`/`html` with `template_uuid` | Use template fields per API schema for template sends                                                                                                                 |
| Skipping sandbox for risky changes        | Preview with sandbox sending / Testing API (see `testing-with-sandbox` and [send test emails](https://docs.mailtrap.io/developers/email-sandbox/send-test-emails.md)) |
