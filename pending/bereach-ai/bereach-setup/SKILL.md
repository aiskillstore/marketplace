---
name: bereach-setup
description: "Sets up Claude for outreach with BeReach: checks the connector and the skills, and audits old memory and instructions that conflict. Use at setup or when output drifts."
---

# BeReach setup

Goal: Claude follows ONE reviewed source of truth for outreach, the skills plus BeReach memory (homes in
step 5); any other rule about tone, length or prospecting is found, decided by the user, removed.

The two pages are drawn as `references/artifacts.md` says; open it before drawing either. Menus below are
Anthropic's current labels; if the app shows another label, follow the app.

## 1. Check the connector

Call `bereach_status`; if it answers, go to step 2.
- A plan is required: give the link the reply names; with no link, the 14-day free trial at
  https://chat.bereach.ai/onboarding?funnel=people_search&from=landing, then test again (signing in again
  will not fix it).
- No BeReach tool: set it up the one way BeReach supports, for every AI: fetch https://bereach.ai/llms.txt
  and follow its setup for where you run (a hosted Claude or ChatGPT: the human adds the connector; Claude Code,
  Codex, Cursor: you add it and hand the human the sign-in link). No other setup steps, no /mcp unless llms.txt
  says so. If you cannot fetch it, give the human the line to paste in a new chat: `set up bereach -
  https://bereach.ai/llms.txt`.

## 2. Check the skills

1. Look at the skills available now. Give install steps only for the missing ones among
   linkedin-outreach-method, linkedin-personas, linkedin-voice, linkedin-messages (cold-email on request).
   - claude.ai or a Claude Desktop chat: the human opens the Code tab of the Claude app on their computer
     (Pro, Max, Team and Enterprise plans), picks a folder and pastes: `set up bereach -
     https://bereach.ai/llms.txt`. Or they upload one ZIP per skill, the skill folder at the ZIP's top, under
     Customize > Skills > "+" > Create skill > Upload a skill, all of them (they read each other's references),
     with code execution on.
   - Claude Code: copy each folder to `~/.claude/skills/<name>/` (all projects) or `.claude/skills/<name>/`
     (one project).
   - Only install skills from sources you trust.
2. `bereach_memory_list` (titles only) for how they write, what they sell, persona cards, an old ICP.
3. The languages come from the linkedin-outreach-method skill's one question round; run alone, ask once.

**Deliver: "Setup check"**, all amber, never a stop: the cards and the voice go on. Entered from another
skill with the connector working: no page, go to step 3. Nothing saved anywhere: one line on the outreach
Overview.

## 3. Audit what Claude already "knows"

Change nothing yet. Never fill a row you did not see.

1. You read: every rule about tone, length, openers or prospecting in your context (memory, profile
   instructions, project instructions), word for word; each BeReach entry with `bereach_memory_list`,
   `fullContent: true`, one call per type and scope (playbook, offering, user-profile, any old ICP); in
   Claude Code, `/memory` too.
2. The user pastes what you cannot see: **Memory** (Settings > Your Claude > **Manage** next to "Your
   memory"; older layout Settings > Memory), every topic; **Instructions for Claude** (Settings > Your
   Claude > Instructions); any other outreach project's instructions and files.
3. Give each rule ONE verdict, never a question or "later":
   - keep;
   - move to how they write (one per language) or to what they sell / who they are;
   - an old who-to-reach rule (ICP, role, size): hand it to linkedin-outreach-method's Plan and personas,
     then delete it, listed under done;
   - delete, with a one-line reason.
4. Red, delete: any rule that contradicts linkedin-messages. Before giving verdicts, read the linkedin-messages
   skill (Hard rules; Judge, then upgrade) and the delete why-chips in `references/artifacts.md`.
5. Amber, move: tu/vous and greeting casing go to how they write in that language (with no saved choice,
   French first contact is vous and "Bonjour"). Any other one-persona rule goes on
   that persona card (linkedin-personas). A rule in a language they do not prospect in is deleted.
6. Two saved rules that conflict: keep the one that passes linkedin-messages' checks; both pass: the one
   the user's own messages show; neither: the skills' default.
7. A list on a removed entry always gets a home named in the verdict (how they write, or the search plan),
   never "stops using it".
8. A place not pasted yet is a grey row.

**Deliver: "What Claude knows"**, only after the first invitations and only when a saved rule fights a
skill or a card. The user validates in ONE answer: everything as proposed, or the rules to change. Nothing
is deleted before it.

## 4. Clean up

Only what the user approved:
- How they write: the linkedin-voice skill merges it into the Voice card (`bereach_memory_save`, type
  `playbook`, only the changed fields). One per language, never mixed.
- What they sell (`offering`) and who they are (`user-profile`) REPLACE the whole entry: read it in full,
  merge, save on the yes of the page that changed it.
- Remove a BeReach entry: `bereach_memory_save` with its type and scope, `remove: true`, no content. Move
  every list it held to its home at once; never remove the only playbook before its replacement is saved.
- Screen-only deletes (the user does them): memory topics one by one (Manage > Topics > Delete, or "forget
  ..."; deleting old chats does NOT delete what they taught), outreach rules in Instructions for Claude and
  in project instructions. Keep only facts true in every chat.
- Only on explicit request: **Reset memory** deletes all memories, project ones included, for good;
  **Pause memory** stops using and making memories but keeps them.

Optional: one Claude project "Outreach" with no tone rules and "Use account memory" off, so outreach chats
see only the skills, the connector and how they write.

**Republish "What Claude knows"** (same page) with the places still to clean, each done only once read
again. It never holds up the outreach.

## 5. Keep it clean

- One home per rule: how to work = skills; how they write = the Voice card (`playbook`, one per language:
  who they are, never the craft, which comes from the skills);
  what they sell, persona cards and templates = `offering` (`## Personas`); persona and test arm = contact
  tags. Never a second copy in memory.
- When the user corrects a draft, update the Voice card with linkedin-voice, not memory.
- Drafts drifted, or the offer or voice changed: rerun step 3.

