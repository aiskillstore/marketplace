# Handing a forgotten skill to a session

Send this only to a session that is still working on that topic. Idle
sessions: queue it, or send it once through the user's supervisor session.

```
Skill hint from the skill chat (no action needed if you're mid-task):

On <date> you were asked "<short quote>". The installed skill `<name>`
covers exactly that and was not loaded.

Next time this comes up: load `<name>` first. The rule from it that applies
to your work: <one rule, one line>.

<repeat for a 2nd skill if any; max 3 per message>
```

Rules:
- Quote the user's real ask with its date. A hint without evidence is noise.
- Max 3 skills per message, one message per session per run.
- Never tell a session to redo finished work because of a hint.
- If 5+ sessions forget the same skill, stop messaging and propose a
  structural fix to the user: one line in the global CLAUDE.md, or a prompt
  hook that names the skill when its trigger words appear.
