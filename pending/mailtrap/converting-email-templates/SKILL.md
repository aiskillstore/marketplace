---
name: converting-email-templates
description: >-
  Use when converting or migrating email templates from another provider
  (SendGrid, Mailgun, Mandrill, Postmark, Brevo, Amazon SES) to
  Mailtrap-compatible Handlebars syntax. Supports single file, bulk
  directory, and inline HTML conversion.
---

# Converting email templates

## Purpose

Automatically convert email templates from other email service providers into Mailtrap-compatible Handlebars syntax. Handles both deterministic pattern conversions (via a Python script) and complex edge cases (via LLM intelligence).

**Related skills:** `using-email-templates` (Handlebars syntax, API template send), `sending-emails` (stream bases and auth), `authorizing-api-requests` (tokens, env vars, `account_id` resolution — needed when creating templates or sending via the Templates API after conversion).

## Input

- **Source provider** (required): `sendgrid`, `mailgun`, `mandrill-handlebars`, `mandrill-mergetags`, `postmark`, `brevo`, or `ses`
- **Input**: a single template file path, a directory of `.html` template files, or raw HTML pasted inline
- **Output directory** (optional): defaults to a `/converted/` subdirectory next to the input

If the user does not specify the source provider, ask before proceeding. If the user provides template HTML inline (pasted in chat), save it to a temporary `.html` file first.

## Workflow

### Step 1: Detect mode

**Fast mode** (default): For providers with deterministic conversion patterns. The Python script handles these reliably.

**Deep mode**: Triggered when:
- Provider is `brevo` AND the template contains nested loops, multiple filters, or complex conditional nesting
- The script flags patterns that could benefit from LLM judgment
- The user explicitly requests deep mode
- Inline HTML is provided (run LLM conversion directly)

### Step 2: Run the converter script

Execute the Python converter script:

```bash
python3 {skill_dir}/scripts/converter.py \
  --provider {provider} \
  --input {input_path} \
  --output {output_dir}
```

Where `{skill_dir}` is the directory containing this SKILL.md file.

**Read the output:**
- Exit code 0: clean conversion, no flags. Proceed to Step 4.
- Exit code 1: conversion completed with flags. Proceed to Step 3.
- Exit code 2: error. Report to user and stop.

Read the `.report.txt` file(s) generated alongside each converted template. For bulk conversions, also read `_summary.txt`.

**Note:** When flags are present, the script automatically:
- Prepends a `<!-- WARNING: ... -->` comment at the top of the converted file
- Wraps unsupported syntax in `<!-- FLAGGED [RULE]: message -->` HTML comments so the file can be pasted into the Mailtrap editor without triggering parser errors

### Step 3: Handle flags (Deep mode)

For each flag in the report:

1. **Read the flagged line** in the original template.
2. **Consult** `references/conversion-rules.md` for the specific rule and recommended action.
3. **Categorize** the flag:
   - **App-layer change required** (e.g., `formatDate`, comparison helpers): Cannot be resolved in the template. Report to the user with a clear explanation of what they need to change in their application code. Suggest the replacement variable name.
   - **Template-level fix possible** (e.g., Brevo nested loops, Mandrill `mc:edit` regions): Apply the conversion using LLM judgment. Show the user the before/after and ask for confirmation before writing.
   - **Ambiguous** (e.g., Postmark closing tag mismatch): Show the user both the original context and the converted output. Ask them to verify.

Present flags grouped by category:
```
## Conversion Complete

### Auto-converted: [count] changes
[Brief summary or collapsed details]

### Needs your application code: [count] flags
[For each: what to change, why, suggested variable name]

### Needs verification: [count] flags
[For each: show before/after, ask for confirmation]
```

### Step 4: Present results

**Single file:**
```
Converted: {filename}
Changes: [count] | Flags: [count]
Output: {output_path}

[Show the conversion report summary]
[If flags exist, show the categorized flag breakdown from Step 3]
```

**Bulk conversion:**
```
Converted: [count] files
Total changes: [count] | Total flags: [count]
Clean: [count] files | Needs review: [count] files
Output: {output_dir}

[Show the summary report]
[List files needing review with their specific flags]
```

### Step 5: API field mapping reminder

After template conversion, always remind the user about the API-side changes they need to make. Reference the quick mapping table:

| Provider | Old template field | Old variables field | Mailtrap field | Mailtrap variables |
|----------|-------------------|--------------------|-----------------------|------------------------|
| SendGrid | `template_id` | `personalizations[].dynamic_template_data` | `template_uuid` | `template_variables` |
| Mailgun | `template` | `t:variables` | `template_uuid` | `template_variables` |
| Mandrill | `template_name` | `global_merge_vars` + `merge_vars` | `template_uuid` | `template_variables` |
| Postmark | `TemplateId`/`TemplateAlias` | `TemplateModel` | `template_uuid` | `template_variables` |
| Brevo | `templateId` | `params` | `template_uuid` | `template_variables` |
| Amazon SES | `TemplateName`/`TemplateArn` | `TemplateData` | `template_uuid` | `template_variables` |

Only show the row for the provider that was just converted.

## Inline conversion (no file)

If the user pastes template HTML directly in chat instead of providing a file path:

1. Identify the source provider (ask if not stated).
2. Apply the conversion rules from `references/conversion-rules.md` directly using LLM intelligence.
3. **Comment out unsupported syntax** in the converted output by wrapping it in `<!-- FLAGGED [RULE]: message -->` HTML comments (same format as the script). This prevents editor errors when the user pastes the output into Mailtrap.
4. If there are flags, prepend a `<!-- WARNING: ... -->` comment at the top of the converted output noting how many flagged patterns need resolution.
5. Present the converted Handlebars output with a list of changes made.
6. Flag any patterns that need app-layer changes.
7. Offer to save the result to a file.

This mode always uses Deep mode (LLM) since there is no file to pass to the script.

## Rules

- **Never silently skip a flagged pattern.** Every flag must be reported to the user.
- **Never modify the original file.** Converted output always goes to the output directory.
- **Preserve HTML structure.** Only modify template syntax (variables, conditionals, loops, helpers). Do not touch HTML tags, attributes, CSS, or non-template content.
- **When in doubt, flag.** If a pattern is ambiguous, flag it for manual review rather than making an incorrect conversion.
- **Report counts.** Always show the number of changes and flags so the user knows the scope.
- **One provider at a time.** If a directory contains templates from multiple providers, ask the user to separate them or specify the provider for the batch.
