---
name: softsync-portals
description: "Set up small sites where customers, members or partners sign in to see and update their own records, fill a form or book a meeting. Use when the user wants a customer portal, or to change, switch off or renew the link of one."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Portals

A portal is a small site for people outside the workspace. Visitors sign in as a record (for example a contact) and see only what the portal's pages show them.

## Tools
- `portals` with action `list` or `get`: each portal, its pages and its public link (`publicUrl`) while it is on.
- `manage_portals` with action `create`: a title, a group, who signs in (`contactTableId`, or leave it out to let anyone look) and the pages. A "records" page lists records of a table: `path` is how the signed-in contact reaches them (`[]` for the contact itself), fieldIds are shown, editFieldIds the visitor may change. A "form" or "booking" page shows that form or meeting type.
- Action `update`: send only what changes. Pages, when sent, replace the whole list, so read the portal first.
- Action `new_link`: a new link; the old one, and everyone signed in through it, stops working at once.
- Action `delete`: the link stops working for everyone.

## Rules
- Portals need the Admin role.
- Take table and field ids from `describe_workspace_schema`; a page with an unknown table or field is refused with the reason.
- Confirm before switching a portal off, giving it a new link or deleting it: visitors lose access at once.
