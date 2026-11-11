---
name: whatsapp-number-onboarding
description: Load when connecting a client's or your own phone number to the WhatsApp Business Platform (Cloud API) inside Meta Business, or when a connected number "is green but nothing arrives", messages arrive twice, templates fail, or Meta blocks a step. Gives the safe order (portfolio → WhatsApp account → number → app → token → webhook → register with PIN → test), the read-back checks after each step, and a troubleshooting table of real blocks with their official error codes and fixes, each marked as official or field-tested. Triggers on "connect WhatsApp to my app", "onboard client number", "WhatsApp Cloud API setup", "number already registered", "No se pudo asignar el socio", "display name in review", "131042", "133010", "133016", "messages not arriving", "conectar el WhatsApp del cliente", "dar de alta el número", "el bot no recibe mensajes", "Meta no me deja". Not an API reference for sending messages or templates (use a WhatsApp Cloud API reference skill) and not sales copy for the bot (use whatsapp-closer).
---

# WhatsApp number onboarding (Meta Cloud API)

Connecting a number looks like 10 clicks. In practice it fails on the order
of steps, on which portfolio owns what, and on Meta screens that say
"connected" when nothing is delivered. This skill is the safe order plus the
blocks that actually happened, with their fixes.

**Confidence tags used below:** `[official]` = stated on developers.facebook.com
(URL in the table); `[field]` = happened in real onboardings and the fix was
confirmed live; `[unconfirmed]` = seen, cause or fix never proven. Never present
`[field]` or `[unconfirmed]` as Meta policy.

## Words: never mix these four
- **Business portfolio** (Business Manager): the company in Meta.
- **WhatsApp Business Account (WABA)**: lives inside a portfolio. In the UI, use the **Messaging account** ID, not the "WhatsApp account/presence" ID (the latter returns "This API is not supported") `[field]`.
- **Phone number**: lives inside a WABA. Its **Phone number ID** is not the phone number.
- **Meta app**: lives in a developer account and is linked to a portfolio; it holds the token, app secret and webhook.

When you state a limit, say which of the four it is about.

## Limits that decide the plan `[official]`
- A new portfolio can register **2 phone numbers**; the cap rises to **20** when the business is verified or reaches the 2,000 messaging limit.
- Messaging limits are **per portfolio, shared by all its numbers**: 250 → 2,000 → 10,000 → 100,000 → unlimited. One busy number can use up everyone's allowance.
- Register and deregister: **10 requests per number per 72 h** each; past that, error 133016 and the number is blocked for 72 h. Do not hammer "Activate" while debugging.
- Adding a number in WhatsApp Manager or the app dashboard **does not register it for Cloud API**; the register call is still needed.
- A number already used with WhatsApp (phone app) cannot be registered until that account is deleted.
- Deleting a number: portfolio admins only, not via API, needs the 2-step PIN if connected, and is **impossible if it sent paid messages in the last 30 days**. Treat deletion as irreversible.

## Before starting (collect once)
Business name exactly as customers will see it, legal name, country, full address, phone, website or Facebook page, email, logo, and the number to connect. The number must not have WhatsApp installed (if it does, delete the WhatsApp account on that phone first). Decide who invents and keeps the 6-digit PIN.

## Safe order (each step ends with a read-back)
1. **Portfolio** (business.facebook.com): fill *Business info* completely (legal name, address, phone, website) **before** adding a number. With it empty, onboarding failed with "your business doesn't meet WhatsApp policy" (#2494070) `[field]`.
2. **WhatsApp account + number** (Portfolio settings → Accounts → WhatsApp accounts → Add → new number). Display name = **the client's business name**, never the agency's. Verify by SMS, or VOICE for landlines `[official]`. Read back: the number appears under the WABA.
3. **Meta app** (developers.facebook.com → Create app → WhatsApp use case), linked to the **same portfolio that owns the WABA**. App in one portfolio and WABA in another: everything showed green and no message was delivered; moving the app into the WABA's portfolio fixed it `[field]`. Settings → Basic: privacy/terms/data-deletion URLs that return 200, category, icon.
4. **System user** in that portfolio with the app and the WABA as assets; token with `whatsapp_business_messaging` + `whatsapp_business_management`, no expiry. A human pastes the token where it is stored; never echo it.
5. **IDs, read by you, not typed by a person:** `GET /{waba-id}/phone_numbers` → Phone number ID. Storing the phone number in the Phone-number-ID variable broke a bot `[field]`.
6. **Environment variables** in the exact hosting project. Several client projects with the same variable names: say the project name and check the title before saving. One client's IDs went into another's project and its live bot pointed to the wrong number `[field]`.
7. **Webhook** (app → WhatsApp → Configuration): `https://<domain>/webhook` plus verify token; subscribe the `messages` field (it is not always on). Then subscribe the WABA to the app: `POST /{waba-id}/subscribed_apps`.
8. **Register the number:** `POST /{phone-number-id}/register` with the 6-digit PIN. If the number already has 2-step verification, use the **existing** PIN `[official]`. Read back: `GET /{phone-number-id}?fields=status,platform_type,name_status` → `CONNECTED` and `CLOUD_API`. Before this it shows `PENDING` / `NOT_APPLICABLE` `[field]`.
9. **Publish the app**, then send "Hi" from a personal phone and see the bot answer.
10. **Billing:** payment method, **timezone and currency** set on the WhatsApp account before sending templates (131042 otherwise) `[official]`.
11. **Final read-back:** number status, `GET /{waba-id}/subscribed_apps` shows only this app, webhook URL and fields, `debug_token` shows the right app and a system-user token.

The display name can stay "in review" for days while the number already works `[field]`; do not click Edit, because editing restarts the review.

## Golden rules
- **Same portfolio** for the app and the WABA. If the client's own portfolio is stuck in review, a field-tested way out is to put the number in a WABA in a portfolio that works (yours), with the app in that same portfolio, inside the 2-number cap `[field]`. The official long-term path is becoming a Tech Provider with Embedded Signup.
- **One app per client, by default.** The app's callback URL is the default destination. Meta supports per-WABA and per-number webhook overrides `[official]`, but if you have not tested them, keep one app per client.
- **When the hosting domain changes, update the webhook in Meta at that moment** and read it back. A domain change silently stopped a bot `[field]`.
- **Never use the "Continue" path that installs the WhatsApp Business app on the phone** for a number that should stay on Cloud API: it takes the number off the API `[field]`.
- **Try what breaks nothing first.** Deregistering, deleting or moving a number come last, only if Meta requires it (see the limits above).
- **A health check is green only when Meta says so:** read the phone status from Meta. A valid token proves nothing about the number `[field]`.
- **A redirect to a portfolio's URL does not prove who owns an asset.** Confirm the portfolio name on screen `[field]`.

## Troubleshooting
| Symptom | Cause | Fix | Tag / source |
|---|---|---|---|
| All green, nothing arrives | App and WABA in different portfolios | New app in the WABA's portfolio; remove the old app's webhook | `[field]` |
| Messages arrive twice / "app secret mismatch" warnings | Two apps subscribed to the same WABA | Remove the old app's webhook and subscription | `[field]` |
| Bot stopped after a deploy | Webhook still on the old domain | Update the webhook and read it back | `[field]` |
| "No se pudo asignar el socio" (assign partner) when the client shares its WABA | Never proven (new or unverified portfolio, account under review) | Avoid the share: build in one portfolio (see the golden rules) | `[unconfirmed]` cause, `[field]` workaround |
| "Business doesn't meet WhatsApp policy" (#2494070) during developer onboarding | Incomplete business info / new portfolio | Complete the business info; add the number from WhatsApp Manager instead | `[field]` |
| "This API is not supported" with the WABA ID | Used the "WhatsApp account" ID | Use the Messaging account ID | `[field]` |
| Status `PENDING`, platform `NOT_APPLICABLE` | Added but not registered | `POST /register` with PIN | `[official]` + `[field]` |
| 133005 | Wrong 2-step PIN | Use the number's existing PIN | [error codes][ec] |
| 133006 | Number not verified | Verify by SMS/VOICE, then register | [error codes][ec] |
| 133008 / 133009 | Too many or too fast PIN attempts | Wait the time in `details` | [error codes][ec] |
| 133010 | Number not registered on the platform | Register it | [error codes][ec] |
| 133015 | Number recently deleted, still deleting | Wait 5 minutes | [error codes][ec] |
| 133016 | Over 10 register/deregister requests in 72 h | Stop; wait for the block to end | [registration][reg] |
| 133000 | A previous deregistration failed | Deregister again, then register | [error codes][ec] |
| "Number already has WhatsApp" | Number still on the phone app or another account | Delete that WhatsApp account first | [phone numbers][pn] |
| 131042 on templates | Payment method: credit line, timezone or currency not set, account suspended | Fix billing in WhatsApp Manager; show the user Meta's `error_data.details` text, not a guess | [error codes][ec] |
| 131042 on a few recipients only | Account-wide per Meta's text, yet in one live check 16 of 18 templates were delivered | Count delivered vs failed in the same period **before** calling it account-wide or pausing anything | `[field]` heuristic |
| 131049 | Not delivered "to maintain healthy ecosystem engagement" | Wait at least 24 h before resending | [error codes][ec] |
| 131026 | Recipient can't receive (no WhatsApp, old version, terms) | Reach them another way | [error codes][ec] |
| 131031 | WABA restricted for a policy violation | See Policy Enforcement and the Health Status API | [error codes][ec] |
| Can't link the number to the Facebook page for click-to-WhatsApp ads | Display name still in review (likely) | Wait for approval, then Page → Linked accounts → WhatsApp | `[unconfirmed]` |

[ec]: https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes
[reg]: https://developers.facebook.com/docs/whatsapp/cloud-api/reference/registration
[pn]: https://developers.facebook.com/docs/whatsapp/cloud-api/phone-numbers

Other official pages: [get started](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started) · [messaging limits](https://developers.facebook.com/docs/whatsapp/messaging-limits) · [webhook overrides](https://developers.facebook.com/docs/whatsapp/embedded-signup/webhooks/override).

## Not verified (say so if it comes up)
- What "No se pudo asignar el socio" really requires.
- Whether a brand-new, unverified portfolio may create a WABA at all.
- Moving a number between WABAs: Meta's guide says it is not supported for accounts on the new account model; it was never completed in the field.
- Official display-name review times. The two official URLs returned 404 in Nov 2026.

## Who does what
The agent does every screen and API check it can. The person only provides what a machine cannot: the SMS/voice code from the phone, the PIN, pasting secrets, identity checks, payments.
