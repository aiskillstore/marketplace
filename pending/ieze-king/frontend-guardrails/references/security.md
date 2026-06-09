# Security (detail)

Read this for any work touching authentication, user data, environment variables, tokens, or rendering untrusted content. Core principle: **assume everything shipped to the browser is readable by anyone.**

## Never put secrets in frontend code
API keys, broad-scope tokens, passwords, and credentials live on the server only — never in the bundle and never in client-exposed env vars. Note that "public" env prefixes ship to the browser (e.g. `NEXT_PUBLIC_`, `VITE_`, Nuxt `runtimeConfig.public`, Angular `environment.ts`). Secrets must use server-only config and run only in server code.

## The frontend reflects authorization; the backend enforces it
Route guards, hidden buttons, and disabled fields are UX, not security. Every protected action must be re-checked by the backend on each request. Never assume "the UI hides it" means it is protected — a user can call the API directly.

## Least data exposure
Request and render only the fields you actually display. Do not fetch a full record and hide fields with CSS — the hidden data still sits in the browser. This matters most for personal data: contact details, exact private addresses, payment info, internal IDs. Design API responses to return the minimum.

## Prevent XSS (cross-site scripting)
Avoid injecting raw, unsanitized HTML: `dangerouslySetInnerHTML` (React), `v-html` (Vue), `bypassSecurityTrustHtml` (Angular), `innerHTML` (plain JS). If unavoidable, sanitize first (e.g. DOMPurify). Untrusted HTML in the DOM lets attackers run scripts in your users' browsers, steal sessions, and act as the user.

## Token storage
Prefer httpOnly cookies for session tokens over `localStorage`/`sessionStorage`, because scripts cannot read httpOnly cookies — which limits the damage if an XSS hole ever appears. Pair with `Secure` and `SameSite` attributes.

## Transport
Always use HTTPS for any data exchange. Never send credentials or tokens over plain HTTP.

## Quick checklist
- [ ] No secrets in client code or client-exposed env vars.
- [ ] Backend re-checks authorization on every protected action.
- [ ] Only displayed fields are fetched and sent to the client.
- [ ] No unsanitized HTML injection anywhere.
- [ ] Tokens in httpOnly + Secure + SameSite cookies where possible.
- [ ] All traffic over HTTPS.
