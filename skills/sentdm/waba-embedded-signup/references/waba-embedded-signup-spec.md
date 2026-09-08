# WABA integration specification

## Capability boundaries

- Organization Embedded Signup is launched in the Sent dashboard.
- No public Sent endpoint starts that hosted signup.
- `POST /v3/profiles` can inherit the organization's WABA or accept a dedicated WABA.
- Direct profile credentials are not an Embedded Signup endpoint.

## Dedicated credentials

```text
whatsapp_business_account
  waba_id           required string
  access_token      required secret string
  phone_number_id   optional string
```

Omitting `phone_number_id` invokes the current provisioning behavior documented by the profile contract. The token is write-only operational input and must never appear in API output, logs, fixtures, traces, analytics, or support text.

## Inheritance

Omit the entire `whatsapp_business_account` object to inherit. This succeeds only if the organization has completed Embedded Signup; otherwise expect `422`.

## Auth matrix

| Key | `x-profile-id` | Result |
| --- | --- | --- |
| Profile key | Omitted | Profile-scoped operation. |
| Profile key | Present | `403`. |
| Organization key | Valid child UUID | Child-scoped operation; organization rate-limit pool. |
| Organization key | Unowned UUID | `404`. |

`x-sender-id` belongs to legacy v1/v2 guidance.

## Profile completion

The request requires `webHookUrl`. A `202` only confirms processing began. A `200` can report an already-complete profile. Completion callback event values include `COMPLETED`, `SUBMITTED`, and `failed`; do not treat that vocabulary as the REST profile enum.

```json
{
  "event": "SUBMITTED",
  "profile_id": "00000000-0000-0000-0000-000000000000",
  "timestamp": "2026-08-09T12:00:00Z"
}
```

Completion callbacks use `event`, not `sub_type`. Meta Embedded Signup browser messages also use an `event` field but have a different producer and payload. Keep the two handlers distinct.
