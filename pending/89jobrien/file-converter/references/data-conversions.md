---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: file-converter
---

# Data Conversion Reference

## Type Coercion

### JSON to CSV

JSON types map to CSV strings. Handle carefully:

```python
import csv
import json

def flatten_for_csv(data):
    if isinstance(data, list) and all(isinstance(d, dict) for d in data):
        return data
    raise ValueError("CSV requires list of flat dictionaries")

with open("input.json") as f:
    data = json.load(f)

flat_data = flatten_for_csv(data)

with open("output.csv", "w", newline="") as f:
    if flat_data:
        writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
        writer.writeheader()
        writer.writerows(flat_data)
```

### CSV to JSON

All CSV values are strings. Convert types explicitly:

```python
import csv
import json

def infer_type(value):
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    return value

with open("input.csv") as f:
    reader = csv.DictReader(f)
    data = [{k: infer_type(v) for k, v in row.items()} for row in reader]

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

## Nested Structures

### Flattening Nested JSON for CSV

```python
def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        elif isinstance(v, list):
            items.append((new_key, json.dumps(v)))
        else:
            items.append((new_key, v))
    return dict(items)
```

### XML Handling

**xmltodict** converts XML to OrderedDict:

```python
import xmltodict
import json

with open("input.xml") as f:
    data = xmltodict.parse(f.read())

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

Attributes become `@attr`, text becomes `#text`:

```xml
<item id="1">value</item>
```

Becomes:

```json
{"item": {"@id": "1", "#text": "value"}}
```

## YAML Specifics

### Multi-document YAML

```python
import yaml

with open("input.yaml") as f:
    docs = list(yaml.safe_load_all(f))
```

### Preserving Order

```python
import yaml

with open("input.yaml") as f:
    data = yaml.safe_load(f)

with open("output.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

## TOML Handling

Python 3.11+ has `tomllib` built-in (read-only):

```python
import tomllib

with open("input.toml", "rb") as f:
    data = tomllib.load(f)
```

For writing, use `tomli-w`:

```python
import tomli_w

with open("output.toml", "wb") as f:
    tomli_w.dump(data, f)
```

## Schema Considerations

When converting between formats, preserve these semantics:

| Source | Target | Watch For |
|--------|--------|-----------|
| JSON | YAML | Dates (JSON has no date type) |
| YAML | JSON | Anchors/aliases (not supported in JSON) |
| CSV | JSON | Header row naming, empty values |
| JSON | CSV | Nested objects, arrays |
| XML | JSON | Attributes vs elements, namespaces |
