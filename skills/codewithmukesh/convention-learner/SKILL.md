---
name: convention-learner
description: >
  Detects and enforces project-specific coding conventions by analyzing
  existing codebase patterns. Learns naming conventions, folder structure,
  test organization, and coding style from the existing code.
  Load when: "conventions", "coding standards", "project patterns",
  "enforce style", "detect patterns", "learn conventions", "code consistency".
---

# Convention Learner

## Core Principles

1. **Observe before enforcing** — Never impose conventions without first analyzing the existing codebase. A project with 200 `internal sealed class` handlers should not get a new `public class` handler. Detect first, then match.
2. **Project conventions override generic rules** — If the project uses `*Service` instead of `*Handler`, follow the project's convention even if the kit default is different. Explicit `.editorconfig` and `Directory.Build.props` rules always win.
3. **Use MCP tools for analysis** — `get_public_api` reveals naming patterns, `get_project_graph` shows structure conventions, `detect_antipatterns` tracks quality trends. Tools provide objective data; file reads provide confirmation.
4. **Document findings** — After detecting conventions, suggest adding them to the project's CLAUDE.md. Undocumented conventions are lost when the original developers leave.
5. **Consistency over perfection** — A project with consistent `snake_case` database columns is better than a project with half `snake_case` and half `PascalCase`. Match the existing pattern, even if another convention is theoretically superior.

## Patterns

### Convention Detection Flow

Systematic analysis to understand a project's coding conventions. Run this when joining an existing project or before generating new code.

**Step 1: Project Structure Analysis**
```
→ get_project_graph
  Detect:
  - Project naming: PascalCase? Dots? (MyApp.Domain vs Domain)
  - Layer organization: by layer (Domain/Application/Infrastructure) or by feature?
  - Test project naming: *.Tests, *.UnitTests, *.IntegrationTests?
  - Shared project: Common/, Shared/, BuildingBlocks/?
```

**Step 2: Type Naming Patterns**
```
→ get_public_api (on 3-5 key types across different layers)
  Detect:
  - Class modifiers: sealed? internal? internal sealed?
  - Interface prefix: I* (standard) or no prefix?
  - Suffix conventions: Handler, Service, Repository, Validator, Endpoint?
  - Record usage: for DTOs? for value objects? for commands/queries?
  - Primary constructor usage: consistently? selectively?
```

**Step 3: Folder Structure Patterns**
Scan the file system for structural conventions:
- Feature folders: `Features/{FeatureName}/` with all files together?
- Layer folders: `Controllers/`, `Services/`, `Repositories/` separate?
- Shared patterns: `Common/`, `Extensions/`, `Middleware/`?
- Configuration location: root? `Config/` folder? `Infrastructure/`?

**Step 4: Configuration Detection**
Check for explicit convention enforcers:

```
→ Look for Directory.Build.props
  - TreatWarningsAsErrors?
  - Nullable enabled globally?
  - ImplicitUsings?
  - AnalysisLevel?

→ Look for .editorconfig
  - Naming rules: camelCase fields? _prefixed privates?
  - Code style: var preferences, expression bodies, using placement

→ Look for global.json
  - SDK version pinned?
  - Roll-forward policy?
```

**Step 5: Build Convention Summary**
Compile findings into a structured summary:

```markdown
## Detected Conventions

### Naming
- Classes: `internal sealed class` (95% of handlers/services)
- Suffixes: Handlers end in `Handler`, validators in `Validator`
- Records: Used for DTOs and commands/queries

### Structure
- Architecture: Vertical Slice Architecture
- Features: `Features/{Name}/` with command, handler, validator, endpoint in one file

### Code Style
- Primary constructors: Used consistently for DI injection
- Nullable: Enabled globally, no suppressions (`!`) used
- File-scoped namespaces: 100% consistent
```

Add categories as needed: EF Core (configurations, naming, migrations), Testing (framework, naming, fixtures), etc.

### Convention Enforcement

Apply detected conventions when generating new code or reviewing existing code.

**When Generating Code:**
Match every detected pattern:

```csharp
// If existing handlers are: internal sealed class + primary constructor
// Generate matching:
internal sealed class CreateProductHandler(AppDbContext db, TimeProvider clock)
{
    // Not: public class CreateProductHandler
    // Not: internal class CreateProductHandler (missing sealed)
}
```

```csharp
// If existing DTOs are records with init properties
// Generate matching:
public record ProductResponse(Guid Id, string Name, decimal Price);
// Not: public class ProductResponse { public Guid Id { get; set; } }
```

**When Reviewing Code:**
Flag deviations from detected conventions:

```
⚠️ Convention violation: CreateOrderHandler is `public class` but project convention
   is `internal sealed class` (detected in 12/12 existing handlers).
   Change to: internal sealed class CreateOrderHandler
```

**Suggesting Enforcement Rules:**
After detecting conventions, suggest `.editorconfig` rules to enforce them automatically:

```ini
# Key .editorconfig rules to suggest based on detected conventions
dotnet_diagnostic.CA1852.severity = warning           # Seal internal types
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_prefer_primary_constructors = true:suggestion
# Add dotnet_naming_rule entries for private field prefix (_camelCase) if detected
```

### Anti-pattern Tracking

Use `detect_antipatterns` to track recurring quality issues across sessions.

**Periodic Check:**
```
→ detect_antipatterns (scope: solution)
  Track over time:
  - Are the same patterns recurring? (DateTime.Now keeps appearing)
  - Are new patterns emerging? (new HttpClient() in a new module)
  - Is the count trending up or down?
```

**Prioritization:**
```
| Anti-pattern | Count | Trend | Priority |
|-------------|-------|-------|----------|
| DateTime.Now | 12 | ↑ +3 | High — add to CLAUDE.md conventions |
| async void | 1 | → same | Medium — one-off fix |
| new HttpClient | 0 | ↓ -2 | Low — already fixing |
```

When patterns recur, add explicit rules to CLAUDE.md:
```markdown
## Conventions
- **NEVER use DateTime.Now** — Use TimeProvider.GetUtcNow() (12 violations found, fixing)
```

## Anti-patterns

### Enforcing Without Detecting

```
# BAD — Imposing kit defaults on a project with its own conventions
"All handlers should be internal sealed class"
# But this project uses public class with interfaces for testing
```

```
# GOOD — Detect first, then follow what exists
→ get_public_api reveals: 8/8 handlers are `public class` implementing `IHandler<T>`
"This project uses public handlers with interfaces. Matching that convention."
```

### Overriding Explicit Project Rules

```
# BAD — Ignoring .editorconfig because kit says otherwise
# .editorconfig says: csharp_style_expression_bodied_methods = false
# But generating expression-bodied methods anyway
```

```
# GOOD — .editorconfig and Directory.Build.props always win
"Your .editorconfig disables expression-bodied methods.
I'll use block-bodied methods to match your project settings."
```

### Applying Generic Conventions to Unconventional Projects

```
# BAD — Forcing Clean Architecture naming on a VSA project
"You need a Services/ folder and a Repositories/ folder"
# But this project uses feature folders with everything co-located
```

```
# GOOD — Match the project's organizational convention
"This project uses feature folders. I'll add the new feature
at Features/Shipping/ with all related files together."
```

### Documenting Conventions Without Evidence

```
# BAD — "Conventions" based on reading one file
"Convention: Use var everywhere" (based on seeing var in one method)
```

```
# GOOD — Document only patterns confirmed across multiple files
→ get_public_api on 5 types: 100% use explicit types for non-obvious cases
"Convention: Use explicit types for non-obvious cases (e.g., method returns),
var for obvious cases (e.g., new MyClass()). Confirmed across 5 files."
```

## Decision Guide

| Scenario | Action | Tool |
|----------|--------|------|
| Joining existing project | Run full convention detection flow | get_project_graph, get_public_api |
| Generating new code | Check detected conventions first | Previous detection results |
| Reviewing code | Flag convention deviations | get_public_api + comparison |
| Convention conflict (kit vs project) | **Project wins** | — |
| Convention conflict (team disagreement) | Document both, suggest .editorconfig | — |
| No conventions detected | Use kit defaults, document them | architecture-advisor skill |
| Recurring anti-pattern | Add to CLAUDE.md conventions | detect_antipatterns |
| New team member onboarding | Run detection, generate convention doc | Full detection flow |
| .editorconfig exists | Trust it, don't override | Read .editorconfig |
| No .editorconfig | Suggest creating one based on detected patterns | Detection + generation |
| Pattern seen once | Create instinct at 0.3 confidence via `instinct-system` skill | instinct-system |
| Pattern confirmed 3+ times | Instinct auto-promotes to 0.7, suggest adding to CLAUDE.md | instinct-system |
