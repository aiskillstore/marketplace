---
name: commit-message-generator
description: Generate appropriate commit messages based on Git diffs
---

## Prerequisites
- This Skill retrieves Git diffs and suggests meaningful commit messages
- Message format should follow Conventional Commits
- Commit messages should have a one-line Conventional Commits header, an optional blank second line, and from the third line onward include a bulleted list summarizing the changes
- Commit messages should be in English
- **Never perform Git commit or Git push**

## Steps
1. Run `git status` to check modified files
2. Retrieve diffs with `git diff` or `git diff --cached`
3. Analyze the diff content and determine if changes should be split into multiple commits
4. For each logical group of changes:
   - List the target files
   - Generate a message in English compliant with Conventional Commits
   - Suggest the command: `git add <files> && git commit -m "<message>"`
5. If changes are extensive and should be split, provide:
   - Rationale for the split
   - Multiple commit suggestions with their respective target files and messages

## Commit Splitting Guidelines
- Split commits when changes span multiple logical concerns (e.g., feature + refactoring)
- Group related files that serve the same purpose
- Keep each commit focused on a single, atomic change

## Notes
- **This Skill must never execute `git commit` or `git push`**
- Only suggest commands; execution is entirely at user's discretion
- Users must explicitly perform commits and pushes themselves
