# Nimply product map

Snapshot: 2026-11-26.

## Contents

- How the pieces fit
- Networks: what works where
- Planner
- Inbox
- Visor
- Nimply Design, Brand Kits and Magic Layers
- Ideas and feeds
- Analytics
- Nimply Pages
- People, leads and memberships
- Workspaces, teams and roles
- Mobile apps and Sidekick
- Help and support

## How the pieces fit

```
                 ┌─────────────── Agents ───────────────┐
                 │ reply · leads · moderate · write ·   │
                 │ design · video · ideas               │
                 └──────────┬───────────────┬───────────┘
        drafts for approval │               │ suggested replies, leads
                            ▼               ▼
  Ideas ─► Nimply Design ─► Planner       Inbox ─► People & Leads
              (Brand Kit)     │             ▲
                              ▼             │
                    Connected social accounts ─► Analytics
                              ▲
        Automations glue any of these together · Visor drives them by chat
        API · MCP server · webhooks · Zapier / Make / n8n reach in from outside
```

The Planner and Inbox are the two rails everything runs on. Agents put drafts
in the Planner and suggestions in the Inbox; people approve; Nimply publishes.

## Networks: what works where

Check this before promising anything. What a network allows changes, and the
user's own channel list (through `list_channels`, or the app) is the final
word.

| Network | Publish | Inbox | Comment-to-DM | Analytics |
|---|---|---|---|---|
| **Instagram** (Business or Creator accounts) | Posts, carousels, Reels, Stories | DMs, comments, mentions | Yes | Yes |
| **Facebook Pages** | Posts, Reels, Stories | DMs, comments, mentions | Yes | Yes |
| **TikTok** | Video, photo carousels | Comments only | No | Yes |
| **YouTube** | Videos and Shorts, with title, tags, privacy, custom thumbnail | Comments | No | Yes |
| **LinkedIn personal profiles** | Posts, multi-image posts, PDF document carousels | No | No | No |
| **X** | Text, images, video | DMs, replies, mentions (optional, per account) | No | Optional, per account |
| **Pinterest** | Image, video and carousel pins, with board and link | No | No | Yes |
| **Threads** | Text, image, video, carousel | Replies and mentions | No | Yes |
| **Telegram channels and groups** | Text, media, albums, polls; edit or delete after posting | Comments, group messages | No | Yes |
| **Telegram Business / your own bot** | No | DMs | No | No |
| **WhatsApp Business** | No | Customer chats | No | No |

Things people assume that are not so:

- **Personal Instagram accounts** cannot be connected. The account must be a
  Business or Creator account (free to switch in Instagram).
- **Facebook Groups and personal Facebook profiles** are not supported.
- **LinkedIn company Pages** are coming soon. Personal profiles work today.
- **Google Business Profile** is not available.
- **Bluesky and Mastodon** are not supported.
- **WhatsApp is inbox only:** no posting, no broadcasts.
- **X costs AI credits.** X charges for its API, so publishing to X and the
  optional X inbox and X analytics use credits. The app shows the cost.
- **The Inbox is switched on per account.** A channel only brings in
  conversations after its inbox toggle is turned on. Facebook and Instagram
  accounts connected long ago may need reconnecting once.

## Planner

The content calendar. Plan, approve and schedule posts to every connected
account from one place.

- Calendar and list views; drafts, approval, scheduled, published.
- **Approval workflow:** send a post for approval, approve or reject with a
  note. Works from the app, mobile, Slack or Telegram.
- **Posting slots and best times:** each account has a weekly schedule of
  slots; "next free slot" fills the queue without picking times.
- Bulk upload from a CSV file; recurring and evergreen posts; first comments;
  hashtag sets; content categories.
- Previews of how a post will look on each network.
- Video covers and custom thumbnails.

## Inbox

Every DM, comment and mention from supported networks in one place.

- AI sorts conversations (question, complaint, lead and so on) and suggests
  replies.
- Assign to teammates, tags, saved replies, status and priority, response-time
  targets, translation.
- Comment tools on supported networks: hide, delete, reply privately.
- Reply agents work here (see `agents.md`).

The Inbox is in the app and mobile only. It is not reachable through the API
or the MCP server.

## Visor

The assistant built into Nimply, on web and mobile. Type or speak what you
need: "plan next week's posts", "make a carousel about our new menu", "set up
an agent to answer DMs". Visor proposes posts, ideas, designs and agents as
cards the user confirms. Nothing is created without an OK.

The free plan has basic Visor. Voice, the stronger AI models and the image
and design tools need a paid plan.

Visor is inside Nimply. To use Nimply from another assistant (Claude, ChatGPT,
Cursor), connect the MCP server instead.

## Nimply Design, Brand Kits and Magic Layers

- **Editor:** a browser design editor with a large template library
  (https://nimply.io/templates and https://nimply.io/design), sizes for every
  network, fonts, charts and mockups. Import PSD, SVG or images; export PNG,
  JPG, WebP, PDF or SVG. Designs go straight to the Planner.
- **Brand Kits:** logo, colours, fonts and voice. Several kits per workspace,
  one assignable per channel. Fill a kit from a website or from several
  sources at once. Nimply can **learn the look** from three or more of the
  brand's own posts.
- **AI design:** describe what you want, get an editable design in the brand
  kit.
- **Magic Layers:** turn a flat image into an editable design with separate
  text, objects and background.
- Also in the studio: AI post writer, AI images, thumbnails, carousels, and
  video editing (clips, captions, resizing).

Not available: video or GIF export from the design editor, and several people
editing one design at the same moment.

The editor is in every plan. The AI tools use credits and need a paid plan or
trial.

## Ideas and feeds

- An Ideas board where ideas become posts in one click.
- Feeds of industry articles to draw from; any website's feed can be followed.
- Trend Scout (an agent) fills the board on a schedule.

## Analytics

Followers, views and engagement per account and per post, best-time heatmap,
AI takeaways, export. Covers Instagram, Facebook, TikTok, YouTube, Pinterest,
Threads and Telegram channels, plus X when switched on for an account.
LinkedIn personal profiles have no analytics.

The free plan sees the last 30 days.

## Nimply Pages

Link-in-bio pages at nimply.link/yourname, built into the same tool.

- Page types: link in bio, booking page, menu, media kit, digital business
  card, event page.
- Templates, an AI first draft, forms that feed People, page statistics.
- Blocks include links, text, post cards, products, coupons, countdowns,
  notice bars, FAQs and testimonials.
- Changes are drafts until the page is published.
- Paid plans remove the "Made with Nimply" badge and add full analytics and
  tracking pixels. A custom domain is on the Agency plan.
- Selling directly from a page (checkout) is not available.

## People, leads and memberships

- **People:** one record for everyone who talks to the business across
  channels, with tags and notes.
- **Leads:** a pipeline with stages (new, contacted, qualified, proposal, won,
  lost). Leads come from reply agents, from Nimply's suggestions that a person
  confirms, from page forms and from Sidekick.
- **Memberships:** tools for running a gated Telegram community, with the
  Community Concierge agent answering member questions. This is a specialised
  feature; do not describe it as a general paywall or subscription checkout.

## Workspaces, teams and roles

- A **workspace** holds one brand's accounts, posts, team, credits and plan.
  Each workspace has its own subscription.
- Agencies and freelancers use **one workspace per client**, which keeps
  accounts, approvals, brand kits and credit use separate.
- Roles: **Owner, Admin, Editor, Viewer**. Editors create and change content;
  owners and admins switch automations on, connect integrations and manage
  the team.
- Nimply is not white-labelled: there is no custom-branded app or client
  portal. Clients approve through the app, Slack or Telegram.

## Mobile apps and Sidekick

- **iPhone and Android apps:** plan and approve posts, answer the inbox,
  manage agents, talk to Visor.
  - App Store: https://apps.apple.com/app/nimply-social-media-manager/id6803057414
  - Google Play: https://play.google.com/store/apps/details?id=io.nimply.app
- **Nimply Sidekick:** browser extension for saving posts and ideas and
  drafting replies from the side panel. See `integrations.md`.

## Help and support

- Help center: https://nimply.io/help
- Getting-started lessons: https://nimply.io/learning
- Email: hello@nimply.io. Live chat in the app on every plan.
- Pages by business type: `https://nimply.io/industries/<type>`,
  by role: `https://nimply.io/roles/<role>`,
  by task: `https://nimply.io/use-cases/<task>`.
