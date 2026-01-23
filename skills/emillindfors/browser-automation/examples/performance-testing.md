# Performance Testing Examples

Patterns for web performance monitoring and testing using the browser automation skill.

## Basic Performance Metrics

```
Task: Get page load performance metrics

Tools used:
- navigate: Load the page
- get_performance_metrics: Get timing data
```

### Example Workflow

```json
// Navigate to page
{"tool": "navigate", "args": {"url": "https://example.com"}}

// Wait for full load
{"tool": "wait_for_element", "args": {"selector": "body", "timeout_ms": 30000}}

// Get performance metrics
{"tool": "get_performance_metrics", "args": {}}
```

### Metrics Returned

```json
{
  "navigation_timing": {
    "dns_lookup": 23,
    "tcp_connect": 45,
    "request": 120,
    "response": 89,
    "dom_interactive": 456,
    "dom_complete": 1234,
    "load_event": 1289
  },
  "first_paint": 234,
  "first_contentful_paint": 456,
  "largest_contentful_paint": 890,
  "resource_count": 45,
  "total_resource_size": 2345678
}
```

## Memory Monitoring

```
Task: Detect memory leaks

Pattern:
1. Load page
2. Perform actions
3. Check memory usage
4. Repeat actions
5. Compare memory to detect leaks
```

### Example Workflow

```json
// Initial memory check
{"tool": "monitor_memory_usage", "args": {}}
// Returns: {"usedJSHeapSize": 10000000, "totalJSHeapSize": 15000000, "jsHeapSizeLimit": 2172649472}

// Perform memory-intensive action
{"tool": "execute_script", "args": {"script": "// Trigger action that might leak memory"}}

// Check memory again
{"tool": "monitor_memory_usage", "args": {}}

// Compare values to detect leaks
```

### Memory Leak Detection Script

```javascript
// Execute this script to monitor memory over time
async function checkForLeaks() {
  const samples = [];

  for (let i = 0; i < 5; i++) {
    // Force garbage collection if available
    if (window.gc) window.gc();

    samples.push(performance.memory.usedJSHeapSize);

    // Perform action that might leak
    document.querySelector('.load-more').click();
    await new Promise(r => setTimeout(r, 2000));
  }

  // Check if memory is continuously growing
  const isGrowing = samples.every((val, i) => i === 0 || val >= samples[i-1]);
  const growth = samples[samples.length-1] - samples[0];

  return {
    samples,
    isGrowing,
    totalGrowth: growth,
    possibleLeak: isGrowing && growth > 5000000
  };
}
return checkForLeaks();
```

## Console Error Monitoring

```
Task: Capture and analyze console errors

Pattern:
1. Load page
2. Get console logs filtered by level
3. Analyze for errors
```

### Example Workflow

```json
// Navigate to page
{"tool": "navigate", "args": {"url": "https://example.com"}}

// Get all console errors
{"tool": "get_console_logs", "args": {"level": "error"}}

// Get warnings too
{"tool": "get_console_logs", "args": {"level": "warning"}}
```

### Analyzing Results

```json
// Example console log output
{
  "logs": [
    {"level": "error", "message": "Uncaught TypeError: Cannot read property 'foo' of undefined", "source": "app.js", "line": 234},
    {"level": "error", "message": "Failed to load resource: 404", "source": "network", "url": "https://example.com/missing.js"},
    {"level": "warning", "message": "Deprecation warning: ...", "source": "react-dom.js"}
  ]
}
```

## Automated Performance Test

```
Task: Run comprehensive performance analysis

The run_performance_test tool automates multi-iteration testing:
```

### Example

```json
{
  "tool": "run_performance_test",
  "args": {
    "url": "https://example.com",
    "iterations": 5
  }
}
```

### Output

```json
{
  "url": "https://example.com",
  "iterations": 5,
  "results": {
    "avg_load_time": 1234,
    "min_load_time": 1100,
    "max_load_time": 1400,
    "avg_first_paint": 345,
    "avg_first_contentful_paint": 567,
    "std_deviation": 78
  },
  "recommendations": [
    "Consider lazy loading images",
    "Reduce JavaScript bundle size",
    "Enable gzip compression"
  ],
  "score": 72
}
```

## Resource Usage Monitoring

```
Task: Monitor ongoing resource usage during user interactions

Pattern:
1. Start monitoring
2. Perform user actions
3. Stop and analyze results
```

### Example

```json
// Monitor for 10 seconds while performing actions
{"tool": "monitor_resource_usage", "args": {"duration_ms": 10000}}
```

### Concurrent Monitoring

```json
// Navigate and trigger actions while monitoring
// Step 1: Start navigation
{"tool": "navigate", "args": {"url": "https://example.com/heavy-page"}}

// Step 2: Monitor during interaction
{
  "tool": "execute_script",
  "args": {
    "script": "// Trigger heavy operations like infinite scroll, video playback, etc."
  }
}

// Step 3: Get resource usage
{"tool": "monitor_resource_usage", "args": {"duration_ms": 5000}}
```

## Performance Testing Recipe

```json
{
  "name": "full-performance-audit",
  "description": "Complete performance audit of a web page",
  "version": "1.0.0",
  "parameters": {
    "url": {"type": "string", "required": true},
    "screenshot_path": {"type": "string", "default": "/tmp/perf-audit.png"}
  },
  "browsers": ["chrome"],
  "steps": [
    {
      "name": "navigate",
      "action": "navigate",
      "arguments": {"url": "${url}"}
    },
    {
      "name": "wait-for-load",
      "action": "wait_for_element",
      "arguments": {"selector": "body", "timeout_ms": 30000}
    },
    {
      "name": "performance-metrics",
      "action": "get_performance_metrics",
      "arguments": {}
    },
    {
      "name": "memory-usage",
      "action": "monitor_memory_usage",
      "arguments": {}
    },
    {
      "name": "console-errors",
      "action": "get_console_logs",
      "arguments": {"level": "error"}
    },
    {
      "name": "console-warnings",
      "action": "get_console_logs",
      "arguments": {"level": "warning"}
    },
    {
      "name": "capture-screenshot",
      "action": "screenshot",
      "arguments": {"path": "${screenshot_path}", "full_page": true}
    }
  ]
}
```

## Comparing Page Versions

```
Task: Compare performance between two versions of a page

Pattern:
1. Test version A
2. Test version B
3. Compare metrics
```

### Example Workflow

```json
// Test version A
{"tool": "run_performance_test", "args": {"url": "https://example.com/v1", "iterations": 3}}
// Save results as version_a

// Test version B
{"tool": "run_performance_test", "args": {"url": "https://example.com/v2", "iterations": 3}}
// Save results as version_b

// Use execute_script to compare
{
  "tool": "execute_script",
  "args": {
    "script": "return { loadTimeDiff: version_b.avg_load_time - version_a.avg_load_time, fcpDiff: version_b.avg_fcp - version_a.avg_fcp }"
  }
}
```

## Best Practices

1. **Multiple Iterations**: Always run multiple iterations to account for variance
2. **Consistent Environment**: Use same browser and network conditions
3. **Clear Cache**: Consider clearing cache between tests for cold-load metrics
4. **Monitor Memory**: Check for memory leaks especially in SPAs
5. **Check Console**: Always capture and analyze console errors
6. **Screenshot Evidence**: Take screenshots to document visual state
7. **Compare Baselines**: Track metrics over time to catch regressions
