# Template validation matrix

This matrix maps UI controls to the body of `POST /v3/templates`.

## Request root

| Field | Client rule |
| --- | --- |
| `definition` | Required object. |
| `category` | Optional `UTILITY`, `MARKETING`, or `AUTHENTICATION`. |
| `language` | Optional locale such as `en_US`. |
| `creation_source` | Optional string. |
| `submit_for_review` | Boolean; default to false in the editor. |
| `sandbox` | Boolean; use true for validation. |

Reject top-level `name`, `channels`, `body`, `header`, `buttons`, and `components`. A `components[]` import is Meta Cloud API source and requires conversion.

## Definition

| Field | Rule |
| --- | --- |
| `body.multiChannel` | Required body content. |
| `body.sms`, `body.whatsapp`, `body.rcs` | Optional complete overrides using the same content schema. |
| `header.template` | Optional, maximum 60 characters. |
| `footer.template` | Optional, maximum 60 characters, no variables. |
| Body `template` | Required non-empty text, maximum 1,024 characters. |
| `definitionVersion` | Optional string; preserve when editing. |
| `authenticationConfig` | Only for `AUTHENTICATION`. |

Every placeholder uses `{{id:type}}`, for example `{{0:variable}}`. Each must map one-to-one to a variable with a non-negative integer `id`, readable `name`, matching `type`, and non-empty `props.sample`. IDs are unique within a body.

## Buttons

| Type | Total allowed | Required properties |
| --- | ---: | --- |
| `QUICK_REPLY` | Up to the overall total of 10 | `text`, `quickReplyType` |
| `URL` | 2 | `text`, `urlType`, `url` |
| `VOICE_CALL` | 1 | `text`, `countryCode`, `phoneNumber` |
| `PHONE_NUMBER` | 1 | `text`, `countryCode`, `phoneNumber` |
| `COPY_CODE` | 1 | `text`, `offerCode` |

There are at most 10 buttons in total, and button text is at most 25 characters. Quick replies and CTA buttons may coexist.

## Authentication

`authenticationConfig` accepts `addSecurityRecommendation` and optional `codeExpirationMinutes` from 1 through 90. Authentication templates should contain one code variable and one copy-code action, with no promotion, unrelated media, URL, or call action.

## Channel-specific product rules

| Channel | Current UI capability |
| --- | --- |
| SMS | Plain text preview and segment estimate. |
| WhatsApp | Header, body, footer, variables, and supported buttons. |
| RCS | Text and up to four suggestion chips. |

Do not expose current Sent controls for RCS rich cards, carousels, or media attachments. They are roadmap features. Do not require an SMS fallback body; automatic routing is a send-time choice made by omitting `channel` or using `["sent"]`.

## Server round trip

Client validation is advisory. Serialize the exact Sent request, run the bundled linter, validate with `sandbox: true`, and reconcile server errors by field. Never silently rewrite submitted copy.
