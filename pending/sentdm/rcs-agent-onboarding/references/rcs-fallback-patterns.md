# RCS routing and fallback patterns

## Automatic routing with fallback

Omit `channel` or send:

```json
{
  "to": ["+12025550100"],
  "channel": ["sent"],
  "template": {"id": "00000000-0000-0000-0000-000000000000"},
  "sandbox": true
}
```

Sent selects the available route. This is the cross-channel fallback mode.

## Pinned RCS

```json
{
  "to": ["+12025550100"],
  "channel": ["rcs"],
  "template": {"id": "00000000-0000-0000-0000-000000000000"},
  "sandbox": true
}
```

This requests RCS only and has no cross-channel fallback. Use it to isolate RCS launch or payload failures.

## Broadcast

Any array containing two or more explicit channel values is broadcast. Sent creates a separate message for each recipient/channel pair. This can duplicate content and charges.

Before a broadcast, calculate:

```text
messages created = recipient count × explicit channel count
```

Require explicit user intent and show the count/cost impact.

## Observability

The send response returns per-recipient message IDs and channels. Persist each record. Webhook message events use `field: "message"`, a message `sub_type`, and `payload.channel`. Determine what happened from the created message records and their activities—not from the ordering of the request array.

## Test matrix

| Test | Request | Expected evidence |
| --- | --- | --- |
| RCS path | `["rcs"]` | One RCS attempt per recipient, no SMS message ID |
| Automatic routing | omitted / `["sent"]` | One selected route per recipient according to availability |
| Broadcast | two explicit channels | Two message IDs per recipient |

There is no documented `fallback_policy` or `force_fallback` field. Do not invent dedicated fallback webhook names.
