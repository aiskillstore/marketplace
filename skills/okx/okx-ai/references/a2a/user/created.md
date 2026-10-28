# Created Task Handoff

## Module Description

Use this leaf for `job_created` after `next-action` has fetched fresh task
state. The CLI-returned playbook owns designated-provider routing, session
creation, prefetch, and all current branch guards.

- Execute the returned playbook exactly once and in order.
- Localize only the user-facing notification; preserve IDs and protocol text.
- Do not recreate a group/session already created by the CLI playbook.
- Do not fall back to public provider discovery when designated-provider state
  is missing.
- A created task is confirmed only by the authoritative event, never by the
  earlier `create-task` broadcast result.
- Enter a scoped runtime watch only when the returned playbook or action asks
  for it. Keep the same `jobId` and generation.

If the playbook reports a concrete CLI/runtime failure, enter
`../../runtime/recovery.md`; never improvise a replacement provider mutation.
