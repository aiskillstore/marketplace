# TCR use cases

## Current Sent API values

| Value | Typical traffic |
| --- | --- |
| `MARKETING` | Promotions, offers, product announcements |
| `ACCOUNT_NOTIFICATION` | Account changes, balances, non-security notices |
| `CUSTOMER_CARE` | Support conversations and case updates |
| `FRAUD_ALERT` | Suspected fraud notifications |
| `TWO_FA` | One-time passcodes and two-factor authentication |
| `DELIVERY_NOTIFICATION` | Shipment and delivery updates |
| `SECURITY_ALERT` | Security events distinct from general account notices |
| `M2M` | Machine-to-machine operational traffic |
| `MIXED` | Multiple standard use cases in one campaign |
| `HIGHER_EDUCATION` | College or university communications |
| `POLLING_VOTING` | Polling and voting interactions |
| `PUBLIC_SERVICE_ANNOUNCEMENT` | Public-interest or government notices |
| `LOW_VOLUME` | Low-volume mixed traffic |

Select what the business will actually send. Do not use `MIXED` or `LOW_VOLUME` to hide a dominant high-risk use case.

## Sample rules

The API structure permits 1–5 samples per use case, up to 1,024 characters each. Compliance policy requires at least two samples for `MARKETING`, `MIXED`, and low-volume mixed traffic. Samples should:

- name the recognizable consumer brand;
- look like real production messages;
- match the selected use case and described message flow;
- include opt-out language when applicable;
- use synthetic names, codes, numbers, and URLs.

## Volume

`volume` is a numeric string. Values below `2000` are in the documented low-volume tier. Exactly `2000` crosses the tier boundary, so validate `1999` and `2000` separately.
