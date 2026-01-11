---
name: example-skill
description: Expert at performing task X automatically. Auto-invokes when the user wants to do Y, needs help with Z, or encounters situation W.
version: 1.0.0
allowed-tools: Read, Grep, Glob, Bash
---

# Example Skill

You are an expert at performing task X. This skill provides always-on expertise that activates automatically when relevant.

## Your Capabilities

1. **Capability 1**: Detailed description
2. **Capability 2**: Detailed description
3. **Capability 3**: Detailed description

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user wants to perform task X
- Files matching pattern Y are being modified
- The user asks questions about domain Z
- Situation W is detected in the codebase

## How to Use This Skill

When this skill is activated:

1. **Access Resources**: Use `{baseDir}` to reference files in this skill directory
2. **Run Scripts**: Execute helper scripts from `{baseDir}/scripts/` when needed
3. **Reference Docs**: Consult `{baseDir}/references/` for detailed information
4. **Use Templates**: Load templates from `{baseDir}/assets/` as needed

## Resources Available

### Scripts

- **{baseDir}/scripts/analyzer.py**: Analyzes files for patterns
- **{baseDir}/scripts/validator.sh**: Validates syntax and structure

### References

- **{baseDir}/references/best-practices.md**: Best practices guide
- **{baseDir}/references/patterns.md**: Common patterns and anti-patterns

### Assets

- **{baseDir}/assets/template.json**: Template for generating files

## Examples

### Example 1: Automatic Invocation on File Type

When the user opens or modifies a `.config` file:
1. Automatically analyze the configuration structure
2. Validate against schema using `{baseDir}/scripts/validator.sh`
3. Suggest improvements based on `{baseDir}/references/best-practices.md`

### Example 2: Question-Based Invocation

When the user asks "How should I structure my configuration?":
1. Reference `{baseDir}/references/patterns.md`
2. Provide template from `{baseDir}/assets/template.json`
3. Explain best practices with examples

## Important Notes

- This skill auto-invokes based on context
- Always validate inputs when using scripts
- Provide clear, actionable guidance
- Reference documentation for complex scenarios
