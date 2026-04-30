# Finding the Skill

If the user gives you a specific path, skip this entirely and proceed to Phase 1.
But often users say things like "test my skill" or "check the chart skill" without
providing a path. When that happens, find the skill before proceeding.

## Step 1: Check the conversation context

Look for clues in the conversation history:
- Did the user mention a skill name or path earlier?
- Did they just finish building a skill with skill-creator? If so, the path is likely
  in the conversation.
- Did they upload files that include a SKILL.md?
- Is there an MCP filesystem server connected that might contain the skill?

If you can identify the skill from context, confirm with the user: "I think you mean
the skill at [path] — is that right?" Then proceed.

## Step 2: Search common locations

If the conversation doesn't give you enough to go on, check these locations in order.
The right locations depend on the environment:

**Claude.ai:**
- `/mnt/skills/user/` — user-uploaded custom skills
- `/mnt/skills/private/` — private skills
- `/mnt/user-data/uploads/` — the user may have uploaded a skill directory

**Claude Code:**
- `.claude/skills/` — project-level skills (relative to project root)
- `~/.claude/skills/` — personal skills
- Any path specified in the project's configuration

**MCP filesystem servers:**
- If filesystem MCP servers are connected, list their allowed directories and search
  for SKILL.md files. The skill might live in an external project folder.

For each location, look for directories that contain a SKILL.md file. A directory with
a SKILL.md is a skill.

## Step 3: Handle what you find

**Found exactly one skill:** Confirm with the user and proceed.
> "I found a skill called 'csv-chart' at /mnt/skills/user/csv-to-chart/. Want me to test it?"

**Found multiple skills:** List them and ask the user to pick.
> "I found 3 skills:\n"
> "1. csv-chart at /mnt/skills/user/csv-to-chart/\n"
> "2. pdf-filler at /mnt/skills/user/pdf-filler/\n"
> "3. email-drafter at /mnt/skills/user/email-drafter/\n"
> "Which one would you like me to test?"

If the user mentioned a name, try to match it against what you found. "Test the chart
skill" should match "csv-chart" or "csv-to-chart" without requiring an exact string match.

**Found nothing:** Tell the user and ask for a path.
> "I couldn't find any skills in the usual locations. Could you give me the path to
> the skill you'd like me to test?"

Don't spend excessive time searching — if the first pass through common locations doesn't
find it, ask the user. They know where their skill lives.
