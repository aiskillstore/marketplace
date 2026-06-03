# How to Migrate Email Templates to Mailtrap

Mailtrap uses Handlebars as its template engine. If your current provider also uses Handlebars (SendGrid, Mailgun, Amazon SES), most of your template markup ports directly. If your provider uses a different syntax (Brevo, Postmark, Mandrill with merge tags), you will need to convert your templates before importing them.

This guide walks you through the full migration process: exporting templates from your current provider, converting syntax where needed, creating templates in Mailtrap, and updating your send calls.

> Note: Mailtrap supports up to 200 email templates per account. If you are migrating a larger template library, prioritize your highest-traffic templates first.

## Prerequisites

Before you start, make sure you have:

- A Mailtrap account with access to the [Email Templates](https://docs.mailtrap.io/email-api-smtp/email-templates) feature
- A [verified sending domain](https://docs.mailtrap.io/email-api-smtp/setup/sending-domain.md) set up within Mailtrap
- An API token with template management permissions (see [Authentication](https://docs.mailtrap.io/developers/authentication) and the `authorizing-api-requests` skill in this repo for env-var conventions used by the examples below)
- Your existing templates exported as HTML from your current provider

## Step 1: Export your templates

Copy the HTML source of each template you want to migrate. You need the raw HTML, subject line, and any metadata (name, category) for each template.

How you export depends on your provider:

- **SendGrid**: Open a template in the Design Editor, switch to the Code Editor tab, and copy the HTML. Or use the `GET /v3/templates/{template_id}` API endpoint.
- **Mailgun**: Open the template in the Mailgun dashboard, copy the HTML from the editor. Or use the Templates API to list and retrieve templates.
- **Mandrill**: Navigate to **Outbound** > **Templates**, open a template, and copy the HTML source. Or use the `POST /api/1.0/templates/info.json` endpoint.
- **Postmark**: Open the template in the Postmark dashboard and copy the HTML. Or use `GET /templates/{templateId}` via the API.
- **Brevo**: Open the template editor in Brevo, switch to the HTML view, and copy the source. Or use `GET /v3/smtp/templates/{templateId}` via the API.
- **Amazon SES**: Use the `GetTemplate` API action or the AWS CLI (`aws sesv2 get-email-template --template-name your-template`).

If you have many templates, scripting the export via API is faster than copying manually.

## Step 2: Convert template syntax to Handlebars

Mailtrap uses standard Handlebars syntax. The supported helpers are:

- `{{variable_name}}` - variable insertion
- `{{object.property}}` - nested/dot notation access
- `{{{variable}}}` - unescaped HTML (triple braces)
- `{{#if}}` / `{{else}}` / `{{/if}}` - conditionals
- `{{#unless}}` / `{{/unless}}` - inverse conditionals
- `{{#each}}` / `{{/each}}` - iteration over arrays
- `{{#with}}` / `{{/with}}` - context switching

Mailtrap does not support custom helpers like `formatDate`, `greaterThan`, `lessThan`, `and`, `or`, or `length`. If your templates use any of these, move that logic to your application and pass the result as a template variable.

Skip to the section for your current provider below. If your provider uses standard Handlebars, you can go straight to [Step 3](#step-3-create-templates-in-mailtrap).

### From SendGrid

SendGrid and Mailtrap both use Handlebars. Basic variable insertion (`{{variable}}`), conditionals (`{{#if}}`), iteration (`{{#each}}`), and unescaped HTML (`{{{variable}}}`) work the same way on both platforms. The differences are in helper functions and default value syntax.

**What needs to change:**

| Pattern | SendGrid | Mailtrap |
|---------|----------|----------|
| Default/fallback value | `{{insert name "default=Customer"}}` | `{{#if name}}{{name}}{{else}}Customer{{/if}}` |
| Date formatting | `{{formatDate timestamp "MMMM DD, YYYY"}}` | Not supported - format dates server-side and pass as a string variable |
| Comparison helpers | `{{#greaterThan a b}}`, `{{#lessThan a b}}`, `{{#notEquals a b}}` | Not supported - compute in your application and pass a boolean |
| Logical operators | `{{#and condition1 condition2}}`, `{{#or condition1 condition2}}` | Not supported - evaluate in your application |

**Before (SendGrid):**

```handlebars
<p>Hello {{insert firstName "default=Customer"}},</p>
<p>Your order was placed on {{formatDate orderDate "MMMM DD, YYYY"}}.</p>
{{#greaterThan orderTotal 100}}
  <p>You qualify for free shipping.</p>
{{/greaterThan}}
```

**After (Mailtrap):**

```handlebars
<p>Hello {{#if firstName}}{{firstName}}{{else}}Customer{{/if}},</p>
<p>Your order was placed on {{formatted_order_date}}.</p>
{{#if qualifies_for_free_shipping}}
  <p>You qualify for free shipping.</p>
{{/if}}
```

In this example, `formatted_order_date` and `qualifies_for_free_shipping` are computed in your application and passed as template variables.

### From Mailgun

Mailgun and Mailtrap both use Handlebars. Your template markup works in Mailtrap without syntax changes.

The only differences are on the API side:

| Field | Mailgun | Mailtrap |
|-------|---------|----------|
| Template identifier | `template` (string name) | `template_uuid` (UUID) |
| Template variables | `t:variables` (JSON string in form data) | `template_variables` (JSON object) |
| Template versioning | `t:version` parameter | Not supported |

> Note: Mailgun's batch sending uses `%recipient.varname%` placeholders, which is a separate system from Handlebars templates. Mailtrap does not support this syntax. For batch sends, use the bulk endpoint (`bulk.api.mailtrap.io/api/send`) with individual `template_variables` per message.

### From Mandrill

Mandrill supports two template syntaxes. Check the `merge_language` field in your send calls to determine which one your templates use.

**If your templates use Handlebars** (`merge_language: "handlebars"`): Copy the HTML into Mailtrap as-is. No markup changes needed.

**If your templates use Mailchimp merge tags** (`merge_language: "mailchimp"` or no `merge_language` set): Convert the syntax to Handlebars.

| Mailchimp merge tag | Handlebars equivalent |
|--------------------|----------------------|
| `*\|FNAME\|*` | `{{fname}}` |
| `*\|IF:FNAME\|*...content...*\|END:IF\|*` | `{{#if fname}}...content...{{/if}}` |
| `*\|IF:FNAME\|*...content...*\|ELSE:\|*...fallback...*\|END:IF\|*` | `{{#if fname}}...content...{{else}}...fallback...{{/if}}` |

**Additional changes:**

- **Editable regions**: Mandrill's `mc:edit` regions (filled via `template_content` in the API) have no equivalent in Mailtrap. Replace them with Handlebars variables in your template markup.
- **Variable format**: Mandrill uses arrays of `{"name": "var", "content": "value"}` objects, split into `global_merge_vars` (all recipients) and `merge_vars` (per-recipient). Mailtrap uses a flat `template_variables` object.

**Mandrill variable format:**

```json
"global_merge_vars": [
  {"name": "company", "content": "Acme Inc"},
  {"name": "year", "content": "2026"}
],
"merge_vars": [
  {
    "rcpt": "recipient@example.com",
    "vars": [{"name": "first_name", "content": "Jane"}]
  }
]
```

**Mailtrap variable format:**

```json
"template_variables": {
  "company": "Acme Inc",
  "year": "2026",
  "first_name": "Jane"
}
```

If you use per-recipient variables via `merge_vars`, send separate API calls per recipient with their specific `template_variables`.

### From Postmark

Postmark uses Mustachio, a Mustache-inspired engine. The syntax is close to Handlebars but not identical.

**What needs to change:**

| Pattern | Postmark (Mustachio) | Mailtrap (Handlebars) |
|---------|---------------------|----------------------|
| Truthy conditional | `{{#var}}...{{/var}}` | `{{#if var}}...{{/if}}` |
| Falsy conditional | `{{^var}}...{{/var}}` | `{{#unless var}}...{{/unless}}` or `{{#if var}}{{else}}...{{/if}}` |
| Variable insertion | `{{variable}}` | `{{variable}}` (no change) |
| Iteration | `{{#each items}}...{{/each}}` | `{{#each items}}...{{/each}}` (no change) |
| Unescaped HTML | `{{{variable}}}` or `{{&variable}}` | `{{{variable}}}` |

**Before (Postmark):**

```handlebars
{{#name}}
  <p>Hello {{name}},</p>
{{/name}}
{{^name}}
  <p>Hello there,</p>
{{/name}}
```

**After (Mailtrap):**

```handlebars
{{#if name}}
  <p>Hello {{name}},</p>
{{else}}
  <p>Hello there,</p>
{{/if}}
```

**Additional changes:**

- **Inline CSS**: If you rely on Postmark's `InlineCss` flag, you will need to inline CSS in your HTML before uploading to Mailtrap. Use a build tool like [juice](https://github.com/Automattic/juice) to handle this.
- **API fields**: Change `TemplateId` or `TemplateAlias` to `template_uuid`, and `TemplateModel` to `template_variables`.

### From Brevo

Brevo uses the Brevo Template Language (based on Pongo2/Django syntax). The `{{ }}` delimiters look similar to Handlebars, but the syntax is not compatible. You will need to rewrite your templates.

**Conversion reference:**

| Pattern | Brevo (Pongo2/Django) | Mailtrap (Handlebars) |
|---------|----------------------|----------------------|
| Variable insertion | `{{ params.variableName }}` | `{{variableName}}` |
| Nested access | `{{ params.order.item.name }}` | `{{order.item.name}}` |
| Conditionals | `{% if params.var %}...{% else %}...{% endif %}` | `{{#if var}}...{{else}}...{{/if}}` |
| Iteration | `{% for item in params.items %}{{ item.name }}{% endfor %}` | `{{#each items}}{{this.name}}{{/each}}` |
| Default/fallback | `{{ params.name \| default:"there" }}` | `{{#if name}}{{name}}{{else}}there{{/if}}` |
| Unescaped HTML | `{{ variable }}` (no escaping by default) | `{{{variable}}}` (triple braces) |
| Date formatting | `{{ params.date \| date:"Y-m-d" }}` | Not supported - format dates server-side |

**Before (Brevo):**

```
{% if params.hasOrder %}
  <p>Hi {{ params.name | default:"there" }},</p>
  <p>Your order details:</p>
  {% for item in params.items %}
    <p>{{ item.name }} - {{ item.price }}</p>
  {% endfor %}
{% endif %}
```

**After (Mailtrap):**

```handlebars
{{#if hasOrder}}
  <p>Hi {{#if name}}{{name}}{{else}}there{{/if}},</p>
  <p>Your order details:</p>
  {{#each items}}
    <p>{{this.name}} - {{this.price}}</p>
  {{/each}}
{{/if}}
```

### From Amazon SES

Amazon SES and Mailtrap both use Handlebars. You can copy your template HTML into Mailtrap without any syntax changes.

The differences are on the API side:

| Field | Amazon SES | Mailtrap |
|-------|-----------|----------|
| Template identifier | `TemplateName` (string, max 64 chars) or `TemplateArn` | `template_uuid` (UUID) |
| Template variables | `TemplateData` (escaped JSON string, e.g. `"{\"name\": \"John\"}"`) | `template_variables` (standard JSON object) |
| Inline templates | Supported via `TemplateContent` (no pre-storage needed) | Not supported - templates must be created in Mailtrap first |

> Note: SES requires `TemplateData` as a double-encoded JSON string. Mailtrap accepts `template_variables` as a regular JSON object, which simplifies your send calls.

## Step 3: Create templates in Mailtrap

Once your template HTML is ready and converted to Handlebars, create the templates in Mailtrap.

### Using the Mailtrap UI

1. Navigate to **Email Sending** > **Email Templates**.
2. Click **New Template**.
3. Choose an editor:
   - **Drag & Drop Editor** - build templates visually without code
   - **HTML Editor** - paste your converted HTML directly
4. Enter the template name, subject line, and category.
5. Paste your converted HTML into the editor.
6. Save the template. The template UUID is displayed in the template details - you will need it for your send calls.

### Using the Templates API

To create a template programmatically, send a `POST` request to the Templates API. This is useful when migrating multiple templates at once.

**Create a template:**

```bash
curl --request POST \
  --url "https://mailtrap.io/api/accounts/$MAILTRAP_ACCOUNT_ID/email_templates" \
  --header "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
  "email_template": {
    "name": "Welcome Email",
    "subject": "Welcome to {{company_name}}!",
    "category": "onboarding",
    "body_html": "<h1>Welcome {{user_name}}!</h1><p>Thanks for signing up.</p>",
    "body_text": "Welcome {{user_name}}! Thanks for signing up."
  }
}'
```

Set `MAILTRAP_API_TOKEN` from an env / `.env` / secret manager (never hardcode), and resolve `MAILTRAP_ACCOUNT_ID` once via `GET https://mailtrap.io/api/accounts` instead of pasting it in by hand. The `authorizing-api-requests` skill in this repo covers both — including the one-liner that exports `MAILTRAP_ACCOUNT_ID` from the response.

The response includes the template `uuid`, which you will use in your send calls:

```json
{
  "id": 123,
  "uuid": "b81aabcd-1a1e-41cf-91b6-eca0254b3d96",
  "name": "Welcome Email",
  "category": "onboarding",
  "subject": "Welcome to {{company_name}}!",
  "body_html": "<h1>Welcome {{user_name}}!</h1><p>Thanks for signing up.</p>",
  "body_text": "Welcome {{user_name}}! Thanks for signing up.",
  "created_at": "2026-01-15T10:30:00.000Z",
  "updated_at": "2026-01-15T10:30:00.000Z"
}
```

**List all templates:**

```bash
curl --request GET \
  --url "https://mailtrap.io/api/accounts/$MAILTRAP_ACCOUNT_ID/email_templates" \
  --header "Authorization: Bearer $MAILTRAP_API_TOKEN"
```

**Update a template:**

```bash
curl --request PATCH \
  --url "https://mailtrap.io/api/accounts/$MAILTRAP_ACCOUNT_ID/email_templates/{email_template_id}" \
  --header "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
  "email_template": {
    "body_html": "<h1>Welcome {{user_name}}!</h1><p>Updated content here.</p>"
  }
}'
```

Only include the fields you want to change. All fields are optional on update.

**Delete a template:**

```bash
curl --request DELETE \
  --url "https://mailtrap.io/api/accounts/$MAILTRAP_ACCOUNT_ID/email_templates/{email_template_id}" \
  --header "Authorization: Bearer $MAILTRAP_API_TOKEN"
```

> Warning: Template deletion is permanent and cannot be undone. Any send calls referencing the deleted template's UUID will fail.

## Step 4: Update your send calls

After creating your templates in Mailtrap, update the API calls in your application to reference the new template UUIDs and pass variables in Mailtrap's format.

**Send an email with a template:**

```bash
curl --request POST \
  --url https://send.api.mailtrap.io/api/send \
  --header "Authorization: Bearer $MAILTRAP_API_TOKEN" \
  --header 'Content-Type: application/json' \
  --data '{
  "from": {
    "email": "sender@yourdomain.com",
    "name": "Your App"
  },
  "to": [
    {
      "email": "recipient@example.com",
      "name": "Jane Doe"
    }
  ],
  "template_uuid": "b81aabcd-1a1e-41cf-91b6-eca0254b3d96",
  "template_variables": {
    "user_name": "Jane Doe",
    "order_number": "12345"
  }
}'
```

When you use `template_uuid`, the subject, HTML body, and text body come from the template. You do not need to include `subject`, `html`, or `text` fields in the request.

**Quick reference for API field changes:**

| Provider | Old template field | Old variables field | Mailtrap template field | Mailtrap variables field |
|----------|-------------------|--------------------|-----------------------|------------------------|
| SendGrid | `template_id` (e.g. `d-abc123`) | `personalizations[].dynamic_template_data` | `template_uuid` | `template_variables` |
| Mailgun | `template` (name string) | `t:variables` (JSON string) | `template_uuid` | `template_variables` |
| Mandrill | `template_name` (slug) | `global_merge_vars` + `merge_vars` | `template_uuid` | `template_variables` |
| Postmark | `TemplateId` or `TemplateAlias` | `TemplateModel` | `template_uuid` | `template_variables` |
| Brevo | `templateId` (integer) | `params` | `template_uuid` | `template_variables` |
| Amazon SES | `TemplateName` or `TemplateArn` | `TemplateData` (escaped JSON string) | `template_uuid` | `template_variables` |

## Step 5: Test with Email Testing

Before sending to real recipients, use [Mailtrap Email Testing](https://docs.mailtrap.io/email-sandbox/overview) to verify your migrated templates render correctly.

1. Point your application's SMTP or API configuration to the Email Testing inbox.
2. Trigger a send for each migrated template.
3. Check the following in the Email Testing inbox:
   - Variable substitution works correctly (no raw `{{variable}}` tags visible)
   - Conditionals and loops render the expected content
   - HTML layout and styling match your original templates
   - Plain text version is readable

This lets you catch conversion issues before they reach real recipients.

## Tips

- Start with your highest-traffic templates. Migrate the templates that handle password resets, order confirmations, and welcome emails first.
- Keep your old provider running in parallel. Send from both providers during migration to avoid downtime, then cut over once all templates are verified.
- Use the Templates API for bulk migration. If you have many templates, script the creation process instead of using the UI. Read the full [API documentation](https://docs.mailtrap.io/developers/) for details.
- Format dates and computed values server-side. Mailtrap's Handlebars does not include date formatting or comparison helpers. Pass pre-formatted strings and pre-computed booleans as template variables.
- Map your template IDs. Keep a spreadsheet or config file that maps old provider template IDs to new Mailtrap `template_uuid` values. This makes updating your codebase easier.
