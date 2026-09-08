# Users, roles, and credential hygiene

## Table of contents

- [User operations](#user-operations)
- [Role model](#role-model)
- [How a role check is evaluated](#how-a-role-check-is-evaluated)
- [Invitation lifecycle](#invitation-lifecycle)
- [Guardrails on user mutations](#guardrails-on-user-mutations)
- [API key model](#api-key-model)
- [Key rotation](#key-rotation)
- [Least-privilege assignments](#least-privilege-assignments)
- [Audit evidence](#audit-evidence)

## User operations

| Operation | Required role | Body | Notes |
| --- | --- | --- | --- |
| `GET /v3/users` | `developer` or higher | — | Lists active, invited, and suspended users |
| `POST /v3/users` | `admin` | `email`, `name`, `role`, optional `sandbox` | `201` with status `invited`; `409 RESOURCE_007` if the user exists |
| `GET /v3/users/{userId}` | `developer` or higher | — | Single user detail |
| `PATCH /v3/users/{userId}` | `admin` | `role`, optional `sandbox` | Role change only |
| `DELETE /v3/users/{userId}` | `admin` | optional `sandbox` | Removes access |

All five accept `x-profile-id` on an organization key to act on a child profile. None is exposed through MCP.

The user object returns `id`, `email`, `name`, `role`, `status`, `invited_at`, `last_login_at`, `created_at`, and `updated_at`.

The roles reference documentation states that the two read operations require "any role," while the OpenAPI specification requires `developer` or higher. Follow the specification and design for `developer` as the read floor; a `billing`-only user should not be assumed able to list users.

## Role model

| Role | Assignable by API | Scope of access |
| --- | --- | --- |
| `owner` | No | The account that created the organization or profile. Implicit, absent from the user list, passes every role check |
| `admin` | Yes | Passes every role check: profile management, user management, and reads |
| `developer` | Yes | Passes any-role checks; dashboard access to development, messaging, number lookup, activities, API keys, webhooks, channels, and settings |
| `billing` | Yes | Passes any-role checks; dashboard access limited to billing |

Note the practical implication of `developer` including API keys and webhooks: a developer can create credentials and change event destinations. Treat the role as privileged even though it cannot manage users.

## How a role check is evaluated

The check resolves against the email address that owns the API key. It passes when that email is the owner email, or when an **active** user with that email exists on the organization or profile holding an allowed role. Users in `invited`, `suspended`, or `rejected` status fail every check.

For a Sender Profile, checks cascade upward: owner or role access at the organization level also grants access to the organization's profiles. A user can therefore hold different effective roles across profiles when invited separately, while an organization-level role applies everywhere beneath it.

Two operational consequences. First, an invitation that has not been accepted grants nothing, so provisioning automation must not assume access after `POST /v3/users` returns `201`. Second, revoking access at the organization level is the only way to remove cascading access; deleting a profile-level user leaves an organization-level grant intact.

## Invitation lifecycle

```text
POST /v3/users → status "invited" → email with token → user accepts → status "active"
                                  └── 7 days elapse → token expires → re-invite required
```

Inviting an email that already has access returns `409 RESOURCE_007`; read the user list first and decide between a role change and an invitation. A provisioning flow that invites tenant staff should record the invitation timestamp and re-invite after expiry rather than retrying blindly, and should verify `status == "active"` before assuming the user can act.

## Guardrails on user mutations

The API refuses to let a caller change their own role, demote the last admin, remove themselves, or remove the last admin. Rather than discovering these as validation errors, check first:

1. `GET /v3/users` and identify the target plus the count of active admins.
2. Confirm the target is not the caller's own account.
3. Confirm the change leaves at least one active admin.
4. Present the intended change and require explicit confirmation from the operator immediately before the call.
5. Record the `meta.request_id` from the response.

Role changes and removals are effectively irreversible from the target user's perspective — re-granting requires a fresh invitation and acceptance — so treat both as destructive operations that deserve a stated diff before execution.

## API key model

There are two key types. An organization key can act for a child profile by sending `x-profile-id` with the profile UUID. A profile-scoped key is confined to its own profile and receives `403 AUTH_004` if it sends `x-profile-id`.

Rate-limit exposure follows the key type: a profile key draws on its own pool, while an organization key acting through `x-profile-id` draws on the organization pool, so one noisy integration can consume quota shared by every profile.

There is **no** endpoint to list, create, or revoke API keys. Key management happens in the Sent Dashboard, where the value is masked in the table and copied with a control. Any runbook that claims to automate key creation is wrong.

Failed authentication is tracked per presented credential rather than per IP address: ten consecutive failures lock that credential with a `429` and escalating lockout windows from one minute up to sixty. A retry loop against a bad key therefore extends its own outage, so authentication failures must stop retrying immediately and alert instead.

`x-sender-id` is legacy v1 and v2 terminology. It has no role in v3 authentication or routing.

## Key rotation

1. Create a replacement key in the dashboard.
2. Update the secret store and redeploy so the new key is in use.
3. Verify with `GET /v3/me` that the new key resolves to the expected account.
4. Disable or delete the old key.

When a key is known to be compromised, invert the first steps and delete the old key immediately, accepting the brief outage. Keep separate keys per environment so rotating production never touches development, and never place a key in a browser, mobile app, or any client the organization does not control.

## Least-privilege assignments

| Workload | Credential | Role |
| --- | --- | --- |
| Server-side sends for one tenant | Profile-scoped key | `developer` |
| Provisioning new profiles | Organization key | `admin` |
| Campaign and brand registration | Organization or profile key per ownership | `admin` |
| Analytics reads | Profile-scoped key where possible | `developer` |
| Webhook management | Key matching the webhook's scope | `developer` |
| Billing review | — | `billing` |
| User administration | Organization key | `admin` |

Prefer profile-scoped keys for runtime send paths so a leak is contained to one tenant, and reserve organization keys for control-plane operations that genuinely require cross-profile reach.

## Audit evidence

Every response carries `meta.request_id` and `meta.timestamp`. Log both alongside the operation name, the acting credential identifier, and — when an organization key acted through `x-profile-id` — the target profile, since the credential alone does not reveal which tenant was affected. The Sent Dashboard's Activities section, visible to owner, admin, and developer roles, is the platform-side counterpart. Because there is no API for key inventory, maintain a written register of which key exists for which environment and workload, who owns it, and when it was last rotated.
