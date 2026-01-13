---
name: reviewing-dotnet-code
description: |
  Reviews and generates .NET/C# code following Microsoft conventions and modern patterns.
  Use when reviewing C# files, writing .NET code, refactoring, or when user mentions
  "C#", ".NET", "dotnet", "csharp", or asks about naming conventions in .NET projects.
tools:
  - Read
  - Edit
  - Grep
  - Glob
---

# Reviewing .NET Code

Apply Microsoft's .NET coding conventions and modern C# patterns when reviewing or generating code.

## Quick Reference

### Naming Conventions

| Element | Style | Example |
|---------|-------|---------|
| Classes, Records | PascalCase | `CustomerService`, `OrderRecord` |
| Interfaces | IPascalCase | `IRepository`, `IDisposable` |
| Methods | PascalCase | `GetCustomer()`, `ValidateOrder()` |
| Properties | PascalCase | `FirstName`, `IsActive` |
| Public Fields | PascalCase | `MaxRetryCount` |
| Parameters | camelCase | `customerId`, `orderDate` |
| Local Variables | camelCase | `itemCount`, `isValid` |
| Private Fields | _camelCase | `_connectionString`, `_logger` |
| Constants | PascalCase | `DefaultTimeout`, `MaxItems` |
| Enums | PascalCase (singular) | `Color.Red`, `Status.Active` |
| Async Methods | PascalCaseAsync | `GetCustomerAsync()` |

### Type Keywords

Always use language keywords over framework types:

```csharp
// Correct
string name;
int count;
bool isActive;

// Avoid
String name;
Int32 count;
Boolean isActive;
```

### Modern C# Patterns (C# 10+)

```csharp
// File-scoped namespaces
namespace MyApp.Services;

// Target-typed new
List<Customer> customers = new();

// Collection expressions
string[] items = ["one", "two", "three"];

// Primary constructors
public class Service(ILogger logger, IRepository repo);

// Records for immutable data
public record CustomerDto(string Name, string Email);

// Raw string literals
var json = """
    { "name": "test" }
    """;
```

## Review Workflow

### Step 1: Check Naming

Scan for naming violations:
- Classes/methods not in PascalCase
- Private fields without underscore prefix
- Parameters/locals not in camelCase
- Async methods missing `Async` suffix

### Step 2: Check Patterns

Look for outdated patterns:
- `String` instead of `string`
- `new List<T>()` instead of `new()` or `[]`
- Block-scoped namespaces
- Manual null checks instead of `?.` or `??`

### Step 3: Check Async/Await

Flag async anti-patterns:
- `async void` (except event handlers)
- `.Result` or `.Wait()` blocking calls
- Missing `ConfigureAwait(false)` in libraries

### Step 4: Check Exception Handling

Verify exception patterns:
- Catching `Exception` instead of specific types
- Empty catch blocks
- Not using `using` for disposables

### Step 5: Check LINQ Usage

Identify LINQ opportunities:
- Manual loops that could be `Select`/`Where`/`Any`
- Multiple enumerations (should `.ToList()`)

## When to Read Reference Files

**Read REFERENCE.md when:**
- User asks for detailed naming rules
- Reviewing complex class hierarchies
- Need specific async/await guidance
- Reviewing exception handling patterns

**Read EXAMPLES.md when:**
- Need before/after refactoring samples
- Showing concrete improvements
- User asks "how should this look?"

## Anti-Patterns to Flag

### Critical (Always Flag)

```csharp
// async void (except event handlers)
public async void ProcessData() { }

// Blocking on async
var result = GetDataAsync().Result;
task.Wait();

// Empty catch
try { } catch { }

// Catching base Exception
catch (Exception ex) { }
```

### Important (Flag in Reviews)

```csharp
// Hungarian notation
int iCount;      // use: count
string strName;  // use: name

// Screaming caps
const int MAX_SIZE = 100;  // use: MaxSize

// System types
String name;  // use: string
```

## Code Generation Templates

### Service Class

```csharp
namespace MyApp.Services;

public class CustomerService(
    ILogger<CustomerService> logger,
    ICustomerRepository repository)
{
    public async Task<Customer?> GetByIdAsync(
        int id,
        CancellationToken cancellationToken = default)
    {
        logger.LogDebug("Getting customer {Id}", id);
        return await repository.FindByIdAsync(id, cancellationToken);
    }
}
```

### Record DTO

```csharp
namespace MyApp.Models;

public record CustomerDto(
    int Id,
    string Name,
    string Email,
    DateOnly CreatedDate);
```

### Interface

```csharp
namespace MyApp.Abstractions;

public interface ICustomerRepository
{
    Task<Customer?> FindByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Customer>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(Customer customer, CancellationToken ct = default);
}
```

## EditorConfig Integration

If project has `.editorconfig`, defer to those rules for style preferences. Check before suggesting style changes.

## Review Checklist

- [ ] Naming follows conventions
- [ ] Using language keywords (string, int, bool)
- [ ] Async methods have Async suffix
- [ ] No async void (except event handlers)
- [ ] No blocking calls (.Result, .Wait())
- [ ] Using statements for disposables
- [ ] Specific exception types caught
- [ ] LINQ used where appropriate
- [ ] Modern C# features applied
