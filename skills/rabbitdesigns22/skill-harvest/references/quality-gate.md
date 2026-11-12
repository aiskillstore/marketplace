# Quality gate

A skill is built only when all six checks pass, and published only when it
also passes the with/without test and the sanitize check.

## The six checks
| # | Check | Pass when |
|---|---|---|
| 1 | Evidence | 3+ asks or failed attempts, across 2+ sessions or 2+ days (a broadcast pasted to many chats counts once) |
| 2 | Method | it teaches steps and judgment that repeat, not a one-off fact |
| 3 | Market | verdict GAP, or EXISTS-WEAK with the missing part named |
| 4 | Testable | 3 real past prompts exist to test it on |
| 5 | General | someone outside this business would use it (otherwise: private only) |
| 6 | Clean | it works without client names, prices, IDs or keys inside it |

## With/without test
1. Take 3 real past prompts from the evidence (rewrite out any private data).
2. Run each twice in fresh subagents: once with the skill's SKILL.md in the
   prompt, once without. Same model, same instructions otherwise.
3. Score both answers against a checklist written BEFORE running: the
   failure from the evidence must be avoided, every fact must be checkable,
   steps must be in a safe order, and nothing must be invented.
4. Ships only if the with-skill version wins on at least 2 of 3 and loses on
   none. Show the table to the user.

## Sanitize before publishing
```bash
grep -rniE "<client1>|<client2>|<phone-or-id-pattern>|@gmail|sk-|key=|token" <skill-folder>
```
Zero hits. Examples in the skill use invented names ("Client A", "+52 55 0000 0000").

## Description check
- First sentence: when to load it.
- Trigger phrases in the user's languages (here: English and Spanish).
- One "Not for ..." line naming the nearest skill, so the two don't fight.
