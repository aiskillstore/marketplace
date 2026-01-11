# BAML DTO Generation Cookbook

How to design and generate Data Transfer Objects (DTOs) with BAML for cross-language type safety.

## What Are DTOs in BAML?

BAML classes serve as DTOs that:
- Define the shape of LLM inputs and outputs
- Generate Python and TypeScript types
- Provide runtime validation
- Document expected data structures

## DTO Design Patterns

### Pattern 1: Request/Response Pairs

Define matching input/output types:

```baml
// Request DTO
class AnalyzeBookRequest {
  text string @description("Full text of the book or chapter")
  analysis_type AnalysisType @description("What kind of analysis to perform")
  max_length int? @description("Maximum length of summary in words")
}

enum AnalysisType {
  SUMMARY
  THEMES
  CHARACTERS
  SENTIMENT
}

// Response DTO
class AnalyzeBookResponse {
  analysis string
  confidence float @description("Confidence score 0-1")
  key_points string[]
  metadata AnalysisMetadata
}

class AnalysisMetadata {
  word_count int
  processing_time_ms int
  model_used string
}
```

### Pattern 2: Nested Types

Break complex types into reusable components:

```baml
// Reusable address type
class Address {
  street string
  city string
  state string
  postal_code string
  country string @description("ISO 3166-1 alpha-2 country code")
}

// Reusable contact type
class ContactInfo {
  email string
  phone string?
  address Address?
}

// Composed user type
class User {
  id int
  name string
  contact ContactInfo
}
```

### Pattern 3: Union Types for Polymorphism

Handle multiple response shapes:

```baml
// Success case
class SuccessResult {
  data ResultData
  warnings string[]
}

// Error case
class ErrorResult {
  error_code string
  message string
  details map<string, string>?
}

// Union type
function ProcessData(input: Input) -> SuccessResult | ErrorResult {
  client GPT4
  prompt #"..."#
}
```

### Pattern 4: Partial Types

For updates that don't require all fields:

```baml
// Full type
class User {
  id int
  email string
  name string
  bio string?
  avatar_url string?
}

// Partial for updates (all optional)
class UserUpdate {
  email string?
  name string?
  bio string?
  avatar_url string?
}
```

## Generated Code Examples

### Python Generated Types

```python
# baml_client/types.py (generated)
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class AnalysisType(str, Enum):
    SUMMARY = "SUMMARY"
    THEMES = "THEMES"
    CHARACTERS = "CHARACTERS"
    SENTIMENT = "SENTIMENT"

class AnalyzeBookRequest(BaseModel):
    text: str
    analysis_type: AnalysisType
    max_length: Optional[int] = None

class AnalysisMetadata(BaseModel):
    word_count: int
    processing_time_ms: int
    model_used: str

class AnalyzeBookResponse(BaseModel):
    analysis: str
    confidence: float
    key_points: List[str]
    metadata: AnalysisMetadata
```

### TypeScript Generated Types

```typescript
// baml_client/types.ts (generated)
export enum AnalysisType {
  SUMMARY = "SUMMARY",
  THEMES = "THEMES",
  CHARACTERS = "CHARACTERS",
  SENTIMENT = "SENTIMENT"
}

export interface AnalyzeBookRequest {
  text: string;
  analysis_type: AnalysisType;
  max_length?: number;
}

export interface AnalysisMetadata {
  word_count: number;
  processing_time_ms: number;
  model_used: string;
}

export interface AnalyzeBookResponse {
  analysis: string;
  confidence: number;
  key_points: string[];
  metadata: AnalysisMetadata;
}
```

## Using Generated DTOs

### Python Usage

```python
from baml_client import b
from baml_client.types import AnalyzeBookRequest, AnalysisType

async def analyze_book(text: str) -> dict:
    request = AnalyzeBookRequest(
        text=text,
        analysis_type=AnalysisType.SUMMARY,
        max_length=200
    )

    response = await b.AnalyzeBook(request)

    return {
        "analysis": response.analysis,
        "confidence": response.confidence,
        "key_points": response.key_points,
        "metadata": response.metadata.model_dump()
    }
```

### TypeScript Usage

```typescript
import { b } from './baml_client';
import type { AnalyzeBookRequest, AnalyzeBookResponse } from './baml_client/types';
import { AnalysisType } from './baml_client/types';

async function analyzeBook(text: string): Promise<AnalyzeBookResponse> {
  const request: AnalyzeBookRequest = {
    text,
    analysis_type: AnalysisType.SUMMARY,
    max_length: 200
  };

  return await b.AnalyzeBook(request);
}
```

## Best Practices

### 1. Use Descriptive Names

```baml
// Good
class BookSearchQuery {
  title_keywords string[]
  author_name string?
  published_after string? @description("ISO date YYYY-MM-DD")
}

// Bad
class Query {
  q string[]
  a string?
  d string?
}
```

### 2. Add Descriptions for LLM Guidance

```baml
class ReviewAnalysis {
  sentiment string @description("One of: positive, negative, neutral, mixed")
  rating float @description("Numeric rating from 1.0 to 5.0")
  highlights string[] @description("3-5 key positive points from the review")
  concerns string[] @description("Any negative points or concerns mentioned")
}
```

### 3. Use Enums for Fixed Values

```baml
// Good - explicit enum
enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

class Task {
  priority Priority
}

// Bad - string that could be anything
class Task {
  priority string  // What values are valid?
}
```

### 4. Keep DTOs Focused

```baml
// Good - focused types
class BookSummary {
  title string
  author string
  summary string
}

class BookDetails {
  isbn string
  publisher string
  pages int
  language string
}

// Bad - everything in one type
class Book {
  title string
  author string
  summary string
  isbn string
  publisher string
  pages int
  language string
  reviews ReviewAnalysis[]
  similar_books string[]
  purchase_links string[]
  // ... too many concerns
}
```

## Validation and Constraints

### Field Constraints via Descriptions

```baml
class UserInput {
  age int @description("Must be between 0 and 150")
  email string @description("Valid email address format")
  username string @description("3-30 alphanumeric characters")
}
```

### Runtime Validation (Python)

```python
from pydantic import field_validator
from baml_client.types import UserInput

class ValidatedUserInput(UserInput):
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if not 0 <= v <= 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

## Migration Strategy

When changing DTOs:

1. **Add** new fields as optional first
2. **Generate** new clients
3. **Update** all consumers
4. **Make** required if needed
5. **Remove** deprecated fields

```baml
// Step 1: Add new field as optional
class User {
  id int
  name string
  email string
  phone string?  // New, optional
}

// Step 4: Make required after migration
class User {
  id int
  name string
  email string
  phone string  // Now required
}
```
