---
name: command-optimization
description: CLI command development specialist. Use when creating commands, designing
  argument parsing, automating tasks, or implementing CLI best practices. Specializes
  in command design patterns and user experience.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Command Optimization

This skill specializes in creating, designing, and optimizing command-line interfaces. It focuses on command design patterns, argument parsing, task automation, and CLI best practices.

## When to Use This Skill

- When creating new CLI commands
- When designing command interfaces
- When optimizing existing commands
- When implementing argument parsing
- When automating tasks via CLI
- When improving command user experience

## What This Skill Does

1. **Command Design**: Creates well-structured CLI commands
2. **Argument Parsing**: Designs intuitive argument and option structures
3. **Task Automation**: Automates repetitive tasks through commands
4. **User Experience**: Improves command usability and feedback
5. **Error Handling**: Implements robust error handling and validation
6. **Documentation**: Creates clear command documentation and help text

## How to Use

### Create Command

```
Create a command to generate React components
```

```
Design a CLI command for database migrations
```

### Optimize Command

```
Improve the user experience of this command
```

## Command Design Patterns

### Task-Oriented Commands

**Structure:**

- Clear action verb (generate, create, build)
- Target object (component, migration, test)
- Options for customization
- Helpful output and feedback

**Example:**

```bash
# Good: Clear and actionable
npm run generate:component UserProfile

# Bad: Unclear purpose
npm run make UserProfile
```

### Analysis Commands

**Structure:**

- Analysis type (analyze, check, audit)
- Target to analyze
- Output format options
- Actionable recommendations

**Example:**

```bash
# Good: Clear analysis command
npm run analyze:dependencies -- --outdated

# Bad: Vague command
npm run check
```

## Argument Handling

### File/Directory Arguments

**Pattern:**

- Accept single file or directory
- Support glob patterns
- Validate existence
- Handle permissions

**Example:**

```bash
# Single file
lint src/utils.js

# Directory
lint src/

# Glob pattern
lint "src/**/*.js"
```

### Configuration Options

**Common Options:**

- `--config`: Custom configuration file
- `--output`: Output directory or format
- `--verbose`: Detailed logging
- `--dry-run`: Preview without execution
- `--force`: Override safety checks

## Error Handling

### Input Validation

**Check:**

- File/directory existence
- Read/write permissions
- File format validity
- Required dependencies
- Configuration syntax

### Error Messages

**Good Error Messages:**

- Clear description of the problem
- Specific location (file, line)
- Suggested fix
- Context about why it failed

**Example:**

```bash
# Good
Error: Configuration file not found: .eslintrc.json
  Run 'npm run init:config' to create it.

# Bad
Error: File not found
```

## Examples

### Example 1: Component Generator Command

**Input**: Create a command to generate React components

**Output**:

```markdown
## Command: generate:component

### Usage
```bash
npm run generate:component ComponentName [options]
```

### Options

- `--path <path>`: Output path (default: src/components)
- `--type <type>`: Component type (functional|class) (default: functional)
- `--with-tests`: Generate test file
- `--with-styles`: Generate stylesheet

### Examples

```bash
# Basic component
npm run generate:component UserCard

# With options
npm run generate:component UserCard --path src/features/users --with-tests --with-styles
```

### Implementation

```javascript
// scripts/generate-component.js
const componentName = process.argv[2];
const options = parseArgs(process.argv.slice(3));

if (!componentName) {
  console.error('Error: Component name required');
  console.log('Usage: npm run generate:component <Name>');
  process.exit(1);
}

generateComponent(componentName, options);
```

### Example 2: Database Migration Command

**Input**: Create a database migration command

**Output**:

```markdown
## Command: db:migrate

### Usage
```bash
npm run db:migrate [migration-name] [options]
```

### Options

- `--create <table>`: Create new migration for table
- `--rollback`: Rollback last migration
- `--status`: Show migration status
- `--to <version>`: Migrate to specific version

### Examples

```bash
# Create migration
npm run db:migrate --create users

# Run migrations
npm run db:migrate

# Check status
npm run db:migrate --status

# Rollback
npm run db:migrate --rollback
```

```

## Reference Files

- **`references/SLASH_COMMAND.template.md`** - Slash command template with frontmatter, dynamic context, and workflow structure

## Best Practices

### Command Design

1. **Clear Names**: Use descriptive, action-oriented names
2. **Consistent Patterns**: Follow project conventions
3. **Helpful Defaults**: Sensible defaults for common use cases
4. **Good Feedback**: Clear output and progress indicators
5. **Error Handling**: Graceful failure with helpful messages

### User Experience

- **Progressive Disclosure**: Show basic usage, advanced options in help
- **Validation**: Validate inputs early with clear errors
- **Confirmation**: Ask for confirmation on destructive operations
- **Dry Run**: Support --dry-run for preview
- **Verbose Mode**: --verbose for detailed output

### Documentation

- **Help Text**: Clear, concise help for each command
- **Examples**: Include practical examples
- **Error Messages**: Explain what went wrong and how to fix
- **README**: Document commands in project README

## Related Use Cases

- Creating project-specific commands
- Automating development tasks
- Building CLI tools
- Improving command usability
- Standardizing command patterns
