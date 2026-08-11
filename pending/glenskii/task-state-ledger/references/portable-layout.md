# Portable Layout

Use `.task-state/` as the default local directory because it is readable, predictable, and independent of a specific client. A project may use another approved local state directory when that convention already exists.

Keep the same two-part structure:

```text
state-directory/
├── task-state.md
└── evidence/
```

Use relative evidence references in `task-state.md`. A relative path remains useful when a project moves between machines or compatible tools. Avoid absolute paths, home-directory shortcuts, and links that require a specific operating system or application.

Do not assume a client will automatically load the state file. Read it intentionally at the start of a resumed task and verify that it belongs to the current project.
