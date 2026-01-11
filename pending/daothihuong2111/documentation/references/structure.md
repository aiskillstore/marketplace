# Documentation Structure

Complete directory structure and organization for documentation.

## Directory Tree

```
docs/
├── README.md                          # Master index with rules
│
├── guides/                            # User and developer guides
│   ├── user-guide.md                  # End-user documentation
│   ├── configuration.md               # Configuration guide
│   └── development.md                 # Developer contribution guide
│
├── architecture/                      # Architecture documentation
│   ├── overview.md                    # 3-layer architecture
│   └── integrations.md                # External integrations guide
│
└── screens/                           # Screen-based documentation
    ├── welcome/                       # Welcome screen
    │   ├── README.md                  # Overview
    │   └── technical.md               # Implementation
    │
    ├── home/                          # Home screen
    │   ├── README.md                  # Overview
    │   ├── features.md                # Detailed features
    │   ├── technical.md               # Implementation
    │   └── flows.md                   # User flows
    │
    └── config/                        # Config screen
        ├── README.md                  # Overview
        └── technical.md               # Implementation
```

## Root Level

### docs/README.md
**Purpose**: Master documentation index

**Content**:
- Documentation rules and guidelines
- Directory structure overview
- Quick navigation links
- When to create/update docs

**DO NOT MODIFY** without explicit approval.

## guides/

User-facing and developer-facing guides.

### guides/user-guide.md
**Purpose**: End-user documentation

**Content**:
- Getting started
- Basic usage
- Common tasks
- Troubleshooting

**Audience**: End users

**Max Lines**: 500

### guides/configuration.md
**Purpose**: Configuration guide

**Content**:
- Configuration options
- Environment variables
- Config file format
- Provider setup

**Audience**: Users setting up the app

**Max Lines**: 300

### guides/development.md
**Purpose**: Developer contribution guide

**Content**:
- Project structure
- Development workflow
- Code style
- Testing
- Pull request process

**Audience**: Contributors

**Max Lines**: 500

## architecture/

Technical architecture documentation.

### architecture/overview.md
**Purpose**: High-level architecture

**Content**:
- 3-layer architecture
- Design patterns (MVP, Repository, Use Case)
- Component relationships
- Data flow
- Design decisions

**Audience**: Developers, architects

**Max Lines**: 500

### architecture/integrations.md
**Purpose**: External integrations

**Content**:
- VS Code extension integration
- MCP client integration
- A2A server integration
- Protocol specifications

**Audience**: Integration developers

**Max Lines**: 500

## screens/

Screen-specific documentation organized by screen name.

### Screen Structure

Each screen MUST have this structure:

```
screens/{screen-name}/
├── README.md         # Overview (REQUIRED)
├── features.md       # Features (OPTIONAL)
├── technical.md      # Technical (REQUIRED)
└── flows.md          # Flows (OPTIONAL)
```

### When to Include Optional Files

**features.md** - Include if:
- Screen has 5+ distinct features
- Features need detailed explanation
- Features have complex configurations

**flows.md** - Include if:
- Screen has multi-step workflows
- Complex state transitions
- Multiple user paths

## Screen File Details

### screens/{screen-name}/README.md
**Purpose**: Screen overview

**Content**:
- What the screen does
- Main features (bullet points)
- Basic usage
- Component hierarchy
- Layout diagram
- Keyboard shortcuts

**Max Lines**: 300

**Template**: See `templates.md` → Screen README

### screens/{screen-name}/features.md
**Purpose**: Detailed feature documentation

**Content**:
- Each feature explained in detail
- Configuration options
- Examples for each feature
- Error handling
- Implementation references

**Max Lines**: 400

**Template**: See `templates.md` → Screen Features

### screens/{screen-name}/technical.md
**Purpose**: Implementation details

**Content**:
- Component architecture
- State management
- Props/interfaces
- Code examples
- Validation logic
- Testing approach
- Performance notes

**Max Lines**: 500

**Template**: See `templates.md` → Screen Technical

### screens/{screen-name}/flows.md
**Purpose**: User interaction flows

**Content**:
- Step-by-step user flows
- State transition diagrams
- Sequence diagrams
- Error recovery flows
- Mermaid diagrams

**Max Lines**: 300

**Template**: See `templates.md` → Screen Flows

## Current Screens

### screens/welcome/
First-time setup wizard.

**Files**:
- `README.md` - Overview of welcome wizard
- `technical.md` - Implementation details

**Key Features**:
- Provider selection
- API key input
- Model configuration

### screens/home/
Main chat interface.

**Files**:
- `README.md` - Overview of home screen
- `features.md` - 10+ features documented
- `technical.md` - Implementation details
- `flows.md` - User interaction flows

**Key Features**:
- Conversation display
- Streaming responses
- Slash commands
- Session management
- Markdown rendering

### screens/config/
Configuration wizard.

**Files**:
- `README.md` - Overview of config wizard
- `technical.md` - Implementation details

**Key Features**:
- Provider selection
- Model configuration
- API key management
- Settings validation

## Adding New Documentation

### Adding a New Screen

1. Create directory: `mkdir -p docs/screens/{screen-name}`
2. Create `README.md` (required)
3. Create `technical.md` (required)
4. Create `features.md` (if 5+ features)
5. Create `flows.md` (if complex workflows)
6. Update `docs/README.md` links

### Adding a New Guide

1. Create file: `docs/guides/{guide-name}.md`
2. Use Guide template from `templates.md`
3. Update `docs/README.md` links
4. Keep under 500 lines

### Adding Architecture Docs

1. Create file: `docs/architecture/{topic}.md`
2. Use Architecture template from `templates.md`
3. Update `docs/README.md` links
4. Keep under 500 lines

## Navigation

### Cross-Referencing

Use relative paths for links:

**From screen to guide:**
```markdown
[Configuration Guide](../../guides/configuration.md)
```

**From guide to screen:**
```markdown
[Home Screen](../screens/home/README.md)
```

**Within same directory:**
```markdown
[Technical Details](./technical.md)
```

### Index Links

Every document should link to:
- Related documents
- Parent index
- Main docs/README.md (if deep nested)

Example:
```markdown
## Related

- [User Guide](../../guides/user-guide.md)
- [Technical Details](./technical.md)
- [Main Index](../../README.md)
```

## File Organization Rules

### Rule 1: One Screen = One Directory
Each screen gets its own directory under `screens/`.

### Rule 2: Required Files
Every screen MUST have:
- `README.md`
- `technical.md`

### Rule 3: Consistent Naming
Use exact names:
- ✅ `README.md`, `features.md`, `technical.md`, `flows.md`
-  `overview.md`, `guide.md`, `manual.md`

### Rule 4: No Nested Screens
Screens are flat:
```
✅ docs/screens/home/
✅ docs/screens/config/
 docs/screens/home/subscreen/
```

### Rule 5: No Loose Files
All docs must be in:
- `guides/`
- `architecture/`
- `screens/{name}/`

Not allowed:
```
 docs/random-file.md
 docs/notes.md
```

## Special Cases

### Integration Documentation
Goes in `architecture/`:
- `architecture/integrations.md` - All integrations
- NOT separate files per integration

### Configuration Documentation
Goes in `guides/`:
- `guides/configuration.md` - User-facing config
- `screens/config/` - Config UI screen

### API Documentation
Goes in `architecture/`:
- Add section to `architecture/overview.md`
- Or create `architecture/api.md` if large

## Migration Guide

If restructuring documentation:

1. Create new structure
2. Copy/consolidate content
3. Update all internal links
4. Delete old files
5. Update docs/README.md
6. Commit with detailed message

Example commit:
```
docs: restructure {topic} documentation

- Consolidated 5 files into 2
- Updated all cross-references
- Deleted redundant files
- Added missing examples
```

## Maintenance

### Regular Reviews

Quarterly, review documentation for:
- Broken links
- Outdated examples
- Missing features
- Code reference accuracy
- File size (split if >450 lines)

### Updates

When code changes:
- Update related documentation
- Update code references (file:line)
- Test all examples
- Update diagrams if needed

### Deletions

When features are removed:
- Delete related documentation
- Update cross-references
- Update docs/README.md
- Commit with explanation
