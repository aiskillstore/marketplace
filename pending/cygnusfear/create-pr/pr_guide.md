# Pull Request Style Guide

This document defines the standards for commit messages and PR descriptions.

## Commit Messages

**Format**: Conventional commits with creative emoji narratives that tell a story

**Structure**: `type: 🎭🌟 Description` where emojis create an unexpected, literary narrative

### Emoji Guidelines

- **Avoid obvious combinations** - no 🐛🔧 for bug fixes
- **Tell cryptic stories** - think literature, mythology, or abstract concepts
- **Examples**:
  - `feat: 🐋🎣 Implement large balance support` (Whales = large balances, fishing = capturing users)
  - `fix: 🌙🔍 Resolve authentication edge cases` (Night investigation = finding hidden bugs)
  - `refactor: 🏛️⚡ Restructure database connections` (Ancient architecture gets lightning speed)
- When you think you're imaginative? BE MORE IMAGINATIVE! GO WILD!
- If you are lost, pick a format:
  - 'a short story of what happened in this PR'
  - 'a description of the final result'
  - greek mythology
  - art history

## Title Guidelines

- **Keep it short** - Less than 50 characters
- **Treat it like a book title** - Should describe the whole PR in a few words
- **No technobabble** - Describe the goal over the changes, give the goal a name

### Title Examples
- `feat: 🐋🎣 Implement large balance support`
- `fix: 🌙🔍 Resolve authentication edge cases`
- `refactor: 🏛️⚡ Restructure database connections`

### Commit Types
- `feat:` - New features
- `fix:` - Bug fixes  
- `refactor:` - Code restructuring without behavior changes
- `docs:` - Documentation updates
- `chore:` - Maintenance tasks

## Pull Request Descriptions

### Structure

1. **Two-sentence summary** - What and why, not how
2. **Key changes list** - Only the most impactful modifications
3. **Additional changes section** (if needed) - Secondary modifications
4. **Testing notes** - Validation approach
5. **Related issues** - ALWAYS MENTION related issues to close and refer to them where applicable
6. **Architectural impact** - System-wide effects
7. **Future work** - Any future work or improvements
8. **Files changed** - List of files that were modified

### Writing Guidelines

- **Focus on 'why' then 'how'** - Explain motivation before implementation
- **Professional yet friendly tone** - Avoid overly elaborate language
- **Legibility over completeness** - Clear single sentences when possible
- **NO "by claude code" mentions** - Keep tool attribution out of descriptions
- **Holistic view for large changes** - Understand architectural implications
- **ALWAYS CLOSE RELATED ISSUES** - Mention related issues to close and refer to them where applicable

### Example Template

TITLE: 
`feat: 🧙⛓️ Implement dynamic chain support from blockchain provider registry`

Brief description of what changed and why it was needed. Second sentence provides additional context about the business value or technical necessity.

## Key Changes
- Implemented X to solve Y problem
- Refactored Z for better performance  
- Added validation for edge case W

## Additional Changes
- Updated documentation
- Fixed minor typos
- Adjusted logging levels

## Testing
- Manual testing of core workflows
- Unit tests added for new functions
- Integration tests verify API contracts

## Related Issues
- Closes #847
- Fixes #848

## Architectural Impact
This change affects the authentication flow by introducing token caching, reducing API calls by ~40% and improving user experience during peak usage.

## Files changed
- src/agents/standalone/prompt-selector.ts
- src/agents/standalone/workflows/steps/completion.ts