---
name: softsync-documents
description: "Design PDF templates such as invoices, quotes and contracts, try them on a record, and make the finished PDF. Use when the user wants a new document layout, to change one, or a PDF for a record."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Documents

A document template turns one record into a PDF, for example an invoice from an invoice record. Each PDF made is listed on the record.

## Tools
- `document_templates` with action `list` or `get`: the templates, their layout, paper and file name.
- `manage_document_templates` with action `create`: a title, the group it lives in, the object it is made from, the layout and the paper. Text may use {{ record.field }} placeholders.
- Action `update`: send only what changes; a layout or page settings, when sent, replace the whole thing, so read the template first.
- `document_templates` with action `preview`: fill a saved template, or a layout you are still trying, from one record and get a PDF to look at. It is not added to the record.
- `manage_document_templates` with action `generate`: make the real PDF and list it on the record.
- Action `delete` removes a template. PDFs already made are kept.

## Signing
- `record_files` with action `list`: a record's Files tab — folders, uploads and documents — with each PDF's signing state and the roles its fields need.
- `send_for_signature`: email one of those PDFs to people to sign. Give one signer per role, named exactly as the fields name it; add people with kind `copy` who only get the signed PDF. People with the same step sign at the same time; a higher step waits for the lower ones. Everyone gets the sealed signed PDF at the end.
- `record_files` with action `signing_status`: who has signed and who is still to sign, for one signing or every signing of a record.

## Rules
- Changing templates needs editor rights in the template's group.
- Sending for signature emails real people. Like other sends, it is held until the user approves it: show the document, who signs in which order, and wait for a clear yes.
- Saving a template makes no PDF and is easy to change back, so save what the user asked for without asking first. Then preview it on a real record and show them the result.
