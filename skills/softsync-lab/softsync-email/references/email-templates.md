<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Email templates

A template is a reusable email for one table, such as contacts. Its {{placeholders}} are filled from each recipient's record when it is sent. Saving a template sends nothing.

## Tools
- `email_templates` with action `list` and no filter to see every template, then action `get` to read one. Find a template by its name.
- `email_templates` with action `variables`: the {{placeholders}} a table offers. Call it before writing a template, and only use what it returns.
- `manage_email_templates` with action `create`: a new template with a name, a subject and a simple HTML body.
- Action `update`: change the name, subject, body or copied addresses. Send only what changes.
- Action `delete`: remove a template. Mail already sent with it is not affected.

## Rules
- When the user says exactly what to change (for example "swap this number for that one"), make the change and show what you saved. Do not ask again.
- When you write the wording yourself, save it and show the user the subject and body so they can ask for changes.
- Writing or changing a template sends nothing, so do not ask before saving it. When it needs a link to one of the workspace's own pages (a booking page, a form), look the link up and put it in; say which one you used. Ask only when several fit equally well.
- Confirm the exact template before deleting it.
