---
name: waba-embedded-signup
description: Guides WhatsApp Business Account onboarding through Sent, separating dashboard Embedded Signup, organization WABA inheritance, and direct child-profile credentials. Use for WABA connection, Meta signup, profile creation, access-token handling, phone number mapping, completion callbacks, or WhatsApp onboarding failures.
---

# WABA Onboarding and Embedded Signup

Keep three integration paths distinct. Calling all of them “Embedded Signup” creates wrong API designs and unsafe credential handling.

## The three paths

| Path | Where it starts | Profile behavior |
| --- | --- | --- |
| Organization Embedded Signup | Sent dashboard | Connects the organization's WABA through the hosted Meta flow. There is no public Sent endpoint that starts this flow. |
| Organization WABA inheritance | `POST /v3/profiles` | Omit `whatsapp_business_account`; the child inherits the organization's connected WABA. |
| Dedicated child-profile WABA | `POST /v3/profiles` | Supply `whatsapp_business_account.waba_id` and `.access_token`; `phone_number_id` is optional. |

If credentials are omitted and the organization has no connected WABA, profile creation returns `422`. Direct WABA credentials are a profile-creation feature, not a public “Embedded Signup endpoint.”

## Authentication

Use either:

- a profile-specific key in `x-api-key`; or
- an organization key in `x-api-key` plus `x-profile-id` when operating for an existing child profile.

Only organization keys may use `x-profile-id`; profile keys receive `403`. `x-sender-id` is legacy v1/v2 terminology.

## Path A: organization Embedded Signup

1. An authorized organization administrator opens the Sent dashboard WhatsApp connection flow.
2. The hosted Meta Embedded Signup UI collects the Meta authorization and WABA/number choices.
3. Confirm the organization shows a connected WABA before creating inheriting children.
4. Record non-secret identifiers and audit who completed the action.

Do not invent a `POST /embedded-signup` or token-exchange endpoint in Sent's public API. If building your own Meta Tech Provider integration outside the Sent dashboard, follow Meta's current documentation and keep that system separate from the Sent API contract.

Meta's browser `postMessage` events use an `event` field and nested data/session information. Do not rewrite them as Sent webhook `sub_type` envelopes.

## Path B: inherit the organization WABA

Omit `whatsapp_business_account`:

```json
{
  "name": "Tenant Support",
  "description": "Synthetic child profile",
  "short_name": "SUPPORT",
  "inherit_templates": true,
  "billing_model": "organization",
  "sandbox": true
}
```

Use this only after the organization WABA is connected. Inheritance means the tenant shares that WABA boundary; confirm this matches the tenant/brand architecture.

## Path C: dedicated WABA credentials

```json
{
  "name": "Dedicated Tenant",
  "whatsapp_business_account": {
    "waba_id": "123456789012345",
    "phone_number_id": "987654321098765",
    "access_token": "<injected secret>"
  },
  "sandbox": true
}
```

`waba_id` and `access_token` are required. `phone_number_id` is optional: when omitted, the current contract describes provisioning and registration during onboarding.

The token needs the applicable WhatsApp Business messaging and management permissions. Inject it from a secret manager. Never log it, echo it, write it to fixtures, return it to the browser, include it in support output, or retain it in general profile storage. Sent does not return it in API responses.

## Complete the profile

Call `POST /v3/profiles/{profileId}/complete` with the required `webHookUrl`:

```json
{
  "webHookUrl": "https://example.com/webhooks/profile-complete",
  "sandbox": true
}
```

- `202` means background processing started; there is no final status in that response.
- `200` can mean the profile was already complete and currently demonstrates lowercase `completed`.
- The completion callback can report `COMPLETED`, `SUBMITTED`, or `failed`.

Treat the completion callback as its own integration surface. Its envelope uses `event`, not `sub_type`:

```json
{
  "event": "COMPLETED",
  "profile_id": "00000000-0000-0000-0000-000000000000",
  "timestamp": "2026-08-09T12:00:00Z"
}
```

Preserve unknown event strings. Verify authenticity using the mechanism Sent documents for the callback endpoint and make processing idempotent.

## Verify operational readiness

- Profile WABA ID matches the intended business.
- Selected number is mapped to the intended profile.
- Template sharing/inheritance is intentional.
- A test template can be created with `sandbox: true`.
- The completion callback is reachable and idempotent.
- Returned message IDs are stored against the tenant/profile before webhook processing.
- Tokens and payment values are absent from logs.

For ordinary message and template webhooks, follow Sent's current events reference; those are separate from Meta browser events and profile-completion callbacks.

## Failure routing

| Failure | Next action |
| --- | --- |
| `422` when credentials are omitted | Connect the organization WABA or provide dedicated credentials. |
| `403` with profile key and `x-profile-id` | Remove `x-profile-id` or use an authorized organization key. |
| Wrong WABA/number | Stop before completion and correct the profile mapping. |
| Expired/under-scoped token | Replace it securely; never print it while diagnosing. |
| Completion remains submitted | Inspect prerequisite and callback evidence; do not assume final failure from the `202`. |

Use [references/waba-embedded-signup-spec.md](references/waba-embedded-signup-spec.md), [references/waba-onboarding-runbook.md](references/waba-onboarding-runbook.md), and [references/whatsapp-sender-profile-mapping.md](references/whatsapp-sender-profile-mapping.md). Use `sender-profile-architect` for tenant boundaries and `waba-template-author` for the first template.
