---
name: softsync-connections
description: "See which outside apps and accounts are connected, whether each one works yet, who may use it, and run actions in them such as looking up an invoice. Use when something \"is not connected\", a connection waits for approval, or the user wants to share or disconnect one."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Connections

A connection is an outside app or account linked to the workspace, such as an accounting system or a mailbox. Connecting one needs a sign-in in the app; everything after that can be done here.

## Is it working?
- `connections` with action `list`: the connections you can use — your own, ones teammates opened to you, and ones for the whole workspace. Each says whether it works: active, pending (waiting for an approval) or incomplete (setup left part-way).
- Action `check`: ask the outside app again whether your pending connection was approved.
- Action `progress`: the setup steps, how far yours got and what comes next.
- Only active connections can be used. Tell the user what is missing rather than trying anyway.

## Who may use it
`connections` with action `access` shows it and `manage_connections` with action `set_access` changes it: only the person who connected it, selected teammates, or the whole workspace. Only the person who connected it may change this, and opening it to everyone lets every member use that account.

## Actions in connected apps
`connections` with action `actions` shows what you can do and the details each needs; `manage_connections` with action `run_action` runs one. Actions that change something in the outside app wait for a person to approve them in the app first.

## Disconnecting
Call `connections` with action `disconnect_impact` first and tell the user which workflows would stop. `manage_connections` with action `disconnect` cannot be undone; connecting again makes a new connection.
