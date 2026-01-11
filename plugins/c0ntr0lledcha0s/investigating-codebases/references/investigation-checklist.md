# Investigation Checklist

Step-by-step guide for thorough code investigation.

## Phase 1: Initial Reconnaissance

### Project Type Identification
- [ ] Check `package.json`, `Cargo.toml`, `setup.py`, `go.mod` for project type
- [ ] Identify primary programming language(s)
- [ ] Note framework(s) used (React, Vue, Django, Express, etc.)
- [ ] Check project version and dependencies

### Directory Structure
- [ ] Map top-level directories and their purposes
- [ ] Identify main source directory (`src/`, `lib/`, `app/`)
- [ ] Locate test directory (`tests/`, `__tests__/`, `spec/`)
- [ ] Find configuration files (`.env.example`, `config/`)
- [ ] Note documentation directory (`docs/`, `README.md`)

### Entry Points
- [ ] Find main entry point(s)
  - Node.js: `index.js`, `server.js`, `main.ts`
  - Python: `__main__.py`, `app.py`, `main.py`
  - Go: `main.go`, `cmd/*/main.go`
  - Rust: `main.rs`, `lib.rs`
- [ ] Identify CLI entry points
- [ ] Locate API/server initialization
- [ ] Find build targets

## Phase 2: Feature Investigation

### Locate Relevant Code
- [ ] Search for feature-related keywords
- [ ] Find route/endpoint definitions
- [ ] Identify controllers/handlers
- [ ] Locate service/business logic layer
- [ ] Find data access layer (repositories, models)

### Trace Execution Flow
- [ ] Start at entry point (route, command, UI trigger)
- [ ] Follow through middleware/interceptors
- [ ] Track to handler/controller
- [ ] Trace to service/business logic
- [ ] Follow to data layer
- [ ] Note response/render path

### Understand Data Flow
- [ ] Identify input sources (request body, params, query)
- [ ] Track data transformations
- [ ] Note validation points
- [ ] Trace database queries
- [ ] Follow data to response

## Phase 3: Pattern Recognition

### Code Organization
- [ ] Note naming conventions (files, functions, variables)
- [ ] Identify organizational patterns (feature-based, layer-based)
- [ ] Recognize module structure
- [ ] Note export/import patterns

### Design Patterns
- [ ] Look for creational patterns (Factory, Singleton, Builder)
- [ ] Identify structural patterns (Adapter, Decorator, Facade)
- [ ] Find behavioral patterns (Observer, Strategy, Command)
- [ ] Note architectural patterns (MVC, Repository, Service Layer)

### Common Utilities
- [ ] Find shared utility functions
- [ ] Identify helper modules
- [ ] Note common abstractions
- [ ] Locate configuration management

## Phase 4: Dependencies & Integration

### Internal Dependencies
- [ ] Map component relationships
- [ ] Track module imports/dependencies
- [ ] Identify circular dependencies
- [ ] Note coupling levels

### External Dependencies
- [ ] List external packages used
- [ ] Note API integrations
- [ ] Identify database connections
- [ ] Find external service calls

### Integration Points
- [ ] Locate API boundaries
- [ ] Find event handlers
- [ ] Note message queue consumers
- [ ] Identify webhooks

## Phase 5: Quality Assessment

### Code Quality
- [ ] Note code organization clarity
- [ ] Assess naming quality
- [ ] Check for code duplication
- [ ] Evaluate function/class sizes
- [ ] Note comment quality

### Error Handling
- [ ] Identify error handling strategy
- [ ] Find error boundaries/middleware
- [ ] Note logging practices
- [ ] Check validation approaches

### Testing
- [ ] Locate test files
- [ ] Identify testing frameworks
- [ ] Note test coverage areas
- [ ] Check for integration/e2e tests

### Security
- [ ] Look for input validation
- [ ] Check authentication implementation
- [ ] Note authorization patterns
- [ ] Identify sensitive data handling

## Phase 6: Documentation

### Create File Reference Map
- [ ] List all key files with line ranges
- [ ] Note file purposes and responsibilities
- [ ] Document relationships between files

### Document Execution Flow
- [ ] Write step-by-step flow description
- [ ] Include file references for each step
- [ ] Note decision points and branches

### Identify Patterns
- [ ] Document design patterns found
- [ ] Note architectural decisions
- [ ] List conventions observed

### Note Improvement Opportunities
- [ ] Identify potential issues
- [ ] Suggest refactoring opportunities
- [ ] Note missing documentation
- [ ] Flag security concerns

## Investigation Quality Checklist

Before concluding investigation:
- [ ] Can you explain the feature/component to someone else?
- [ ] Do you know where to find the main logic?
- [ ] Can you trace the complete execution flow?
- [ ] Have you identified the key files and their purposes?
- [ ] Do you understand how data flows through the system?
- [ ] Have you noted relevant patterns and conventions?
- [ ] Can you identify potential edge cases or issues?
- [ ] Have you documented your findings with file references?

## Tips

**Start Broad, Then Narrow**
- Get high-level overview before diving deep
- Understand architecture before implementation details

**Follow the Data**
- Data flow often reveals system structure
- Track transformations and validations

**Use Multiple Search Strategies**
- Keyword search for concepts
- Pattern search for structures
- File name search for conventions

**Document As You Go**
- Note findings immediately
- Include file references
- Mark areas for deeper investigation

**Verify Assumptions**
- Cross-reference findings
- Check multiple examples of patterns
- Test hypotheses by tracing code

---

*Part of research-agent/investigating-codebases skill*
