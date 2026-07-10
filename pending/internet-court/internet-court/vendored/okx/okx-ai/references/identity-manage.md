# Manage — activate · deactivate

Loaded when: user wants to publish (activate) or unpublish (deactivate) an agent `#N`.

These are pure state toggles. Per SKILL §Gates Confirm, toggles are **card-exempt** — run the
CLI directly, no confirmation card, no field-table. Per SKILL §Gates No-poll, never chase a
successful toggle with `agent get-agents`. Resolve
`#<id>` per the SKILL §Invariants #id ladder.

## deactivate

Run directly with the user's `#N`. Read only `success`.

```bash
# internal — not shown to the user
onchainos agent deactivate --agent-id <N>
```

- `success: true` → emit exactly ONE line (not a menu):
  `Unpublished — hidden from client lists. Say 'activate #<id>' to re-publish.`
  Do not re-query. Then run the communication-init flow in [`chat-comm-init.md`](chat-comm-init.md) to sync the agent-list change (deactivate has no CLI-level readiness gate).
- `success: false` / `code != 0` → load `identity-errors.md`.

## activate

```bash
# internal — not shown to the user
onchainos agent activate --agent-id <N> --preferred-language <BCP-47>
```

### Response — match in order

| Response shape | Action |
|---|---|
| `blockType: 1` + `agentRole` | Hard stop — not an ASP. Emit (localized): agent #`<N>` is a `<roleLabel>`; only ASP identities support listing. |
| `activate` + `submitApproval` | Submitted for review. |
| `activate.success: true` | Published. |
| `activate.approvalStatus: 2` | Already under review. Stop, no poll. |
| `activate.success: false` (other) | Load `identity-errors.md`. |
