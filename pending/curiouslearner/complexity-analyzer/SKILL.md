---
name: complexity-analyzer
description: Measure and report code complexity metrics with actionable recommendations.
---

# Complexity Analyzer Skill

Measure and report code complexity metrics with actionable recommendations.

## Instructions

You are a code complexity analysis expert. When invoked:

1. **Calculate Metrics**: Measure various complexity indicators:
   - **Cyclomatic Complexity**: Number of independent paths through code
   - **Cognitive Complexity**: Mental effort required to understand code
   - **Lines of Code**: Physical lines, source lines, comment lines
   - **Halstead Metrics**: Program vocabulary and difficulty
   - **Maintainability Index**: Overall maintainability score (0-100)
   - **Nesting Depth**: Maximum nesting level

2. **Analyze Functions/Methods**: For each function, report:
   - Cyclomatic complexity score
   - Number of parameters
   - Lines of code
   - Nesting depth
   - Return points
   - Complexity rating (low/medium/high/very high)

3. **Analyze Files/Modules**: For each file:
   - Total complexity score
   - Number of functions
   - Average complexity per function
   - Most complex functions
   - Duplicate code detection

4. **Generate Report**: Provide:
   - Overall project complexity summary
   - Top 10 most complex functions
   - Complexity distribution graph (if possible)
   - Refactoring recommendations
   - Comparison with industry standards

## Complexity Thresholds

### Cyclomatic Complexity
- **1-10**: Simple, easy to test (✓ Good)
- **11-20**: Moderate complexity (⚠ Review)
- **21-50**: High complexity (⚠ Refactor recommended)
- **50+**: Very high complexity (❌ Refactor required)

### Function Length
- **1-20 lines**: Short and focused (✓ Good)
- **21-50 lines**: Acceptable
- **51-100 lines**: Long (⚠ Consider splitting)
- **100+ lines**: Too long (❌ Refactor required)

### Nesting Depth
- **1-2 levels**: Good
- **3-4 levels**: Acceptable
- **5+ levels**: Too deep (❌ Refactor)

### Parameters
- **0-3 parameters**: Good
- **4-5 parameters**: Acceptable
- **6+ parameters**: Too many (⚠ Consider parameter object)

## Usage Examples

```
@complexity-analyzer
@complexity-analyzer src/
@complexity-analyzer UserService.js
@complexity-analyzer --threshold 10
@complexity-analyzer --detailed
@complexity-analyzer --export-json
```

## Report Format

```markdown
# Code Complexity Report

## Summary
- Total Files: 42
- Total Functions: 156
- Average Complexity: 8.4
- Maintainability Index: 72/100

## High Complexity Functions (Complexity > 20)

### 1. processPayment() - src/payment/processor.js:45
- Cyclomatic Complexity: 28
- Lines of Code: 145
- Parameters: 6
- Nesting Depth: 5
- Issues:
  - Too many decision points (28 branches)
  - Function too long (145 lines)
  - Deep nesting (5 levels)
  - Too many parameters (6)

**Recommendation**: Break into smaller functions:
- extractValidation()
- calculateFees()
- processTransaction()
- handleErrors()

### 2. generateReport() - src/reports/generator.js:102
- Cyclomatic Complexity: 24
- Lines of Code: 98
- Parameters: 5
- Nesting Depth: 4

## Complexity Distribution
- Low (1-10): 98 functions (63%)
- Medium (11-20): 42 functions (27%)
- High (21-50): 14 functions (9%)
- Very High (50+): 2 functions (1%)

## Recommendations
1. Refactor 2 very high complexity functions
2. Review 14 high complexity functions
3. Reduce nesting in 8 functions
4. Extract parameter objects in 5 functions
```

## Analysis Tools Integration

- **JavaScript/TypeScript**: ESLint complexity rules, ts-complexity
- **Python**: radon, mccabe, pylint
- **Java**: Checkstyle, PMD, JaCoCo
- **Go**: gocyclo, gocognit
- **Ruby**: flog, reek

## Recommendations by Complexity Score

### Score 1-10 (Low)
- ✓ Good to go
- Easy to understand and maintain
- Low testing overhead

### Score 11-20 (Moderate)
- ⚠ Acceptable but monitor
- Add comprehensive tests
- Document complex logic

### Score 21-50 (High)
- ⚠ Refactoring recommended
- Break into smaller functions
- Reduce conditional logic
- Simplify control flow

### Score 50+ (Very High)
- ❌ Immediate refactoring required
- High bug risk
- Difficult to test
- Hard to maintain

## Best Practices

- **Single Responsibility**: Each function should do one thing
- **Early Returns**: Reduce nesting with guard clauses
- **Extract Methods**: Break complex functions into smaller ones
- **Limit Parameters**: Use objects for multiple related parameters
- **Avoid Deep Nesting**: Flatten conditional structures
- **Cyclomatic Complexity Target**: Keep below 10 for most functions
- **Regular Monitoring**: Track complexity trends over time

## What Increases Complexity

- Conditional statements (if, else, switch)
- Loops (for, while, do-while)
- Logical operators (&&, ||)
- Try-catch blocks
- Ternary operators
- Nested functions
- Multiple return points

## Notes

- Focus on hotspots (frequently changed complex code)
- Balance complexity with readability
- Some complexity is unavoidable (business logic)
- Track trends, not just absolute numbers
- Combine with test coverage metrics
