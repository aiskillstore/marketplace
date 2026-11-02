---
name: softsync-groups-and-views
description: "Organise records into groups, share them with people, set up table, board and calendar views, and keep report dashboards. Use when the user wants a list of records, to share records with teammates, a saved way to look at them, or a chart saved for the team."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Groups and views

A group is a named area of the workspace, listed in the sidebar, holding records with its own members and access levels. People also call it a section, space, area or folder. A view is a saved way of looking at a group's records (a table, board or calendar); it holds no records itself.

## Groups
- Find groups through `describe_workspace_schema`, then `groups` with action `get` for one group and its views.
- `manage_groups` with action `create`, `update` (name, description, sharing), `duplicate` or `delete`. Renaming a group means changing its `title`; the description is a separate note under it.
- A group is either private to its members or visible to the whole workspace.

## People in a group
- `groups` with action `members` lists them. `manage_groups` with action `add_member`, `update_member_role` or `remove_member` changes them.
- Roles: Owner (full control), Admin (manage people and views), Editor (change records), Viewer (read only).
- Someone added by email who is not yet in the workspace joins as a guest.

## Views
- `views` with action `list` or `get` to read them; `manage_views` with action `create`, `update` or `delete` to change them.
- Four kinds: table, kanban board, calendar and timeline (a Gantt chart).
- A board needs a choice field to make its columns; a calendar needs a date field; a timeline needs a start date and can take an end date and a "waits on" link to the same object.
- Views refer to fields by id. Take them from `describe_workspace_schema`.

## Report dashboards
- A group's reports are dashboards of charts the whole group sees. `list_dashboards` shows them and each chart's position.
- `manage_dashboards` with action `create`, `update` (rename) or `delete` changes a dashboard; `add_chart`, `update_chart` or `remove_chart` changes one chart, by its position. Group editors may change charts; renaming or deleting a dashboard needs a group owner or admin.
- A chart takes the same definition as `generate_analytics`, forecasts and past snapshots included. Try it there first; a chart that cannot be drawn is refused with the reason.

## Rules
- Check for an existing group before creating a new one.
- Adding someone gives them access to everything in the group. Confirm the person and the role first.
