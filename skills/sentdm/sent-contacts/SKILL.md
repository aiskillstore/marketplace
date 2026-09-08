---
name: sent-contacts
description: Lists, finds, inspects, bulk-creates, summarizes, or deletes Sent contacts with the Sent MCP tools. Use when a user asks to search contacts, get a contact by ID, import or deduplicate a contact list, review a contact's messaging summary, remove a contact, or manage direct contact records. Requires confirmation gates for creates and deletes.
---

# Sent Contacts

Operate contacts with `contacts.list`, `contacts.get`, `contacts.create_many`, `contacts.delete`, and `contacts.message_summary`.

## Establish connection and scope

Use client-managed OAuth 2.1/PKCE. Never request or expose a token, API key, authorization header, client ID, or secret. Before a mutation, surface the active organization and Sender Profile from the connection context; if either is unavailable, use `sent-account-readiness` to inspect the authorized scope. Reauthorize in the client to change scope.

Mask phone numbers where practical. Return only the contact fields needed for the task, and do not repeat contact data after it has been reviewed. Number presence or messaging history does not establish consent.

## Read contacts

- Use `contacts.list` to search or page through contacts. Apply the narrowest available filter and do not dump an entire contact book unnecessarily.
- Use `contacts.get` when an exact contact identifier is known or before a delete.
- Use `contacts.message_summary` for the contact's messaging summary. Distinguish summary data from proof of consent or current reachability.

Read-only calls do not require mutation confirmation.

## Create contacts in bulk

1. Validate and deduplicate the proposed records locally. Preserve only fields the user actually supplied.
2. Build the exact `contacts.create_many` arguments without calling the tool.
3. Show a payload preview with the selected organization, Sender Profile, record count, duplicate handling, and each exact target. Mask phone numbers where the operator can still verify them; reveal full values once only when exact verification requires it.
4. Ask for explicit confirmation for this exact batch. Earlier or general approval is not sufficient.
5. Call `contacts.create_many` immediately after confirmation. Any change to the records or scope invalidates confirmation.

Never call `contacts.create_many` without a preview and explicit confirmation immediately before the call. Treat every retry as a new mutation with a fresh preview and new explicit confirmation.

## Delete a contact

1. Resolve the requested contact to one unambiguous identifier.
2. Fetch the exact target first with `contacts.get`. Never delete from a guessed identifier, broad filter, or stale list result.
3. Show a delete preview containing the selected organization, Sender Profile, exact contact identifier, display label, and masked address. State that deletion is destructive.
4. Ask for explicit confirmation to delete that exact target.
5. Call `contacts.delete` immediately after confirmation. If the target, scope, or record changes, fetch it again and repeat the preview.

Never call `contacts.delete` without fetching the target and obtaining explicit confirmation immediately before the call. Every retry requires another fetch, a fresh preview, and new explicit confirmation.

## Report results

Report counts and stable identifiers, not full contact records. If a create or delete outcome is ambiguous, do not assume success and do not retry automatically. Re-read the exact target when possible, explain the uncertainty, and require a new confirmation before any further mutation.
