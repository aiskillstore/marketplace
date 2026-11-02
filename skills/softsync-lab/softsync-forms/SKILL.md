---
name: softsync-forms
description: "Create and manage public forms that save every answer as a record, and share their links. Use when the user wants a sign-up, contact or event form, or to open, close or change one."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Forms

A form is a public page anyone with the link can fill in. Each answer becomes a new record in the form's table, such as a new contact.

## Tools
- `forms` with action `list`: every form with its public link (`publicUrl`), whether it is open, and the table answers go to.
- `forms` with action `get`: one form, the fields it asks for, and what happens after someone answers.
- `manage_forms` with action `create`: a new form. Pick the table and group from the workspace description and list the fields to ask for by their apiName. When asked for someone's name, include both the first and last name fields. The form is open at once; share its `publicUrl`.
- Action `update`: rename it, open or close it (`enabled`), or change the thank-you message or the page people go to afterwards.
- Action `delete`: the link stops working. Records it already created are kept.
- Action `new_link`: a new public link when the old one was shared where it should not be. The old link stops working at once.

## Answers
There is no separate answers list: answers are records in the form's table. Use `search_records` on that table, newest first by `__system_created_at`, to see who answered.

## Rules
- Creating, changing and deleting forms needs the Admin role.
- Reordering fields, changing where answers go or the look of the form is done in the app.
- Confirm before closing or deleting a form: people with the link can no longer answer.
