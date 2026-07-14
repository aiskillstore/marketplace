---
description: How the JMAP envelope `using` array interacts with MCP/CLI defaults and bare methodCalls arrays (RFC 8620).
---

# JMAP `using` and inline ops

RFC 8620 requires each JMAP request to include a **`using`** array: the set of
capability URNs that apply to **all** method calls in that batch. If a method
belongs to a URN you did not declare, the request is not valid for a
standards-following server.

## Full envelope vs bare `methodCalls`

Clients may send either:

1. **Full envelope:** `{ "using": ["urn:ietf:params:jmap:core", ...], "methodCalls": [...] }`
2. **Bare array:** `[["Email/query", {...}, "q0"], ...]` — the host then supplies
   a default `using` for the envelope it builds.

Atomic Mail **MCP** (`jmap_request`) and **AgentSkill / CLI** use the same
default `using` when you pass only a bare `methodCalls` array:

- `urn:ietf:params:jmap:core`
- `urn:ietf:params:jmap:mail`

That pair covers **Mailbox/***, **Email/***, **Thread/***, **SearchSnippet/***,
and other types declared under the mail capability. For built-in recipes and
when to add more URNs, use **`help --topic jmap_cheatsheet`** (CLI) or the MCP
`help` tool with topic **`jmap_cheatsheet`**.

## Pitfall: submission, identity, and blob methods

If you pass a **bare `methodCalls` array** (no envelope) and rely on the default
`using`, you **must** extend `using` whenever the batch includes methods that
need other URNs, for example:

| Methods (examples) | Add to `using` |
| -------------------- | -------------- |
| `EmailSubmission/*`, `Identity/*` | `urn:ietf:params:jmap:submission` |
| `Blob/upload`, `Blob/get`, `Blob/lookup` | `urn:ietf:params:jmap:blob` |

Ways to do that:

- Put a full **`{ "using": [...], "methodCalls": [...] }`** object in `ops` /
  your JSON file, with every URN you need; or
- **MCP:** set the tool’s **`using`** input array so it includes `submission`
  and/or `blob` in addition to core and mail when your inline ops need them; or
- Use **bundled presets** (for example `send_mail.json`), which already embed the
  correct `using` for their method calls.

For a narrative send/read example, see [`Raw JMAP requests`](/jmap).
