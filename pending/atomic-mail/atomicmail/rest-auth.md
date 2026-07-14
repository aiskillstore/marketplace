---
description: HTTP-only signup and login—PoW challenge, session JWT, capability JWT, and token TTLs for calling JMAP without MCP or AgentSkill.
---

# REST Authentication Flow

Use this path when you are integrating directly over HTTP, including custom
client libraries and non-wrapper runtimes.

Base URLs:

- Auth: `https://auth.atomicmail.ai`
- API: `https://api.atomicmail.ai`

## PoW and token flow

1. `POST /api/v1/challenge` -> receive challenge JWT in `Authorization: Bearer <challengeJWT>`.
2. Solve `scrypt` PoW locally.
3. `POST /api/v1/session` with challenge JWT in `Authorization` and PoW payload in JSON body.
   Receive session JWT from response `Authorization: Bearer <sessionJWT>`.
4. `POST /api/v1/capability` with session bearer.
   Receive capability JWT from response `Authorization: Bearer <capabilityJWT>`.
5. Use capability JWT for JMAP requests.

Token TTLs:

- Session JWT: 1 hour
- Capability JWT: 2 minutes

## Agent hints in auth responses

Authentication endpoints are designed to be self-guiding for agents.

- Auth errors include:
  - `error.message` (what failed)
  - `error.hint` (how to fix and retry)
  - `error.docs_url` (deep link to relevant docs)
- Successful auth responses may include `_next`, a list of suggested follow-up
  steps (for example: request capability JWT, then call JMAP).

Example error shape:

```json
{
  "error": {
    "message": "Invalid or expired challenge",
    "hint": "Request a fresh challenge from POST /api/v1/challenge, solve PoW again, and retry.",
    "docs_url": "https://atomicmail.ai/llms.txt#auth-flow-reference"
  }
}
```

Example success hint shape:

```json
{
  "_next": [
    "Acquire the capability JWT by presenting your session JWT at POST /api/v1/capability",
    "Refresh it every 2 minutes",
    "Use it as a bearer auth token for JMAP requests"
  ]
}
```

## Request challenge JWT

```bash
curl -i -X POST https://auth.atomicmail.ai/api/v1/challenge
```

Read challenge JWT from response header:

```http
Authorization: Bearer <challengeJWT>
```

## Create session JWT

```bash
curl -X POST https://auth.atomicmail.ai/api/v1/session \
  -H "Authorization: Bearer <challengeJWT>" \
  -H "Content-Type: application/json" \
  -d '{"powHex":"<powHex>","nonce":"<nonce>","username":"myagent"}'
```

Read session JWT from response header:

```http
Authorization: Bearer <sessionJWT>
```

For login with an existing API key, send:

```json
{"powHex":"<powHex>","nonce":"<nonce>","apiKey":"<apiKey>"}
```

## Create capability JWT

```bash
curl -X POST https://auth.atomicmail.ai/api/v1/capability \
  -H "Authorization: Bearer <sessionJwt>"
```

Read capability JWT from response header:

```http
Authorization: Bearer <capabilityJWT>
```

Continue with [`Raw JMAP requests`](/jmap) to execute mail method
calls after capability token issuance.
