# Tool Schema Reference

## JSON Schema Best Practices

### Complete Schema Example

```python
Tool(
    name="search_api",
    description="Search external API for information. Returns JSON results.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query string (supports AND, OR operators)",
                "minLength": 1,
                "maxLength": 500
            },
            "filters": {
                "type": "object",
                "description": "Optional filters to narrow results",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["news", "blog", "documentation"],
                        "description": "Content category"
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string", "format": "date"},
                            "end": {"type": "string", "format": "date"}
                        }
                    }
                }
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (1-100)",
                "minimum": 1,
                "maximum": 100,
                "default": 10
            }
        },
        "required": ["query"]
    }
)
```

### Complex Schema Example

```python
Tool(
    name="create_user",
    description="Create a new user account with validation",
    inputSchema={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "Unique username (alphanumeric, 3-20 chars)",
                "pattern": "^[a-zA-Z0-9_]{3,20}$"
            },
            "email": {
                "type": "string",
                "description": "Valid email address",
                "format": "email"
            },
            "role": {
                "type": "string",
                "description": "User role determining permissions",
                "enum": ["admin", "editor", "viewer"],
                "default": "viewer"
            },
            "metadata": {
                "type": "object",
                "description": "Optional user metadata",
                "properties": {
                    "department": {"type": "string"},
                    "title": {"type": "string"}
                },
                "additionalProperties": False
            }
        },
        "required": ["username", "email"],
        "additionalProperties": False
    }
)
```

## Schema Design Principles

### 1. Use Descriptive Names
```python
# ✅ Good
"search_customer_by_email"
"calculate_shipping_cost"
"generate_invoice_pdf"

# ❌ Bad
"search"
"calc"
"gen"
```

### 2. Provide Comprehensive Descriptions
```python
# ✅ Good
description="""
Search for customers by email address. Returns customer profile including:
- Contact information
- Order history
- Account status
Use this when you need to look up a specific customer by their email.
"""

# ❌ Bad
description="Search customers"
```

### 3. Use Enums for Fixed Options
```python
# ✅ Good
"status": {
    "type": "string",
    "enum": ["pending", "approved", "rejected"],
    "description": "Application status"
}

# ❌ Bad
"status": {
    "type": "string",
    "description": "Status (pending/approved/rejected)"
}
```

### 4. Set Reasonable Constraints
```python
# ✅ Good
"limit": {
    "type": "integer",
    "minimum": 1,
    "maximum": 1000,
    "default": 50,
    "description": "Number of results (1-1000)"
}

# ❌ Bad
"limit": {
    "type": "integer"
}
```

### 5. Use Nested Objects for Complex Data
```python
# ✅ Good
"filters": {
    "type": "object",
    "properties": {
        "date_range": {
            "type": "object",
            "properties": {
                "start": {"type": "string", "format": "date"},
                "end": {"type": "string", "format": "date"}
            }
        },
        "categories": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}
```

## Validation Patterns

### Input Validation
```python
from jsonschema import validate, ValidationError

async def call_tool(name: str, arguments: dict):
    # Get tool schema
    tool_schema = get_tool_schema(name)

    # Validate arguments
    try:
        validate(instance=arguments, schema=tool_schema["inputSchema"])
    except ValidationError as e:
        return [TextContent(
            type="text",
            text=f"Validation error: {e.message}",
            isError=True
        )]

    # Execute tool
    return await execute_tool(name, arguments)
```

## Common Schema Patterns

### String with Pattern
```python
"email": {
    "type": "string",
    "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
}
```

### Array with Item Constraints
```python
"tags": {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 1,
    "maxItems": 10,
    "uniqueItems": true
}
```

### Conditional Properties
```python
"properties": {
    "type": {
        "type": "string",
        "enum": ["email", "sms"]
    },
    "email_address": {
        "type": "string",
        "format": "email"
    },
    "phone_number": {
        "type": "string",
        "pattern": "^\\+[1-9]\\d{1,14}$"
    }
},
"oneOf": [
    {
        "properties": {"type": {"const": "email"}},
        "required": ["email_address"]
    },
    {
        "properties": {"type": {"const": "sms"}},
        "required": ["phone_number"]
    }
]
```
