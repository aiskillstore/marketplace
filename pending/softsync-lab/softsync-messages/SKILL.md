---
name: softsync-messages
description: "Read emails, notes and saved meeting summaries linked to records, search them by content, answer from the workspace's own help articles, and send a text. Use when the user asks what was said, agreed or sent — \"what did Acme reply?\", \"summarise our last call\" — asks a how-to or policy question, or wants to text someone."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Messages

Messages are everything the workspace has received or written about its records: synced emails, notes and notifications.

## Which tool
- **About a company or person** ("last week's emails with Acme"): resolve them to record ids, then `query_messages` with those ids and a time window. See the `finding-messages` reference for the exact sequence.
- **By topic, with no company or person named** ("emails about the renewal"): `semantic_search_messages`. Never use it as a fallback when `query_messages` finds nothing for a company or person — similar text is not proof it is about them.
- **Full text of one message**: `get_message_by_id` after finding it.
- **Calendar events** ("my meetings this week", "when did we last meet Acme?"): use `calendar_events` (action `list`) from the meetings skill, not `query_messages`.
- **Meeting summaries**: a summary someone saved to a record is a note on that record. Find it with `query_messages` on the record. Recordings that were never saved to a record stay in the desktop app and cannot be reached from here.
- **How many** ("how many emails have we exchanged with Acme?"): `get_message_statistics` counts messages linked to a record or person.
- **How-to and policy questions** ("what is our refund policy?", "how do I reset the router?"): `search_knowledge` finds the passages in the workspace's own articles and guides. Quote them and name the source; do not answer from memory. When drafting a reply to a customer, set `audience` to `public` so only what the help center already shows customers is used.

## Sending a text
- `send_message` sends a text (SMS) to a contact (`toRecordId`) or a phone number (`to`). It shows on the contact's timeline like an email.
- To answer a text conversation in a shared inbox, reply there instead (shared inbox skill), so the answer stays in the same thread.
- A text reaches a real phone and cannot be recalled. Show the exact text and recipient and wait for a clear yes. Pass a `clientRef` of your own so a retry never sends twice.
- People who replied STOP are skipped; say so if the result reports it rather than claiming it was sent.

## Rules
- Resolve a company or person to its record id first (see the records skill), then filter messages by that id.
- You only see messages linked to records you can access. Say so if something the user expects is missing, rather than claiming it does not exist.
- Never guess a message id.

## More detail
Read these when the task needs them:
- [finding-messages](references/finding-messages.md): The required call sequence for "what did we discuss with Acme?" and when topic search is the wrong tool.
- [resolving-records](references/resolving-records.md): Turning a company or person into every linked record id before reading their messages or acting on them.
