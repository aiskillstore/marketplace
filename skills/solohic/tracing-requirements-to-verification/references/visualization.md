# Optional Local Trace View

Conversation remains the primary RVTF interface. The local view is a read-only
aid for inspecting one recorded trace; it does not create work, approve a
decision, update a trace, or replace an explanation in the conversation.

## When to use it

Start a view only when the user clearly asks to see the trace or its visual
progress. If relationships are hard to explain, a single short suggestion is
fine; do not open a page automatically. If the user declines, continue in
conversation and do not re-offer it for each trace update.

Resolve the trace from the current task's explicit records. If more than one
candidate path remains, explain the choices and ask the user; do not search for
an unrelated trace. Reuse an active, reachable URL already started for the same
task rather than discovering services across the system. Keep the process handle
for an instance you start, so a later close request stops only that instance.

## Start and return

First check that the selected CLI supports `rvtf view --help`. If it is absent,
too old, or its loopback URL cannot be reached from the user's environment,
briefly explain that limitation and continue the task in conversation. Do not
install or upgrade a CLI without authorization, and do not weaken any existing
host validation gate.

For a supported CLI, run:

```bash
rvtf view TRACE [--port PORT] [--no-open] [--block N]
```

Node.js 20.19.0 or newer is required. The server binds to `127.0.0.1` and uses
an available port unless `--port` is supplied. Confirm the resulting local URL,
then return to the conversation with a concise summary of what the read-only
view shows. Copy any useful detail back into the conversation rather than
leaving the user with a link alone.

`TRACE` may be a `.yaml`/`.yml` file, or a `.md`/`.markdown` file with a
top-level YAML/YML fenced block. One Markdown candidate is selected
automatically; multiple candidates require an explicit one-based `--block`.
This extraction is only for `view`: `rvtf validate` remains YAML-only.

Invalid command arguments end with status `2`. A source or data error remains
visible in the page and does not end the running viewer; a normally started
viewer exits `0` when closed. Treat displayed contents as recorded trace truth,
not Agent telemetry or a completion decision.
