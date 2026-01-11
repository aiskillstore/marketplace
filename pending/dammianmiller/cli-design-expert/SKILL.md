---
name: cli-design-expert
description: Expert CLI/TUI designer for building intuitive, user-friendly, and professional command-line interfaces. Focuses on UX patterns, help systems, progressive disclosure, and developer ergonomics.
---

# CLI Design Expert

## Overview

This skill provides expert guidance for designing and implementing professional CLI tools with:

- **Intuitive UX**: Commands that work as users expect
- **Progressive Disclosure**: Simple by default, powerful when needed
- **Excellent Help**: Self-documenting commands with rich examples
- **Error Recovery**: Helpful errors that guide users to success
- **Professional Polish**: Consistent styling, colors, and output formatting

## PROACTIVE USAGE

**Invoke this skill before:**
- Creating new CLI commands
- Designing command structures
- Writing help text and documentation
- Implementing error messages
- Adding interactive prompts

---

## Critical Design Principles

### 1. Command Structure - Follow Git's Model

```bash
# Noun-verb pattern (preferred)
uam memory query          # <tool> <resource> <action>
uam worktree create       # <tool> <resource> <action>

# Common structure
<tool> <command> [subcommand] [arguments] [--options]

# Examples
uam init                              # Simple command
uam init --interactive               # With flag
uam generate --output ./out          # With option value
uam memory query "search term"       # With argument
uam worktree create fix-bug --base develop  # Full example
```

### 2. Option Naming Conventions

```bash
# Short + Long options (always provide both for common options)
-v, --version           # Version
-h, --help              # Help
-o, --output <path>     # Output path
-f, --force             # Force/overwrite
-q, --quiet             # Suppress output
-d, --debug             # Debug mode
-n, --dry-run           # Preview without changes

# Flags (boolean) vs Options (values)
--verbose               # Flag (boolean)
--format json           # Option with value
--count 10              # Option with number

# Negatable flags
--color / --no-color    # Allow disabling defaults
--cache / --no-cache
```

### 3. Exit Codes

```typescript
// Standard exit codes
const EXIT_SUCCESS = 0;           // Success
const EXIT_ERROR = 1;             // General error
const EXIT_USAGE = 2;             // Invalid usage/arguments
const EXIT_CONFIG = 78;           // Configuration error
const EXIT_NOINPUT = 66;          // Input file not found
const EXIT_CANTCREAT = 73;        // Can't create output

// Usage
process.exit(EXIT_SUCCESS);
process.exit(EXIT_ERROR);
```

---

## Help System Design

### 1. Three Levels of Help

```bash
# Level 1: Command overview (--help on root)
$ uam --help
Universal Agent Memory - AI agent memory and workflow system

Usage: uam [command] [options]

Commands:
  init        Initialize a new project
  generate    Generate CLAUDE.md and agent files
  memory      Manage agent memory (short-term and long-term)
  worktree    Git worktree management for isolated development

Options:
  -v, --version    Show version number
  -h, --help       Show help

Run 'uam <command> --help' for more information on a command.

# Level 2: Command help (--help on command)
$ uam memory --help
Manage agent memory systems

Usage: uam memory <subcommand> [options]

Subcommands:
  query     Search long-term memory
  store     Store a new memory
  status    Show memory system status
  start     Start memory services

Examples:
  uam memory query "redis caching"
  uam memory store lesson "Always check network policies" --tags networking --importance 8

# Level 3: Subcommand help (detailed with examples)
$ uam memory query --help
Search long-term memory using semantic similarity

Usage: uam memory query <search-term> [options]

Arguments:
  search-term    Keywords to search for

Options:
  -l, --limit <n>     Maximum results (default: 10)
  -t, --tags <tags>   Filter by tags (comma-separated)
  --min-score <n>     Minimum similarity score (0-1, default: 0.5)
  --json              Output as JSON

Examples:
  # Basic search
  uam memory query "authentication flow"

  # Search with filters
  uam memory query "database" --tags postgres,migration --limit 5

  # JSON output for scripting
  uam memory query "API design" --json | jq '.results[0]'
```

### 2. Example-Driven Documentation

```typescript
// Every command should have at least 3 examples
const command = new Command('generate')
  .description('Generate CLAUDE.md and agent configuration files')
  .option('-o, --output <path>', 'Output directory', '.')
  .option('--dry-run', 'Preview without writing files')
  .addHelpText('after', `
Examples:
  # Generate with defaults
  $ uam generate

  # Generate to specific directory
  $ uam generate --output ./docs

  # Preview what would be generated
  $ uam generate --dry-run

  # Generate for specific platform
  $ uam generate --platform factory

Common Issues:
  If generation fails, ensure you have a .uam.json config file.
  Run 'uam init' to create one interactively.
`);
```

---

## Error Message Design

### 1. Helpful Error Format

```typescript
// ❌ BAD - Cryptic error
throw new Error('ENOENT');

// ✅ GOOD - Helpful error with solution
console.error(`
${chalk.red('Error:')} Configuration file not found

  Looking for: ${chalk.cyan('.uam.json')}
  Searched in: ${chalk.dim(process.cwd())}

${chalk.yellow('How to fix:')}
  Run ${chalk.cyan('uam init')} to create a configuration file.

${chalk.dim('For more help: uam init --help')}
`);
```

### 2. Error Categories

```typescript
interface CLIError {
  code: string;
  message: string;
  suggestion?: string;
  docs?: string;
}

const ERROR_MESSAGES: Record<string, CLIError> = {
  CONFIG_NOT_FOUND: {
    code: 'CONFIG_NOT_FOUND',
    message: 'Configuration file .uam.json not found',
    suggestion: 'Run `uam init` to create a configuration file',
    docs: 'https://github.com/DammianMiller/universal-agent-memory#configuration',
  },
  INVALID_CONFIG: {
    code: 'INVALID_CONFIG',
    message: 'Configuration file is invalid',
    suggestion: 'Check the JSON syntax and required fields',
    docs: 'https://github.com/DammianMiller/universal-agent-memory#configuration',
  },
  GIT_NOT_FOUND: {
    code: 'GIT_NOT_FOUND',
    message: 'Not a git repository',
    suggestion: 'Initialize git with `git init` or run from a git repository',
  },
};

function formatError(error: CLIError): void {
  console.error(chalk.red(`\nError [${error.code}]:`), error.message);
  if (error.suggestion) {
    console.error(chalk.yellow('\nSuggestion:'), error.suggestion);
  }
  if (error.docs) {
    console.error(chalk.dim('\nDocumentation:'), error.docs);
  }
}
```

### 3. Validation Errors

```typescript
// Show all validation errors at once
function validateConfig(config: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!config || typeof config !== 'object') {
    return { valid: false, errors: ['Configuration must be an object'] };
  }

  const c = config as Record<string, unknown>;
  
  if (!c.project) {
    errors.push('Missing required field: project');
  }
  if (!c.project?.name) {
    errors.push('Missing required field: project.name');
  }
  if (c.memory?.shortTerm?.maxEntries && typeof c.memory.shortTerm.maxEntries !== 'number') {
    errors.push('Invalid type: memory.shortTerm.maxEntries must be a number');
  }

  return { valid: errors.length === 0, errors };
}

// Display validation errors nicely
function showValidationErrors(errors: string[]): void {
  console.error(chalk.red('\nConfiguration validation failed:\n'));
  errors.forEach((err, i) => {
    console.error(chalk.red(`  ${i + 1}.`), err);
  });
  console.error(chalk.dim('\nCheck .uam.json and fix the issues above.'));
}
```

---

## Interactive Prompts

### 1. Inquirer.js Patterns

```typescript
import inquirer from 'inquirer';

// Grouped questions with conditional flow
async function initInteractive(): Promise<Config> {
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'projectName',
      message: 'Project name:',
      default: basename(process.cwd()),
      validate: (input) => input.length > 0 || 'Project name is required',
    },
    {
      type: 'input',
      name: 'description',
      message: 'Description (optional):',
    },
    {
      type: 'list',
      name: 'platform',
      message: 'Primary AI platform:',
      choices: [
        { name: 'Claude Code (Desktop)', value: 'claudeCode' },
        { name: 'Factory.AI', value: 'factory' },
        { name: 'VS Code', value: 'vscode' },
        { name: 'OpenCode', value: 'opencode' },
      ],
    },
    {
      type: 'confirm',
      name: 'enableMemory',
      message: 'Enable memory system?',
      default: true,
    },
    {
      type: 'list',
      name: 'memoryBackend',
      message: 'Long-term memory backend:',
      choices: [
        { name: 'Qdrant (local Docker)', value: 'qdrant' },
        { name: 'Qdrant Cloud', value: 'qdrant-cloud' },
        { name: 'GitHub (JSON files)', value: 'github' },
        { name: 'None', value: 'none' },
      ],
      when: (answers) => answers.enableMemory,
    },
  ]);

  return buildConfig(answers);
}
```

### 2. Confirmation for Destructive Actions

```typescript
async function handleDestructiveAction(
  action: string,
  details: string,
  execute: () => Promise<void>
): Promise<void> {
  console.log(chalk.yellow(`\n⚠️  ${action}\n`));
  console.log(chalk.dim(details));
  
  const { confirmed } = await inquirer.prompt([{
    type: 'confirm',
    name: 'confirmed',
    message: 'Are you sure you want to proceed?',
    default: false,
  }]);

  if (!confirmed) {
    console.log(chalk.dim('Cancelled.'));
    return;
  }

  await execute();
}

// Usage
await handleDestructiveAction(
  'Delete worktree and branch',
  `This will delete:\n  - Worktree: .worktrees/123-feature\n  - Branch: feature/123-feature`,
  async () => await deleteWorktree(id)
);
```

---

## Output Formatting

### 1. Tables

```typescript
// Simple aligned table
function printTable(headers: string[], rows: string[][]): void {
  const widths = headers.map((h, i) => 
    Math.max(h.length, ...rows.map(r => (r[i] || '').length))
  );
  
  // Header
  console.log(headers.map((h, i) => h.padEnd(widths[i]!)).join('  '));
  console.log(widths.map(w => '─'.repeat(w)).join('  '));
  
  // Rows
  for (const row of rows) {
    console.log(row.map((cell, i) => (cell || '').padEnd(widths[i]!)).join('  '));
  }
}

// Usage
printTable(
  ['ID', 'Branch', 'Status', 'Created'],
  [
    ['1', 'feature/add-auth', 'active', '2024-01-15'],
    ['2', 'fix/memory-leak', 'merged', '2024-01-14'],
  ]
);
```

### 2. JSON Output for Scripting

```typescript
interface CommandOptions {
  json?: boolean;
  quiet?: boolean;
}

function output<T>(data: T, options: CommandOptions): void {
  if (options.json) {
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  
  if (options.quiet) {
    // Minimal output for scripting
    if (Array.isArray(data)) {
      data.forEach(item => console.log(item.id || item));
    } else {
      console.log((data as { id?: string }).id || data);
    }
    return;
  }
  
  // Human-readable output
  prettyPrint(data);
}
```

### 3. Progress Indicators

```typescript
import ora from 'ora';

// Single task
const spinner = ora('Processing...').start();
try {
  await doWork();
  spinner.succeed('Done!');
} catch (e) {
  spinner.fail('Failed');
  throw e;
}

// Multi-step with status
async function runPipeline(steps: Array<{ name: string; run: () => Promise<void> }>): Promise<void> {
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i]!;
    const prefix = chalk.dim(`[${i + 1}/${steps.length}]`);
    const spinner = ora(`${prefix} ${step.name}`).start();
    
    try {
      await step.run();
      spinner.succeed(`${prefix} ${step.name}`);
    } catch (e) {
      spinner.fail(`${prefix} ${step.name}`);
      throw e;
    }
  }
}
```

---

## Color Usage

```typescript
import chalk from 'chalk';

// Semantic colors
const colors = {
  // Status
  success: chalk.green,      // ✔ Operations completed
  error: chalk.red,          // ✖ Errors
  warning: chalk.yellow,     // ⚠ Warnings
  info: chalk.cyan,          // ℹ Information
  
  // Emphasis
  primary: chalk.blue,       // Important values
  secondary: chalk.dim,      // Less important
  highlight: chalk.bold,     // Emphasis
  
  // Data types
  path: chalk.cyan,          // File paths
  command: chalk.cyan,       // Commands to run
  code: chalk.yellow,        // Code snippets
  url: chalk.underline.blue, // URLs
};

// Symbols
const symbols = {
  success: chalk.green('✔'),
  error: chalk.red('✖'),
  warning: chalk.yellow('⚠'),
  info: chalk.cyan('ℹ'),
  bullet: chalk.dim('•'),
  arrow: chalk.dim('→'),
};
```

---

## Shell Completion

```typescript
// Generate completion script
program
  .command('completion')
  .description('Generate shell completion script')
  .argument('<shell>', 'Shell type (bash, zsh, fish)')
  .action((shell: string) => {
    switch (shell) {
      case 'bash':
        console.log(generateBashCompletion());
        break;
      case 'zsh':
        console.log(generateZshCompletion());
        break;
      case 'fish':
        console.log(generateFishCompletion());
        break;
      default:
        console.error(`Unknown shell: ${shell}`);
        process.exit(1);
    }
  });

// Example bash completion
function generateBashCompletion(): string {
  return `
_uam_completions() {
  local cur="\${COMP_WORDS[COMP_CWORD]}"
  local prev="\${COMP_WORDS[COMP_CWORD-1]}"
  
  case "\${prev}" in
    uam)
      COMPREPLY=($(compgen -W "init generate memory worktree droids" -- "\${cur}"))
      ;;
    memory)
      COMPREPLY=($(compgen -W "query store status start stop" -- "\${cur}"))
      ;;
    worktree)
      COMPREPLY=($(compgen -W "create list pr cleanup" -- "\${cur}"))
      ;;
  esac
}

complete -F _uam_completions uam
`;
}
```

---

## Review Checklist

Before releasing any CLI command:

- [ ] `--help` provides clear, example-rich documentation
- [ ] Short and long options for common flags
- [ ] Exit codes are meaningful (0 = success, non-zero = error)
- [ ] Error messages explain what went wrong AND how to fix it
- [ ] Destructive actions require confirmation (unless `--force`)
- [ ] `--json` output available for scripting
- [ ] `--quiet` / `--verbose` options where appropriate
- [ ] Colors are used semantically and respect `NO_COLOR` env var
- [ ] Progress indicators for long-running operations
- [ ] Validation shows all errors at once, not one at a time
