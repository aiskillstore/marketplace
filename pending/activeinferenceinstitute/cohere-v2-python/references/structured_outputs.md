# Cohere Structured Outputs with JSON Schema Mode

## Overview

Cohere's Structured Outputs feature forces the LLM to strictly follow a user-defined JSON schema, ensuring responses conform to specified data structures. This is essential for entity extraction, data validation, and seamless integration with downstream applications.

## Two Modes of Operation

### JSON Mode (Basic)

Instructs the model to return valid JSON without enforcing a specific structure:

```python
response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": "Extract the person's name and age from: 'John Smith is 30 years old.' Return as JSON."
        }
    ],
    response_format={"type": "json_object"}
)
```

**Important**: Always explicitly instruct the model to generate JSON in your prompt when using JSON mode.

### JSON Schema Mode (Advanced)

Enforces a specific schema structure:

```python
response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": "Extract the person's name and age from: 'John Smith is 30 years old.'"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
    }
)
```

## Schema Requirements

### Basic Structure

- Top-level type must be `"object"`
- Each object must have at least one required field
- Unlimited nesting levels supported in schema mode

### Required Fields

Every schema must specify required fields:

```python
{
    "type": "object",
    "properties": {
        "field1": {"type": "string"},
        "field2": {"type": "integer"}
    },
    "required": ["field1", "field2"]  # At least one required
}
```

## Supported Data Types

### Basic Types

**String:**
```python
{"type": "string"}
```

**Integer:**
```python
{"type": "integer"}
```

**Number (Float):**
```python
{"type": "number"}
```

**Boolean:**
```python
{"type": "boolean"}
```

### Arrays

**Simple arrays:**
```python
{
    "tags": {
        "type": "array",
        "items": {"type": "string"}
    }
}
```

**Arrays of objects:**
```python
{
    "people": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
    }
}
```

### Nested Objects

```python
{
    "type": "object",
    "properties": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            },
            "required": ["name"]
        }
    },
    "required": ["person"]
}
```

## Advanced Schema Features

### Enums

Restrict values to a specific set:

```python
{
    "sentiment": {
        "type": "string",
        "enum": ["positive", "negative", "neutral"]
    }
}
```

### Patterns (Regex)

Validate string patterns:

```python
{
    "email": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    }
}
```

### Format Validation

Built-in format validators:

```python
{
    "created_at": {
        "type": "string",
        "format": "date-time"  # ISO 8601: 2024-01-01T12:00:00Z
    },
    "birth_date": {
        "type": "string",
        "format": "date"  # YYYY-MM-DD
    },
    "meeting_time": {
        "type": "string",
        "format": "time"  # HH:MM:SS
    },
    "user_id": {
        "type": "string",
        "format": "uuid"  # UUID format
    }
}
```

### Schema References ($ref and $def)

Reuse schema definitions:

```python
{
    "type": "object",
    "$defs": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
    },
    "properties": {
        "author": {"$ref": "#/$defs/person"},
        "reviewer": {"$ref": "#/$defs/person"}
    },
    "required": ["author"]
}
```

## Entity Extraction Patterns

### Single Entity Extraction

```python
import cohere

co = cohere.ClientV2(api_key="<YOUR API KEY>")

text = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976."

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": f"Extract the company information from: {text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string"},
                "founder": {"type": "string"},
                "location": {"type": "string"},
                "founded_year": {"type": "integer"}
            },
            "required": ["company_name"]
        }
    }
)

import json
result = json.loads(response.message.content[0].text)
print(result)
# {"company_name": "Apple Inc.", "founder": "Steve Jobs", "location": "Cupertino, California", "founded_year": 1976}
```

### Multiple Entity Extraction

```python
text = """
John Smith works at Google as a Software Engineer. He lives in San Francisco.
Jane Doe is a Data Scientist at Meta, residing in New York.
"""

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": f"Extract all people and their information from: {text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "people": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "company": {"type": "string"},
                            "role": {"type": "string"},
                            "location": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }
            },
            "required": ["people"]
        }
    }
)

result = json.loads(response.message.content[0].text)
# {"people": [{"name": "John Smith", "company": "Google", "role": "Software Engineer", "location": "San Francisco"}, ...]}
```

### Hierarchical Entity Extraction

```python
text = """
The meeting on January 15, 2024 included:
- Project Alpha: Led by Alice Johnson, Budget: $50,000
- Project Beta: Led by Bob Williams, Budget: $75,000
"""

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": f"Extract the meeting information: {text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "meeting_date": {
                    "type": "string",
                    "format": "date"
                },
                "projects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "lead": {"type": "string"},
                            "budget": {"type": "number"}
                        },
                        "required": ["name", "lead"]
                    }
                }
            },
            "required": ["meeting_date", "projects"]
        }
    }
)
```

### Entity Extraction with Classification

```python
text = "I love the new iPhone! The battery life is amazing but the price is too high."

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": f"Extract product mentions and sentiment: {text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "overall_sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral", "mixed"]
                },
                "aspects": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "aspect": {"type": "string"},
                            "sentiment": {
                                "type": "string",
                                "enum": ["positive", "negative", "neutral"]
                            },
                            "mention": {"type": "string"}
                        },
                        "required": ["aspect", "sentiment"]
                    }
                }
            },
            "required": ["product", "overall_sentiment"]
        }
    }
)
```

### Named Entity Recognition (NER)

```python
text = "Dr. Sarah Johnson from Stanford University will speak at the AI Conference in Seattle on March 15th."

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "user",
            "content": f"Extract all named entities with their types: {text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {
                                "type": "string",
                                "enum": ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "EVENT", "TITLE"]
                            },
                            "context": {"type": "string"}
                        },
                        "required": ["text", "type"]
                    }
                }
            },
            "required": ["entities"]
        }
    }
)
```

## Schema Limitations

### Unsupported Constraints

The following JSON Schema constraints are NOT supported:
- **Numeric ranges**: `minimum`, `maximum`, `exclusiveMinimum`, `exclusiveMaximum`
- **Array length**: `minItems`, `maxItems`
- **String length**: `minLength`, `maxLength`
- **Complex regex patterns**: Some advanced regex features may not work

### Field Limits

- **Tools mode**: Maximum 200 fields across all tools
- **Schema mode**: No explicit field limit for response_format schemas

## Performance Considerations

### Schema Caching

- **First request**: Incurs latency overhead for schema processing
- **Subsequent requests**: Schema is cached for faster responses
- **Recommendation**: Reuse schemas across multiple requests

### Latency Impact

JSON Schema mode adds processing overhead:
- Simple schemas: Minimal impact
- Complex nested schemas: Moderate impact
- Consider complexity vs. validation tradeoffs

## Best Practices

### 1. Always Specify Required Fields

```python
# Good
{
    "properties": {...},
    "required": ["essential_field"]
}

# Bad - will fail
{
    "properties": {...}
    # Missing required array
}
```

### 2. Use Explicit Instructions in JSON Mode

```python
# Good
content = "Extract name and age as JSON: 'John is 30'"

# Bad
content = "'John is 30'"  # May generate infinite tokens
```

### 3. Start Simple, Then Add Complexity

```python
# Start with basic schema
basic_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    },
    "required": ["name"]
}

# Then expand as needed
complex_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "details": {
            "type": "object",
            "properties": {...}
        }
    },
    "required": ["name"]
}
```

### 4. Use Enums for Classification

```python
# Better than free-form strings
{
    "category": {
        "type": "string",
        "enum": ["tech", "finance", "healthcare", "education"]
    }
}
```

### 5. Validate and Handle Errors

```python
try:
    response = co.chat(
        model="command-a-03-2025",
        messages=[...],
        response_format={"type": "json_object", "schema": schema}
    )
    result = json.loads(response.message.content[0].text)
except json.JSONDecodeError:
    print("Failed to parse JSON response")
except Exception as e:
    print(f"Error: {e}")
```

### 6. Use $ref for Reusable Structures

```python
# Define once, use multiple times
schema = {
    "$defs": {
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    },
    "properties": {
        "home_address": {"$ref": "#/$defs/address"},
        "work_address": {"$ref": "#/$defs/address"}
    }
}
```

## Complete Entity Extraction Example

```python
import cohere
import json

co = cohere.ClientV2(api_key="<YOUR API KEY>")

# Business card extraction
text = """
John Smith
Senior Software Engineer
Acme Corporation
123 Tech Street, San Francisco, CA 94105
Phone: (555) 123-4567
Email: john.smith@acme.com
"""

schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "title": {"type": "string"},
        "company": {"type": "string"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
                "state": {"type": "string"},
                "zip": {"type": "string"}
            },
            "required": ["city"]
        },
        "phone": {"type": "string"},
        "email": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        }
    },
    "required": ["name", "company"]
}

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {
            "role": "system",
            "content": "Extract structured information from business cards accurately."
        },
        {
            "role": "user",
            "content": f"Extract all information from this business card:\n\n{text}"
        }
    ],
    response_format={
        "type": "json_object",
        "schema": schema
    }
)

contact = json.loads(response.message.content[0].text)
print(json.dumps(contact, indent=2))
```

## Additional Resources

- **Structured Outputs Documentation**: https://docs.cohere.com/v2/docs/structured-outputs
- **JSON Schema Specification**: https://json-schema.org/
- **Python SDK**: https://github.com/cohere-ai/cohere-python
