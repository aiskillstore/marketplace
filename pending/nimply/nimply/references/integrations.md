# Nimply integrations and ecosystem

Snapshot: 2026-11-26. Setup guides for each one:
https://developer.nimply.io/docs/integrations

## Contents

- How to choose
- AI assistants (MCP)
- No-code platforms: Zapier, Make, n8n
- Team tools: Slack and Telegram
- Messaging channels: WhatsApp Business and Telegram
- CRM and data: HubSpot, Google Sheets
- Design and media sources
- Nimply Sidekick (browser extension)
- Common patterns

## How to choose

| The need | Use |
|---|---|
| "Let my AI assistant run my social media" | MCP server |
| "When X happens in Nimply, do Y in another app" | Zapier, Make or n8n; or a webhook |
| "When X happens in another app, post in Nimply" | Zapier, Make or n8n actions; or the API |
| "Tell my team when a post is live or needs approval" | Slack or Telegram |
| "Get leads into my CRM" | HubSpot; or lead webhooks; or n8n |
| "Let the reply agent use my price list" | Google Sheets |
| "Use my Canva designs" | Canva import |
| "Save things I see while browsing" | Nimply Sidekick |

If the need can be met inside Nimply with an automation, prefer that: one
less tool to pay for and maintain.

## AI assistants (MCP)

One hosted server, https://mcp.nimply.io/mcp. See `developer-platform.md` for
what it can do.

| Client | How it connects |
|---|---|
| claude.ai, Claude Desktop | Sign in with Nimply (OAuth connector). Nimply is in the Claude connectors directory |
| ChatGPT | Sign in with Nimply; needs a ChatGPT plan with connector support |
| Grok | Sign in with Nimply as a custom connector; a Grok Build plugin also exists |
| Claude Code | Sign in or API key |
| Cursor, VS Code (Copilot agent mode), Windsurf, Codex CLI, Gemini CLI, Perplexity, OpenClaw, Raycast | API key in the client's config |
| Any other MCP client | Covered by a generic guide, including stdio-only clients |

Connecting needs a workspace owner or admin.

## No-code platforms

All three can both react to Nimply and act in Nimply.

### Zapier

- Sign in with Nimply.
- **Triggers** (instant): post published, post failed, post approval
  requested, post approved, post rejected, channel disconnected.
- **Actions:** create a post (and platform-specific YouTube, TikTok,
  Pinterest, LinkedIn versions), upload media, update, schedule, unschedule,
  publish now, delete, request approval, approve, reject, add a link-page
  block.
- **Searches:** find a channel, a post or a link page; get workspace
  analytics.
- No lead, agent or automation triggers.
- Listing in Zapier's public directory is in progress; check the Zapier guide
  for how to get access today.

### Make

- Sign in with Nimply.
- **Watch Events** (instant) for post and channel events.
- **Modules:** create a post (and platform-specific versions), update,
  schedule, unschedule, upload media from a URL or as a file, list channels,
  add a link block, list and publish link pages.
- No lead events.
- In Make's review; available as a custom app in the meantime.

### n8n

- The widest coverage of the three.
- Community node `@nimply/n8n-nodes-nimply` (on npm; community nodes need
  self-hosted n8n). On n8n Cloud use the built-in HTTP Request and Webhook
  nodes with an API key.
- **Resources:** posts (including bulk and approvals), channels, media,
  analytics, link pages, designs, brand kits, **agents** (hire, run, follow
  runs) and **automations** (build, test, switch on, run).
- **Nimply Trigger:** every webhook event including leads, with signature
  checking built in.

Recommend n8n when the workflow involves agents, designs or leads; Zapier or
Make when it is about posts and approvals and the team already uses them.

## Team tools

### Slack

Alerts when a post is published, fails, needs approval, or a channel
disconnects. Approve and Reject buttons work inside Slack for owners and
admins. Connect in Settings → Integrations.

### Telegram alerts bot

The same alerts and approve / reject buttons, plus commands to check status,
the queue and what is pending. Text sent to the bot in a private chat becomes
a draft post. One chat per workspace.

Both are good answers to "my client / boss needs to approve posts but won't
log in".

## Messaging channels

### WhatsApp Business

- **Inbox only.** Customer conversations arrive in the Nimply Inbox and reply
  agents can answer them. Nimply does not publish to WhatsApp and does not
  send broadcasts or marketing campaigns.
- Connected through Meta's official sign-up. It can run alongside the
  WhatsApp Business phone app.
- Replies follow Meta's rule: free-form replies within 24 hours of the
  customer's last message.
- Needs a paid plan; the number of WhatsApp numbers depends on the plan.
- Nimply adds no per-message fee. Meta bills its own delivery charges
  directly.

### Telegram channels and groups

- A full publishing channel: albums, polls, buttons, silent posts, pinning,
  auto-delete, and editing or removing a post after it is published.
- Also an inbox channel, and Telegram Business for personal DMs.
- Community tools through automations: join-request approval, welcomes,
  moderation, muting and banning.

## CRM and data

### HubSpot

Leads captured in Nimply that have an email or phone are sent to HubSpot
contacts, and the lead's stage is kept in step. Connected in Settings →
Integrations.

### Google Sheets

Reply agents can read a sheet the business already keeps (prices, menu,
stock, opening hours) at the moment they answer. Read-only. This is the
simplest way to keep an agent's answers current: the owner edits the sheet,
the agent's answers change.

For other CRMs or sheets, use lead webhooks or the n8n trigger.

Do not overstate these two. HubSpot is a lead sync, not campaign or reporting
integration. Google Sheets is for agents to read facts, not a way to turn a
spreadsheet into scheduled posts; for that, use bulk upload from a CSV file
in the Planner, or the API's bulk endpoint. Airtable and Notion integrations
do not exist.

## Design and media sources

- **Canva:** import designs into the Nimply media library as images, reopen
  them in Canva, re-import the latest version.
- **Google Drive, OneDrive, Dropbox, Google Photos:** pick files straight into
  the media library.
- **Unsplash:** free stock photos, no account needed.

## Nimply Sidekick (browser extension)

Available from the Chrome Web Store (which also covers Brave, Vivaldi and Arc)
and for Safari on the Mac App Store. Edge, Firefox and Opera versions are
coming soon. It works in the browser's side panel.

- Keep a post you are looking at as an idea
- Write a post from it
- Get help drafting a reply (copied to the clipboard for you to paste)
- Save an image to the media library
- Save a person as a lead

It never posts, likes, comments, follows or messages on your behalf, and it
never changes the page. That is a design rule, not a missing feature.

## Common patterns

**Client approval without a login.** Agency drafts posts → request approval →
client gets a Slack or Telegram message with Approve / Reject → approved posts
schedule themselves.

**Blog to social.** New article in a feed → "news site visuals" recipe makes a
carousel draft → approve → published. No outside tool needed.

**Store to social.** New product in a shop platform → Zapier or Make → create
a Nimply draft with the product photo → approve.

**Leads to CRM.** Sales & Lead Agent captures a lead in DMs → HubSpot
directly, or `lead.created` webhook / n8n trigger → any CRM or sheet.

**Assistant as the social media manager.** Connect the MCP server → "plan
next week" → drafts land in the Planner for approval → "what performed best?"
from analytics.

**Video once, everywhere.** Post a video in Instagram as usual → Everywhere
copies it to the other channels for approval.

**Failure safety net.** "Failure triage" recipe plus a Slack alert, so a
disconnected account is noticed the same day.
