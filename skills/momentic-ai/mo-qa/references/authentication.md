# Authentication

Read this after a fresh installation or when an operational command reports an
authentication error.

## Sign in

```bash
mo login
```

Use `mo login --no-browser` when the environment cannot open a browser. Login
saves the API key and server URL to `~/.momentic/auth.json`.

In CI, set `MOMENTIC_API_KEY` instead. It takes precedence over the saved login.
Treat an existing value as intentional. Only ask the user to replace or unset
it after an authentication failure or when they explicitly request it.

## Sign out

```bash
mo logout
```

This removes only the saved login. It does not unset `MOMENTIC_API_KEY`. Never
print credentials, paste them into a Mo message or target URL, or commit them.
