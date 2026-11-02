---
name: softsync-workspace
description: "Run the workspace itself: who is in it and what they may do, its name, country and currency, and ready-made add-ons such as a service desk. Use when the user wants to invite or remove a teammate, change a role, or install an add-on."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Workspace

## People
- `list_workspace_members`: everyone with their role — Admin, Editor or Viewer.
- `manage_workspace` with action `add_member`: invite by email. They get an invitation and a seat is used.
- Action `update_member_role`: change what someone may do. The last admin cannot step down.
- Action `remove_member`: take someone out of the workspace and all its groups. Their records stay. Admins can remove anyone; others only themselves.

## Settings
`manage_workspace` with action `update`: the name, country, currency or language. Send only what changes.

## Add-ons
1. `add_ons` with action `list`: the ready-made add-ons, what each adds, and whether it is installed or has an update.
2. `add_ons` with action `preview`: what installing would add, and any clash with fields the team already has. Show this to the user.
3. `manage_add_ons` with action `install`: install or update for the whole workspace. It only adds what is missing and never changes what the team already has.
4. `manage_add_ons` with action `uninstall`: hides the add-on's groups from everyone. Records are kept, and installing again brings the groups back.

## Rules
- People, settings and add-ons need the Admin role.
- Inviting uses a paid seat and emails a real person. Confirm the address and the role first.
- Everything here affects the whole team. Say so before changing it.
