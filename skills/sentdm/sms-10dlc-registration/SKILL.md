---
name: sms-10dlc-registration
description: Prepares and validates Sent US A2P 10DLC brand and campaign registration through Sender Profiles, including inheritance, all campaign use cases, opt-in evidence, sample-message policy, autoresponses, sandbox validation, TCR status, and rejection remediation.
---

# SMS 10DLC Registration

Use this skill for US A2P SMS over 10-digit long codes. Separate the compliance evidence packet from the exact Sent API request; they have different schemas and validators.

## Current Sent resource model

There is no standalone brand CRUD path in the current v3 API.

- Create a dedicated brand inside `POST /v3/profiles` using `brand` and `inherit_tcr_brand: false`.
- List/create campaigns with `GET|POST /v3/profiles/{profileId}/campaigns`.
- Update/delete with `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}`.

Reject guidance that reintroduces a free-standing brand path.

## Choose inheritance deliberately

| Brand | Campaign | Settings |
| --- | --- | --- |
| Inherit both | Organization brand and campaign | `inherit_tcr_brand: true`, `inherit_tcr_campaign: true` |
| Inherit brand, own campaign | Shared legal brand with tenant-specific traffic | brand true, campaign false |
| Own both | Dedicated tenant/business | both false and supply `brand` during profile creation |

Inherited campaigns are read-only. A profile cannot supply `brand` while brand inheritance is true.

## Two validation layers

### Evidence readiness packet

The private packet uses the explicit internal version `sent-10dlc-evidence/v1` and snake_case evidence fields. It is not an API payload.

```bash
python scripts/validate_10dlc_packet.py evidence.json
```

Collect legal identity, public website/policy links, consent proof, message flow, opt-in/opt-out/help responses and keywords, use cases, and realistic samples. See [references/10dlc-evidence-checklist.md](references/10dlc-evidence-checklist.md).

### Sent campaign request

The API request uses exact camelCase and a `campaign` wrapper:

<!-- sent-campaign-request -->
```json
{
  "campaign": {
    "name": "Acme account notifications",
    "description": "Account and delivery notifications for opted-in customers.",
    "type": "App",
    "useCases": [
      {
        "messagingUseCaseUs": "ACCOUNT_NOTIFICATION",
        "sampleMessages": [
          "Acme Example: Your account preference was updated. Reply STOP to opt out."
        ]
      }
    ],
    "volume": "2000",
    "messageFlow": "Customers opt in in account settings before notifications begin.",
    "privacyPolicyLink": "https://example.com/privacy",
    "termsAndConditionsLink": "https://example.com/terms",
    "optinMessage": "Acme Example: You are subscribed. Reply STOP to opt out.",
    "optoutMessage": "Acme Example: You are unsubscribed and will receive no more messages.",
    "helpMessage": "Acme Example: Visit https://example.com/support for help.",
    "optinKeywords": "START,YES",
    "optoutKeywords": "STOP,UNSUBSCRIBE",
    "helpKeywords": "HELP,INFO"
  },
  "sandbox": true
}
```

Validate it with:

```bash
python scripts/validate_campaign_payload.py campaign.json
```

## API use cases

Support all 13 current values:

`MARKETING`, `ACCOUNT_NOTIFICATION`, `CUSTOMER_CARE`, `FRAUD_ALERT`, `TWO_FA`, `DELIVERY_NOTIFICATION`, `SECURITY_ALERT`, `M2M`, `MIXED`, `HIGHER_EDUCATION`, `POLLING_VOTING`, `PUBLIC_SERVICE_ANNOUNCEMENT`, and `LOW_VOLUME`.

Each use case structurally accepts 1–5 samples, each no longer than 1,024 characters. The compliance layer requires at least two samples for marketing and mixed traffic, including low-volume mixed. Keep that policy distinction visible instead of pretending OpenAPI requires two for all traffic.

## Volume and status

`volume` is optional and, when supplied, is a numeric string. Values below `"2000"` use the documented low-volume tier; `"2000"` is the boundary to the next tier.

Campaign responses currently expose statuses `SENT_CREATED`, `ACTIVE`, and `EXPIRED`, plus `submittedToTCR`. Preserve unknown future status strings. Do not confuse a successful Sent record creation with TCR submission or carrier activation.

## Safe workflow

1. Confirm this is US A2P 10DLC traffic and the actual sending business is identified.
2. Select brand/campaign inheritance.
3. Validate the versioned evidence packet.
4. Create or confirm the profile brand.
5. Translate evidence into the exact camelCase campaign request.
6. Validate locally and use `sandbox: true`.
7. Show the payload and obtain confirmation before a real create/update/delete.
8. Store profile ID, campaign ID, `submittedToTCR`, raw status, and review evidence.
9. Complete the profile with required `webHookUrl` only after prerequisites are ready.

Never use real consumer data in fixtures or samples. Use [references/tcr-use-cases.md](references/tcr-use-cases.md) for classification and [references/10dlc-rejection-remediation.md](references/10dlc-rejection-remediation.md) for failures.
