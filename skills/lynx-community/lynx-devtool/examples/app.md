# Send App Command

Send an App-level command.

```bash
agent-lynx app -m <method> [options] [params]
```

- `-m, --method <method>`: The App method name (e.g., `App.openPage`).
- `-c, --client <clientId>`: (Optional) Client ID.
- `[params]`: (Optional) JSON string of parameters.

> You **MUST** read [Supported App Methods](../references/app/index.md) before sending an App command.
