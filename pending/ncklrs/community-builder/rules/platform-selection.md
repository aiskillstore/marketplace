---
title: Community Platform Selection
impact: CRITICAL
tags: platform, discord, slack, circle, discourse, selection
---

## Community Platform Selection

**Impact: CRITICAL**

Platform choice shapes community culture, engagement patterns, and scalability. The wrong platform creates friction; the right one becomes invisible.

### Platform Comparison Matrix

| Platform | Best For | Pricing | Real-time | Async | SEO | Learning Curve |
|----------|----------|---------|-----------|-------|-----|----------------|
| **Discord** | Gaming, devs, young audience | Free | Excellent | Poor | None | Medium |
| **Slack** | Professional, B2B, enterprise | $$$$ | Excellent | Medium | None | Low |
| **Circle** | Courses, creators, paid communities | $$$ | Medium | Good | Good | Low |
| **Discourse** | Open source, long-form, knowledge | $$ | Poor | Excellent | Excellent | Medium |
| **GitHub Discussions** | Open source, developers | Free | Poor | Good | Good | Low |
| **Reddit** | Public discovery, large scale | Free | Poor | Excellent | Excellent | Low |
| **Mighty Networks** | Creator economy, courses | $$$ | Medium | Good | Medium | Low |
| **Bettermode** | Branded, customer communities | $$$ | Medium | Good | Good | Low |

### Platform Selection Framework

| Factor | Questions to Ask |
|--------|------------------|
| **Audience** | Where do your members already spend time? |
| **Communication Style** | Real-time chat or async discussion? |
| **Scale** | How large will community grow? |
| **Content Type** | Short messages or long-form posts? |
| **Discoverability** | Need SEO? Or private? |
| **Integration** | Connect to product, support, CRM? |
| **Budget** | What's sustainable long-term? |
| **Control** | Own data? White-label? Custom domain? |

### Discord Deep Dive

**Best For:** Developer communities, gaming, crypto, real-time collaboration

**Strengths:**
- Rich feature set (voice, video, threads, roles)
- Free at scale
- Bot ecosystem
- Familiar to technical audiences
- Server discovery for growth

**Weaknesses:**
- Overwhelming UX for newcomers
- No SEO (content is invisible to search)
- Notifications can be noisy
- Professional audience may resist

**Good Discord Setup:**
```
Server Structure:
├── 📋 START HERE
│   ├── #welcome (rules, intro)
│   ├── #introductions (new member posts)
│   └── #announcements (read-only)
├── 💬 COMMUNITY
│   ├── #general
│   ├── #help
│   └── #show-and-tell
├── 🔧 PRODUCT
│   ├── #feature-requests
│   ├── #bug-reports
│   └── #beta-testing
├── 🎯 TOPICS
│   ├── #topic-1
│   ├── #topic-2
│   └── #topic-3
└── 🎉 SOCIAL
    ├── #off-topic
    └── #wins-celebrations

Roles:
- @Team (staff, different color)
- @Champion (active contributors)
- @Beta Tester (early access)
- @New Member (auto-assigned)
```

**Bad Discord Setup:**
```
✗ 30+ channels visible on day one
  → Analysis paralysis, members don't know where to post

✗ No welcome channel or rules
  → Chaotic, spam-prone

✗ No role-based permissions
  → Noise everywhere, important stuff buried

✗ No moderation bots
  → Spam takes over quickly
```

### Slack Deep Dive

**Best For:** Professional communities, B2B, enterprise, workplace-adjacent

**Strengths:**
- Familiar to professionals
- Excellent search
- Thread organization
- Enterprise-grade security
- App integrations

**Weaknesses:**
- Expensive at scale ($7.25/user/month for Pro)
- 90-day message limit on free
- Requires email invite
- Can feel like "more work"

**Good Slack Setup:**
```
Channel Structure:
├── #welcome (pinned resources, rules)
├── #introductions
├── #announcements (admin-only posting)
├── #general (main conversation)
├── #help-and-support
├── #share-your-work
├── #jobs-and-opportunities
├── #random (off-topic)
└── Topic channels as needed

Slack Connect:
- Enable for partner collaboration
- Create shared channels with power users
```

**Cost Management:**
```
Free tier works if:
- Community is < 500 active members
- 90-day history is acceptable
- Basic integrations suffice

Consider paid if:
- Need full history search
- Compliance requirements
- Advanced admin controls
```

### Circle Deep Dive

**Best For:** Course creators, paid communities, creator economy

**Strengths:**
- Beautiful, modern UX
- Spaces organize topics clearly
- Events and courses built-in
- Good mobile experience
- SEO-friendly options

**Weaknesses:**
- Less real-time feel
- Smaller ecosystem
- Can feel empty if low activity
- Pricing scales with members

**Good Circle Setup:**
```
Space Structure:
├── Start Here
│   ├── Welcome (rules, orientation)
│   └── Introduce Yourself
├── Main Community
│   ├── General Discussion
│   └── Ask the Community
├── Learning
│   ├── Resources
│   └── Course Content
├── Showcase
│   └── Member Wins
└── Events
    └── Upcoming Sessions
```

### Discourse Deep Dive

**Best For:** Open source, technical discussions, knowledge bases

**Strengths:**
- SEO excellence (content ranks)
- Threaded discussions scale
- Trust level system built-in
- Self-hosted option
- Mature, stable platform

**Weaknesses:**
- Forum UX feels dated to some
- Less real-time
- Steeper setup for self-hosted
- Mobile experience just okay

**Good Discourse Setup:**
```
Category Structure:
├── Welcome (rules, FAQ)
├── General Discussion
├── Help & Support
├── Feature Requests
├── Show & Tell
└── Meta (community feedback)

Trust Levels:
- TL0: New user (limited actions)
- TL1: Basic (earned through reading)
- TL2: Member (active participation)
- TL3: Regular (highly trusted)
- TL4: Leader (moderator-lite)
```

### Platform Decision Tree

```
Start Here
    │
    ├─▶ Is real-time chat critical?
    │       │
    │       ├─▶ Yes ──▶ Is audience technical/gaming?
    │       │              │
    │       │              ├─▶ Yes ──▶ Discord
    │       │              └─▶ No  ──▶ Slack (if budget) or Discord
    │       │
    │       └─▶ No ──▶ Is SEO/discoverability important?
    │                      │
    │                      ├─▶ Yes ──▶ Discourse or Circle
    │                      └─▶ No  ──▶ Circle or Mighty Networks
    │
    └─▶ Is this for developers/open source?
            │
            ├─▶ Yes ──▶ GitHub Discussions or Discourse
            └─▶ No  ──▶ Continue above
```

### Hybrid Platform Strategies

| Combination | Use Case |
|-------------|----------|
| **Discord + Discourse** | Real-time chat + searchable knowledge base |
| **Slack + Circle** | Work conversations + community content |
| **GitHub Discussions + Discord** | Async technical + real-time social |

### Migration Considerations

| Factor | Risk | Mitigation |
|--------|------|------------|
| **History loss** | Past conversations disappear | Export and archive before |
| **Member drop-off** | Not everyone will migrate | Over-communicate, incentivize |
| **Culture reset** | Norms may not transfer | Re-establish explicitly |
| **Integration breaks** | Bots, automations stop working | Rebuild before migration |

### Platform Evaluation Checklist

- [ ] Where does target audience already hang out?
- [ ] What's the communication style (real-time vs async)?
- [ ] What's the 3-year growth projection?
- [ ] What integrations are required?
- [ ] What's the sustainable budget?
- [ ] Who will administer and moderate?
- [ ] What's the content strategy (SEO needs)?
- [ ] What are compliance/security requirements?
- [ ] Is white-label/custom branding needed?
- [ ] How will you handle migration if needed?

### Anti-Patterns

- **Choosing based on personal preference** — What you like isn't what your audience uses
- **Discord for enterprise B2B** — Professionals may see it as "gaming app"
- **Slack for 10k+ free community** — Cost becomes prohibitive
- **Multiple platforms from day one** — Fragments community, exhausts team
- **Ignoring mobile experience** — 50%+ access via mobile
- **No bot/automation strategy** — Manual moderation doesn't scale
- **Choosing for features, not culture fit** — Features < where members thrive
- **Assuming you can migrate easily** — Platform switching is painful
