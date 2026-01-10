---
name: cohere-v2-python
description: Master Cohere v2 Chat API with Python, specializing in entity extraction using JSON Schema mode for structured outputs. Use when extracting entities from text, building data extraction pipelines, implementing NER systems, or requiring validated JSON responses from LLMs.
---

# Cohere v2 Python

## Overview

Cohere's v2 Chat API provides powerful conversational AI capabilities with a specialized focus on structured outputs through JSON Schema mode. This skill covers entity extraction, data validation, and integration patterns for building production-ready systems that require consistent, validated responses from LLMs.

## When to Use This Skill

Apply this skill when:
- Extracting structured entities from unstructured text (names, dates, locations, organizations)
- Building Named Entity Recognition (NER) systems
- Implementing data extraction pipelines with validated outputs
- Requiring JSON responses that conform to specific schemas
- Processing documents for information extraction
- Building classification systems with constrained outputs
- Integrating LLM responses with downstream databases or APIs

## Core Capabilities

### 1. Basic Chat API

Initialize and use the Cohere Client for conversational tasks:

```python
import cohere

co = cohere.ClientV2(api_key="<YOUR API KEY>")

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": "Summarize the key features of quantum computing."}
    ],
)

print(response.message.content[0].text)
```

Available models:
- `command-a-03-2025` - Latest generation model

For comprehensive API parameters, streaming, RAG, and tool use, refer to `references/chat_api.md`.

### 2. Entity Extraction with JSON Schema Mode

The primary strength of Cohere v2 is structured outputs using JSON Schema mode, which guarantees responses conform to your specified schema.

**Simple Entity Extraction:**

```python
text = "Dr. Sarah Johnson from Stanford University will speak at the AI Conference in Seattle on March 15th."

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": f"Extract all entities: {text}"}
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "person": {"type": "string"},
                "title": {"type": "string"},
                "organization": {"type": "string"},
                "event": {"type": "string"},
                "location": {"type": "string"},
                "date": {"type": "string", "format": "date"}
            },
            "required": ["person"]
        }
    }
)

import json
entities = json.loads(response.message.content[0].text)
```

**Key Principles:**
- Top-level type must be `"object"`
- At least one field must be in `"required"` array
- Schema is strictly enforced - invalid responses are regenerated
- First request has latency overhead; subsequent requests are cached

### 3. Multiple Entity Extraction

Extract arrays of entities for batch processing:

```python
text = """
John Smith works at Google as a Software Engineer in San Francisco.
Jane Doe is a Data Scientist at Meta in New York.
Bob Wilson leads the AI team at OpenAI in Seattle.
"""

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": f"Extract all people and their details: {text}"}
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
                        "required": ["name", "company"]
                    }
                }
            },
            "required": ["people"]
        }
    }
)

result = json.loads(response.message.content[0].text)
for person in result["people"]:
    print(f"{person['name']} works at {person['company']}")
```

### 4. Classification with Enums

Use enums to constrain outputs to specific categories:

```python
text = "I absolutely love this product! The quality is amazing and customer service was helpful."

response = co.chat(
    model="command-a-03-2025",
    messages=[
        {"role": "user", "content": f"Analyze sentiment and aspects: {text}"}
    ],
    response_format={
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
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
                            }
                        },
                        "required": ["aspect", "sentiment"]
                    }
                }
            },
            "required": ["overall_sentiment", "aspects"]
        }
    }
)
```

**Benefits of Enums:**
- Guarantees valid category values
- Eliminates post-processing validation
- Enables direct database insertion
- Supports downstream logic without error handling

## Common Entity Extraction Patterns

### Named Entity Recognition (NER)

```python
schema = {
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
                        "enum": ["PERSON", "ORGANIZATION", "LOCATION", "DATE", "EVENT", "PRODUCT"]
                    },
                    "context": {"type": "string"}
                },
                "required": ["text", "type"]
            }
        }
    },
    "required": ["entities"]
}
```

### Resume/CV Parsing

```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        "phone": {"type": "string"},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "role": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"},
                    "description": {"type": "string"}
                },
                "required": ["company", "role"]
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree": {"type": "string"},
                    "field": {"type": "string"},
                    "graduation_year": {"type": "integer"}
                },
                "required": ["institution"]
            }
        },
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["name"]
}
```

### Invoice/Receipt Extraction

```python
schema = {
    "type": "object",
    "properties": {
        "invoice_number": {"type": "string"},
        "invoice_date": {"type": "string", "format": "date"},
        "vendor": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {"type": "string"},
                "tax_id": {"type": "string"}
            },
            "required": ["name"]
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "total": {"type": "number"}
                },
                "required": ["description", "total"]
            }
        },
        "subtotal": {"type": "number"},
        "tax": {"type": "number"},
        "total": {"type": "number"}
    },
    "required": ["invoice_number", "vendor", "total"]
}
```

### Medical Report Extraction

```python
schema = {
    "type": "object",
    "properties": {
        "patient": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "gender": {
                    "type": "string",
                    "enum": ["male", "female", "other", "unknown"]
                }
            },
            "required": ["name"]
        },
        "diagnosis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string"},
                    "severity": {
                        "type": "string",
                        "enum": ["mild", "moderate", "severe"]
                    },
                    "notes": {"type": "string"}
                },
                "required": ["condition"]
            }
        },
        "medications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "dosage": {"type": "string"},
                    "frequency": {"type": "string"}
                },
                "required": ["name"]
            }
        },
        "visit_date": {"type": "string", "format": "date"}
    },
    "required": ["patient", "visit_date"]
}
```

## Advanced Schema Features

### Nested Objects with Validation

```python
schema = {
    "type": "object",
    "properties": {
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "headquarters": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "country": {"type": "string"}
                    },
                    "required": ["city", "country"]
                }
            },
            "required": ["name"]
        }
    },
    "required": ["company"]
}
```

### Schema Reuse with $ref

```python
schema = {
    "type": "object",
    "$defs": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"}
            },
            "required": ["name"]
        }
    },
    "properties": {
        "primary_contact": {"$ref": "#/$defs/person"},
        "secondary_contact": {"$ref": "#/$defs/person"}
    },
    "required": ["primary_contact"]
}
```

### Format Validation

```python
schema = {
    "type": "object",
    "properties": {
        "created_at": {
            "type": "string",
            "format": "date-time"  # ISO 8601: 2024-01-01T12:00:00Z
        },
        "birth_date": {
            "type": "string",
            "format": "date"  # YYYY-MM-DD
        },
        "user_id": {
            "type": "string",
            "format": "uuid"
        },
        "email": {
            "type": "string",
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        }
    },
    "required": ["user_id"]
}
```

## Workflow: Building an Entity Extraction Pipeline

### Step 1: Define Your Schema

```python
# Identify entities you need to extract
entity_schema = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "type": {"type": "string", "enum": ["PERSON", "ORG", "LOCATION"]},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]}
                },
                "required": ["text", "type"]
            }
        }
    },
    "required": ["entities"]
}
```

### Step 2: Create Extraction Function

```python
def extract_entities(text, schema):
    response = co.chat(
        model="command-a-03-2025",
        messages=[
            {
                "role": "system",
                "content": "Extract entities accurately with appropriate confidence levels."
            },
            {
                "role": "user",
                "content": f"Extract all entities: {text}"
            }
        ],
        response_format={
            "type": "json_object",
            "schema": schema
        }
    )
    return json.loads(response.message.content[0].text)
```

### Step 3: Batch Processing

```python
documents = [
    "Text 1...",
    "Text 2...",
    "Text 3..."
]

results = []
for doc in documents:
    entities = extract_entities(doc, entity_schema)
    results.append({
        "document": doc,
        "entities": entities["entities"]
    })
```

### Step 4: Store in Database

```python
import surrealdb  # Example with SurrealDB

async def store_entities(entities):
    async with Surreal("ws://localhost:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("entities", "database")

        for entity in entities["entities"]:
            await db.create("entity", entity)
```

## Best Practices

### Schema Design
- Start with required fields only, add optional fields iteratively
- Use enums for classification to guarantee valid outputs
- Leverage format validation (date, uuid, email) for data quality
- Use $ref for repeated structures to keep schemas DRY

### Prompting
- System messages override user instructions - use for extraction guidelines
- Be explicit about what to extract in user messages
- Always instruct model to generate JSON in JSON mode (without schema)
- Provide examples in system message for complex extractions

### Performance
- Schemas are cached after first request - reuse schemas across calls
- Simple schemas have minimal latency overhead
- Complex nested schemas add moderate processing time
- Consider batching extractions when processing multiple documents

### Error Handling
- Always wrap JSON parsing in try-except blocks
- Validate required fields exist even with schema enforcement
- Handle API errors gracefully with exponential backoff
- Log failed extractions for debugging and reprocessing

### Production Considerations
- Monitor token usage via `response.meta.tokens`
- Implement rate limiting and request queuing
- Cache common extractions to reduce API calls
- Use appropriate model for task complexity vs. cost

## Limitations

### Unsupported Schema Features
- Numeric ranges (minimum/maximum)
- Array length constraints (minItems/maxItems)
- String length constraints (minLength/maxLength)
- Some complex regex patterns

### Current Restrictions
- RAG not supported in JSON mode
- Maximum 200 fields in tools mode
- Schema mode adds latency overhead

## Reference Documentation

This skill includes comprehensive reference documentation:

- **`references/chat_api.md`** - Complete Chat API reference including parameters, streaming, tool use, RAG, and conversation management
- **`references/structured_outputs.md`** - In-depth structured outputs guide with JSON Schema mode, validation, entity extraction patterns, and advanced features

Load these references when implementing specific features or troubleshooting issues.

## Additional Resources

- **API Documentation**: https://docs.cohere.com/v2/docs/chat-api
- **Structured Outputs**: https://docs.cohere.com/v2/docs/structured-outputs
- **Python SDK**: https://github.com/cohere-ai/cohere-python
- **PyPI Package**: https://pypi.org/project/cohere/
- **JSON Schema Specification**: https://json-schema.org/
