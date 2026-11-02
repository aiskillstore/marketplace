---
name: softsync-shared-inbox
description: "Work a shared team mailbox such as support@: see which customer emails are waiting, who has which, hand them out, and mark them done. Use when the user asks \"what is unassigned in support?\", \"give the Acme email to Anna\" or \"close the ones I answered\"."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Shared inbox

Each customer conversation in a shared mailbox is a normal task record in the group chosen for that mailbox. The task is the single place for who has it and whether it is done; there is no separate inbox assignment.

## How a conversation maps to its task
- `ticket_id` is the task's ticket number (e.g. `TICK-000042`). The app gives it on create; never send it. Search by it to find a ticket the user names.
- `contacts` and `customers` link the customer's contact and company when known. A brand-new customer is linked once the team replies.
- The task's `email_thread` field is `<mailboxId>:<conversationId>`: the mailbox (integration) id and the id of the email that started the conversation. `get_message_by_id` shows it: a reply has a `thread_reply` relation whose `messageId` is that first email; an email without one started its own conversation.
- `owner` is who handles it (empty = unassigned). `status` says whether it is done: `completed` or `cancelled` is done, anything else is open.
- The task is in the group chosen for the mailbox when tasks were set up. Look the group up with `describe_workspace_schema`.

## Common requests
- **Unassigned**: `search_records` on tasks in the mailbox's group where `owner` is empty and `status` is neither `completed` nor `cancelled`. The inbox's Unassigned view also lists conversations that have no task yet, such as mail from before tasks were set up; those only show up in `query_messages`.
- **Mine**: the same, with `owner` equal to `@me` (the person asking).
- **Give it to someone**: `update_record` the task's `owner`. **Done**: set `status` to `completed`. **Open again**: set it to `not_started`.
- **Read the emails**: `query_messages` for the mailbox and time window, then `get_message_by_id` for the full text. A task's `email_thread` names the mailbox and the conversation's first email.
- **A conversation with no task** (older mail, or one nobody made a task for): build its `email_thread` from the email, check with `search_records` that no task has it, then `record_creation` a task in the mailbox's group with the subject as `title` and that `email_thread`. A task you create is yours; clear `owner` with `update_record` if it should wait for the team.

## Rules
- New tasks come from the "Turn customer emails into tasks" automation, set up once in the app. It only covers mail that arrives after it was set up; older conversations stay without a task until someone assigns, closes or creates one. If the mailbox has no tasks at all, tell the user to set it up from the shared inbox.
- Reading the mail needs access to the mailbox; seeing the task needs membership of the mailbox's group. These are separate, so say which one is missing when something is not visible.
- Confirm before handing out or closing many tasks at once.

## Reading and replying in the inbox
- `inbox` with action `mailboxes`: the shared inboxes you can work, with unread, waiting and yours counts.
- `inbox` with action `list` for one inbox's conversations, newest first, then action `get` for the whole thread.
- `manage_inbox` with action `mark`: read or unread, for you only.
- `manage_inbox` with action `reply`: answer as the shared mailbox in the same thread — an email for email, a text for texts. Pass a client reference of your own so a retry never sends twice.
- `inbox` with action `channels`: which kinds of messages the workspace keeps and the connections texts can go out through.
- A reply reaches the customer and cannot be recalled. Show the text and wait for a clear yes.
