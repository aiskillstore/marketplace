# FiftyOne Plugin Structure

## Directory Layout

```
my-plugin/
├── fiftyone.yml          # Required: Plugin manifest
├── __init__.py           # Python operators/panels
├── requirements.txt      # Python dependencies (optional)
├── assets/               # Static assets (optional)
│   └── icon.svg
├── package.json          # JS only
├── src/                  # JS only
│   └── index.tsx
└── dist/                 # JS only (compiled)
    └── index.umd.js
```

## fiftyone.yml

```yaml
name: "@your-org/plugin-name"
type: plugin
author: Your Name
version: 1.0.0
url: https://github.com/your-org/plugin-name
license: Apache 2.0
description: Brief description
fiftyone:
  version: ">=0.22"
operators:
  - operator_one
  - operator_two
panels:
  - panel_name
secrets:
  - API_KEY_NAME
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Use `@org/name` format |
| `type` | Yes | Always `plugin` |
| `author` | No | Your name or organization |
| `version` | No | Semantic version (1.0.0) |
| `url` | No | Repository URL |
| `license` | No | License type |
| `description` | No | Brief description |
| `fiftyone.version` | No | Minimum FiftyOne version |
| `operators` | No* | List of operator names |
| `panels` | No* | List of panel names |
| `secrets` | No | Required environment variables |

*At least one of `operators` or `panels` required.

## __init__.py Template

```python
"""My Plugin - Brief description"""
import fiftyone.operators as foo
import fiftyone.operators.types as types


class MyOperator(foo.Operator):
    @property
    def config(self):
        return foo.OperatorConfig(
            name="my_operator",
            label="My Operator",
            description="What it does",
            dynamic=False,
            execute_as_generator=False,
            unlisted=False,
            allow_immediate_execution=True,
            allow_delegated_execution=False,
        )

    def resolve_input(self, ctx):
        inputs = types.Object()
        # Add input fields
        return types.Property(inputs)

    def execute(self, ctx):
        # Implementation
        return {}

    def resolve_output(self, ctx):
        outputs = types.Object()
        return types.Property(outputs)


def register(p):
    p.register(MyOperator)
```

## Naming Conventions

| Type | Format | Examples |
|------|--------|----------|
| Plugin | `@org/plugin-name` | `@voxel51/brain`, `@myorg/custom-labels` |
| Operator | snake_case | `compute_embeddings`, `export_to_coco` |
| Panel | snake_case | `embeddings_panel`, `annotation_viewer` |

## Plugin Location

```bash
# Default
~/.fiftyone/plugins/

# Check your config
python -c "import fiftyone as fo; print(fo.config.plugins_dir)"
```
