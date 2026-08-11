# Local Brandkit state routing

Store approval state in the active project's `brandkit/state.json`. Drafts never enter it. The bundled script writes atomically and tracks independent logo, palette, typography, visual-axis, and downstream-element revisions.

Use the path variables established by `SKILL.md`:

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" state \
  --state-file "$BRANDKIT_STATE" \
  --action ACTION [--input "$BRANDKIT_WORKDIR/input.json"]
```

Create payload files as JSON under `"$BRANDKIT_WORKDIR"`. Never interpolate user text into a shell command argument. Before the first state write, load [exact state payloads](state-payloads.md) and replace values, not keys or nesting.

## Persistence

- The local state file survives turns and agent restarts. Do not export it into chat or paste it into prompts.
- Read state only through the script. Do not hand-edit revisions, origins, dependencies, or approvals.
- Store durable references: absolute local paths, confirmed URLs, upload IDs, or completed job IDs.
- If the state file is missing but the conversation claims prior approvals, stop and ask whether to restart or locate the previous project directory. Never infer approvals.
- Do not commit `brandkit/state.json` unless the user explicitly wants brand state versioned with the project.

## Call moments

### Start of every Brandkit turn

```bash
python3 "$SKILL_ROOT/scripts/brandkit.py" state \
  --state-file "$BRANDKIT_STATE" --action get_status
```

### Lock user-supplied official assets

Immediately after asset analysis, call only the matching action:

```text
lock_authoritative_logo       {"source_summary": "...", "logo": {...}}
lock_authoritative_palette    {"source_summary": "...", "palette": {...}}
lock_authoritative_typography {"source_summary": "...", "typography": {...}}
```

These actions preserve official assets. They do not approve generated drafts, and a generated choice cannot replace an authoritative slot.

### Persist visual axes

Call `set_visual_axes` with:

```json
{
  "visual_axes": {
    "restrained_expressive": 50,
    "geometric_organic": 50,
    "familiar_experimental": 50
  }
}
```

### Read only the required slot

- `get_logo` before placement, export, or logo-dependent revisions.
- `get_palette` before color-dependent work.
- `get_typography` before type-dependent work.
- `get_essential_kit` only when all three slots are genuinely required.

Never make `get_essential_kit` a universal gate for partial outputs.

### Approve generated foundation slots

After an explicit user selection:

```text
approve_logo       {"approval_summary": "...", "logo": {...}}
approve_palette    {"approval_summary": "...", "palette": {...}}
approve_typography {"approval_summary": "...", "typography": {...}}
```

A generated logo records the active palette revision. Replacing that palette removes the generated logo and invalidates logo-dependent outputs. Replacing typography does not invalidate a symbol-only logo.

### Browse and approve downstream elements

Call `list_brandbook_elements`, then `get_brandbook_element` with:

```json
{ "key": "exact-element-key" }
```

After explicit approval, call `approve_brandbook_element` with the exact slots used:

```json
{
  "approval_summary": "User approved the primary mockup.",
  "required_slots": ["logo", "palette"],
  "brandbook_element": {
    "key": "mockup-primary",
    "kind": "mockup",
    "name": "Primary packaging mockup",
    "asset": {
      "path": "/absolute/path/to/mockup.png"
    }
  }
}
```

## Never

- Never put drafts into state.
- Never delay locking a user-declared official asset.
- Never infer approval from generation success or recency.
- Never require an unrelated missing slot.
- Never use this state outside Brandkit.
- Never overwrite or clear the state file without explicit user instruction.
