# .NET Reference Guide

Detailed rules for naming, patterns, and conventions.

## Table of Contents

- [Naming Conventions](#naming-conventions)
- [Type Design](#type-design)
- [Member Design](#member-design)
- [Exception Handling](#exception-handling)
- [Async/Await Patterns](#asyncawait-patterns)
- [LINQ Best Practices](#linq-best-practices)
- [Nullable Reference Types](#nullable-reference-types)

## Naming Conventions

### PascalCase Rules

Use for all public/protected members:

| Element | Rule | Example |
|---------|------|---------|
| Classes | Noun or noun phrase | `CustomerService`, `OrderProcessor` |
| Records | Noun, often with Dto/Request/Response suffix | `CustomerDto`, `CreateOrderRequest` |
| Interfaces | "I" + adjective/noun | `IDisposable`, `ICustomerRepository` |
| Methods | Verb or verb phrase | `GetCustomer`, `ValidateOrder`, `ProcessPayment` |
| Properties | Noun, adjective, or question | `Name`, `IsActive`, `HasChildren` |
| Events | Verb or verb phrase | `Clicked`, `PropertyChanged`, `OrderProcessed` |
| Enums | Singular noun (plural for flags) | `Color`, `Status`, `FilePermissions` |

### camelCase Rules

Use for parameters, locals, and private fields:

```csharp
// Parameters
public void ProcessOrder(int orderId, string customerName)

// Local variables
var itemCount = 0;
var isProcessed = false;

// Private fields (with underscore)
private readonly ILogger _logger;
private int _retryCount;
```

### Abbreviation Rules

- Avoid abbreviations except common ones: `Id`, `Xml`, `Html`, `Url`, `Uri`
- Two-letter abbreviations: ALL CAPS (`IO`, `UI`)
- Three+ letter abbreviations: PascalCase (`Html`, `Xml`)

```csharp
// Correct
public int CustomerId { get; set; }
public string HtmlContent { get; set; }
public IOStream GetStream();
public UIElement CreateElement();

// Avoid
public int CustomerID { get; set; }  // Use: CustomerId
public string HTMLContent { get; set; }  // Use: HtmlContent
```

### Boolean Naming

Prefix with question words:

```csharp
// Properties
public bool IsActive { get; set; }
public bool HasChildren { get; }
public bool CanExecute { get; }
public bool ShouldProcess { get; }

// Methods
public bool IsValid();
public bool Contains(string item);
public bool TryGetValue(string key, out object value);
```

### Async Method Naming

Suffix with `Async` when:
- Method returns `Task` or `Task<T>`
- Both sync and async versions exist

```csharp
// Async methods
public Task<Customer> GetCustomerAsync(int id);
public Task SaveChangesAsync(CancellationToken ct);

// Sync counterpart exists
public Customer GetCustomer(int id);
public Task<Customer> GetCustomerAsync(int id);
```

## Type Design

### Class Guidelines

```csharp
// Prefer sealed for non-inherited classes
public sealed class CustomerService { }

// Use abstract for base classes with shared logic
public abstract class RepositoryBase<T> { }

// Use static for utility classes
public static class StringExtensions { }
```

### Record Guidelines

Use records for:
- Immutable data transfer objects
- Value equality semantics
- Positional data with deconstruction

```csharp
// Positional record (immutable)
public record CustomerDto(int Id, string Name, string Email);

// Record with additional members
public record OrderSummary(int Id, decimal Total)
{
    public string FormattedTotal => Total.ToString("C");
}

// Mutable record (rare)
public record MutableData
{
    public string Name { get; set; } = "";
}
```

### Interface Guidelines

```csharp
// Repository pattern
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    Task UpdateAsync(T entity, CancellationToken ct = default);
    Task DeleteAsync(T entity, CancellationToken ct = default);
}

// Service interface
public interface IOrderService
{
    Task<OrderResult> ProcessOrderAsync(CreateOrderRequest request);
    Task<Order?> GetOrderAsync(int orderId);
}
```

### Enum Guidelines

```csharp
// Simple enum (singular name)
public enum OrderStatus
{
    Pending,
    Processing,
    Shipped,
    Delivered,
    Cancelled
}

// Flags enum (plural name)
[Flags]
public enum FilePermissions
{
    None = 0,
    Read = 1,
    Write = 2,
    Execute = 4,
    All = Read | Write | Execute
}
```

## Member Design

### Property Guidelines

```csharp
// Auto-properties
public string Name { get; set; }
public int Id { get; init; }  // Immutable after construction
public string FullName => $"{FirstName} {LastName}";  // Computed

// Required properties (C# 11+)
public required string Email { get; set; }
```

### Method Guidelines

```csharp
// Expression body for single-line
public override string ToString() => Name;

// CancellationToken as last parameter with default
public async Task ProcessAsync(int id, CancellationToken ct = default)

// Out parameters with Try pattern
public bool TryParse(string input, out int result)
```

### Constructor Guidelines

```csharp
// Primary constructor (C# 12+)
public class OrderService(ILogger<OrderService> logger, IOrderRepository repo)
{
    public async Task<Order> CreateAsync(CreateOrderRequest request)
    {
        logger.LogInformation("Creating order");
        // use repo...
    }
}

// Traditional constructor with validation
public class Customer
{
    public Customer(string name, string email)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Email = email ?? throw new ArgumentNullException(nameof(email));
    }

    public string Name { get; }
    public string Email { get; }
}
```

## Exception Handling

### Throwing Exceptions

```csharp
// Use specific exception types
throw new ArgumentNullException(nameof(customer));
throw new ArgumentOutOfRangeException(nameof(count), "Must be positive");
throw new InvalidOperationException("Order already processed");

// Custom exceptions for domain errors
public class OrderNotFoundException : Exception
{
    public OrderNotFoundException(int orderId)
        : base($"Order {orderId} not found")
    {
        OrderId = orderId;
    }

    public int OrderId { get; }
}
```

### Catching Exceptions

```csharp
// Catch specific exceptions
try
{
    await ProcessOrderAsync(order);
}
catch (OrderNotFoundException ex)
{
    logger.LogWarning("Order {Id} not found", ex.OrderId);
    return NotFound();
}
catch (ValidationException ex)
{
    logger.LogWarning("Validation failed: {Message}", ex.Message);
    return BadRequest(ex.Message);
}

// Avoid catching base Exception (unless re-throwing)
catch (Exception ex)
{
    logger.LogError(ex, "Unexpected error");
    throw;  // Re-throw to preserve stack trace
}
```

### Using Statements

```csharp
// Declaration pattern (preferred)
using var connection = new SqlConnection(connectionString);
using var reader = await command.ExecuteReaderAsync();

// Async disposal
await using var context = new AppDbContext();
```

## Async/Await Patterns

### Do's

```csharp
// Return Task directly when no await needed
public Task<Customer> GetCustomerAsync(int id)
    => _repository.FindByIdAsync(id);

// Use ConfigureAwait(false) in libraries
public async Task<Data> GetDataAsync()
{
    var result = await _client.GetAsync(url).ConfigureAwait(false);
    return await result.Content.ReadFromJsonAsync<Data>().ConfigureAwait(false);
}

// Accept CancellationToken
public async Task ProcessAsync(CancellationToken ct = default)
{
    await Task.Delay(1000, ct);
}
```

### Don'ts

```csharp
// DON'T use async void (except event handlers)
public async void ProcessData() { }  // BAD

// DON'T block on async
var result = GetDataAsync().Result;  // BAD
task.Wait();  // BAD
Task.WaitAll(tasks);  // BAD

// DON'T wrap sync code in Task.Run unnecessarily
public Task<int> GetCountAsync()
    => Task.Run(() => _items.Count);  // BAD if _items.Count is fast
```

### ValueTask Usage

```csharp
// Use ValueTask for frequently synchronous completions
public ValueTask<int> GetCachedCountAsync()
{
    if (_cache.TryGetValue("count", out int count))
        return ValueTask.FromResult(count);

    return new ValueTask<int>(LoadCountAsync());
}
```

## LINQ Best Practices

### Query Syntax vs Method Syntax

```csharp
// Method syntax (preferred for simple queries)
var activeCustomers = customers
    .Where(c => c.IsActive)
    .OrderBy(c => c.Name)
    .ToList();

// Query syntax (better for complex joins)
var orderDetails =
    from o in orders
    join c in customers on o.CustomerId equals c.Id
    where o.Total > 100
    select new { o.Id, c.Name, o.Total };
```

### Avoid Multiple Enumeration

```csharp
// BAD - enumerates twice
var items = GetItems();
if (items.Any())
    ProcessItems(items.ToList());

// GOOD - enumerate once
var items = GetItems().ToList();
if (items.Count > 0)
    ProcessItems(items);
```

### Deferred vs Immediate Execution

```csharp
// Deferred - query not executed yet
var query = customers.Where(c => c.IsActive);

// Immediate - forces execution
var list = customers.Where(c => c.IsActive).ToList();
var array = customers.Where(c => c.IsActive).ToArray();
var first = customers.FirstOrDefault(c => c.IsActive);
var count = customers.Count(c => c.IsActive);
```

## Nullable Reference Types

### Annotations

```csharp
// Non-nullable (must have value)
public string Name { get; set; }

// Nullable (can be null)
public string? MiddleName { get; set; }

// Null-forgiving operator (when you know better)
var length = possiblyNull!.Length;
```

### Null Checking Patterns

```csharp
// Null-conditional
var name = customer?.Name;
var length = customer?.Name?.Length ?? 0;

// Null-coalescing
var name = customer.Name ?? "Unknown";
var list = items ?? Array.Empty<string>();

// Null-coalescing assignment
_cache ??= new Dictionary<string, object>();

// Pattern matching
if (customer is { Name: var name, IsActive: true })
{
    Console.WriteLine(name);
}
```
