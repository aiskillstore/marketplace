# Documentation Examples

Real examples from this project showing good documentation practices.

## Example 1: Screen Overview (Home Screen)

**File**: `docs/screens/home/README.md`

**What makes it good:**
- ✅ Clear structure with sections
- ✅ Bullet-point features
- ✅ Table for keyboard shortcuts
- ✅ ASCII diagram for layout
- ✅ Links to related docs
- ✅ Under 300 lines

**Excerpt:**

```markdown
# Home Screen

Main chat interface for interacting with Claude AI.

## Features

### Core Features (Phase 1)
1. **Conversation History Display**: Shows all messages
2. **Streaming Support**: Real-time response streaming
3. **Interactive Input Box**: Text input with history
4. **Error Handling**: Clear error messages

### Advanced Features (Phase 2)
5. **Slash Commands**: 10+ commands (/, /save, /load, etc.)
6. **Todos Management**: Track and display todos
7. **Session Management**: Save and load conversations

## Keyboard Shortcuts

| Key      | Action                               |
| -------- | ------------------------------------ |
| `Enter`  | Send message                         |
| `↑/↓`    | Navigate command history             |
| `Tab`    | Autocomplete slash command           |
| `Ctrl+C` | Exit                                 |
```

**Why it works:**
- Quick scan shows all features
- Table makes shortcuts easy to find
- Clear hierarchy with H2/H3 headings

---

## Example 2: Technical Documentation (Config Screen)

**File**: `docs/screens/config/technical.md`

**What makes it good:**
- ✅ Architecture diagram with dependencies
- ✅ TypeScript interfaces
- ✅ Code examples with explanations
- ✅ Validation logic shown
- ✅ Code references (file:line)

**Excerpt:**

```markdown
# Config Screen - Technical

## Architecture

### Dependencies

\```
Config (CLI)
  ├── useNavigation()
  ├── useConfigWizard()
  │   └── ConfigPresenter
  │       ├── ConfigLoader
  │       │   ├── FileConfigRepository
  │       │   └── EnvConfigRepository
  │       └── Configuration (Domain Model)
  └── useConfigKeyboard()
\```

## State Management

### State Interface

\```typescript
interface WizardState {
  currentStep: ConfigStep;
  selectedProvider: Provider | null;
  selectedModel: string;
  apiKey: string;
  error: string | null;
}
\```

## Validation

### Model Validation

\```typescript
function validateModel(model: string): boolean {
  return model.trim() !== '';
}
\```

**Location:** source/cli/hooks/useConfigWizard.ts:145
```

**Why it works:**
- Visual dependency tree is clear
- Real TypeScript code (not pseudo-code)
- Code reference tells where to find it
- Focused on implementation details

---

## Example 3: Feature Documentation (Slash Commands)

**File**: `docs/screens/home/features.md`

**What makes it good:**
- ✅ Table for structured data
- ✅ Usage examples for each command
- ✅ Error handling documented
- ✅ Implementation reference

**Excerpt:**

```markdown
# Home Screen - Features

## Feature 5: Slash Commands

Execute commands by typing `/` prefix in the input box.

### Available Commands

| Command            | Description       | Example            |
| ------------------ | ----------------- | ------------------ |
| `/help`            | Show help overlay | `/help`            |
| `/clear`           | Clear conversation| `/clear`           |
| `/save [name]`     | Save session      | `/save my-session` |
| `/load [name]`     | Load session      | `/load my-session` |
| `/config`          | Open config       | `/config`          |

### Usage

Type `/` to see autocomplete suggestions:

\```
> /sa
  ↓ /save
  ↓ /sample
\```

Press `Tab` to autocomplete or continue typing.

### Error Handling

| Error              | Cause                  | Solution          |
|--------------------|------------------------|-------------------|
| "Invalid command"  | Command doesn't exist  | Type `/help`      |
| "Session not found"| Session name invalid   | Use `/list`       |

### Implementation

**Location:** source/cli/hooks/useSlashCommands.ts:45

\```typescript
const handleSlashCommand = (input: string) => {
  const [command, ...args] = input.slice(1).split(' ');

  switch (command) {
    case 'save':
      return saveSession(args[0]);
    case 'load':
      return loadSession(args[0]);
    // ...
  }
};
\```
```

**Why it works:**
- Table makes commands scannable
- Examples show exact usage
- Error table helps troubleshooting
- Code shows implementation

---

## Example 4: User Flows (Message Send Flow)

**File**: `docs/screens/home/flows.md`

**What makes it good:**
- ✅ Step-by-step flow
- ✅ ASCII diagram
- ✅ Mermaid diagram for complexity
- ✅ Error cases included

**Excerpt:**

```markdown
# Home Screen - User Flows

## Flow 1: Basic Chat Flow

### Steps

\```
User enters Home Screen
  → See empty conversation area
  → Type message in input box
  → Press Enter
  → Message sent to API
  → Streaming response appears word-by-word
  → Complete message displayed
  → Ready for next input
\```

### Visual Flow

\```
┌─────────────┐
│ User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Send API   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Streaming  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Complete   │
└─────────────┘
\```

### Mermaid Diagram

\```mermaid
sequenceDiagram
  User->>Home: Type message
  User->>Home: Press Enter
  Home->>API: Send request
  API-->>Home: Stream chunk 1
  Home-->>User: Display chunk 1
  API-->>Home: Stream chunk 2
  Home-->>User: Display chunk 2
  API-->>Home: Done
  Home-->>User: Show complete
\```

### Error Cases

**Network Error:**
\```
User → Send → Network Error → Retry Dialog → User Chooses Retry
\```
```

**Why it works:**
- Text flow for quick reading
- ASCII for simple visualization
- Mermaid for complex sequences
- Error paths documented

---

## Example 5: Architecture Documentation

**File**: `docs/architecture/overview.md`

**What makes it good:**
- ✅ High-level diagram first
- ✅ Layer-by-layer explanation
- ✅ Pattern examples with code
- ✅ Benefits and trade-offs

**Excerpt:**

```markdown
# 3-Layer Architecture

## Overview

\```
┌─────────────────────────────────────────┐
│         Layer 1: CLI (Presentation)      │
│  React Ink Components, Screens, Hooks   │
└────────────────┬────────────────────────┘
                 │ depends on
┌────────────────▼────────────────────────┐
│      Layer 2: Core (Business Logic)     │
│   Domain Models, Use Cases, Services    │
└────────────────┬────────────────────────┘
                 │ depends on
┌────────────────▼────────────────────────┐
│    Layer 3: Infrastructure (External)   │
│   API Clients, File I/O, Integrations   │
└─────────────────────────────────────────┘
\```

## Patterns

### MVP Pattern

**Purpose:** Separate presentation from business logic

**Implementation:**

\```typescript
// Presenter (Business Logic)
class HomePresenter {
  async sendMessage(text: string): Promise<void> {
    const message = Message.create({text});
    await this.apiClient.send(message);
  }
}

// View (React Component)
function HomeScreen() {
  const presenter = usePresenter(HomePresenter);

  return (
    <InputBox onSubmit={presenter.sendMessage} />
  );
}
\```

**Benefits:**
- Testable business logic
- Reusable presenters
- Clear separation of concerns

**Trade-offs:**
- More files
- Indirection
```

**Why it works:**
- Diagram shows big picture first
- Pattern has purpose, code, benefits, trade-offs
- Real code from the project
- Explains "why" not just "what"

---

## Example 6: Code Reference Format

**Good examples:**

```markdown
The `HomePresenter` class is defined in source/cli/presenters/HomePresenter.ts:12

Streaming is implemented in source/infrastructure/api/AnthropicClient.ts:67

Configuration validation occurs in source/core/domain/models/Configuration.ts:54
```

**Why good:**
- Full path from repo root
- Includes line number
- Uses backticks for code names
- Easy to find in codebase

**Bad examples:**

```markdown
 The HomePresenter is in HomePresenter.ts
 See HomePresenter
 Check the presenters folder
```

**Why bad:**
- No path
- No line number
- Ambiguous location

---

## Example 7: Code Block with Language

**Good:**

````markdown
```typescript
interface Props {
  value: string;
  onChange: (value: string) => void;
}
```
````

**Why good:**
- Specifies `typescript`
- Gets syntax highlighting
- Clear and readable

**Bad:**

````markdown
```
interface Props {
  value: string;
  onChange: (value: string) => void;
}
```
````

**Why bad:**
- No language specified
- No syntax highlighting

---

## Example 8: Table Usage

**Good use of tables:**

**Keyboard shortcuts:**
```markdown
| Key      | Action           |
|----------|------------------|
| `Enter`  | Send message     |
| `Ctrl+C` | Exit             |
```

**Configuration options:**
```markdown
| Option     | Type   | Default | Required |
|------------|--------|---------|----------|
| provider   | string | -       | Yes      |
| model      | string | -       | Yes      |
| apiKey     | string | -       | No       |
```

**Feature comparison:**
```markdown
| Feature    | Home | Config | Welcome |
|------------|------|--------|---------|
| Input      | ✅   | ✅     | ✅      |
| Streaming  | ✅   |      |       |
```

**Why good:**
- Structured data easy to scan
- Consistent formatting
- Clear headers

---

## Example 9: Anti-Pattern (What NOT to Do)

**BAD Documentation:**

```markdown
# Home Screen

This is the home screen.

## Features

It has features.

## Usage

Use it to do things.
```

**Why it's bad:**
- Vague descriptions
- No examples
- No code references
- No structure
- Useless content

**GOOD Documentation:**

```markdown
# Home Screen

Main chat interface for interacting with Claude AI.

## Features

1. **Conversation Display**: Shows message history with streaming support
2. **Input Box**: Multi-line input with command history (↑/↓)
3. **Slash Commands**: Execute `/save`, `/load`, `/clear` commands

## Usage

### Send a Message

Type message and press Enter:

\```
> Hello Claude
\```

Result: Message sent, streaming response displayed

### Save Session

\```
> /save my-conversation
\```

Result: Session saved to `~/.codeh/sessions/my-conversation.json`

**Implementation:** source/cli/screens/Home.tsx:16
```

**Why it's good:**
- Specific descriptions
- Real examples with results
- Code reference
- Actionable content

---

## Example 10: Git Commit Messages

**Good commits:**

```bash
# Single file update
git commit -m "docs(home): add keyboard shortcuts table"

# Multiple changes
git commit -m "docs: restructure configuration documentation

- Split config.md into overview and technical
- Add 5 usage examples
- Update code references to match new structure
- Add validation examples
"

# Consolidation
git commit -m "docs: consolidate duplicate home screen docs

- Merged 3 duplicate files into screens/home/README.md
- Deleted home_screen/ directory (52 files)
- Updated all cross-references
- Reduced from 5,000 to 800 lines
"
```

**Why good:**
- Follows convention (docs: or docs(scope):)
- Descriptive
- Bullet points for multiple changes
- Explains "what" and "why"

**Bad commits:**

```bash
 git commit -m "update docs"
 git commit -m "fix"
 git commit -m "documentation changes"
```

**Why bad:**
- Too vague
- Doesn't say what changed
- No context

---

## Summary: What Makes Good Documentation

Based on examples above:

1. **Structure**: Clear H2/H3 hierarchy
2. **Examples**: Real, working code
3. **References**: file:line format
4. **Tables**: For structured data
5. **Diagrams**: ASCII or Mermaid
6. **Specificity**: Exact descriptions, not vague
7. **Results**: Show expected outcomes
8. **Size**: Under 500 lines
9. **Links**: Cross-reference related docs
10. **Testing**: All examples work

**Apply these patterns** when creating documentation.
