# Nimply automations

Snapshot: 2026-11-26. When the Nimply MCP server is connected,
`list_automation_recipes` and `list_automation_step_types` are the source of
truth; prefer them over this file.

## Contents

- What an automation is
- Ready-made recipes
- Building blocks: triggers, actions, logic
- Comment-to-DM
- Everywhere (copy a new video to your other channels)
- Testing and switching on
- Limits
- What an AI assistant or the API may and may not do

## What an automation is

A visual "when this happens, do that" flow: one trigger, then steps. It is the
glue between Nimply's parts: a published post can hand off to an agent, a
comment can start a DM, a schedule can run an agent every Monday.

Automations have three states: draft, on, paused. A new automation is always a
draft and does nothing until someone switches it on.

To a non-technical user, describe the outcome ("everyone who comments LINK
gets your link by DM"), not the flow.

## Ready-made recipes

Start from a recipe whenever one fits. It is faster and already tested.

| Recipe | What it does |
|---|---|
| **Comment-to-DM** | DMs a link to anyone who comments a keyword (Instagram and Facebook) |
| **Everywhere** | Copies each new video you post on one channel to your other channels, waiting for approval |
| **Run an agent when a post publishes** | Hands each published post to an agent, for example the Content Repurposer |
| **Daily trend carousel** | Every morning Trend Scout finds a topic and the Designer makes a carousel for approval |
| **Daily trend design** | Same, for a single design; skips a trend it designed in the last week |
| **Weekly ad refresh** | Every Monday Ad Creative Studio makes a new set of ads. Nothing is posted or run as an ad |
| **News site visuals** | Each new article from a feed you follow becomes a carousel draft |
| **Website visuals by webhook** | Your website pings Nimply and an image is drafted (set up in the app) |
| **Failed post alert** | Tells you in the app when a post fails, with the channel and the reason |
| **Failure triage** | If a post failed because an account needs reconnecting, says so; otherwise a general alert |
| **Publish notification** | Sends a Slack or Telegram message when a post goes live |
| **Approval reminder** | Nudges the team when a post is waiting for approval |
| **Weekly planning reminder** | A reminder every Monday morning |
| **Telegram join gate** | Approves join requests and DMs a welcome with your rules |
| **Telegram welcome** | Welcomes new members in the group |
| **Telegram comment moderation** | Sends every Telegram comment to the Community Moderator agent |
| **Outgoing webhook** | Sends every published post to a URL you choose (set up in the app) |

## Building blocks

### Triggers (what starts it)

| Trigger | Starts when |
|---|---|
| Workspace event | A post is created, published, failed, sent for approval, approved or rejected; a channel connects or disconnects; a new conversation or message arrives; an agent run finishes or fails; a person is added or tagged; a lead is created or changes stage |
| New comment | Someone comments on Instagram, a Facebook Page or a Telegram channel |
| Schedule | A time you set (any repeating schedule, in your timezone) |
| Manual | Someone presses Run |
| New feed item | A news source you follow publishes an article, optionally matching keywords |
| New video on a channel | You post a video outside Nimply on Instagram, a Facebook Page or Threads |
| Person tagged | A tag is added to someone in People |
| Lead stage changed | A lead moves stage (new, contacted, qualified, proposal, won, lost) |
| Telegram join request / member joined or left | Telegram community events |
| Webhook received | Another system calls a secret URL (set up in the app) |

### Actions (what it does)

| Action | Notes |
|---|---|
| Run an agent | Uses AI credits. Content the agent makes waits for approval |
| Create a draft post | Never publishes directly |
| Create a design | Carousel, image, pin or story in the brand kit; draft post or library only. Uses AI credits |
| Repeat a post | Weekly or monthly copies of a Planner post (set up in the app) |
| Post the video everywhere | The Everywhere step |
| Send a notification | Slack, Telegram or in the app |
| Reply & DM by keyword | The Comment-to-DM step |
| Inbox steps | Sort a conversation with AI, reply, assign to a teammate, tag, change status or priority |
| People steps | Add or remove a tag, add a note, move a lead to a stage (syncs to HubSpot when connected) |
| Telegram steps | Approve or decline a join request, mute or ban, send a message |
| Send to a URL | Call another system (set up in the app) |

### Logic

- **If:** branch on a value (equals, contains, greater than, exists, and so on).
- **Wait:** pause from 1 minute up to 30 days.

## Comment-to-DM

The most-used automation. Someone comments a keyword under a post and gets a
DM with your message or link, plus an optional public reply ("Sent! Check your
DMs").

Facts to state correctly:

- Real DMs are sent on **Instagram professional accounts and Facebook Pages**
  only. Do not promise it for TikTok, LinkedIn, X or YouTube.
- Keywords match whole words, ignoring case: "guide" matches "GUIDE!" but not
  "guidance".
- Several keywords can each send a different message, and a rule can be
  limited to one post.
- An optional catch-up can DM people who commented before it was switched on,
  within Meta's 7-day window for private replies.
- It sends messages to customers with no human check, so it is switched on in
  the Nimply app, by an owner or admin. An assistant can build and test it but
  cannot switch it on.

Good fits: giveaways, "comment LINK for the recipe", lead magnets, menus,
price lists, booking links. Pair it with a Nimply Page or the Lead Magnet
Builder agent so the link leads somewhere useful.

## Everywhere

For people who film and post in one app and want the video everywhere else.

- Watches one Instagram professional account, Facebook Page or Threads account
  for videos posted **outside** Nimply.
- Copies each new video to the other channels you pick: Instagram, Facebook
  Pages, Threads, TikTok, YouTube, LinkedIn, X, Telegram channels. Pinterest
  is not included.
- Copies wait for approval by default. YouTube copies always wait, and so does
  anything that looks like a duplicate of what is already there.
- The caption is kept as written, or adapted per platform with AI (about one
  AI credit per channel).
- Each video is copied to each channel once. New videos are usually noticed
  within an hour.
- It does not pick up photos, videos posted before it was switched on, shares
  of someone else's video, or anything Nimply itself published.
- Some videos are skipped, and the workspace is told why. The common case:
  Instagram does not hand over videos that use licensed music.
- Needs a paid plan or an active trial.

## Testing and switching on

Always follow this order, in the app or through an assistant:

1. Build it as a draft.
2. **Test** it. A test runs once with sample data. Steps that would change
   something (create a post, send a message, run an agent) are previewed, not
   done, and waits are skipped. Tell the user tests may still use a small
   number of credits.
3. Show the user what it would do.
4. Switch it on only after the user says yes.

Who can do what: owners, admins and editors can build, change and test;
only owners and admins can switch on or off, run now, or delete.

## Limits

- Up to 30 steps per automation.
- Up to 20 automations switched on per workspace.
- Up to 60 live runs per hour per workspace, 5 at a time.
- How many automations and monthly runs a plan includes: see
  `pricing-and-credits.md`.

## What an AI assistant or the API may and may not do

Allowed through the public API and MCP server: list building blocks and
recipes, create from a recipe or from steps, change, test, switch on or off,
run now (schedule and manual triggers), read runs, delete.

Refused, with a pointer to the app (`SET_IN_APP`):

- Switching on anything that messages customers without a human check:
  Comment-to-DM and inbox replies.
- Everywhere copies that publish without approval.

Never available outside the app: calling outside URLs, stored secrets,
incoming-webhook triggers, and repeat-a-post. Runs report each step's status
but never the content that passed through it, and no call reads or sends
inbox messages.

Automations managed by Nimply itself or tied to an agent's schedule are
read-only from outside.
