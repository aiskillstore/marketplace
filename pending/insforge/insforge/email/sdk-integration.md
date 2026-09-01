# Email SDK Integration

Send custom transactional HTML emails via `insforge.emails.send`. Routes through AWS SES under per-project tenant identities, with automatic List-Unsubscribe headers and unsubscribe filtering.

> **🛑 No SMTP, no third-party packages.** `insforge.emails.send()` works on every paid project — no `nodemailer` / `resend` / `sendgrid` / `mailgun` / `postmark`, no `SMTP_HOST`, no provider API keys. The platform manages the SES sender. Server-only sends still authenticate with your own project API key (see below) — that is InsForge auth, not an email-provider credential. Custom sender domain → dashboard, not `package.json`.
>
> **Scope.** This module sends **custom** transactional emails (welcome, receipt, newsletter, alerts). For auth flows (signup verification, password reset, invites), use `insforge.auth.*` — those ship on **every plan**, also no SMTP.

> **⚠️ Private preview.** Custom email is in private preview. The API may change; pin to a tested SDK version. Custom email requires a **paid plan** — free-tier projects can only use the built-in auth emails.

## Setup

Ensure your `.env` is configured with your InsForge URL and anon key. Get the anon key with `npx -y @insforge/cli secrets get ANON_KEY`. See the main [SKILL.md](../SKILL.md) for framework-specific variable names.

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,       // adjust prefix for your framework
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY   // adjust prefix for your framework
})
```

`emails.send` requires an authenticated caller — **the anon key is not sufficient.** A signed-out client sends its anon key as the bearer credential, and the route rejects that with `401 Sending emails requires an authenticated user`. Sign the user in first: the SDK swaps the anon key for that user's JWT on the same client, and the call then succeeds.

For server-only code with no signed-in user, authenticate as project admin instead:

```javascript
import { createAdminClient } from '@insforge/sdk'

const admin = createAdminClient({
  baseUrl: process.env.INSFORGE_URL,
  apiKey: process.env.INSFORGE_API_KEY
})
```

`admin.emails.send()` takes the same options as the examples below. Get the key with `npx -y @insforge/cli secrets get API_KEY` and keep it server-side — it is a full-access admin key, never a client bundle. See [SKILL.md](../SKILL.md).

## Send an Email

```javascript
// emails.send uses whatever credential the client is holding, so the user
// must be signed in first. Any flow in ../auth/sdk-integration.md works;
// substitute the credentials your own sign-in form collects.
const { error: signInError } = await insforge.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'securepassword123',
});
if (signInError) throw signInError;

const { data, error } = await insforge.emails.send({
  to: 'user@example.com',
  subject: 'Welcome to Acme',
  html: '<h1>Hi!</h1><p>Thanks for joining Acme.</p>',
  from: 'Acme Updates',          // optional display name
  replyTo: 'support@acme.com',   // optional
});

if (error) {
  console.error('Email failed:', error.message);
  return;
}
console.log('Sent:', data?.id);
```

## Send to Multiple Recipients

```javascript
const { data, error } = await insforge.emails.send({
  to: ['alex@example.com', 'sam@example.com'],
  cc: 'manager@example.com',
  bcc: ['archive@example.com'],
  subject: 'April update',
  html: '<h1>This month at Acme</h1><p>...</p>',
  from: 'Acme Updates',
});

// data.skipped lists any recipients that have unsubscribed and were silently dropped
if (data?.skipped?.length) {
  console.log('Skipped (unsubscribed):', data.skipped);
}
```

## API Reference

```typescript
emails.send(options: {
  to: string | string[];          // required, 1–50 addresses
  subject: string;                // required, 1–500 chars
  html: string;                   // required, HTML body
  cc?: string | string[];         // optional
  bcc?: string | string[];        // optional
  from?: string;                  // optional display name only (NOT email address)
  replyTo?: string;               // optional email address
}): Promise<{
  data: { id: string; skipped?: string[] } | null;
  error: Error | null;
}>
```

### Sender Address Rules

- **`from` is a display name only.** The actual sending address is always `noreply@<appkey>.send.insforge.dev` (your project's SES tenant subdomain). You cannot send from `hello@yourdomain.com`.
- Use `replyTo` to route replies to a real inbox you control.
- The backend appends a per-recipient `List-Unsubscribe` footer and headers automatically — do not add your own.

### Limits

| Limit | Value |
|---|---|
| Max recipients per request | 50 (across `to` + `cc` + `bcc`) |
| Hourly send rate | 10–50 emails depending on plan |
| Subject length | 1–500 chars |
| Plan requirement | Paid plan (free tier returns `On-demand email service is only available for paid plans`) |

Each address in `to`/`cc`/`bcc` counts as one delivery (per SES billing) — a single send to 30 addresses is 30 emails against your quota.

## REST Fallback

If you can't use the SDK (e.g. cURL, server-side calls without the JS SDK), authenticate with a project admin API key (`ik_…`) or a signed-in user's JWT — the anon key is rejected here for the same reason it is rejected in the SDK:

```bash
curl -X POST "$INSFORGE_URL/api/email/send-raw" \
  -H "Authorization: Bearer $INSFORGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "Welcome",
    "html": "<h1>Hello</h1>",
    "from": "Acme",
    "replyTo": "support@acme.com"
  }'
```

Success: `HTTP 200` with body `{}` (REST endpoint omits the wrapping; SDK adds `{ data, error }`).

## Common Errors

| Error message | Cause | Fix |
|---|---|---|
| `On-demand email service is only available for paid plans` | Free tier project | Upgrade billing in the InsForge dashboard |
| `Rate limit exceeded. Try again in N minutes` | Hourly send cap reached | Wait `rateLimit.resetIn` seconds and retry, or upgrade plan |
| `Invalid ARN provided` | Backend infra config issue (missing `AWS_ACCOUNT_ID` env on the cloud backend) | Not a client bug — file with InsForge support |
| `Sending emails requires an authenticated user` (`401 AUTH_INVALID_CREDENTIALS`) | Called with the anon key — no user is signed in | Sign the user in and retry on the same client (the SDK sends their JWT), or call server-side with a project admin API key. Re-checking `anonKey` will not fix this |
| `401 Unauthorized` | Missing, malformed, or expired `Authorization` header | Confirm the header is sent; if a user JWT has expired, refresh the session and retry |
| Email lands in spam | Cold SES tenant reputation | Warm up with a few low-volume sends; use a recognizable display name; avoid spammy HTML and link-heavy bodies |

## Common Mistakes

- **Installing `nodemailer` / `resend` / `sendgrid` / `mailgun` / `postmark` or asking for SMTP credentials.** The built-in service is already wired in — `insforge.emails.send()` is all you need.
- **Trying to set `from` to an email address.** Only the display-name part is honored. The address is fixed.
- **Adding your own unsubscribe link.** The backend already injects one — adding another duplicates UX and confuses ESPs.
- **Treating skipped recipients as failures.** `data.skipped` recipients have unsubscribed; the request still returns success.
- **Sending one big request to 30 unrelated users without per-recipient personalization.** The backend already sends individual messages internally for personalized unsubscribe links — you just pass the array.
- **Calling from the free tier and reporting an "API bug".** Check `subscriptionPlan` first; the rejection is by design.

## Quick Reference

| Task | Code |
|------|------|
| Send to one recipient | `insforge.emails.send({ to, subject, html })` |
| Send to many | `insforge.emails.send({ to: [a, b], cc, bcc, subject, html })` |
| Set sender display name | `from: 'Acme Updates'` |
| Route replies | `replyTo: 'support@acme.com'` |
| Inspect skipped (unsubscribed) | `data.skipped` |
| REST endpoint | `POST {baseUrl}/api/email/send-raw` |
