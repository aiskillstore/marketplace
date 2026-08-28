# Tunneling local or private applications

Use this when Mo needs access to a local or private service that is unavailable
on the public internet, such as a local development build.

## Start a tunnel

Expose only the required `hostname:port` addresses:

```bash
tunnel_json=$(mo tunnel start localhost:3000)
tunnel_id=$(jq -r .tunnelId <<<"$tunnel_json")
```

Pass multiple addresses only when the tested flow needs them:

```bash
mo tunnel start localhost:3000 api.internal:8080
```

Tunnels run in the background by default. Use `--foreground` only when the
current terminal should own the tunnel process.

## Start Mo with tunnel access

Keep the exact local or private URL in the QA brief, then pass the tunnel ID
when creating the session:

```bash
session_json=$(mo start "$brief" --tunnel "$tunnel_id")
```

## Revoke access

```bash
mo tunnel list
mo tunnel stop "$tunnel_id"
```

Always stop a tunnel after its last session. If setup fails, do not expose more
addresses, deploy the application, or share credentials without user direction.
