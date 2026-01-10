# Fit Evaluation Guide

Determine if building a ChatGPT App is right for your product.

## Know/Do/Show Framework

Every valuable ChatGPT App must excel in at least one of these pillars:

### Know (New Context)
Your app provides data ChatGPT doesn't have access to.

**Strong signals:**
- Live/real-time data (prices, inventory, sensor readings)
- User-specific information (their tasks, their orders, their metrics)
- Internal/private data (company dashboards, team analytics)
- Specialized datasets (domain-specific knowledge bases)

**Examples:**
- "What's my current account balance?" → Requires banking integration
- "Show tasks assigned to me" → Requires project management integration
- "What's the weather at my office?" → Requires location + weather API

**Weak signals:**
- General knowledge ChatGPT already knows
- Publicly available static data
- Information easily found via web search

### Do (Real Actions)
Your app can take concrete actions on the user's behalf.

**Strong signals:**
- Create, update, or delete records
- Send messages or notifications
- Schedule events or reminders
- Trigger workflows or automations
- Execute transactions

**Examples:**
- "Create a new task for tomorrow" → Creates record in system
- "Send this summary to my team on Slack" → Sends actual message
- "Book a meeting with John for next week" → Creates calendar event

**Weak signals:**
- Actions that only affect local state
- Actions the user could easily do themselves
- Duplicate functionality of other common apps

### Show (Better Presentation)
Your app displays information more effectively than plain text.

**Strong signals:**
- Interactive lists with actions (checkboxes, buttons)
- Data visualizations (charts, graphs, timelines)
- Media galleries (images, videos, albums)
- Geographic displays (maps, routes)
- Comparison views (tables, side-by-side)

**Examples:**
- Task list with complete/delete buttons
- Sales pipeline as a Kanban board
- Photo album with fullscreen viewer
- Restaurant results on a map

**Weak signals:**
- Simple text that doesn't benefit from formatting
- Static displays without interaction
- One-time information delivery

---

## Evaluation Questions

Ask these questions to assess fit:

### Product Understanding
1. What is the core job-to-be-done your product enables?
2. What would users ask ChatGPT if your app existed?
3. What can't users accomplish in ChatGPT today without your app?

### Value Assessment
4. What unique data does your product have? (Know)
5. What actions can users take through your product? (Do)
6. What information benefits from visual display? (Show)

### Scope Definition
7. What are the 2-3 most valuable capabilities to expose?
8. Can you deliver value in the first interaction without onboarding?
9. Are your operations small and composable (not tunnel-like flows)?

### Technical Feasibility
10. Do you have an API or can you build one?
11. Is user authentication required?
12. What data needs to flow between ChatGPT and your system?

---

## Prohibited Categories

The following are NOT allowed in ChatGPT Apps:

### Content Restrictions
- Adult content (explicit sexual material)
- Gambling and betting services
- Illegal drugs or controlled substances
- Weapons, explosives, or dangerous materials
- Counterfeit or stolen goods
- Fake IDs or fraudulent documents

### Commerce Restrictions
- Digital products, subscriptions, tokens, or credits (physical goods only)
- Advertisements within the app
- Cryptocurrency speculation or trading
- Unregulated financial services
- Deceptive lending practices
- Prescription medications

### Data Restrictions
Never collect or transmit:
- Payment card information (PCI DSS)
- Protected health information (PHI)
- Social security numbers
- Passwords, API keys, or MFA codes
- Full chat logs or conversation history

### Age Restrictions
- Apps must be suitable for users 13+
- No apps targeting children under 13
- Adult (18+) content requires age verification

---

## Go/No-Go Decision

### GREEN LIGHT (Proceed)
- Strong signal in at least one pillar (Know/Do/Show)
- No prohibited categories
- Clear 2-3 core capabilities
- API available or buildable
- Can deliver value immediately

### YELLOW LIGHT (Reconsider)
- Weak signals across all pillars
- Overlaps heavily with existing apps
- Requires complex onboarding
- Borderline prohibited content

### RED LIGHT (Do Not Build)
- Falls into prohibited category
- No unique value over native ChatGPT
- Requires restricted data collection
- Full product port (not focused capabilities)

---

## Golden Prompt Set Template

Create evaluation prompts for testing discovery and triggering:

### Direct Prompts (5 minimum)
Users explicitly mention your product:
```
1. Show my [ProductName] [resource]
2. Create a new [resource] in [ProductName]
3. What's in my [ProductName] account?
4. Use [ProductName] to [action]
5. Open [ProductName] and [task]
```

### Indirect Prompts (5 minimum)
Users describe intent without naming your product:
```
1. What should I work on today?
2. Help me track my [resource type]
3. I need to [goal related to your domain]
4. Show me my [resource category]
5. Can you help me [action in your domain]?
```

### Negative Prompts (3 minimum)
Similar but should NOT trigger your app:
```
1. [Similar action but different domain]
2. [Generic request that other apps handle]
3. [Related but not your specific capability]
```

**Example for TaskFlow (project management):**

Direct:
1. Show my TaskFlow tasks
2. Create a task in TaskFlow
3. What's due this week in TaskFlow?
4. Use TaskFlow to add a reminder
5. Open TaskFlow and show my projects

Indirect:
1. What should I work on today?
2. Help me track my to-dos
3. I need to organize my work
4. Show me what's overdue
5. Can you help me plan my week?

Negative:
1. Create a calendar reminder (calendar app, not task manager)
2. Send an email to my team (email app)
3. Set an alarm for 7am (device alarm, not task)
