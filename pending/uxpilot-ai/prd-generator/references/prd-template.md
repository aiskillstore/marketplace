# PRD template

Fill every part in this order. The top half is for the people deciding; the bottom half is for whoever builds it. Use the user's own words for things and people. Keep each part as short as it can be while still settling the decision.

```markdown
# PRD: <product or feature name>

## Decision summary
<3 to 5 lines: who it is for, the problem, what version 1 does, why now.>

## Assumptions I made
- <each assumption, so the user can confirm or correct it>

## Scope
**Version 1 does:**
- <one capability per line>

**Not in version 1:**
- <item>: <one-line reason>

## Constraints
<only what the user stated: platform, tech stack, brand, legal, deadlines. Write "None stated" if there are none.>

## Screens
<the screen list as a hierarchy, for example:>
- Sign in
- Home
  - Item detail
- Settings

### <Screen name>
- **Purpose:** <the one thing a person does here>
- **Reached from:** <screens or events that lead here>
- **Shows:** <content in order of importance, as a list of what is on the screen, not where it sits>
- **Actions:** <each action and where it leads>

| State | What the user sees and can do | Words on screen |
|---|---|---|
| First use | | |
| Empty | | |
| Loading | | |
| Error | | |
| Success | | |
| <No permission or plan limit, only when it applies> | | |

**Done when:**
- <a check a person or agent can run on this screen>

<repeat the screen block for every screen>

## Main flows
1. <flow name>: <screen> > <action> > <screen> > ... > <end state>

## Rules and limits
- <business rules, limits, defaults and timings as exact numbers>
- <how each thing a user turns on is turned off, and what can be undone>

## Decisions
- **Locked:** <what the builder must not change>
- **Builder may choose:** <what is left open on purpose>
- **Open questions:** <what still needs an answer, and who answers it>

## Measure
<optional: one number that shows version 1 works, and the one event that records it>

## Build order
1. <slice: one screen or one flow, with its states and done checks, small enough to hand over alone>
<3 to 7 slices; each slice names the screen blocks it covers so it can be handed over on its own>
```

## Notes on the parts

- **Decision summary.** Lead with the decision, not background. Leave out market sizing, personas and competitor research unless the user asked for them.
- **Scope.** "Not in version 1" stops a builder adding features nobody asked for, so make it specific ("No shared lists: each list has one owner in version 1").
- **Screens.** A screen is a place a person goes. A state of a screen (empty, error) is not a separate screen, and a dialog belongs to the screen that opens it. "Shows" lists content in order of importance, which tells a designer what matters most without deciding the layout.
- **Words on screen.** Functional words only: button labels, headings that orient, the empty-state line, error and success messages. Tone and brand voice belong to whoever designs it.
- **Rules and limits.** Write numbers that a builder could otherwise soften: "up to 5 attachments per request, 10 MB each", not "a few attachments".
- **Build order.** Each slice should be something the user can paste into a builder or hand to a designer on its own, with the screen blocks it needs. Start with the slice that proves the core job.
