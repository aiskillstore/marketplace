# BAML Patterns Reference

Common patterns and best practices for BAML type definitions and functions.

## Type Definition Patterns

### Simple Types

```baml
// Basic scalar types
class SimpleEntity {
  id int
  name string
  active bool
  score float
  created_at string @description("ISO 8601 datetime")
}
```

### Optional Fields

```baml
class UserProfile {
  id int
  email string           // Required
  name string?           // Optional
  bio string?            // Optional
  avatar_url string?     // Optional
}
```

### Collections

```baml
class Document {
  id int
  title string
  tags string[]                    // Array of strings
  metadata map<string, string>     // Key-value pairs
  sections Section[]               // Array of objects
}

class Section {
  heading string
  content string
}
```

### Enums

```baml
enum Status {
  DRAFT
  PENDING_REVIEW
  APPROVED
  REJECTED
  PUBLISHED
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  URGENT @description("Requires immediate attention")
}
```

### Union Types

```baml
// Simple union
class Result {
  value string | int | float
}

// Complex union with classes
class APIResponse {
  result SuccessData | ErrorData
}

class SuccessData {
  data map<string, string>
}

class ErrorData {
  code int
  message string
}
```

## Function Patterns

### Basic Function

```baml
function SummarizeText(text: string) -> string {
  client GPT4
  prompt #"
    Summarize the following text in 2-3 sentences:

    {{ text }}
  "#
}
```

### Structured Input/Output

```baml
function AnalyzeDocument(doc: DocumentInput) -> DocumentAnalysis {
  client GPT4
  prompt #"
    Analyze the following document:

    Title: {{ doc.title }}
    Content: {{ doc.content }}
    Type: {{ doc.document_type }}

    Provide a structured analysis.

    {{ ctx.output_format }}
  "#
}

class DocumentInput {
  title string
  content string
  document_type DocumentType
}

enum DocumentType {
  ARTICLE
  REPORT
  EMAIL
  MEMO
}

class DocumentAnalysis {
  summary string
  key_points string[]
  sentiment Sentiment
  topics string[]
  action_items string[]
}

enum Sentiment {
  POSITIVE
  NEUTRAL
  NEGATIVE
  MIXED
}
```

### Multi-Step Function

```baml
// Step 1: Extract entities
function ExtractEntities(text: string) -> EntityList {
  client GPT4
  prompt #"..."#
}

// Step 2: Classify entities
function ClassifyEntities(entities: EntityList) -> ClassifiedEntities {
  client GPT4
  prompt #"..."#
}

// Combined pipeline (in application code, not BAML)
```

### Function with Examples

```baml
function ClassifyIntent(query: string) -> Intent {
  client GPT4
  prompt #"
    Classify the user's intent.

    Examples:
    - "What's the weather?" -> WEATHER_QUERY
    - "Set an alarm for 7am" -> CREATE_REMINDER
    - "Tell me a joke" -> ENTERTAINMENT

    User query: {{ query }}

    {{ ctx.output_format }}
  "#
}

enum Intent {
  WEATHER_QUERY
  CREATE_REMINDER
  SEARCH_INFO
  ENTERTAINMENT
  NAVIGATION
  OTHER
}
```

## Client Configuration Patterns

### Basic Client

```baml
client GPT4 {
  provider openai
  options {
    model "gpt-4-turbo"
    temperature 0.7
    max_tokens 2000
  }
}
```

### Client with Retry

```baml
client GPT4Reliable {
  provider openai
  options {
    model "gpt-4-turbo"
  }
  retry_policy {
    max_retries 3
    strategy exponential_backoff
    initial_delay_ms 1000
  }
}
```

### Client Fallback Chain

```baml
client_fallback Production {
  primary GPT4
  fallback [Claude, GPT35Turbo]
  options {
    timeout_ms 30000
  }
}
```

### Multiple Clients for Different Tasks

```baml
// Fast, cheap for simple tasks
client Fast {
  provider openai
  options {
    model "gpt-3.5-turbo"
    temperature 0
  }
}

// Powerful for complex reasoning
client Powerful {
  provider openai
  options {
    model "gpt-4-turbo"
    temperature 0.3
  }
}

// Creative for generation
client Creative {
  provider openai
  options {
    model "gpt-4-turbo"
    temperature 0.9
  }
}

// Use appropriate client per function
function QuickClassify(text: string) -> Category {
  client Fast
  prompt #"..."#
}

function DeepAnalysis(doc: Document) -> Analysis {
  client Powerful
  prompt #"..."#
}

function GenerateContent(prompt: ContentPrompt) -> Content {
  client Creative
  prompt #"..."#
}
```

## Prompt Patterns

### With Output Format

```baml
function ExtractData(text: string) -> ExtractedData {
  client GPT4
  prompt #"
    Extract structured data from:
    {{ text }}

    {{ ctx.output_format }}
  "#
}
```

### With System Context

```baml
function AssistUser(request: UserRequest) -> Response {
  client GPT4
  prompt #"
    You are a helpful assistant specializing in {{ request.domain }}.

    User request: {{ request.query }}

    Respond helpfully and accurately.

    {{ ctx.output_format }}
  "#
}
```

### With Few-Shot Examples

```baml
function TranslateFormat(input: InputFormat) -> OutputFormat {
  client GPT4
  prompt #"
    Convert the input to the specified output format.

    Example 1:
    Input: { "name": "John", "age": 30 }
    Output: Name=John, Age=30

    Example 2:
    Input: { "city": "NYC", "country": "USA" }
    Output: City=NYC, Country=USA

    Now convert:
    Input: {{ input }}

    {{ ctx.output_format }}
  "#
}
```

### With Chain of Thought

```baml
function SolveComplexProblem(problem: Problem) -> Solution {
  client GPT4
  prompt #"
    Solve the following problem step by step:

    {{ problem.description }}

    Think through this carefully:
    1. First, identify the key components
    2. Then, analyze relationships
    3. Finally, propose a solution

    {{ ctx.output_format }}
  "#
}

class Solution {
  reasoning string @description("Step-by-step thought process")
  answer string
  confidence float
}
```

## Description Best Practices

### Clear Constraints

```baml
class Rating {
  score float @description("Score from 1.0 to 5.0, where 5.0 is best")
  explanation string @description("2-3 sentences explaining the rating")
}
```

### Format Specifications

```baml
class DateRange {
  start_date string @description("ISO 8601 date: YYYY-MM-DD")
  end_date string @description("ISO 8601 date: YYYY-MM-DD, must be >= start_date")
}
```

### Enum Values

```baml
enum Urgency {
  LOW @description("Can wait days or weeks")
  MEDIUM @description("Should be addressed within 1-2 days")
  HIGH @description("Needs attention within hours")
  CRITICAL @description("Requires immediate action")
}
```

## Anti-Patterns to Avoid

### Don't: Overly Generic Types

```baml
// Bad - too generic
function Process(input: string) -> string

// Good - specific types
function AnalyzeSentiment(review: ReviewText) -> SentimentResult
```

### Don't: Missing Descriptions

```baml
// Bad - unclear
class Result {
  v float
  s string
}

// Good - clear
class SentimentResult {
  score float @description("Sentiment score from -1.0 (negative) to 1.0 (positive)")
  label string @description("One of: positive, negative, neutral")
}
```

### Don't: Deeply Nested Optional Chains

```baml
// Bad - hard to work with
class Response {
  data Data?
}
class Data {
  result Result?
}
class Result {
  value Value?
}

// Good - flatten or use union types
class Response {
  value Value | null
  error string?
}
```
