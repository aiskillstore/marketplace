# Clerk CLI - Recipes

Copy-pasteable patterns for common tasks. Treat these as starting points; confirm exact paths and parameters with `clerk api ls <keyword>` and `clerk <command> --help`, since the Clerk API evolves.

## Discovery first

```sh
clerk api ls                  # everything Backend API exposes
clerk api ls users            # filter by keyword
clerk api ls --platform       # Platform API (account-level)
```

The bundled catalog is cached locally for 1 hour. There is no force-refresh flag - once the TTL expires the next `clerk api ls` re-fetches automatically; on fetch failure the CLI falls back to the stale cache and prints a warning.

## Users

```sh
# List users (preferred; curated flags). --limit defaults to 100 (max 250).
# JSON output is `{ data: [...], hasMore }` so callers can paginate without /users/count.
clerk users list
clerk users list --limit 50 --offset 0 --order-by -created_at

# Count users (no curated subcommand; use the raw API)
clerk api /users/count

# Fetch a user (no curated subcommand; use the raw API)
clerk api /users/user_abc123

# Search by email
clerk users list --email-address alice@example.com

# Open a user's profile in the dashboard
clerk users open user_abc123
clerk users open user_abc123 --print     # print the URL instead of opening

# Create a user (preferred; curated flags)
clerk users create \
  --email alice@example.com \
  --password 'SuperSecret123!' \
  --first-name Alice \
  --last-name Doe \
  --yes

# Equivalent raw BAPI call. Use only when curated flags don't cover a field.
clerk api /users -d '{
  "email_address": ["alice@example.com"],
  "password": "SuperSecret123!",
  "first_name": "Alice",
  "last_name": "Doe"
}'

# Update (PATCH merges)
clerk api /users/user_abc123 -X PATCH -d '{"first_name":"Alicia"}'

# Ban / unban
clerk api /users/user_abc123/ban -X POST
clerk api /users/user_abc123/unban -X POST

# Lock / unlock
clerk api /users/user_abc123/lock -X POST
clerk api /users/user_abc123/unlock -X POST

# Delete (PREVIEW FIRST)
clerk api /users/user_abc123 -X DELETE --dry-run
clerk api /users/user_abc123 -X DELETE --yes
```

### Test users (development only)

For test accounts you need to sign into without real email or SMS delivery, Clerk provides two magic patterns that both verify with the fixed OTP `424242`. Use them on development instances; production rejects them.

**By email.** Any address with the `+clerk_test` subaddress is recognized as a test email. The domain portion is arbitrary.

```sh
# Create a test user with a test email (dev instance)
# `skip_password_checks` isn't a curated flag, so pass the body via `-d`.
clerk users create -d '{
  "email_address": ["demo+clerk_test@example.com"],
  "password": "TestPass123!",
  "skip_password_checks": true
}' --yes
```

**By phone.** Any US fictional phone number in the `+1 (XXX) 555-0100` through `+1 (XXX) 555-0199` range is recognized as a test phone. Pass the E.164 form.

```sh
# Create a test user with a test phone (dev instance)
clerk users create -d '{
  "phone_number": ["+12015550100"],
  "password": "TestPass123!",
  "skip_password_checks": true
}' --yes
```

When signing in as either user in a browser or Playwright, enter `424242` at the OTP prompt.

These patterns only apply to development instances. In production, Device Trust blocks sign-in regardless of suffix or number, and using real-looking test addresses is highly discouraged. Test addresses and numbers do not count against the dev-instance monthly caps (20 SMS, 100 emails). See [Clerk's test emails and phones reference](https://clerk.com/docs/guides/development/testing/test-emails-and-phones) for the full contract.

## Organizations

```sh
# List
clerk api /organizations
clerk api '/organizations?limit=20&query=acme'

# Fetch
clerk api /organizations/org_abc123

# Create
clerk api /organizations -d '{"name":"Acme","created_by":"user_abc123"}'

# Update
clerk api /organizations/org_abc123 -X PATCH -d '{"name":"Acme Inc."}'

# Members
clerk api /organizations/org_abc123/memberships
clerk api /organizations/org_abc123/memberships -d '{"user_id":"user_xyz","role":"org:member"}'
clerk api /organizations/org_abc123/memberships/user_xyz -X PATCH -d '{"role":"org:admin"}'
clerk api /organizations/org_abc123/memberships/user_xyz -X DELETE --dry-run

# Invitations
clerk api /organizations/org_abc123/invitations -d '{"email_address":"new@acme.com","role":"org:member"}'
```

If organization endpoints return `organization_not_enabled_in_instance`, enable the feature first with the dedicated toggle:

```sh
# Inspect org settings
clerk api /instance/organization_settings

# Preview, then enable organizations for this instance
clerk enable orgs --dry-run
clerk enable orgs --yes
```

For org settings the toggle flags don't cover, fall back to `clerk config patch --json '{"organization_settings":{...}}'`. Deeper org workflows (roles, memberships, components) live in the `clerk-orgs` skill.

## Sessions

```sh
# List active sessions for a user
clerk api '/sessions?user_id=user_abc123&status=active'

# Revoke a session
clerk api /sessions/sess_abc123/revoke -X POST
```

## Impersonation (sign in as a user)

Impersonation goes through `clerk impersonate` (alias `imp`): it creates an actor token stamped `cli:<your-email>` so every impersonation session is traceable. Requires `clerk auth login`.

```sh
# Print the sign-in URL for a user (agent-safe: no browser, no prompt)
clerk imp user_abc123 --print

# Resolve by exact email instead of user ID
clerk imp alice@example.com --print

# Short-lived token, no confirmation prompt
clerk imp user_abc123 --yes --expires-in 900

# Revoke a pending actor token (the id is printed at creation - capture it then)
clerk imp revoke act_abc123
```

To mint a one-time **sign-in token** instead - for building custom token sign-in flows, signing in *as* the user with no actor audit trail - use the raw API:

```sh
clerk api /sign_in_tokens -d '{"user_id":"user_abc123"}'
```

## Invitations (top-level, not org-scoped)

```sh
clerk api /invitations
clerk api /invitations -d '{"email_address":"new@example.com","redirect_url":"https://example.com/welcome"}'
clerk api /invitations/inv_abc123/revoke -X POST
```

## JWT templates

```sh
clerk api /jwt_templates
clerk api /jwt_templates/jtmp_abc123
clerk api /jwt_templates -d '{
  "name": "supabase",
  "claims": {"aud": "authenticated", "role": "authenticated"},
  "lifetime": 60
}'
```

## Webhooks (local testing)

`listen` talks only to the Svix relay and `verify` is pure local HMAC - neither needs auth or a linked project.

```sh
# 1. Mint a token and open a pinned tunnel that forwards deliveries to your handler.
#    The command prints a relay inbox URL (https://webhooks.clerk.com/in/c_.../).
clerk webhooks listen --token "$(clerk webhooks token)" --forward-to http://localhost:3000/api/webhooks

# 2. Add that relay URL as a webhook endpoint in the Clerk Dashboard.
#    Real events now stream to your terminal and forward to your local handler.
#    svix-* headers are preserved, so verifyWebhook() in your handler still
#    verifies against that endpoint's signing secret.

# 3. Capture events for replay/verification (agent mode emits NDJSON automatically)
clerk webhooks listen --forward-to http://localhost:3000/api/webhooks --json > events.ndjson

# 4. Verify a saved delivery offline against the endpoint's signing secret
clerk webhooks verify --secret whsec_... --delivery @event.json
```

Pin the token (`--token`) whenever you want the inbox URL to survive across machines and restarts - otherwise the relay URL can change and the Dashboard endpoint needs re-pointing.

## Instance configuration

Prefer the dedicated `config` commands over raw `api` calls - they handle confirmation, dry-run, and formatting.

```sh
# Pull the current dev config
clerk config pull
clerk config pull --output config.dev.json

# Pull production
clerk config pull --instance prod --output config.prod.json

# Look at the schema to know what's available
clerk config schema --keys session sign_in social

# PATCH: surgical updates
clerk config patch --json '{"session":{"lifetime":3600}}' --dry-run
clerk config patch --json '{"session":{"lifetime":3600}}' --yes

# PUT: replace everything (destructive - always --dry-run first)
clerk config put --file config.prod.json --dry-run
clerk config put --file config.prod.json --instance prod --yes
```

## Environment variables

```sh
# Pull dev keys into .env.local (auto-detects framework and key names)
clerk env pull

# Pull production keys
clerk env pull --instance prod

# Target a specific file
clerk env pull --file .env
```

`env pull` merges into the existing file: existing Clerk keys are updated in place; new ones are appended under a `# Clerk` header; everything else is preserved.

## Applications (Platform API)

```sh
# List your apps
clerk apps list
clerk apps list --json

# Fetch one (raw API)
clerk api /v1/platform/applications/app_abc123 --platform
```

## Scripting patterns

### Save large responses to a file before reading them

`users list`, `apps list`, `config pull`, and most `clerk api` GETs can return responses ranging from kilobytes to megabytes. Reading the full payload into an LLM-driven session burns context for no benefit. Persist the response, then query just the slice you need:

```sh
# Persist once, query as many times as you need.
clerk users list --json --limit 250 > /tmp/users.json

jq '.data | length'                   /tmp/users.json   # count rows on the page
jq '.hasMore'                         /tmp/users.json   # any more pages?
jq '.data[0] | keys'                  /tmp/users.json   # learn the shape of one record
jq '.data[] | {id, email_addresses}'  /tmp/users.json   # project to relevant fields only
```

If `jq` is not on `PATH`, fall back to Python or Node, which most environments have:

```sh
python3 -c 'import json; d=json.load(open("/tmp/users.json")); print(len(d["data"]), d["hasMore"])'
node    -e 'const d=require("/tmp/users.json"); console.log(d.data.length, d.hasMore)'
```

Only `cat`/`head` the file when you genuinely need the raw structure for one-off debugging.

### Pipe to `jq`

For small responses (or one-shot lookups), inline piping to `jq` is fine:

```sh
# Get a list of user IDs from the current page (the page envelope is `{ data, hasMore }`)
clerk users list --json | jq -r '.data[] | .id'

# Count banned users on the current page
clerk users list --json | jq '[.data[] | select(.banned)] | length'

# Walk every page until hasMore is false. Save each page to its own file so you
# can inspect them independently without re-fetching.
offset=0
while :; do
  page="/tmp/users-${offset}.json"
  clerk users list --json --limit 250 --offset "$offset" > "$page"
  jq -r '.data[] | .id' "$page"
  [ "$(jq -r '.hasMore' "$page")" = "true" ] || break
  offset=$((offset + 250))
done
```

### Read body from stdin

```sh
echo '{"first_name":"Bob"}' | clerk api /users/user_abc123 -X PATCH
jq -n '{email_address:["c@d.co"]}' | clerk api /users
```

### Loop safely

```sh
# Always --dry-run first across the whole set. `users list` paginates;
# bump --limit (max 250) and walk pages with --offset until .hasMore is false.
for id in $(clerk users list --json --limit 250 | jq -r '.data[] | .id'); do
  clerk api /users/$id -X PATCH -d '{"public_metadata":{"migrated":true}}' --dry-run
done
# Re-run without --dry-run once the previews look right
```

### Target multiple instances

```sh
# Copy config from dev to staging for review
clerk config pull --instance dev --output /tmp/dev-config.json
clerk config patch --instance ins_staging --file /tmp/dev-config.json --dry-run
```

## When in doubt

```sh
clerk api ls <keyword>        # find the right endpoint
clerk <command> --help        # authoritative flag list
clerk doctor --json           # health check
```
