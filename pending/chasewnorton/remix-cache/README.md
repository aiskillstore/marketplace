# Remix Cache Skill

This directory contains a comprehensive **Agent Skill** for working with the remix-cache library.

## What is an Agent Skill?

Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources that Claude uses automatically when relevant. Skills provide domain-specific expertise that transforms general-purpose agents into specialists.

## What's in this skill?

This skill provides Claude with complete expertise on remix-cache:

- **SKILL.md** - Main skill file with quick reference and navigation
- **GETTING_STARTED.md** - Installation, setup, and first cache definition
- **API_REFERENCE.md** - Complete API documentation for all methods and options
- **PATTERNS.md** - Common caching patterns and best practices
- **REACT_INTEGRATION.md** - SSE setup and React hooks for real-time invalidation
- **EXAMPLES.md** - Real-world examples (e-commerce, sessions, API caching, blogs, analytics, SaaS)
- **TROUBLESHOOTING.md** - Common issues and solutions
- **TESTING.md** - Testing strategies and patterns

## How it works

When Claude Code loads this skill, it can:

1. **Level 1 (Always loaded)**: Know that remix-cache skill exists and when to use it
2. **Level 2 (Loaded on demand)**: Read SKILL.md to understand the library structure
3. **Level 3+ (As needed)**: Access specific documentation files for detailed guidance

This progressive disclosure approach means the skill provides comprehensive context without consuming tokens until needed.

## Using this skill

### In Claude Code

If you're using Claude Code, place this directory in:
```
~/.claude/skills/remix-cache-skill/
```

Or for project-specific:
```
your-project/.claude/skills/remix-cache-skill/
```

Claude will automatically discover and use it when you ask questions about caching, Remix, or Redis.

### In Claude API

You can upload this as a custom skill via the Skills API (`/v1/skills` endpoints).

### Example prompts that trigger this skill

- "How do I set up caching in my Remix app?"
- "Implement tag-based cache invalidation"
- "Add real-time cache revalidation with SSE"
- "Debug why my cache isn't invalidating"
- "Write tests for my cache definitions"
- "Set up stale-while-revalidate for my API cache"

## Skill coverage

This skill covers remix-cache v0.1.0 with complete implementation:

✅ Core caching with Redis backend
✅ Type-safe cache definitions
✅ Stale-while-revalidate
✅ Sliding window TTL
✅ Pattern & tag-based invalidation
✅ Circuit breaker pattern
✅ Request deduplication
✅ Server/serverless modes
✅ SSE real-time invalidation
✅ React hooks for auto-revalidation

## Contributing

To update this skill:

1. Update the relevant markdown files
2. Test that Claude can access the information correctly
3. Ensure all internal links work
4. Keep examples up-to-date with the actual implementation

## License

Same license as remix-cache library.
