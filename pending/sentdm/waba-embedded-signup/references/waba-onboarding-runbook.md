# WABA onboarding runbook

## 1. Choose the path

- Organization needs its first WABA: use dashboard Embedded Signup.
- Child shares the organization WABA: create a profile and omit credentials.
- Child owns a dedicated WABA: create a profile with `waba_id` and `access_token`; optionally include `phone_number_id`.

Record why the choice matches brand, tenant, compliance, and blast-radius requirements.

## 2. Prepare access

Use a profile key alone or an organization key with `x-profile-id` for existing-child operations. Do not use `x-profile-id` with a profile key. Remove legacy `x-sender-id` examples.

## 3. Handle secrets

- Receive tokens only through a protected server-side path.
- Store them in a secret manager if your system must retain them.
- Redact request bodies before logging.
- Never send tokens back to the frontend.
- Do not include tokens in screenshots, fixtures, errors, or support tickets.

## 4. Create or update the profile

Use `sandbox: true` first. On a dedicated WABA path, confirm that the returned non-secret WABA and number identifiers match intent. On inheritance, treat `422` as evidence the organization WABA prerequisite is absent.

## 5. Complete

Send `webHookUrl` to `/v3/profiles/{profileId}/complete`. Persist the request ID and profile ID. A `202` is not final approval.

The callback handler:

1. verifies the callback;
2. reads top-level `event`;
3. deduplicates by profile/event and delivery identity when available;
4. preserves unknown event strings;
5. records `COMPLETED`, `SUBMITTED`, or `failed` without coercing REST status.

## 6. Smoke test

- Create a synthetic draft template with the Sent `definition` request shape.
- Validate with `sandbox: true`.
- Submit only after explicit review.
- Send to a controlled recipient.
- Persist the returned `message_id` with tenant/profile attribution.
- Verify the normal Sent message webhook separately from the completion callback.

## 7. Rollback

If the WABA or number is wrong, stop new sends, revoke exposed credentials, correct profile mapping, and retain audit evidence. Avoid deleting a profile until number ownership and message retention are resolved.
