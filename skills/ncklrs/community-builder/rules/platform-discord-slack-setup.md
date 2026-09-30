---
title: Discord and Slack Community Setup
impact: CRITICAL
tags: discord, slack, platform, setup, bots, channels
---

## Discord and Slack Community Setup

**Impact: CRITICAL**

Discord and Slack are the two dominant real-time community platforms. Each requires specific setup, bots, and configuration to run effectively. A well-configured server creates clarity; a poorly configured one creates chaos.

### Discord Server Setup

#### Channel Structure

**Good Discord Structure:**
```
📋 WELCOME
├── #rules (read-only, pinned CoC)
├── #announcements (admin-only, important updates)
├── #introductions (new member posts)
└── #roles (self-assign interests)

💬 GENERAL
├── #general (main conversation)
├── #off-topic (non-work chat)
└── #random (memes, fun)

❓ SUPPORT
├── #help (questions and answers)
├── #troubleshooting (technical issues)
└── #feedback (product feedback)

🔧 PRODUCT
├── #feature-requests
├── #bug-reports
└── #beta (invite-only)

📚 RESOURCES
├── #tutorials (pinned guides)
├── #showcase (member projects)
└── #jobs (career opportunities)

🎉 COMMUNITY
├── #wins (celebrations)
├── #events (upcoming activities)
└── #content (member blogs, videos)

🔒 PRIVATE
├── #champions (invite-only)
├── #team (staff only)
└── #mods (moderator discussion)
```

**Bad Discord Structure:**
```
✗ 30+ visible channels
  → Overwhelming, nobody knows where to post

✗ Unclear channel names
  → #channel-1, #stuff, #misc

✗ No read-only channels
  → Announcements get buried

✗ Everything visible to everyone
  → No progression or exclusivity
```

#### Discord Role Setup

| Role | Color | Permissions | Assignment |
|------|-------|-------------|------------|
| **Admin** | Red | All | Manual |
| **Moderator** | Orange | Manage messages, timeout | Manual |
| **Team** | Blue | Staff identifier | Manual |
| **Champion** | Purple | Access to private channels | Earned |
| **Member** | Green | Full community access | After intro/verify |
| **New** | Gray | Limited (no links, rate limited) | Auto on join |

#### Discord Bot Essentials

| Bot | Purpose | Key Features |
|-----|---------|--------------|
| **MEE6** | Moderation, leveling | Auto-mod, welcome, XP system |
| **Carl-bot** | Moderation, roles | Reaction roles, logging |
| **Dyno** | All-purpose | Auto-mod, custom commands |
| **Wick** | Security | Anti-raid, verification |
| **Ticket Tool** | Support | Private support tickets |
| **Statbot** | Analytics | Server statistics |

#### Discord Verification Flow

```
New Member Joins
       ↓
Lands in #rules (only visible channel)
       ↓
Reads rules, reacts with ✅
       ↓
Bot assigns @Member role
       ↓
Full server access unlocked
       ↓
Welcome bot DMs with quick start
       ↓
Posts intro in #introductions
```

#### Discord Best Practices

```
✓ Use threads for extended conversations
  → Keeps channels clean, creates context

✓ Set slow mode for high-traffic channels
  → #general: 5-10 seconds prevents spam

✓ Use forums for Q&A channels
  → Searchable, structured, resolvable

✓ Pin important messages (sparingly)
  → 3-5 pins max per channel

✓ Create reaction roles for interests
  → Let members opt into topic channels

✓ Set up server discovery
  → Allows organic growth (if public)

✓ Configure logging
  → Track joins, leaves, deletions for safety
```

### Slack Workspace Setup

#### Channel Structure

**Good Slack Structure:**
```
PUBLIC CHANNELS
├── #announcements (admin-only posting)
├── #introductions (new member posts)
├── #general (main conversation)
├── #random (off-topic, social)
├── #help (questions and support)
├── #feedback (product feedback)
├── #jobs (career posts)
├── #events (community events)
├── #wins (celebrations)
└── #resources (links, guides)

TOPIC CHANNELS (as needed)
├── #topic-frontend
├── #topic-backend
├── #topic-devops
└── #topic-design

PRIVATE CHANNELS
├── #champions (invite-only)
├── #team (staff only)
└── #mods (moderator discussion)
```

**Bad Slack Structure:**
```
✗ No default channels
  → People join and see nothing

✗ Too many channels too early
  → Empty channels signal dead community

✗ No topic organization
  → Everything in #general, chaos

✗ Private channels for general discussion
  → Fragments community
```

#### Slack Workspace Settings

| Setting | Recommendation | Why |
|---------|----------------|-----|
| **Default channels** | #announcements, #introductions, #general | Everyone starts together |
| **Who can create channels** | Admins + request process | Prevent proliferation |
| **Who can post in #announcements** | Admins only | Keep signal high |
| **Invitation policy** | Anyone with link (or approval) | Balance growth and quality |
| **Message retention** | As long as plan allows | Free tier: 90 days |

#### Slack Apps and Integrations

| App | Purpose | Use Case |
|-----|---------|----------|
| **Slackbot** | Custom responses | Auto-answers to common questions |
| **Donut** | Introductions | Random 1:1 pairing |
| **Polly** | Polls/surveys | Community feedback |
| **Zapier/Make** | Automation | Connect to other tools |
| **Loom** | Video | Async video messages |
| **Notion/Confluence** | Docs | Knowledge base links |

#### Slack Etiquette Guidelines

```
Channel Guidelines:

#general
- All community topics welcome
- Use threads for extended discussions
- Keep it constructive and helpful

#help
- Search before asking (Cmd+K)
- Be specific: include error messages, code
- Use code blocks for code (```)
- Mark questions as resolved with ✅

#announcements
- Admin posts only
- Important updates and news
- React with 👍 to acknowledge

#random
- Off-topic, social, fun
- Memes welcome
- Be respectful
```

### Discord vs Slack: When to Use

| Factor | Choose Discord | Choose Slack |
|--------|---------------|--------------|
| **Audience** | Developers, gaming, young | Professional, enterprise, B2B |
| **Cost** | Need free at scale | Budget for $7.25/user/month |
| **Real-time** | Heavy real-time, voice | Chat-focused |
| **Search** | Less critical | Need full history search |
| **Integration** | Bot ecosystem | Workplace tool integration |
| **Mobile** | Good | Good |
| **Perception** | "Gaming app" (changing) | "Work tool" |

### Bot Configuration Best Practices

#### Welcome Bot Setup

**Good Welcome Message:**
```
Welcome to [Community], {username}!

You've joined [X,000] [identity] who [value prop].

Quick start:
1. Read #rules and react ✅ to get full access
2. Introduce yourself in #introductions
3. Browse #resources for guides
4. Ask questions in #help

Questions? DM any @Team member or post in #help.

See you around!
```

**Bad Welcome Message:**
```
✗ Too long (10+ lines)
✗ No clear next action
✗ Generic ("Welcome to our server")
✗ Overwhelming with options
```

#### Auto-Moderation Setup

| Rule | Action | Threshold |
|------|--------|-----------|
| **Spam detection** | Delete + warn | Repeated messages |
| **Link restriction** | Delete for new users | First 24h |
| **Profanity filter** | Flag for review | Context-dependent |
| **Mass mention** | Block | >5 mentions |
| **Raid protection** | Auto-lockdown | 10+ joins/minute |
| **Invite links** | Delete in most channels | Except #promos |

### Channel Naming Conventions

| Platform | Convention | Example |
|----------|------------|---------|
| **Discord** | #emoji-category or #lowercase | #💬-general, #help |
| **Slack** | #prefix-topic | #team-engineering, #help-product |

**Prefixes for Slack:**
```
#team-*     → Team channels
#proj-*     → Project channels
#help-*     → Support channels
#social-*   → Social channels
#announce-* → Announcements
```

### Notification Management

**Discord:**
```
Server Settings:
- Notification settings: Only @mentions
- Suppress @everyone/@here for most roles
- Create #announcements with @everyone sparingly

Member guidance:
"Right-click channels → Notification Settings
Set most to 'Only @mentions' to avoid overwhelm"
```

**Slack:**
```
Channel Defaults:
- #announcements: All messages
- #general: Mentions only (after initial period)
- Topic channels: Mentions only

Member guidance:
"Click channel name → Notifications → Customize
Most channels work best with 'Mentions only'"
```

### Migration Between Platforms

| Step | Action |
|------|--------|
| 1 | Announce migration with clear timeline |
| 2 | Set up new platform, invite core members first |
| 3 | Run parallel for 2-4 weeks |
| 4 | Port critical content (pins, resources) |
| 5 | Gradual wind-down of old platform |
| 6 | Final sunset with clear deadline |
| 7 | Keep read-only archive if possible |

### Anti-Patterns

**Discord:**
- **Too many channels** — Start with 10, add when needed
- **Complicated role system** — Simple hierarchy wins
- **No verification** — Bots and spam flood server
- **Voice channels everywhere** — Nobody uses most of them
- **No thread culture** — Channels become unreadable

**Slack:**
- **Free tier forever** — 90-day limit hurts community memory
- **Channel explosion** — Create policy before proliferation
- **No default channels** — New members see empty workspace
- **Email-like behavior** — DMs when channels would build community
- **No threading** — Conversations collide

**Both:**
- **No onboarding** — Join → confusion → leave
- **No moderation bots** — Manual moderation doesn't scale
- **Admin-only posting everywhere** — Kills conversation
- **No analytics** — Flying blind on engagement
- **Copy-paste setup** — Every community has different needs
