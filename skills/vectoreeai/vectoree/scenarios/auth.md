# App Auth (your users)

Use this playbook for **C09**. Parent skill: `SKILL.md` in this folder.

**Not the same as logging into Vectoree Cloud.** If the developer said "登录一下 Vectoree" / `vectoree login` / open the Cloud dashboard, that is **S01**. Stop this playbook.

Need a project API key first (`scenarios/connect.md`). Need `@vectoree/cli` ≥ **0.1.11** (`npx`).

Two login systems (do not mix):

| | Vectoree Cloud (you / CLI) | Auth product (your app's users) |
|---|---|---|
| Who | Developer, org, `vectoree login` | People who use the app you are building |
| API prefix | `/api/system/auth/*` | `/api/auth/*` |
| Users | `system.users` | `auth.users` (per project) |
| CLI | `login` / `whoami` | `auth status` / `snippet` / `open` |
| Mail | Platform SMTP (console) | Resend (org wallet ≈ $0.0005 / send) or project SMTP |

Docs: https://docs.vectoree.ai/auth · `npx @vectoree/cli docs get auth-sdk`

---

## Hard rules (C09 first)

1. Identity lives in Vectoree `auth.users`. **Do not** `CREATE TABLE users` or `accounts`.
2. On business tables, `user_id` = Auth JWT `sub` (`aud=app`).
3. **Never** call `POST /api/system/auth/signup` (or any `/api/system/auth/*`) from the app. That is Console registration.
4. Do not copy `/dashboard/login` into the product UI.
5. Do not write OAuth Client Secret into the repo. Do not reuse Vectoree Cloud Google/GitHub keys for the app.
6. Email verification is on by default (**8-digit** code). App-user mail is Resend (billed to the org wallet). Console mail is unrelated.
7. **Credentials for custom UI (what `auth snippet` teaches):**
   - Browser → **your BFF only**. Never put `VECTOREE_API_KEY` / `sk-ve-v1-…` in `NEXT_PUBLIC_*` or the bundle.
   - BFF → Vectoree with a project API Key that has `auth:*` (`Authorization: Bearer …`).
   - The key selects the project; Auth endpoints do **not** take `X-Project-Id`.
8. **`pk_…` (publishable key)** is safe in the browser for hosted Auth UI / public data-plane use. It is **not** a substitute for the BFF secret on App Auth register/verify REST. Do not call Gateway (`/api/v1/*`) with `pk_`.

---

## C09: add login to *my* app

```bash
npx @vectoree/cli auth status
npx @vectoree/cli docs get auth-sdk
```

Email + password is already on. Google/GitHub: if `auth status` shows no oauth providers, **stop and tell the owner** to open:

- https://vectoree.ai/dashboard/authentication/auth-methods
- https://docs.vectoree.ai/auth

or run `npx @vectoree/cli auth open`. They paste **their** Client ID/Secret. Then continue.

```bash
npx @vectoree/cli auth snippet --ui
npx @vectoree/cli auth snippet --rest --lang ts
# --no-ui is an alias of --rest
```

- `--ui` — browser form that posts only to **your** `/api/app-auth` BFF, plus a server route that holds `VECTOREE_API_KEY`.
- `--rest` / `--no-ui` — server-side REST examples (TS or Python). Prefer this for custom backends.

### Runtime paths (server / BFF with `auth:*` key)

- `POST /api/auth/users` — register (**already emails** the 8-digit code when verification is on)
- `POST /api/auth/sessions` — password login (also emails a code if still unverified, then 403)
- `POST /api/auth/email/send-verification` — **resend only**; do not call right after register/login or the user gets two OTPs
- `POST /api/auth/email/verify` — body field `otp`, 8 digits
- `GET /api/auth/oauth/google` or `/github` — only after the owner configured them
- `GET /api/auth/methods` — what `auth status` uses

After verify/login, keep the App JWT (`accessToken`) for the end user. Business tables: `user_id` = JWT `sub`.

C09 done when the app can register, verify the 8-digit code, and never exposes the project secret to the browser.
