---
name: sent-profile-provisioning
description: Executes the Sent Sender Profile lifecycle over the API — creating profiles with the right inheritance, sharing, billing, and WhatsApp options, driving profile completion and its callback, managing 10DLC campaigns per profile, and administering users and roles. Use when calling POST /v3/profiles, handling a completion callback or unclear profile status, choosing inherit or dedicated resources, wiring per-tenant onboarding, or inviting and role-managing users.
---

# Sent Profile Provisioning

This skill is the execution counterpart to profile architecture: once the tenancy boundary is decided, it drives the API calls, the completion callback, the campaign registration, and the user administration that make a profile able to send. Design the boundary with `sender-profile-architect` first; provision it here.

## Provisioning sequence

1. **Confirm the credential.** `POST /v3/profiles` requires an organization key with `admin`. Profile-scoped keys cannot create profiles, and a profile key that sends `x-profile-id` receives `403`.
2. **Decide inheritance and sharing before the call.** These flags shape compliance posture and are awkward to unwind later.
3. **Create the profile**, validating the payload with `"sandbox": true` first when the shape is uncertain. Use a different idempotency key for the live create because a successful sandbox response is cached for 24 hours.
4. **Attach or inherit WhatsApp** via exactly one of the three supported paths.
5. **Register campaigns** for US SMS under the profile.
6. **Complete the profile** with `POST /v3/profiles/{profileId}/complete` and a reachable `webHookUrl`.
7. **Reconcile status** from the callback, or by polling if the callback is missed.
8. **Invite users** with least-privilege roles.

## Create payload essentials

`name` is the only required field. The consequential optional fields group into identity, sharing, inheritance, billing, WhatsApp, and brand.

```json
{
  "name": "Northwind Retail",
  "short_name": "Northwind",
  "description": "Retail brand tenant",
  "allow_contact_sharing": false,
  "allow_template_sharing": false,
  "inherit_contacts": false,
  "inherit_templates": false,
  "inherit_tcr_brand": true,
  "inherit_tcr_campaign": true,
  "billing_model": "profile",
  "billing_contact": {
    "name": "Ada Ops",
    "email": "ops@example.com",
    "phone": "+14155550100",
    "address": "1 Example Way, Springfield"
  },
  "sandbox": true
}
```

`short_name` must be 3 to 11 characters of letters, numbers, and spaces with at least one letter. Inheritance flags default to true, so a profile created with no flags consumes the organization's contacts, templates, brand, and campaigns. The example opts into contact and template isolation explicitly while inheriting the organization's compliance registrations. Sharing flags expose this profile's resources outward; inheritance flags consume the organization's resources inward. They are independent directions and are frequently confused.

Create permits `name` alone, but completion also requires `short_name`, `description`, profile KYC information, and any required campaign or channel setup. When `inherit_tcr_brand` is true, the API rejects a `brand` object in the create request even though the profile still needs its own KYC submission; complete that KYC through the dashboard before calling the completion endpoint.

`billing_model` accepts `profile`, `organization`, or `profile_and_organization`. Any model that includes `profile` requires `billing_contact` when none exists, and `payment_details` is only accepted for those models. Card fields are forwarded to the payment processor and must never be logged, echoed, or persisted anywhere in the application.

Field-by-field rules, error codes, and the update-only fields are in [references/profile-lifecycle.md](references/profile-lifecycle.md).

## Inheritance decisions

| Flag | `true` means | Consequence |
| --- | --- | --- |
| `inherit_tcr_brand` | Use the organization's registered brand | A `brand` object in the same request is rejected |
| `inherit_tcr_campaign` | Use the organization's campaigns | Those campaigns are read-only for this profile; creating one returns a validation error |
| `inherit_contacts` | Read the organization's contacts | No contact isolation between tenants |
| `inherit_templates` | Read the organization's templates | No template isolation between tenants |

An inherited brand with `inherit_tcr_campaign: false` is a supported and common pattern: shared legal identity, dedicated messaging use cases per tenant.

## WhatsApp: exactly three paths

1. Organization Embedded Signup, performed in the Sent Dashboard. **No public endpoint starts this flow.**
2. Child-profile inheritance — omit `whatsapp_business_account` once the organization has a WABA.
3. Dedicated profile credentials — supply `whatsapp_business_account` with `waba_id` and `access_token`, optionally `phone_number_id`.

Supplying credentials on `POST /v3/profiles` is not an Embedded Signup endpoint. Omitting `whatsapp_business_account` when the organization has no WABA configured returns `422`; complete organization Embedded Signup or supply valid direct credentials. Use `waba-embedded-signup` for the operational signup flow.

## Completion and status

`POST /v3/profiles/{profileId}/complete` requires `webHookUrl`.

```json
{
  "webHookUrl": "https://provisioning.example.com/callbacks/profile-complete",
  "sandbox": false
}
```

A `202` means processing started and carries no final status. A `200` means the profile was already complete and its body carries a status. The callback body is `{profileId, success, status, timestamp}` and is **delivered once with no retry**, so the receiver must be live before the call and the flow must degrade to polling `GET /v3/profiles/{profileId}`. This callback is separate from subscribed Sent webhooks and is not documented as carrying the webhook HMAC headers; use a unique callback path tied to the provisioning record, reject unknown profile ids, and treat polling as the authoritative recovery path.

Profile status vocabulary differs by surface: the create response demonstrates lowercase `incomplete`, the completion `200` demonstrates lowercase `completed`, the completion callback uses `COMPLETED`, `SUBMITTED`, and `failed`, and `GET /v3/profiles/{id}` documents `approved`, `submitted`, `processing`, and `failed`. Do not assert a closed enum, do not lowercase-normalize into a fixed set, and record which surface produced each value. Compare statuses case-insensitively and preserve unknown strings.

## Campaigns per profile

Campaign management lives under the profile: `GET|POST /v3/profiles/{profileId}/campaigns` and `PUT|DELETE /v3/profiles/{profileId}/campaigns/{campaignId}`. There are no standalone brand endpoints; a dedicated brand is created with the profile.

<!-- sent-campaign-request -->
```json
{
  "campaign": {
    "name": "Northwind order notifications",
    "description": "Order and delivery notifications for opted-in Northwind customers.",
    "type": "App",
    "useCases": [
      {
        "messagingUseCaseUs": "ACCOUNT_NOTIFICATION",
        "sampleMessages": [
          "Northwind: Your order 12345 has shipped. Reply STOP to opt out."
        ]
      }
    ],
    "volume": "1500",
    "messageFlow": "Customers opt in at checkout before notifications begin.",
    "privacyPolicyLink": "https://example.com/privacy",
    "termsAndConditionsLink": "https://example.com/terms"
  }
}
```

`messagingUseCaseUs` accepts one of thirteen values, `sampleMessages` holds 1 to 5 entries of at most 1,024 characters each, and a numeric `volume` string below 2,000 selects the low-volume tier while 2,000 or above selects the standard tier. Campaign statuses are `SENT_CREATED`, `ACTIVE`, and `EXPIRED`. Use `sms-10dlc-registration` for use-case selection and sample-copy policy.

## Users and roles

Five operations administer access: `GET /v3/users`, `POST /v3/users` (invite), `GET /v3/users/{userId}`, `PATCH /v3/users/{userId}` (role), and `DELETE /v3/users/{userId}`. None is exposed through MCP. Assignable roles are `admin`, `billing`, and `developer`; `owner` is implicit for the creating account and never appears in the list. Mutations require `admin`.

Role checks resolve against the email that owns the API key and pass only for the owner or an **active** user with an allowed role — `invited`, `suspended`, and `rejected` users fail. Organization-level access cascades to child profiles. Invitations expire after seven days, and inviting an existing user returns `409`.

Before any user mutation, read the current state, then confirm explicitly with the operator. The API refuses to let you change your own role, demote the last admin, remove yourself, or remove the last admin, but checking first produces a clear explanation instead of a validation error. The full role matrix and key-hygiene rules are in [references/users-and-roles.md](references/users-and-roles.md).

There is no endpoint to list, create, or revoke API keys; key management is a dashboard operation. Rotation is create-new, deploy, verify with `GET /v3/me`, then disable or delete the old key — deleting first only when the key is compromised.

## Multi-tenant provisioning notes

Webhook events never carry your application's tenant identifier. Before the first send, persist `message_id -> {tenant, profile, logical_send_id, channel}` and `receiving_number -> {tenant, profile}`. Do not infer tenant ownership from `account_id`, since many tenant profiles can share one organization. Provision one webhook registration per environment so a failing lower-environment receiver cannot auto-disable production.

## Boundaries

Use `sender-profile-architect` for the isolation, credential, and blast-radius design decision; `waba-embedded-signup` for the WhatsApp signup flow; `sms-10dlc-registration` for brand vetting and campaign policy; and `sent-webhook-engineer` for subscribed message-event receivers. Profile-completion callbacks use the separate verification and polling guidance in this skill.
