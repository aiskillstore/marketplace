# Template status handling

## Resource states

Sent template resources currently surface `DRAFT`, `PENDING`, `APPROVED`, `REJECTED`, and `PAUSED`. Use an unknown state in the UI because contracts evolve.

## Provider webhook states

WhatsApp approval events use this envelope:

```json
{
  "field": "templates",
  "timestamp": "2026-08-09T12:00:00Z",
  "payload": {
    "account_id": "00000000-0000-0000-0000-000000000000",
    "template_id": "11111111-1111-1111-1111-111111111111",
    "template_name": "order_update",
    "whatsapp_template_id": "2222222222222222",
    "status": "CATEGORY_UPDATED",
    "language": "en_US",
    "category": "MARKETING",
    "channel": "whatsapp",
    "reason": "Provider category update"
  }
}
```

Template events have `field: "templates"` and no `sub_type` or `event`. Known provider values include `PENDING`, `APPROVED`, `REJECTED`, and `CATEGORY_UPDATED`; values such as `PAUSED` and `DISABLED` may be forwarded verbatim.

## UI behavior

| Value | UI response |
| --- | --- |
| `DRAFT` | Editable; offer validate and submit actions. |
| `PENDING` | Lock provider-reviewed fields and show submission time. |
| `APPROVED` | Show usable status and immutable submitted content. |
| `REJECTED` | Show the reason and create a revision path. |
| `PAUSED` / `DISABLED` | Block new WhatsApp usage and surface remediation. |
| `CATEGORY_UPDATED` | Show old/new category when known and re-evaluate pricing/policy UX. |
| Unknown | Preserve raw value, use a neutral badge, and avoid destructive assumptions. |

Verify webhook signatures, deduplicate transitions, retrieve the current resource before overwriting local state, and tolerate delayed or out-of-order deliveries. Polling may be used as recovery, not as evidence that invented webhook event names exist.
