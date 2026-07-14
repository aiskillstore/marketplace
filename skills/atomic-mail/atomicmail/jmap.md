---
description: Call Atomic Mail JMAP after auth—session discovery, POST to session apiUrl batches, and agent-oriented error hints on auth failures.
---

# Raw JMAP Requests

> **Using MCP or the AgentSkill CLI?** Start with [Getting started](/getting-started), then use the built-in **`help`** command (or MCP **`help`** tool) for presets and copy-paste JMAP recipes. This page is aimed at **direct HTTP JMAP** once you hold a capability bearer token.

After obtaining `capabilityJwt`, run JMAP directly:

- Session discovery: `GET /.well-known/jmap` (on your API host, e.g.
  `https://api.atomicmail.ai/.well-known/jmap`)
- Method calls: `POST` to the **`apiUrl`** string from that session JSON (RFC
  8620); do not assume a fixed path such as `/jmap` unless your session says so.
- Envelope **`using`** vs a bare `methodCalls` array (MCP/CLI defaults): see
  [JMAP `using` and inline ops](/jmap-using).

## Successful responses and `_next`

When you call JMAP through **Atomic Mail MCP** or **AgentSkill**, a successful
JSON body may include a top-level **`_next`** array of short suggested
follow-ups (the same “self-documenting” idea as REST responses in
[`REST authentication flow`](/rest-auth)).

That field is **not** part of RFC 8620’s JMAP response model. If you pipe the
body into a strict JMAP-only tool, ignore unknown top-level keys or strip
`_next` before parsing `methodResponses`.

## Agent hints on authorization failures

For authorization/authentication failures (for example expired or invalid bearer
token), JMAP responses may include agent-oriented hints:

- `error.message`
- `error.hint`
- `error.docs_url`

This hint behavior applies to authorization errors only. Standard JMAP method
errors (business/data validation errors inside `methodResponses`) should be
handled as regular JMAP errors and are not guaranteed to carry agent hint
fields.

## Discover accountId

```bash
curl https://api.atomicmail.ai/.well-known/jmap \
  -H "Authorization: Bearer <capabilityJwt>"
```

Use `primaryAccounts["urn:ietf:params:jmap:mail"]` as your `accountId`.

Session also provides RFC 8620 blob templates:

- `uploadUrl` (contains `{accountId}`)
- `downloadUrl` (contains `{accountId}`, `{blobId}`, `{name}`, `{type}`)

## Send email (JMAP batch)

Minimal **RFC 8621–credible** flow: draft in at least one mailbox, then submit.
Resolve `<inboxMailboxId>` with `Mailbox/query` and `filter: { "role": "inbox" }`
(see [Read inbox](#read-inbox-query-get)).

You may omit `envelope` on `EmailSubmission/set` create; RFC 8621 allows the
server to derive it from the Email’s From/Sender and To/Cc/Bcc. Supplying
`envelope` explicitly (as below) matches common agent and MTA expectations.

```json
{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail",
    "urn:ietf:params:jmap:submission"
  ],
  "methodCalls": [
    [
      "Email/set",
      {
        "accountId": "<accountId>",
        "create": {
          "d1": {
            "mailboxIds": { "<inboxMailboxId>": true },
            "from": [{ "email": "<from@example.com>" }],
            "to": [{ "email": "<to@example.com>" }],
            "subject": "Hi",
            "textBody": [{ "partId": "b", "type": "text/plain" }],
            "bodyValues": { "b": { "value": "Hello." } },
            "keywords": { "$draft": true }
          }
        }
      },
      "c0"
    ],
    [
      "EmailSubmission/set",
      {
        "accountId": "<accountId>",
        "create": {
          "s1": {
            "emailId": "#d1",
            "envelope": {
              "mailFrom": { "email": "<from@example.com>" },
              "rcptTo": [{ "email": "<to@example.com>" }]
            }
          }
        }
      },
      "c1"
    ]
  ]
}
```

## If submission fails: identities (Cyrus JMAP)

Atomic Mail’s mail store uses **Cyrus IMAP’s JMAP**. Many flows omit
**`identityId`** on `EmailSubmission/set` when the server can infer the
identity from the draft’s `from` and/or `envelope`. If you have multiple
identities, wildcards, or you see `invalidProperties` / identity-related errors,
set **`identityId`** explicitly (`Identity/get`, pick the `id` whose `email`
matches the address you send as). See [RFC 8621](https://www.rfc-editor.org/rfc/rfc8621)
for submission semantics.

## Read inbox (query + get)

`inMailbox` must be the JMAP **mailbox id**. Resolve it once with
`Mailbox/query` and `filter: { "role": "inbox" }`, or use the same id the agent
substitutes as `$INBOX_MAILBOX_ID`.

```json
{
  "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:mail"],
  "methodCalls": [
    [
      "Email/query",
      {
        "accountId": "<accountId>",
        "filter": { "inMailbox": "<inboxMailboxId>" },
        "limit": 20
      },
      "q0"
    ],
    [
      "Email/get",
      {
        "accountId": "<accountId>",
        "#ids": { "resultOf": "q0", "name": "Email/query", "path": "/ids" }
      },
      "g0"
    ]
  ]
}
```

For direct HTTP clients, keep request bodies as standard JSON payloads and send
them unchanged to the session **`apiUrl`** with a capability bearer token.

## Attachments: RFC 9404 inline blob flow

Use `Blob/upload` and `Blob/get` on the session **`apiUrl`** with
`urn:ietf:params:jmap:blob` in `using`. Each `Blob/upload` `create` value is an
**UploadObject**: **`data`** is a JSON **array** of **DataSourceObject** entries;
each entry uses **exactly one** of `data:asText`, `data:asBase64`, or `blobId`
(+ optional range). Optional **`type`** is a media-type hint. Invalid shapes
include `data` as a plain string, or `data:asBase64` on the upload object
instead of **inside** an array element. Attach in `Email/set` with `attachments[]`
and **`blobId`** (for example `"#b1"` for create key `b1`) plus **`type`** /
**`name`**.

**Further reading:** [RFC 9404 §4.1](https://www.rfc-editor.org/rfc/rfc9404#section-4.1).

Bundled **`send_mail_attachment.json`** uses
`"data": [{ "data:asBase64": "…" }]` plus **`type`**, as in the example below.

```json
{
  "using": [
    "urn:ietf:params:jmap:core",
    "urn:ietf:params:jmap:mail",
    "urn:ietf:params:jmap:submission",
    "urn:ietf:params:jmap:blob"
  ],
  "methodCalls": [
    [
      "Blob/upload",
      {
        "accountId": "<accountId>",
        "create": {
          "b1": {
            "data": [{ "data:asBase64": "SGVsbG8gYXR0YWNobWVudA==" }],
            "type": "text/plain"
          }
        }
      },
      "b0"
    ],
    [
      "Email/set",
      {
        "accountId": "<accountId>",
        "create": {
          "m1": {
            "mailboxIds": { "<inboxMailboxId>": true },
            "from": [{ "email": "<from@example.com>" }],
            "to": [{ "email": "<to@example.com>" }],
            "subject": "Inline blob",
            "bodyValues": { "body1": { "value": "See attachment." } },
            "textBody": [{ "partId": "body1", "type": "text/plain" }],
            "attachments": [
              { "blobId": "#b1", "type": "text/plain", "name": "note.txt" }
            ]
          }
        }
      },
      "m0"
    ],
    [
      "EmailSubmission/set",
      {
        "accountId": "<accountId>",
        "create": {
          "s1": {
            "emailId": "#m1",
            "envelope": {
              "mailFrom": { "email": "<from@example.com>" },
              "rcptTo": [{ "email": "<to@example.com>" }]
            }
          }
        }
      },
      "s0"
    ]
  ]
}
```

Blob retrieval in-band:

```json
{
  "using": ["urn:ietf:params:jmap:core", "urn:ietf:params:jmap:blob"],
  "methodCalls": [
    [
      "Blob/get",
      {
        "accountId": "<accountId>",
        "ids": ["<blobId>"],
        "properties": ["data:asBase64", "size"]
      },
      "g0"
    ]
  ]
}
```

For **`properties`**, use only names allowed by [RFC 9404 §4.2](https://www.rfc-editor.org/rfc/rfc9404#section-4.2)
(for example `data:asBase64`, `size`). Each result still includes `id`; do not
list `id` or `type` in `properties`.

## RFC 9404 account blob limits

The JMAP session includes per-account blob settings under
`accounts[<accountId>].accountCapabilities["urn:ietf:params:jmap:blob"]` (see
[RFC 9404 §3.1](https://www.rfc-editor.org/rfc/rfc9404#section-3.1)):

- **`maxSizeBlobSet`**: maximum blob size in octets the server allows you to
  create (including concatenated `data` sources). `null` means no advertised
  limit (the server may still reject oversized blobs).
- **`maxDataSources`**: maximum `DataSourceObject` entries per `Blob/upload`
  create.
- **`supportedTypeNames`**, **`supportedDigestAlgorithms`**: used for
  `Blob/lookup` and `Blob/get` digest properties respectively.

**Atomic Mail MCP and AgentSkill** read these values from `GET /.well-known/jmap`
and, when they are present, **reject before POST** any RFC 8620 attachment file
or in-band `Blob/upload` whose size or `data` array length would violate
`maxSizeBlobSet` or `maxDataSources`, with an error that suggests using the
upload endpoint / MCP `attachments` for large binaries when appropriate. Creates
that reference a **literal** (non-`#`) `blobId` slice are not size-checked on the
client because the referenced blob’s length is unknown without a round trip.

## Blob/lookup (RFC 9404)

`Blob/lookup` reverse-maps blob ids to ids of other types (for example `Email`,
`Mailbox`, `Thread`) that reference those blobs. It requires
`urn:ietf:params:jmap:blob` in `using`, plus `accountId`, `typeNames`, and `ids`.
Unknown types or missing capabilities for a requested type yield the
`unknownDataType` error (see [RFC 9404 §4.3](https://www.rfc-editor.org/rfc/rfc9404#section-4.3)).

## Attachments: RFC 8620 upload/download endpoints

For out-of-band blob transfer:

1. Resolve `uploadUrl` / `downloadUrl` from session.
2. Expand URI-template variables (`accountId`, and for download: `blobId`,
   `name`, `type`).
3. Use capability bearer auth for upload/download HTTP requests.
4. Use returned `blobId` in normal JMAP mail methods (`Email/set`, etc.).

This path is useful when a client/tool needs direct binary transport outside
JMAP method calls.
