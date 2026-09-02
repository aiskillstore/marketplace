# WhatsApp Sender Profile mapping

## Recommended records

```text
tenant_id
sent_profile_id
waba_mode                 # organization_inherited | dedicated
waba_id
whatsapp_phone_number_id
whatsapp_phone_number
profile_key_secret_ref
status_raw
status_surface
```

Do not store `access_token` in this record. Use a secret-manager reference when retention is necessary.

## Mapping invariants

- A dedicated WABA profile has a recorded `waba_id` matching the intended tenant.
- An inherited profile explicitly records that it shares the organization WABA.
- A WhatsApp number maps to one current tenant/profile route unless the product has a documented coexistence model.
- `message_id` is persisted with tenant and profile before webhook events arrive.
- Unknown REST or completion callback statuses are stored verbatim with their surface.

## Auth ownership

Profile keys minimize tenant credential blast radius. Organization keys with `x-profile-id` centralize control but share the organization rate-limit pool and expand credential impact. Never expose the organization key to tenant code.

## Event surfaces

| Surface | Discriminator |
| --- | --- |
| Meta Embedded Signup browser message | `event` plus Meta session/data fields |
| Sent profile completion callback | top-level `event` |
| Sent message webhook | `field: "message"` plus `sub_type` |
| Sent template webhook | `field: "templates"`, no `sub_type` |

Do not copy envelopes between these integrations. They have different producers, authenticity checks, and retry behavior.
