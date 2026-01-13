# Convert PRD Workflow

Step-by-step process for transforming a PRD into an app_spec.txt.

## Prerequisites

- PRD file path (will prompt if not provided)
- Output directory (defaults to `prompts/`)

## Step 1: Locate and Read PRD

```
1. If PRD path not provided, ask: "What is the path to your PRD file?"
2. Read the entire PRD file
3. Identify document structure (headers, code blocks, tables)
```

**Validate PRD contains**:
- Project name/title
- Tech stack information
- Some form of feature/requirement description
- Implementation details or code examples

## Step 2: Extract Project Metadata

### Project Name
- Extract from first H1 heading
- Or from "Project:" field if present
- Clean to remove version numbers for the name

### Overview
Synthesize a 3-5 sentence summary from:
- Any "Overview" section
- "Key Principles" or "Goals" sections
- Opening paragraphs describing purpose

**Template**:
```
Build a [type of system] that [primary purpose].
[Key architectural decision].
[Primary interface/usage pattern].
[Core value proposition].
```

## Step 3: Extract Technology Stack

### Parse Tech Stack Table
Look for tables with columns like:
| Component | Choice | Why |

Transform to:
```xml
<technology_stack>
  <language>Python 3.11+</language>
  <package_manager>uv</package_manager>
  <core_dependencies>
    <dependency name="ccxt">Exchange data fetching</dependency>
    <dependency name="pandas">Data processing</dependency>
    ...
  </core_dependencies>
</technology_stack>
```

### Include from Directory Structure
Reference directory layout for context on where code lives.

## Step 4: Transform Data Models

### From Pydantic → Schema Format

**Input pattern**:
```python
class ModelName(BaseModel):
    field: type = Field(constraint)
    ...
```

**Output pattern**:
```xml
<table_name>
  - field: type (constraint description)
  - field2: type
  ...
</table_name>
```

### Transformation Rules

| Pydantic | App Spec |
|----------|----------|
| `Field(gt=0)` | `(positive)` |
| `Field(ge=0)` | `(non-negative)` |
| `Field(default=x)` | `(default: x)` |
| `Optional[T]` | `nullable` |
| `list[T]` | `array of T` |
| `datetime` | `datetime` |
| `@field_validator` | Add constraint note |

### Example Transformation

**PRD**:
```python
class Candle(BaseModel):
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
```

**App Spec**:
```xml
<candles>
  - timestamp: datetime
  - open: float (positive)
  - high: float (positive, must >= low)
  - low: float (positive)
  - close: float (positive)
  - volume: float (non-negative)
</candles>
```

## Step 5: Extract Core Features

### From Implementation Code → Feature Descriptions

**Strategy**: Read function/class docstrings and summarize behavior.

**Input pattern**:
```python
def fetch_candles(config: FetchConfig) -> pd.DataFrame:
    """Fetch candles from exchange.

    If config.since is provided, fetches historical data...
    """
```

**Output pattern**:
```xml
<data_fetching>
  - Fetch OHLCV candles from configurable exchange
  - Support historical data via date parameter
  - Validate trading pair exists on exchange
  - Handle network errors with descriptive exceptions
</data_fetching>
```

### Group Features by Domain

Look for natural groupings:
- Data ingestion/fetching
- Processing/analysis
- Output/visualization
- CLI/API interface
- Configuration/settings

## Step 6: Extract API/CLI Endpoints

### From CLI Code → Command Summary

**Input pattern**:
```python
@app.command()
def run(
    symbol: str = typer.Argument("BTC/USDT"),
    timeframe: str = typer.Option("4h", "-t"),
    since: str = typer.Option(None, "--since"),
):
    """Run full pipeline: fetch → analyze → chart."""
```

**Output pattern**:
```xml
<cli_commands>
  - run [SYMBOL] -t TIMEFRAME --since DATE
    Run full pipeline: fetch, analyze, and generate chart
  - analyze-cmd [SYMBOL] --json
    Fetch and analyze only, optional JSON output
</cli_commands>
```

### Include Library API
If library-first design, document importable functions:
```xml
<library_api>
  - fetch_candles(config) -> DataFrame
  - analyze(df, symbol, timeframe) -> Analysis
  - generate_chart(df, analysis) -> Path
</library_api>
```

## Step 7: Transform Implementation Plan

### From Epics/Tasks → Numbered Steps

**Input pattern**:
```markdown
| E1 | Project Setup | 5 tasks | `uv sync` |
| E2 | Exception Hierarchy | 2 tasks | ... |
```

**Output pattern**:
```xml
<implementation_steps>
  <step number="1">
    <title>Project Setup and Foundation</title>
    <tasks>
      - Initialize project with package manager
      - Set up dependency file (pyproject.toml)
      - Create directory structure
      - Configure testing framework
      - Verify setup with test collection
    </tasks>
  </step>
  ...
</implementation_steps>
```

### Consolidation Rules
- Merge small epics (2-3 tasks) into logical groups
- Aim for 6-10 implementation steps
- Each step should be a meaningful milestone

## Step 8: Derive Success Criteria

### Sources for Criteria

1. **Test assertions**:
   ```python
   assert len(df) == 50
   assert df["high"].ge(df["low"]).all()
   ```
   → "Data structure validation (OHLC relationships maintained)"

2. **CLI usage examples**:
   ```bash
   # Output: BULLISH | PREMIUM | $98,400.00
   ```
   → "Produces readable output with bias, zone, and price"

3. **Key Principles from PRD**:
   ```
   - Library First
   - Type Safety
   - Testable
   ```
   → Corresponding quality criteria

### Structure Output

```xml
<success_criteria>
  <functionality>
    - Data fetching from exchange works reliably
    - Analysis produces consistent, valid results
    - Chart generation creates readable visualizations
  </functionality>
  <technical_quality>
    - Type-safe data structures throughout
    - Comprehensive error handling
    - Test coverage for core modules
  </technical_quality>
</success_criteria>
```

## Step 9: Assemble and Validate

### Assemble Full Document

```xml
<project_specification>
  <project_name>...</project_name>
  <overview>...</overview>
  <technology_stack>...</technology_stack>
  <prerequisites>...</prerequisites>
  <core_features>...</core_features>
  <database_schema>...</database_schema>
  <api_endpoints_summary>...</api_endpoints_summary>
  <implementation_steps>...</implementation_steps>
  <success_criteria>...</success_criteria>
</project_specification>
```

### Validation Checklist

- [ ] XML is well-formed (matching tags)
- [ ] No code snippets remain (converted to descriptions)
- [ ] All PRD sections have corresponding output
- [ ] Implementation steps are actionable
- [ ] Success criteria are measurable

## Step 10: Write Output

1. Write to `prompts/app_spec.txt` (or user-specified path)
2. Report transformation summary:
   ```
   Created app_spec.txt:
   - Project: [name]
   - Features: [N] groups
   - Models: [N] tables
   - Steps: [N] implementation phases
   - Criteria: [N] success metrics
   ```

## Troubleshooting

### PRD Missing Sections

If PRD lacks certain sections:
- **No tech stack table**: Extract from imports and comments
- **No explicit features**: Derive from function names and docstrings
- **No implementation plan**: Create from directory structure order

### Ambiguous Transformations

When unsure how to transform:
1. Prefer declarative over procedural
2. Focus on WHAT not HOW
3. Keep constraints but remove implementation details
4. Ask user for clarification on critical decisions

## Example Execution

```
User: Convert PRD.md to an app spec

Agent:
1. Reading PRD.md... (1522 lines)
2. Extracted: "SMC Chart Analysis Pipeline" v5.0
3. Found tech stack: Python 3.11+, uv, 9 dependencies
4. Converted 6 Pydantic models:
   - Candle, CandleData, Analysis, FetchConfig...
5. Extracted 4 feature groups:
   - data_fetching, analysis, charting, cli
6. Transformed 11 epics → 8 implementation steps
7. Derived 9 success criteria from tests

Writing to prompts/app_spec.txt...
Done!
```
