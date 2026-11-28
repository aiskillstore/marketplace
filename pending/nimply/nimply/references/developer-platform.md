# Nimply developer platform

Snapshot: 2026-11-26. For exact parameters and schemas, read the live docs
(see "Reading the live docs" at the end). This file is the map: what exists,
what it is for, and where the edges are.

## Contents

- The four ways in
- Public surfaces and addresses
- REST API
- Authentication and permissions
- Posts: the core object
- Webhooks
- MCP server
- Designs and brand kits
- What the platform will not do
- Errors, limits and safe retries
- Reading the live docs

## The four ways in

Pick by who is building, not by what is most powerful.

| Who | Use | Why |
|---|---|---|
| A person working in an AI assistant (Claude, ChatGPT, Cursor…) | **MCP server** | Nothing to code. Sign in, approve, talk |
| A non-developer connecting other apps | **Zapier, Make or n8n** | Visual, no code |
| A developer or an internal tool | **REST API + webhooks** | Full control |
| Inside Nimply itself | **Automations** | No outside tool needed; see `automations.md` |

All four act on one workspace with the permissions that were granted, and all
of them go through the same approval rules, plan limits and channel rules as
the app.

## Public surfaces and addresses

| Surface | Address |
|---|---|
| Marketing site | https://nimply.io |
| Web app | https://app.nimply.io |
| REST API | https://api.nimply.io (all routes under `/v1`) |
| MCP server | https://mcp.nimply.io/mcp |
| Developer docs | https://developer.nimply.io |
| API changelog | https://developer.nimply.io/changelog |
| Link-in-bio pages | https://nimply.link/yourname |
| Mobile apps | iPhone (App Store) and Android (Google Play) |
| Browser extension | Nimply Sidekick |

## REST API

Versioned at `/v1`. Within v1, changes are additive: new fields, endpoints and
values may appear; existing ones are not renamed or removed without a
deprecation period. Build clients that ignore fields they do not know.

Resource areas:

| Area | What you can do |
|---|---|
| Workspace | Read the workspace and the permissions the credential has |
| Channels | List connected accounts, their health and posting schedule |
| Posts | Create, read, update, schedule, unschedule, publish, delete; bulk create up to 50; platform-specific create for YouTube, TikTok, Pinterest, LinkedIn |
| Approvals | Request approval, approve, reject with a note |
| Media | Import from a public URL, or upload a file directly; list and delete |
| Analytics | Workspace, channel and post metrics for a date range |
| Webhooks | Manage endpoints and send a test event |
| Link pages | List pages, add and update blocks, publish |
| Designs | Generate a design from a brief, turn an image into editable layers, follow the job, estimate cost |
| Brand kits | Create, fill from a website or several sources, teach a look from examples |
| Agents | Browse templates, hire, change, pause, remove, run, follow runs |
| Automations | Browse recipes and step types, build, test, switch on or off, run |

Channels are connected in the Nimply app, not through the API. An integration
needs the user to have connected at least one account first.

The typical flow: authenticate → list channels → (optionally) upload media →
create a post as a draft, at a time, in the channel's next free slot, or now.

## Authentication and permissions

Two kinds of credential, both tied to **one workspace**:

- **API key** (`nim_live_…`): created in the app under Settings → Developers,
  shown once. For scripts, servers and config-file clients. Send as
  `Authorization: Bearer nim_live_…`. Keep it server-side.
- **OAuth 2.1** (with PKCE and dynamic client registration): for assistants
  and apps acting for a user. The user signs in, picks a workspace and
  approves permissions. Connecting needs an owner or admin. Access is revoked
  in the app under Settings → Connected apps.

The workspace always comes from the credential. No endpoint takes a workspace
id from the caller, so one credential can never reach another workspace. An
agency with ten client workspaces uses ten credentials.

Permissions (scopes). New keys are read-only until write scopes are added:

| Scope | Allows |
|---|---|
| `workspace:read`, `channels:read` | Read the workspace and connected accounts |
| `posts:read` / `posts:write` | Read posts / create, change and delete drafts |
| `posts:publish` | Schedule and publish |
| `media:read` / `media:write` | Read / upload and delete media |
| `analytics:read` | Read metrics |
| `webhooks:manage` | Manage webhook endpoints |
| `links:read` / `links:write` | Read / edit and publish link pages |
| `designs:read` / `designs:write` | Read designs and kits / start design jobs (uses AI credits) |
| `agents:read` / `agents:write` / `agents:run` | Browse / hire and change / run agents (runs use AI credits) |
| `automations:read` / `automations:write` | Browse / build, test, switch and run automations |

Recommend the smallest set that does the job. A reporting dashboard needs
only read scopes. Leaving out `posts:publish` guarantees an integration can
draft but never post.

Scopes are not the only gate. Some actions also need a workspace role (for
example only owners and admins can switch an automation on), and some need a
paid plan or trial (agent runs, design jobs, link-page analytics).

## Posts: the core object

One post belongs to one channel. Posting the same thing to five accounts is
five posts (the bulk endpoint handles that).

Status lifecycle:

```
DRAFT → PENDING_APPROVAL → SCHEDULED → PUBLISHED
                 ↓ reject        ↘ FAILED
               DRAFT
```

- Approving a post that has a future time schedules it; without a time it
  returns to draft.
- "Publish now" passes through SCHEDULED. Publishing is asynchronous: poll the
  post, or better, listen for the `post.published` / `post.failed` webhook.
- A published post cannot be edited or deleted through the API (Telegram is
  the exception).
- Posts made outside Nimply can appear as read-only, external posts.

Content types: a standard post (several media make a carousel), reel, story,
video. Video posts can set a custom thumbnail or a cover frame.

## Webhooks

Nimply calls your URL when something happens, so you do not have to poll.

Events:

- Posts: `post.created`, `post.updated`, `post.published`, `post.failed`,
  `post.deleted`, `post.approval_requested`, `post.approved`, `post.rejected`
- Channels: `channel.connected`, `channel.disconnected`
- Leads: `lead.created`, `lead.stage_changed`

Every delivery has the same envelope:

```json
{
  "id": "evt_…",
  "type": "lead.created",
  "createdAt": "2026-11-26T10:15:00Z",
  "workspaceId": "…",
  "data": { }
}
```

- Post events carry `data.postId`, `channelId`, `status`, `publishedAt`,
  `postUrl` and `error`.
- Lead events carry `data.lead` with `id`, `person_id`, `name`, `handle`,
  `profile_url`, `platform`, `source`, `temperature`, `interest`, `stage`,
  `value`, `currency`, `follow_up_at`, `contact_email`, `contact_phone`,
  `lost_reason`, `created_at`, `updated_at`. `lead.stage_changed` adds
  `previous_stage`.
- Headers: `X-Nimply-Event` (the type), `X-Nimply-Delivery` (the event id,
  the same on every retry) and `X-Nimply-Signature`.

Leads reach the outside world through these webhooks only; there is no
endpoint that lists leads.

What a receiver must do:

- **Verify the signature.** The header looks like
  `X-Nimply-Signature: t=<unix seconds>,v1=<hex>`, where `v1` is the
  HMAC-SHA256 of `"{t}.{raw body}"` made with the endpoint's secret
  (`whsec_…`). Compute it over the raw body, before parsing. Compare in
  constant time and reject old timestamps (about five minutes).
- **Answer 2xx within 15 seconds.** Do slow work after responding.
- **Expect retries and duplicates.** A failed delivery is tried five times in
  all, with growing delays. Events can arrive out of order or, rarely, twice, so
  de-duplicate on the envelope id.
- **Watch for auto-disable.** An endpoint that keeps failing is switched off
  and must be re-enabled.

Lead webhooks are how a CRM or sheet stays in sync without Nimply exposing
the inbox: the lead (name, handle, interest, stage, contact details) is sent,
the conversation is not.

## MCP server

A hosted server (Streamable HTTP, nothing to install) that gives an AI
assistant about 70 tools over the same API. Connect with OAuth where the
client supports connectors, or with an API key header in config-file clients.

Tool groups: channels, posts and platform-specific posting, media, approvals,
analytics, link pages, designs, brand kits and learned brand look, agents,
automations.

Supported clients with a setup guide each: claude.ai, Claude Desktop, Claude
Code, ChatGPT, Grok, Perplexity, Cursor, VS Code, Windsurf, Codex CLI, Gemini
CLI, OpenClaw, Raycast, and any other MCP client.

Fastest setup lines:

```bash
# Claude Code
claude mcp add --transport http nimply https://mcp.nimply.io/mcp
```

```json
{ "mcpServers": { "nimply": { "url": "https://mcp.nimply.io/mcp" } } }
```

In claude.ai and ChatGPT: add a connector with the server URL, sign in to
Nimply, choose a workspace, approve.

Behaviour to expect and to respect when operating it:

- Nimply receives the tool calls, never the conversation.
- Create posts as drafts unless the user gave a time or said to publish.
- Approve a post only when the user says so.
- Design and agent jobs are asynchronous: start, poll, then show the preview
  and the edit link.
- Check the estimated credits before starting a design and tell the user.
- Build automations as drafts, test, and switch on only after the user agrees.

## Designs and brand kits

- **Create a design** from a written brief, in up to three sizes, using a
  brand kit. The result is an editable design with a preview image and a link
  that opens it in the Nimply editor. Carousels go up to 7 slides.
- **Image to editable layers:** turn a flat image into a design with separate
  text, object and background layers.
- **Brand kits:** logo, colours, fonts, voice. Fill one from a website, or
  from several sources at once (website, pasted text, a PDF brand book, a
  connected channel, images).
- **Learned look:** give a kit three or more of the brand's own posts or
  images and Nimply learns the look; the owner can add their own rules.

Design jobs and learning use AI credits and need a paid plan or trial. An
estimate endpoint returns the cost before anything runs. Designs are saved to
the workspace and are never published on their own.

## What the platform will not do

State these plainly when a request runs into them. They are deliberate.

- **No inbox through the API or MCP.** Nothing reads or sends DMs or
  comments. Inbox agents and inbox automation steps can be set up, but
  messages stay in the app. Use lead webhooks to get outcomes out.
- **No text or caption generation endpoint.** Design generation is available;
  writing is not. An assistant using the MCP server writes the text itself.
- **No switching off human checks from outside.** Auto-reply, autopilot,
  unreviewed scheduling by agents, and Comment-to-DM activation are set in
  the app only.
- **No connecting social accounts through the API.** That happens in the app.
- **No billing actions.** Plans and credits are managed in the app.
- **No cross-workspace credentials.** One credential, one workspace.

On the docs roadmap as ideas only, with no commitment: organisation-level
keys across workspaces, CSV report exports, an Inbox API. Do not promise
them.

## Errors, limits and safe retries

- Errors are RFC 9457 problem details (`application/problem+json`) with a
  machine-readable `code`. Useful ones: `MISSING_FIELDS` (ask the user and
  resend), `SET_IN_APP` (comes with a link to the right app screen),
  `INSUFFICIENT_CREDITS` (402, says how many are needed and available),
  `PAID_PLAN_REQUIRED`, `INSUFFICIENT_ROLE`.
- A resource in another workspace returns 404, not 403.
- Requests are rate-limited per key per minute. Read the `X-RateLimit-*`
  headers and honour `Retry-After` on a 429 instead of hard-coding a number.
  Starting agent runs, design jobs and automation runs has tighter limits
  (about 10 a minute).
- Send an `Idempotency-Key` header on writes so a retry cannot create a
  second post. Responses are remembered for 24 hours.
- Lists use cursor pagination (`limit` and `cursor`, then `nextCursor`).
- Signed media URLs expire after 24 hours; do not store them.

## Reading the live docs

The developer docs are built to be read by assistants. When a question needs
exact field names, current tool lists or anything that may have changed, fetch
instead of guessing:

- Index of every page: https://developer.nimply.io/llms.txt
- Everything in one file: https://developer.nimply.io/llms-full.txt
- One page as Markdown:
  `https://developer.nimply.io/llms.mdx/docs/<page>/content.md`, where
  `<page>` is for example `quickstart`, `authentication`, `webhooks`,
  `errors`, `mcp`, `agents`, `automations`, `designs`, `brand-kits`,
  `link-pages`, `data-model`
- Worked examples (carousel, reel, bulk from CSV, client approval flow,
  webhook receiver…): the `examples/` pages listed in the index
- What changed and when: https://developer.nimply.io/changelog
