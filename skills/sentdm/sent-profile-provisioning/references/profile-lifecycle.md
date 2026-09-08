# Sender Profile lifecycle reference

## Table of contents

- [Operation catalog](#operation-catalog)
- [Create field reference](#create-field-reference)
- [Update-only fields](#update-only-fields)
- [Inheritance and sharing matrix](#inheritance-and-sharing-matrix)
- [Billing configuration](#billing-configuration)
- [WhatsApp attachment paths](#whatsapp-attachment-paths)
- [Completion flow and callback](#completion-flow-and-callback)
- [Status vocabulary by surface](#status-vocabulary-by-surface)
- [Error catalog for provisioning](#error-catalog-for-provisioning)
- [Idempotency and sandbox](#idempotency-and-sandbox)
- [Offboarding](#offboarding)

## Operation catalog

Ten operations cover profiles and their campaigns. None is available through MCP, so provisioning is REST-only.

| Operation | Purpose |
| --- | --- |
| `POST /v3/profiles` | Create a profile |
| `GET /v3/profiles` | List profiles |
| `GET /v3/profiles/{profileId}` | Read one profile, including current status |
| `PATCH /v3/profiles/{profileId}` | Update configuration and number references |
| `DELETE /v3/profiles/{profileId}` | Remove a profile |
| `POST /v3/profiles/{profileId}/complete` | Start completion; requires `webHookUrl` |
| `GET /v3/profiles/{profileId}/campaigns` | List campaigns |
| `POST /v3/profiles/{profileId}/campaigns` | Create a campaign |
| `PUT /v3/profiles/{profileId}/campaigns/{campaignId}` | Update a campaign |
| `DELETE /v3/profiles/{profileId}/campaigns/{campaignId}` | Delete a campaign |

Creation requires an organization API key whose owning email holds `admin`. An organization key may target a child with `x-profile-id`; a profile-scoped key sending that header receives `403`, and a profile outside the organization returns `404`.

## Create field reference

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `name` | string | — | The only required field |
| `icon` | string | — | Display asset |
| `description` | string | — | Free text |
| `short_name` | string | — | 3–11 chars, letters, numbers, spaces, at least one letter |
| `allow_contact_sharing` | boolean | `false` | Exposes this profile's contacts outward |
| `allow_template_sharing` | boolean | `false` | Exposes this profile's templates outward |
| `inherit_contacts` | boolean | `true` | Consumes the organization's contacts |
| `inherit_templates` | boolean | `true` | Consumes the organization's templates |
| `inherit_tcr_brand` | boolean | `true` | Uses the organization's brand; forbids a `brand` object |
| `inherit_tcr_campaign` | boolean | `true` | Inherited campaigns are read-only for this profile |
| `billing_model` | enum | `profile` | `profile`, `organization`, or `profile_and_organization` |
| `billing_contact` | object | — | `name`, `email`, `phone`, `address`; required when the model includes `profile` and none exists |
| `whatsapp_business_account` | object | — | `waba_id` and `access_token` required, `phone_number_id` optional |
| `brand` | object | — | `contact` and `compliance` required, `business` optional; forbidden when `inherit_tcr_brand` is true |
| `payment_details` | object | — | `card_number`, `expiry`, `cvc`, `zip_code`; only for models including `profile` |
| `sandbox` | boolean | `false` | Simulate without side effects |

`payment_details` is ephemeral and forwarded to the payment processor. Never log it, never echo it back to a user, never store it, and never place it in a file that could be committed.

Although creation requires only `name`, completion also requires `short_name`, `description`, profile KYC information, and any required campaign or channel setup. A profile inheriting the organization's TCR brand cannot include a `brand` object in the API request but still needs profile-level KYC submitted through the dashboard before completion.

## Update-only fields

`PATCH /v3/profiles/{profileId}` accepts the create fields plus number references:

- `sending_phone_number_profile_id`
- `sending_whatsapp_number_profile_id`
- `sending_phone_number`
- `whatsapp_phone_number`
- `allow_number_change_during_onboarding`

Model reference identifiers separately from literal numbers, and guard against cycles when one profile's sending number points at another profile that points back.

## Inheritance and sharing matrix

Inheritance pulls resources in; sharing pushes them out. They are independent.

| Configuration | Result |
| --- | --- |
| `inherit_contacts: true`, `allow_contact_sharing: false` | Reads organization contacts; does not expose its own |
| `inherit_contacts: false`, `allow_contact_sharing: true` | Isolated contact store that other profiles may read |
| `inherit_tcr_brand: true`, `inherit_tcr_campaign: true` | Fully inherited compliance posture; campaigns read-only here |
| `inherit_tcr_brand: true`, `inherit_tcr_campaign: false` | Shared legal identity with per-tenant use cases — the common multi-tenant pattern |
| `inherit_tcr_brand: false` | Dedicated brand supplied in the same create request |

For tenant isolation, set `inherit_contacts` and `inherit_templates` to false explicitly, because both default to true and a silently inherited store means one tenant can read another's data model.

## Billing configuration

| Model | Meaning | Requires |
| --- | --- | --- |
| `profile` | The profile pays | `billing_contact`, optionally `payment_details` |
| `organization` | The organization pays | Nothing profile-side |
| `profile_and_organization` | Profile first with organization fallback | `billing_contact` |

Effective balance follows this configuration, so a balance reading for a profile with `organization` billing reflects the organization's funds. Confirm which model a profile uses before interpreting a balance or diagnosing a `BLOCKED` message.

## WhatsApp attachment paths

| Path | How | When |
| --- | --- | --- |
| Organization Embedded Signup | Sent Dashboard only; no public endpoint exists | The organization owns one WABA used across profiles |
| Child inheritance | Omit `whatsapp_business_account` | Tenants share the organization's WABA |
| Dedicated credentials | `whatsapp_business_account` with `waba_id` and `access_token` | The tenant owns its own WABA |

Requesting inheritance when the organization has no WABA configured returns `422 VALIDATION_001`. Do not invent a hybrid, and do not describe the create payload as an Embedded Signup endpoint.

## Completion flow and callback

```json
{
  "webHookUrl": "https://provisioning.example.com/callbacks/profile-complete",
  "sandbox": false
}
```

Responses: `202` means processing started and contains no final status; `200` means the profile was already complete and the body carries a status.

The callback body is `{profileId, success, status, timestamp}`, documented with `COMPLETED`, `SUBMITTED`, and `failed`. It is delivered **once, with no retry**, which drives three requirements: the receiver must be reachable before the completion call, the receiver must be idempotent on `profileId`, and a reconciliation job must poll `GET /v3/profiles/{profileId}` for profiles that have been awaiting completion beyond a timeout.

Note that this callback is not part of the `/v3/webhooks` subscription system and is not documented as carrying the `x-webhook-signature` scheme. Give each provisioning record a unique, hard-to-guess callback path, treat its payload as untrusted input, verify `profileId` against the record you created, and never take action on an unrecognized identifier. Polling the profile remains the recovery and reconciliation authority.

## Status vocabulary by surface

| Surface | Observed values |
| --- | --- |
| Create response | lowercase `incomplete` |
| Completion `200` | lowercase `completed` |
| Completion callback | `COMPLETED`, `SUBMITTED`, `failed` |
| `GET /v3/profiles/{profileId}` guide | `approved`, `submitted`, `processing`, `failed` |
| REST guides versus OpenAPI | Publish different status sets |

Handle this by comparing case-insensitively, preserving unknown strings verbatim, recording which surface produced the value, and never switch-casing over an assumed closed enum. A provisioning state machine should treat any unrecognized status as "needs human review" rather than as an error.

## Error catalog for provisioning

| Status | Code | Meaning |
| --- | --- | --- |
| 400 | `VALIDATION_001` | Invalid payload, including a `brand` object alongside `inherit_tcr_brand: true` |
| 400 | `VALIDATION_001` | Cannot create campaigns when `inherit_tcr_campaign` is true, or the campaigns are read-only |
| 403 | `AUTH_004` | Profile key attempted `x-profile-id`, or insufficient role |
| 404 | `RESOURCE_005` | Organization not found |
| 404 | `RESOURCE_014` | Profile not found |
| 404 | `RESOURCE_009` | Brand not found for the profile |
| 404 | `RESOURCE_010` | Campaign not found |
| 422 | `VALIDATION_001` | Organization has no WABA configured |

The response envelope carries `error.code`, `error.message`, `error.details`, and `error.doc_url`, plus `meta.request_id`. Log `request_id` for every provisioning call; it is the correlation handle for support.

## Idempotency and sandbox

`Idempotency-Key` is honored on POST, PUT, and PATCH with a value of 1 to 255 characters from `[A-Za-z0-9_-]`. Successful responses are cached 24 hours per key per customer, replays return the cached body with `Idempotent-Replayed: true` and `X-Original-Request-Id`, a duplicate arriving while the original is in flight waits up to five seconds and then fails `409 CONFLICT_001`, and if the idempotency store is unavailable the API returns `503 SERVICE_001` rather than risk a double execution. Use a deterministic key derived from your own provisioning record so a retry after a network timeout cannot create a second profile.

`"sandbox": true` authenticates and validates without persisting, queueing, calling providers, deducting balance, or looking up resources. Use it to prove a payload shape in CI. A successful sandbox mutation is itself cached by idempotency, so use a distinct key for the later live mutation or the live call will replay the sandbox response. Sandbox does not protect deletions in the webhook API, so never rely on it as a general dry-run guard.

## Offboarding

Deprovisioning a tenant is an ordered, evidence-preserving sequence rather than a single delete:

1. Stop new sends at the application layer.
2. Disable or delete the tenant's API keys in the dashboard.
3. Remove or downgrade the tenant's users, keeping at least one admin on the organization.
4. Disable webhook registrations that pointed at tenant infrastructure.
5. Detach shared resources deliberately, checking whether other profiles inherit from them.
6. Retain delivery and consent records for the applicable retention period before deleting the profile.
7. Record the `request_id` and timestamp of each step as the audit trail.

Contact deletion dissociates the contact from the calling customer while shared contact, capability, and delivery records persist, so deletion is not an erasure mechanism.
