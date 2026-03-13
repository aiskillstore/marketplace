---
name: log-analysis
description: Analyze application logs to identify errors, performance issues, and security anomalies. Use when debugging issues, monitoring system health, or investigating incidents. Handles various log formats including Apache, Nginx, application logs, and JSON logs.
allowed-tools: Read Grep Glob
metadata:
  tags: logs, analysis, debugging, monitoring, grep, patterns
  platforms: Claude, ChatGPT, Gemini
---


# Log Analysis


## When to use this skill

- **Error debugging**: analyze the root cause of application errors
- **Performance analysis**: analyze response times and throughput
- **Security audit**: detect anomalous access patterns
- **Incident response**: investigate the root cause during an outage

## Instructions

### Step 1: Locate Log Files

```bash
# Common log locations
/var/log/                    # System logs
/var/log/nginx/              # Nginx logs
/var/log/apache2/            # Apache logs
./logs/                      # Application logs
```

### Step 2: Search for Error Patterns

**Common error search**:
```bash
# Search ERROR-level logs
grep -i "error\|exception\|fail" application.log

# Recent errors (last 100 lines)
tail -100 application.log | grep -i error

# Errors with timestamps
grep -E "^\[.*ERROR" application.log
```

**HTTP error codes**:
```bash
# 5xx server errors
grep -E "HTTP/[0-9.]+ 5[0-9]{2}" access.log

# 4xx client errors
grep -E "HTTP/[0-9.]+ 4[0-9]{2}" access.log

# Specific error code
grep "HTTP/1.1\" 500" access.log
```

### Step 3: Pattern Analysis

**Time-based analysis**:
```bash
# Error count by time window
grep -i error application.log | cut -d' ' -f1,2 | sort | uniq -c | sort -rn

# Logs for a specific time window
grep "2025-01-05 14:" application.log
```

**IP-based analysis**:
```bash
# Request count by IP
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20

# Activity for a specific IP
grep "192.168.1.100" access.log
```

### Step 4: Performance Analysis

**Response time analysis**:
```bash
# Extract response times from Nginx logs
awk '{print $NF}' access.log | sort -n | tail -20

# Slow requests (>= 1 second)
awk '$NF > 1.0 {print $0}' access.log
```

**Traffic volume analysis**:
```bash
# Requests per minute
awk '{print $4}' access.log | cut -d: -f1,2,3 | uniq -c

# Requests per endpoint
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -20
```

### Step 5: Security Analysis

**Suspicious patterns**:
```bash
# SQL injection attempts
grep -iE "(union|select|insert|update|delete|drop).*--" access.log

# XSS attempts
grep -iE "<script|javascript:|onerror=" access.log

# Directory traversal
grep -E "\.\./" access.log

# Brute force attack
grep -E "POST.*/login" access.log | awk '{print $1}' | sort | uniq -c | sort -rn
```

## Output format

### Analysis report structure

```markdown
# Log analysis report

## Summary
- Analysis window: YYYY-MM-DD HH:MM ~ YYYY-MM-DD HH:MM
- Total log lines: X,XXX
- Error count: XXX
- Warning count: XXX

## Error analysis
| Error type | Occurrences | Last seen |
|----------|-----------|----------|
| Error A  | 150       | 2025-01-05 14:30 |
| Error B  | 45        | 2025-01-05 14:25 |

## Recommended actions
1. [Action 1]
2. [Action 2]
```

## Best practices

1. **Set time range**: clearly define the time window to analyze
2. **Save patterns**: script common grep patterns
3. **Check context**: review logs around the error too (`-A`, `-B` options)
4. **Log rotation**: search compressed logs with zgrep as well

## Constraints

### Required Rules (MUST)
1. Perform read-only operations only
2. Mask sensitive information (passwords, tokens)

### Prohibited (MUST NOT)
1. Do not modify log files
2. Do not expose sensitive information externally

## References

- [grep manual](https://www.gnu.org/software/grep/manual/)
- [awk guide](https://www.gnu.org/software/gawk/manual/)
- [Log analysis best practices](https://www.loggly.com/ultimate-guide/)

## Examples

### Example 1: Basic usage
<!-- Add example content here -->

### Example 2: Advanced usage
<!-- Add advanced example content here -->
