---
name: golang-performance
description: Go performance optimization techniques including profiling with pprof,
  memory optimization, concurrency patterns, and escape analysis.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Golang Performance

This skill provides guidance on optimizing Go application performance including profiling, memory management, concurrency optimization, and avoiding common performance pitfalls.

## When to Use This Skill

- When profiling Go applications for CPU or memory issues
- When optimizing memory allocations and reducing GC pressure
- When implementing efficient concurrency patterns
- When analyzing escape analysis results
- When optimizing hot paths in production code

## Profiling with pprof

### Enable Profiling in HTTP Server

```go
import (
    "net/http"
    _ "net/http/pprof"
)

func main() {
    // pprof endpoints available at /debug/pprof/
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()

    // Main application
}
```

### CPU Profiling

```bash
# Collect 30-second CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Interactive commands
(pprof) top10          # Top 10 functions by CPU
(pprof) list FuncName  # Show source with timing
(pprof) web            # Open flame graph in browser
```

### Memory Profiling

```bash
# Heap profile
go tool pprof http://localhost:6060/debug/pprof/heap

# Allocs profile (all allocations)
go tool pprof http://localhost:6060/debug/pprof/allocs

# Interactive commands
(pprof) top10 -cum     # Top by cumulative allocations
(pprof) list FuncName  # Show allocation sites
```

### Programmatic Profiling

```go
import (
    "os"
    "runtime/pprof"
)

func profileCPU() {
    f, _ := os.Create("cpu.prof")
    defer f.Close()

    pprof.StartCPUProfile(f)
    defer pprof.StopCPUProfile()

    // Code to profile
}

func profileMemory() {
    f, _ := os.Create("mem.prof")
    defer f.Close()

    runtime.GC() // Get accurate stats
    pprof.WriteHeapProfile(f)
}
```

## Memory Optimization

### Reduce Allocations

```go
// BAD: Allocates on every call
func Process(items []string) []string {
    result := []string{}
    for _, item := range items {
        result = append(result, transform(item))
    }
    return result
}

// GOOD: Pre-allocate with known capacity
func Process(items []string) []string {
    result := make([]string, 0, len(items))
    for _, item := range items {
        result = append(result, transform(item))
    }
    return result
}
```

### Use sync.Pool for Frequent Allocations

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func ProcessRequest(data []byte) []byte {
    buf := bufferPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufferPool.Put(buf)
    }()

    // Use buffer
    buf.Write(data)
    return buf.Bytes()
}
```

### Avoid String Concatenation in Loops

```go
// BAD: O(n^2) allocations
func BuildString(parts []string) string {
    result := ""
    for _, part := range parts {
        result += part
    }
    return result
}

// GOOD: Single allocation
func BuildString(parts []string) string {
    var builder strings.Builder
    for _, part := range parts {
        builder.WriteString(part)
    }
    return builder.String()
}
```

### Slice Memory Leaks

```go
// BAD: Keeps entire backing array alive
func GetFirst(data []byte) []byte {
    return data[:10]
}

// GOOD: Copy to release backing array
func GetFirst(data []byte) []byte {
    result := make([]byte, 10)
    copy(result, data[:10])
    return result
}
```

## Escape Analysis

```bash
# Show escape analysis decisions
go build -gcflags="-m" ./...

# More verbose
go build -gcflags="-m -m" ./...
```

### Avoiding Heap Escapes

```go
// ESCAPES: Returned pointer
func NewUser() *User {
    return &User{}  // Allocated on heap
}

// STAYS ON STACK: Value return
func NewUser() User {
    return User{}  // May stay on stack
}

// ESCAPES: Interface conversion
func Process(v interface{}) { ... }

func main() {
    x := 42
    Process(x)  // x escapes to heap
}
```

## Concurrency Optimization

### Worker Pool Pattern

```go
func ProcessItems(items []Item, workers int) []Result {
    jobs := make(chan Item, len(items))
    results := make(chan Result, len(items))

    // Start workers
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for item := range jobs {
                results <- process(item)
            }
        }()
    }

    // Send jobs
    for _, item := range items {
        jobs <- item
    }
    close(jobs)

    // Wait and collect
    go func() {
        wg.Wait()
        close(results)
    }()

    var output []Result
    for r := range results {
        output = append(output, r)
    }
    return output
}
```

### Buffered Channels for Throughput

```go
// SLOW: Unbuffered causes blocking
ch := make(chan int)

// FAST: Buffer reduces contention
ch := make(chan int, 100)
```

### Avoid Lock Contention

```go
// BAD: Global lock
var mu sync.Mutex
var cache = make(map[string]string)

func Get(key string) string {
    mu.Lock()
    defer mu.Unlock()
    return cache[key]
}

// GOOD: Sharded locks
type ShardedCache struct {
    shards [256]struct {
        mu    sync.RWMutex
        items map[string]string
    }
}

func (c *ShardedCache) getShard(key string) *struct {
    mu    sync.RWMutex
    items map[string]string
} {
    h := fnv.New32a()
    h.Write([]byte(key))
    return &c.shards[h.Sum32()%256]
}

func (c *ShardedCache) Get(key string) string {
    shard := c.getShard(key)
    shard.mu.RLock()
    defer shard.mu.RUnlock()
    return shard.items[key]
}
```

### Use sync.Map for Specific Cases

```go
// Good for: keys written once, read many; disjoint key sets
var cache sync.Map

func Get(key string) (string, bool) {
    v, ok := cache.Load(key)
    if !ok {
        return "", false
    }
    return v.(string), true
}

func Set(key, value string) {
    cache.Store(key, value)
}
```

## Data Structure Optimization

### Struct Field Ordering (Memory Alignment)

```go
// BAD: 24 bytes (padding)
type Bad struct {
    a bool   // 1 byte + 7 padding
    b int64  // 8 bytes
    c bool   // 1 byte + 7 padding
}

// GOOD: 16 bytes (no padding)
type Good struct {
    b int64  // 8 bytes
    a bool   // 1 byte
    c bool   // 1 byte + 6 padding
}
```

### Avoid Interface{} When Possible

```go
// SLOW: Type assertions, boxing
func Sum(values []interface{}) float64 {
    var sum float64
    for _, v := range values {
        sum += v.(float64)
    }
    return sum
}

// FAST: Concrete types
func Sum(values []float64) float64 {
    var sum float64
    for _, v := range values {
        sum += v
    }
    return sum
}
```

## Benchmarking Patterns

```go
func BenchmarkProcess(b *testing.B) {
    data := generateTestData()
    b.ResetTimer() // Exclude setup time

    for i := 0; i < b.N; i++ {
        Process(data)
    }
}

// Memory benchmarks
func BenchmarkAllocs(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        _ = make([]byte, 1024)
    }
}

// Compare implementations
func BenchmarkComparison(b *testing.B) {
    b.Run("old", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            OldImplementation()
        }
    })
    b.Run("new", func(b *testing.B) {
        for i := 0; i < b.N; i++ {
            NewImplementation()
        }
    })
}
```

Run with:

```bash
go test -bench=. -benchmem ./...
go test -bench=. -benchtime=5s ./...  # Longer runs
```

## Common Pitfalls

### Defer in Hot Loops

```go
// BAD: Defer overhead per iteration
for _, item := range items {
    mu.Lock()
    defer mu.Unlock()  // Defers stack up!
    process(item)
}

// GOOD: Explicit unlock
for _, item := range items {
    mu.Lock()
    process(item)
    mu.Unlock()
}

// BETTER: Extract to function
for _, item := range items {
    processWithLock(item)
}

func processWithLock(item Item) {
    mu.Lock()
    defer mu.Unlock()
    process(item)
}
```

### JSON Encoding Performance

```go
// SLOW: Reflection on every call
json.Marshal(v)

// FAST: Reuse encoder
var buf bytes.Buffer
encoder := json.NewEncoder(&buf)
encoder.Encode(v)

// FASTER: Code generation (easyjson, ffjson)
```

## Best Practices

1. **Measure before optimizing** - Profile to find actual bottlenecks
2. **Pre-allocate slices** - Use `make([]T, 0, capacity)` when size is known
3. **Pool frequently allocated objects** - Use `sync.Pool` for buffers
4. **Minimize allocations in hot paths** - Reuse objects, avoid interfaces
5. **Right-size channels** - Buffer to reduce blocking without wasting memory
6. **Avoid premature optimization** - Clarity first, optimize measured problems
7. **Use value receivers for small structs** - Avoid pointer indirection
8. **Order struct fields by size** - Largest to smallest reduces padding
