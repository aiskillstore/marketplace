# Reader brief (same text for every batch)

Paste this to each reading subagent, replacing the file list and the one-line
description of the user's business.

```
You analyze agent "skills" (SKILL.md packages that teach an agent a method).
The user is <one line: who they are and what their sessions do>.

Read these session digests IN FULL (each has title, skills loaded, and the
list of what the human asked):
<absolute paths>

Installed skills = the folders in ~/.claude/skills (ls it; read the
description of any you suspect covers something).

Return, max 900 words:
A) NEW SKILL CANDIDATES (max 6): proposed-name (kebab-case), the repeatable
   method it teaches, evidence (1-2 short quotes with session and date),
   why someone outside this business would want it, and the closest
   installed skill (or "none"). Only methods that repeated or took several
   attempts/corrections. Nothing invented.
B) FORGOTTEN SKILLS: per session, the installed skill that applied to what
   was asked and is NOT in "skills loaded", with the ask that proves it.
   Ignore skills created after the ask's date.
C) REPEATED CORRECTIONS: complaints that recur ("again", "I told you",
   errors). These are the strongest signal of a missing method.
No evidence, no line. Do not modify any file.
```

Why a fixed brief: identical sections merge mechanically in step 4, and the
"no evidence, no line" rule is what keeps readers from inventing candidates.
