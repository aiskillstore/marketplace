---
name: softsync-notes
description: "Write, edit, share and delete notes on records, such as a summary after a call. Use when the user wants to write something down on a company, person or deal."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Notes

Notes are written by people in the workspace and appear on the timelines of the records they are attached to.

## Tools
`manage_notes`, with one of these actions:
- `create`: write a note in markdown. Attach it to records so it shows on their timelines, and make it private if only the author should see it.
- `edit`: replace a note's text. Only the author can edit.
- `switch_visibility`: move a note between private and shared with the workspace.
- `delete`: remove a note. Only the author can delete.

## Rules
- Find existing notes with the messages skill: notes are messages from the notes source.
- Attach a note to the company, contact or deal it is about, looking the record up first.
- Keep to what the user said. Do not add facts that were not provided.
