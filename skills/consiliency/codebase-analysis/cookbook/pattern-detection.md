# Pattern Detection

Identify architectural patterns from directory structure and code organization.

## Directory-Based Detection

### MVC Pattern

```bash
# Check for MVC structure
ls -d */ 2>/dev/null | grep -iE "model|view|controller"
```

**Signs:**
- `models/`, `views/`, `controllers/` directories
- Clear separation of data, presentation, logic
- Models contain data structures
- Controllers handle requests

### Layered Architecture

```bash
# Check for layered structure
ls -d */ 2>/dev/null | grep -iE "presentation|business|data|domain|infrastructure|application"
```

**Signs:**
- `presentation/`, `business/`, `data/` layers
- Layer imports only go downward
- Clear abstraction boundaries

### Hexagonal / Ports & Adapters

```bash
# Check for hexagonal structure
ls -d */ 2>/dev/null | grep -iE "domain|ports|adapters|core|infrastructure"
```

**Signs:**
- `domain/` or `core/` - Business logic
- `ports/` - Interfaces
- `adapters/` - Implementations
- Domain has no external dependencies

### Clean Architecture

```bash
# Check for clean architecture
ls -d */ 2>/dev/null | grep -iE "entities|usecases|interfaces|frameworks"
```

**Signs:**
- Dependency rule: outer depends on inner
- Entities at center
- Use cases contain application logic
- Frameworks at outer layer

### Microservices

```bash
# Check for service boundaries
ls -d services/*/ packages/*/ apps/*/ 2>/dev/null
```

**Signs:**
- Multiple independent services
- Each with own dependencies
- Service-to-service communication
- Separate deployables

### Monolith

**Signs:**
- Single `app/` or `src/` directory
- Shared database access throughout
- No clear service boundaries
- Single deployment unit

### Event-Driven

```bash
# Check for event patterns
ls -d */ 2>/dev/null | grep -iE "events|handlers|subscribers|listeners"

# Check for event code patterns
grep -r "emit\|publish\|subscribe\|on\(" --include="*.ts" | head -20
```

**Signs:**
- `events/`, `handlers/` directories
- Event emitter patterns
- Message queues integration
- Loose coupling via events

### CQRS

```bash
# Check for CQRS structure
ls -d */ 2>/dev/null | grep -iE "commands|queries|read|write"
```

**Signs:**
- Separate `commands/` and `queries/`
- Different read/write models
- Event sourcing often paired

## Framework Pattern Indicators

| Framework | Implied Pattern |
|-----------|-----------------|
| React + Redux | Flux/unidirectional |
| Angular | Component-based + DI |
| Express | Middleware pipeline |
| NestJS | Modular + DI |
| Django | MTV (Model-Template-View) |
| Rails | MVC + Convention |
| Spring | Layered + DI |
| FastAPI | Repository pattern common |

## Code-Based Detection

### Dependency Injection

```bash
# Look for DI patterns
grep -r "@Injectable\|@Inject\|@Autowired" --include="*.ts" --include="*.java"
```

### Repository Pattern

```bash
# Look for repository classes
grep -rl "Repository\|interface.*Repository" --include="*.ts"
```

### Factory Pattern

```bash
# Look for factory classes
grep -rl "Factory\|create.*Instance" --include="*.ts"
```

## Output Format

```markdown
## Detected Patterns

### Primary Architecture: Layered

**Evidence:**
- Directory structure: `presentation/`, `business/`, `data/`
- Imports flow: presentation → business → data
- Clear layer boundaries

### Secondary Patterns:

| Pattern | Location | Purpose |
|---------|----------|---------|
| Repository | `data/repositories/` | Data access abstraction |
| Factory | `business/factories/` | Object creation |
| DI | Throughout | Dependency management |

### Framework Influence: NestJS

- Modular structure
- Decorator-based DI
- Controller/Service/Module organization
```
