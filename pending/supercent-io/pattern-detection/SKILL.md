---
name: pattern-detection
description: Detect patterns, anomalies, and trends in code and data. Use when identifying code smells, finding security vulnerabilities, or discovering recurring patterns. Handles regex patterns, AST analysis, and statistical anomaly detection.
allowed-tools: Read Grep Glob
metadata:
  tags: patterns, anomalies, regex, code-analysis, security, trends
  platforms: Claude, ChatGPT, Gemini
---


# Pattern Detection


## When to use this skill

- **Code review**: Proactively detect problematic patterns
- **Security review**: Scan for vulnerability patterns
- **Refactoring**: Identify duplicate code
- **Monitoring**: Alert on anomalies

## Instructions

### Step 1: Detect code smell patterns

**Detect long functions**:
```bash
# Find functions with 50+ lines
grep -n "function\|def\|func " **/*.{js,ts,py,go} | \
  while read line; do
    file=$(echo $line | cut -d: -f1)
    linenum=$(echo $line | cut -d: -f2)
    # Function length calculation logic
  done
```

**Duplicate code patterns**:
```bash
# Search for similar code blocks
grep -rn "if.*==.*null" --include="*.ts" .
grep -rn "try\s*{" --include="*.java" . | wc -l
```

**Magic numbers**:
```bash
# Search for hard-coded numbers
grep -rn "[^a-zA-Z][0-9]{2,}[^a-zA-Z]" --include="*.{js,ts}" .
```

### Step 2: Security vulnerability patterns

**SQL Injection risks**:
```bash
# SQL query built via string concatenation
grep -rn "query.*+.*\$\|execute.*%s\|query.*f\"" --include="*.py" .
grep -rn "SELECT.*\+.*\|\|" --include="*.{js,ts}" .
```

**Hard-coded secrets**:
```bash
# Password, API key patterns
grep -riE "(password|secret|api_key|apikey)\s*=\s*['\"][^'\"]+['\"]" --include="*.{js,ts,py,java}" .

# AWS key patterns
grep -rE "AKIA[0-9A-Z]{16}" .
```

**Dangerous function usage**:
```bash
# eval, exec usage
grep -rn "eval\(.*\)\|exec\(.*\)" --include="*.{py,js}" .

# innerHTML usage
grep -rn "innerHTML\s*=" --include="*.{js,ts}" .
```

### Step 3: Code structure patterns

**Import analysis**:
```bash
# Candidates for unused imports
grep -rn "^import\|^from.*import" --include="*.py" . | \
  awk -F: '{print $3}' | sort | uniq -c | sort -rn
```

**TODO/FIXME patterns**:
```bash
# Find unfinished code
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.{js,ts,py}" .
```

**Error handling patterns**:
```bash
# Empty catch blocks
grep -rn "catch.*{[\s]*}" --include="*.{js,ts,java}" .

# Ignored errors
grep -rn "except:\s*pass" --include="*.py" .
```

### Step 4: Data anomaly patterns

**Regex patterns**:
```python
import re

patterns = {
    'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    'phone': r'\d{3}[-.\s]?\d{4}[-.\s]?\d{4}',
    'ip_address': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
    'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
    'ssn': r'\d{3}-\d{2}-\d{4}',
}

def detect_sensitive_data(text):
    found = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            found[name] = len(matches)
    return found
```

**Statistical anomaly detection**:
```python
import numpy as np
from scipy import stats

def detect_anomalies_zscore(data, threshold=3):
    """Z-score-based outlier detection"""
    z_scores = np.abs(stats.zscore(data))
    return np.where(z_scores > threshold)[0]

def detect_anomalies_iqr(data, k=1.5):
    """IQR-based outlier detection"""
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return np.where((data < lower) | (data > upper))[0]
```

### Step 5: Trend analysis

```python
import pandas as pd

def analyze_trend(df, date_col, value_col):
    """Time-series trend analysis"""
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)

    # Moving averages
    df['ma_7'] = df[value_col].rolling(window=7).mean()
    df['ma_30'] = df[value_col].rolling(window=30).mean()

    # Growth rate
    df['growth'] = df[value_col].pct_change() * 100

    # Trend direction
    recent_trend = df['ma_7'].iloc[-1] > df['ma_30'].iloc[-1]

    return {
        'trend_direction': 'up' if recent_trend else 'down',
        'avg_growth': df['growth'].mean(),
        'volatility': df[value_col].std()
    }
```

## Output format

### Pattern detection report

```markdown
# Pattern Detection Report

## Summary
- Files scanned: XXX
- Patterns detected: XX
- High severity: X
- Medium severity: X
- Low severity: X

## Detected patterns

### Security vulnerabilities (HIGH)
| File | Line | Pattern | Description |
|------|------|------|------|
| file.js | 42 | hardcoded-secret | Hard-coded API key |

### Code smells (MEDIUM)
| File | Line | Pattern | Description |
|------|------|------|------|
| util.py | 100 | long-function | Function length: 150 lines |

## Recommended actions
1. [Action 1]
2. [Action 2]
```

## Best practices

1. **Incremental analysis**: Start with simple patterns
2. **Minimize false positives**: Use precise regex
3. **Check context**: Understand the context around a match
4. **Prioritize**: Sort by severity

## Constraints

### Required rules (MUST)
1. Read-only operation
2. Perform result verification
3. State the possibility of false positives

### Prohibited (MUST NOT)
1. Do not auto-modify code
2. Do not log sensitive information

## References

- [Regex101](https://regex101.com/)
- [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [Code Smell Catalog](https://refactoring.guru/refactoring/smells)

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
