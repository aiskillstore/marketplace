---
name: fiftyone-develop-plugin
description: Develop custom FiftyOne plugins (operators and panels) from scratch. Use when user wants to create a new plugin, extend FiftyOne with custom operators, build interactive panels, or integrate external APIs into FiftyOne. Guides through requirements, design, coding, testing, and iteration.
---

# Develop FiftyOne Plugins

## Overview

Create custom FiftyOne plugins with full lifecycle support: requirements gathering, code generation, local testing, and iterative refinement.

**Use this skill when:**
- User asks to create/build/develop a FiftyOne plugin
- User wants to add custom functionality to FiftyOne App
- User needs to integrate an external API or service

## Prerequisites

- FiftyOne installed (`pip install fiftyone`)
- Python 3.8+ (for Python plugins)
- Node.js 16+ (only for JavaScript panels)

## Key Directives

**ALWAYS follow these rules:**

### 1. Understand before coding
Ask clarifying questions. Never assume what the plugin should do.

### 2. Plan before implementing
Present file structure and design. Get user approval before generating code.

### 3. Search existing plugins for patterns
```python
list_plugins(enabled=True)
list_operators(builtin_only=False)
get_operator_schema(operator_uri="@voxel51/brain/compute_similarity")
```

### 4. Test locally before done
Install plugin and verify it works in FiftyOne App.

### 5. Iterate on feedback
Refine until the plugin works as expected.

## Workflow

### Phase 1: Requirements

Ask these questions:

1. "What should your plugin do?" (one sentence)
2. "Operator (action) or Panel (interactive UI)?"
3. "What inputs from the user?"
4. "What outputs/results?"
5. "External APIs or secrets needed?"
6. "Background execution for long tasks?"

### Phase 2: Design

1. Search existing plugins for similar patterns
2. Create plan with:
   - Plugin name (`@org/plugin-name`)
   - File structure
   - Operator/panel specs
   - Input/output definitions
3. **Get user approval before coding**

See [PLUGIN-STRUCTURE.md](PLUGIN-STRUCTURE.md) for file formats.

### Phase 3: Generate Code

Create these files:

| File | Required | Purpose |
|------|----------|---------|
| `fiftyone.yml` | Yes | Plugin manifest |
| `__init__.py` | Yes | Python operators/panels |
| `requirements.txt` | If deps | Python dependencies |
| `package.json` | JS only | Node.js metadata |
| `src/index.tsx` | JS only | React components |

Reference docs:
- [PYTHON-OPERATOR.md](PYTHON-OPERATOR.md)
- [PYTHON-PANEL.md](PYTHON-PANEL.md)
- [JAVASCRIPT-PANEL.md](JAVASCRIPT-PANEL.md)

### Phase 4: Install & Test

```bash
# Find plugins directory
python -c "import fiftyone as fo; print(fo.config.plugins_dir)"

# Copy plugin
cp -r ./my-plugin ~/.fiftyone/plugins/

# Verify detection
python -c "import fiftyone as fo; print(fo.plugins.list_plugins())"
```

Test in App:
```python
launch_app(dataset_name="test-dataset")
# Press Cmd/Ctrl + ` to open operator browser
# Search for your operator
```

### Phase 5: Iterate

1. Get user feedback
2. Fix issues
3. Re-copy to plugins directory
4. Restart App if needed
5. Repeat until working

## Quick Reference

### Plugin Types

| Type | Language | Use Case |
|------|----------|----------|
| Operator | Python | Data processing, computations |
| Panel | Python | Simple interactive UI |
| Panel | JavaScript | Rich React-based UI |

### Operator Config Options

| Option | Effect |
|--------|--------|
| `dynamic=True` | Recalculate inputs on change |
| `execute_as_generator=True` | Stream progress |
| `allow_delegated_execution=True` | Background execution |
| `unlisted=True` | Hide from browser |

### Input Types

| Type | Method |
|------|--------|
| Text | `inputs.str()` |
| Number | `inputs.int()` / `inputs.float()` |
| Boolean | `inputs.bool()` |
| Dropdown | `inputs.enum()` |
| File | `inputs.file()` |
| View | `inputs.view_target()` |

## Minimal Example

**fiftyone.yml:**
```yaml
name: "@myorg/hello-world"
type: plugin
operators:
  - hello_world
```

**__init__.py:**
```python
import fiftyone.operators as foo
import fiftyone.operators.types as types

class HelloWorld(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="hello_world",
            label="Hello World"
        )

    def resolve_input(self, ctx):
        inputs = types.Object()
        inputs.str("message", label="Message", default="Hello!")
        return types.Property(inputs)

    def execute(self, ctx):
        print(ctx.params["message"])
        return {"status": "done"}

def register(p):
    p.register(HelloWorld)
```

## Troubleshooting

**Plugin not appearing:**
- Check `fiftyone.yml` exists in plugin root
- Verify location: `~/.fiftyone/plugins/`
- Check for Python syntax errors
- Restart FiftyOne App

**Operator not found:**
- Verify operator listed in `fiftyone.yml`
- Check `register()` function
- Run `list_operators()` to debug

**Secrets not available:**
- Add to `fiftyone.yml` under `secrets:`
- Set environment variables before starting FiftyOne

## Resources

- [Plugin Development Guide](https://docs.voxel51.com/plugins/developing_plugins.html)
- [FiftyOne Plugins Repo](https://github.com/voxel51/fiftyone-plugins)
- [Operator Types API](https://docs.voxel51.com/api/fiftyone.operators.types.html)

## License

Copyright 2017-2025, Voxel51, Inc.
Apache 2.0 License
