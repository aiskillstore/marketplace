# .NET Code Examples

Before/after samples demonstrating best practices.

## Table of Contents

- [Naming Fixes](#naming-fixes)
- [Modern C# Upgrades](#modern-c-upgrades)
- [Async/Await Fixes](#asyncawait-fixes)
- [Exception Handling](#exception-handling)
- [LINQ Improvements](#linq-improvements)
- [Class Design](#class-design)

## Naming Fixes

### Hungarian Notation

```csharp
// Before
public class CustomerManager
{
    private string strCustomerName;
    private int iOrderCount;
    private bool bIsActive;

    public void SetName(string strName)
    {
        strCustomerName = strName;
    }
}

// After
public class CustomerManager
{
    private string _customerName;
    private int _orderCount;
    private bool _isActive;

    public void SetName(string name)
    {
        _customerName = name;
    }
}
```

### Screaming Caps Constants

```csharp
// Before
public class Configuration
{
    public const int MAX_RETRY_COUNT = 3;
    public const string DEFAULT_CONNECTION_STRING = "...";
    public const double TAX_RATE = 0.08;
}

// After
public class Configuration
{
    public const int MaxRetryCount = 3;
    public const string DefaultConnectionString = "...";
    public const double TaxRate = 0.08;
}
```

### System Types

```csharp
// Before
public class DataProcessor
{
    public String ProcessData(String input)
    {
        Int32 length = input.Length;
        Boolean isValid = length > 0;
        return isValid ? input : String.Empty;
    }
}

// After
public class DataProcessor
{
    public string ProcessData(string input)
    {
        int length = input.Length;
        bool isValid = length > 0;
        return isValid ? input : string.Empty;
    }
}
```

## Modern C# Upgrades

### Target-Typed New

```csharp
// Before
private readonly Dictionary<string, List<Customer>> _cache =
    new Dictionary<string, List<Customer>>();

public Order CreateOrder()
{
    var items = new List<OrderItem>();
    return new Order(items);
}

// After
private readonly Dictionary<string, List<Customer>> _cache = new();

public Order CreateOrder()
{
    List<OrderItem> items = new();
    return new Order(items);
}
```

### Collection Expressions

```csharp
// Before
private readonly string[] _validStatuses = new string[] { "active", "pending" };
private readonly List<int> _defaultIds = new List<int> { 1, 2, 3 };

// After
private readonly string[] _validStatuses = ["active", "pending"];
private readonly List<int> _defaultIds = [1, 2, 3];
```

### File-Scoped Namespaces

```csharp
// Before
namespace MyApp.Services
{
    public class CustomerService
    {
        public Customer GetCustomer(int id)
        {
            // Implementation
        }
    }
}

// After
namespace MyApp.Services;

public class CustomerService
{
    public Customer GetCustomer(int id)
    {
        // Implementation
    }
}
```

### Primary Constructors

```csharp
// Before
public class OrderService
{
    private readonly ILogger<OrderService> _logger;
    private readonly IOrderRepository _repository;
    private readonly IEmailService _emailService;

    public OrderService(
        ILogger<OrderService> logger,
        IOrderRepository repository,
        IEmailService emailService)
    {
        _logger = logger;
        _repository = repository;
        _emailService = emailService;
    }

    public async Task ProcessAsync(int orderId)
    {
        _logger.LogInformation("Processing {OrderId}", orderId);
        var order = await _repository.GetByIdAsync(orderId);
        await _emailService.SendConfirmationAsync(order);
    }
}

// After
public class OrderService(
    ILogger<OrderService> logger,
    IOrderRepository repository,
    IEmailService emailService)
{
    public async Task ProcessAsync(int orderId)
    {
        logger.LogInformation("Processing {OrderId}", orderId);
        var order = await repository.GetByIdAsync(orderId);
        await emailService.SendConfirmationAsync(order);
    }
}
```

### Records for DTOs

```csharp
// Before
public class CustomerDto
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string Email { get; set; }

    public override bool Equals(object obj)
    {
        if (obj is not CustomerDto other) return false;
        return Id == other.Id && Name == other.Name && Email == other.Email;
    }

    public override int GetHashCode() => HashCode.Combine(Id, Name, Email);
}

// After
public record CustomerDto(int Id, string Name, string Email);
```

## Async/Await Fixes

### Async Void

```csharp
// Before (dangerous)
public async void ProcessOrder(Order order)
{
    await _repository.SaveAsync(order);
    await _emailService.SendConfirmationAsync(order);
}

// After
public async Task ProcessOrderAsync(Order order)
{
    await _repository.SaveAsync(order);
    await _emailService.SendConfirmationAsync(order);
}
```

### Blocking Calls

```csharp
// Before (can deadlock)
public Customer GetCustomer(int id)
{
    return GetCustomerAsync(id).Result;
}

public void ProcessAll()
{
    var tasks = items.Select(ProcessItemAsync);
    Task.WaitAll(tasks.ToArray());
}

// After
public async Task<Customer> GetCustomerAsync(int id)
{
    return await _repository.FindByIdAsync(id);
}

public async Task ProcessAllAsync()
{
    var tasks = items.Select(ProcessItemAsync);
    await Task.WhenAll(tasks);
}
```

### Missing CancellationToken

```csharp
// Before
public async Task<List<Order>> GetOrdersAsync()
{
    var response = await _httpClient.GetAsync("/api/orders");
    return await response.Content.ReadFromJsonAsync<List<Order>>();
}

// After
public async Task<List<Order>> GetOrdersAsync(CancellationToken ct = default)
{
    var response = await _httpClient.GetAsync("/api/orders", ct);
    return await response.Content.ReadFromJsonAsync<List<Order>>(ct) ?? [];
}
```

### Unnecessary Task.Run

```csharp
// Before
public Task<int> GetCountAsync()
{
    return Task.Run(() => _items.Count);
}

// After (if sync is acceptable)
public int GetCount() => _items.Count;

// Or (if async interface required)
public Task<int> GetCountAsync() => Task.FromResult(_items.Count);
```

## Exception Handling

### Empty Catch

```csharp
// Before
public void ProcessFile(string path)
{
    try
    {
        var content = File.ReadAllText(path);
        Process(content);
    }
    catch
    {
        // Swallowed
    }
}

// After
public void ProcessFile(string path)
{
    try
    {
        var content = File.ReadAllText(path);
        Process(content);
    }
    catch (FileNotFoundException ex)
    {
        _logger.LogWarning("File not found: {Path}", path);
    }
    catch (IOException ex)
    {
        _logger.LogError(ex, "Error reading file: {Path}", path);
        throw;
    }
}
```

### Using Statements

```csharp
// Before
public string ReadFile(string path)
{
    var stream = new FileStream(path, FileMode.Open);
    var reader = new StreamReader(stream);
    var content = reader.ReadToEnd();
    reader.Dispose();
    stream.Dispose();
    return content;
}

// After
public string ReadFile(string path)
{
    using var stream = new FileStream(path, FileMode.Open);
    using var reader = new StreamReader(stream);
    return reader.ReadToEnd();
}

// Async version
public async Task<string> ReadFileAsync(string path)
{
    await using var stream = new FileStream(path, FileMode.Open);
    using var reader = new StreamReader(stream);
    return await reader.ReadToEndAsync();
}
```

### Catching Base Exception

```csharp
// Before
public async Task<Order> GetOrderAsync(int id)
{
    try
    {
        return await _repository.FindByIdAsync(id);
    }
    catch (Exception ex)
    {
        _logger.LogError("Error getting order");
        return null;
    }
}

// After
public async Task<Order?> GetOrderAsync(int id)
{
    try
    {
        return await _repository.FindByIdAsync(id);
    }
    catch (EntityNotFoundException)
    {
        _logger.LogWarning("Order {Id} not found", id);
        return null;
    }
    catch (DbException ex)
    {
        _logger.LogError(ex, "Database error getting order {Id}", id);
        throw;
    }
}
```

## LINQ Improvements

### Manual Loops

```csharp
// Before
public List<string> GetActiveCustomerNames(List<Customer> customers)
{
    var result = new List<string>();
    foreach (var customer in customers)
    {
        if (customer.IsActive)
        {
            result.Add(customer.Name);
        }
    }
    return result;
}

// After
public List<string> GetActiveCustomerNames(List<Customer> customers)
{
    return customers
        .Where(c => c.IsActive)
        .Select(c => c.Name)
        .ToList();
}
```

### Multiple Enumeration

```csharp
// Before (enumerates twice)
public void ProcessCustomers(IEnumerable<Customer> customers)
{
    if (customers.Any())
    {
        Console.WriteLine($"Processing {customers.Count()} customers");
        foreach (var c in customers)
            Process(c);
    }
}

// After
public void ProcessCustomers(IEnumerable<Customer> customers)
{
    var customerList = customers.ToList();
    if (customerList.Count > 0)
    {
        Console.WriteLine($"Processing {customerList.Count} customers");
        foreach (var c in customerList)
            Process(c);
    }
}
```

### Complex Null Checking

```csharp
// Before
public string GetCustomerCity(Order order)
{
    if (order != null)
    {
        if (order.Customer != null)
        {
            if (order.Customer.Address != null)
            {
                return order.Customer.Address.City;
            }
        }
    }
    return "Unknown";
}

// After
public string GetCustomerCity(Order order)
{
    return order?.Customer?.Address?.City ?? "Unknown";
}
```

## Class Design

### Full Service Refactor

```csharp
// Before
namespace MyApp.Services
{
    public class CustomerService
    {
        private ICustomerRepository _repo;
        private ILogger _logger;

        public CustomerService(ICustomerRepository repo, ILogger logger)
        {
            _repo = repo;
            _logger = logger;
        }

        public async void SaveCustomer(CustomerDTO dto)
        {
            try
            {
                Customer customer = new Customer();
                customer.Name = dto.Name;
                customer.Email = dto.Email;
                await _repo.SaveAsync(customer);
            }
            catch (Exception ex)
            {
                // Log and swallow
            }
        }

        public Customer GetCustomer(Int32 id)
        {
            return _repo.GetByIdAsync(id).Result;
        }
    }
}

// After
namespace MyApp.Services;

public sealed class CustomerService(
    ICustomerRepository repository,
    ILogger<CustomerService> logger)
{
    public async Task SaveCustomerAsync(
        CustomerDto dto,
        CancellationToken ct = default)
    {
        var customer = new Customer
        {
            Name = dto.Name,
            Email = dto.Email
        };

        try
        {
            await repository.SaveAsync(customer, ct);
            logger.LogInformation("Saved customer {Email}", dto.Email);
        }
        catch (DbException ex)
        {
            logger.LogError(ex, "Failed to save customer {Email}", dto.Email);
            throw;
        }
    }

    public async Task<Customer?> GetCustomerAsync(
        int id,
        CancellationToken ct = default)
    {
        return await repository.GetByIdAsync(id, ct);
    }
}

public record CustomerDto(string Name, string Email);
```
