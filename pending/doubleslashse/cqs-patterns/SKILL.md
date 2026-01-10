---
name: cqs-patterns
description: Command Query Separation (CQS) and CQRS patterns for .NET. Use when designing methods, handlers, and application architecture. Ensures predictable, testable code.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Command Query Separation (CQS)

## The Principle

> A method should either be a **Command** that performs an action, or a **Query** that returns data, but not both.

```
┌─────────────────────────────────────────────────────────┐
│                        METHOD                           │
├───────────────────────┬─────────────────────────────────┤
│       COMMAND         │            QUERY                │
├───────────────────────┼─────────────────────────────────┤
│ - Changes state       │ - Returns data                  │
│ - Returns void        │ - No side effects               │
│ - "Do something"      │ - "Tell me something"           │
│ - Imperative verbs    │ - Noun or question              │
│   (Create, Update,    │   (Get, Find, Is, Has,          │
│    Delete, Process)   │    Calculate, Count)            │
└───────────────────────┴─────────────────────────────────┘
```

---

## CQS at Method Level

### Violation Examples
```csharp
// BAD: Method both modifies state AND returns data
public class Stack<T>
{
    public T Pop()  // Both removes item AND returns it
    {
        var item = _items[_count - 1];
        _count--;
        return item;
    }
}

// BAD: Getter with side effects
public class Counter
{
    private int _value;

    public int Value
    {
        get { return _value++; }  // Query that modifies state!
    }
}

// BAD: Command returns data
public class UserService
{
    public User CreateUser(string email, string name)  // Returns created user
    {
        var user = new User { Email = email, Name = name };
        _repository.Add(user);
        return user;  // CQS violation
    }
}
```

### Correct CQS Implementation
```csharp
// GOOD: Separated commands and queries
public class Stack<T>
{
    // Query - returns data, no side effects
    public T Peek()
    {
        if (_count == 0)
            throw new InvalidOperationException("Stack is empty");
        return _items[_count - 1];
    }

    // Command - modifies state, returns void
    public void Pop()
    {
        if (_count == 0)
            throw new InvalidOperationException("Stack is empty");
        _count--;
    }

    // Usage: separate calls
    var top = stack.Peek();
    stack.Pop();
}

// GOOD: Counter with pure query
public class Counter
{
    private int _value;

    public int Value => _value;  // Pure query

    public void Increment() => _value++;  // Command
}

// GOOD: User service with CQS
public class UserService
{
    // Command - creates user, returns identifier only
    public Guid CreateUser(string email, string name)
    {
        var userId = Guid.NewGuid();
        var user = new User { Id = userId, Email = email, Name = name };
        _repository.Add(user);
        return userId;  // Returning ID is acceptable
    }

    // Query - retrieves user
    public User? GetUser(Guid userId)
    {
        return _repository.GetById(userId);
    }
}
```

---

## CQS Exceptions

Some situations justify combining command and query:

### 1. Atomic Operations
```csharp
// Acceptable: Interlocked operations need to be atomic
public int IncrementAndGet()
{
    return Interlocked.Increment(ref _counter);
}

// Acceptable: Compare-and-swap patterns
public bool TryUpdate(int expected, int newValue)
{
    return Interlocked.CompareExchange(ref _value, newValue, expected) == expected;
}
```

### 2. Fluent APIs
```csharp
// Acceptable: Builder pattern returns this
public class QueryBuilder
{
    public QueryBuilder Where(string condition)
    {
        _conditions.Add(condition);
        return this;  // Returns modified builder
    }

    public QueryBuilder OrderBy(string column)
    {
        _orderBy = column;
        return this;
    }
}
```

### 3. Factory Methods
```csharp
// Acceptable: Creation returns the created object
public static Order Create(int customerId, IEnumerable<OrderItem> items)
{
    return new Order
    {
        Id = Guid.NewGuid(),
        CustomerId = customerId,
        Items = items.ToList()
    };
}
```

---

## CQRS - Command Query Responsibility Segregation

CQRS applies CQS at the **architectural level**, using separate models for reads and writes.

```
                    ┌─────────────────────────────────────┐
                    │           APPLICATION               │
                    └─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
           ┌───────────────┐               ┌───────────────┐
           │   COMMANDS    │               │    QUERIES    │
           │    (Write)    │               │    (Read)     │
           └───────────────┘               └───────────────┘
                    │                               │
                    ▼                               ▼
           ┌───────────────┐               ┌───────────────┐
           │ Command       │               │ Query         │
           │ Handlers      │               │ Handlers      │
           └───────────────┘               └───────────────┘
                    │                               │
                    ▼                               ▼
           ┌───────────────┐               ┌───────────────┐
           │ Domain Model  │               │ Read Model    │
           │ (Rich)        │               │ (DTOs)        │
           └───────────────┘               └───────────────┘
                    │                               │
                    ▼                               ▼
           ┌───────────────┐               ┌───────────────┐
           │ Write DB      │──────────────▶│ Read DB       │
           │ (Normalized)  │  Sync/Events  │ (Optimized)   │
           └───────────────┘               └───────────────┘
```

### Commands and Queries

```csharp
// === MARKER INTERFACES ===

public interface ICommand { }

public interface ICommand<TResult> { }

public interface IQuery<TResult> { }

// === COMMANDS ===

public record CreateOrderCommand(
    int CustomerId,
    List<OrderItemDto> Items
) : ICommand<Guid>;

public record UpdateOrderStatusCommand(
    Guid OrderId,
    OrderStatus NewStatus
) : ICommand;

public record CancelOrderCommand(Guid OrderId) : ICommand;

// === QUERIES ===

public record GetOrderByIdQuery(Guid OrderId) : IQuery<OrderDto?>;

public record GetOrdersByCustomerQuery(
    int CustomerId,
    int Page = 1,
    int PageSize = 10
) : IQuery<PagedResult<OrderSummaryDto>>;

public record GetOrderStatisticsQuery(
    DateTime From,
    DateTime To
) : IQuery<OrderStatisticsDto>;
```

### Command Handlers

```csharp
// === HANDLER INTERFACES ===

public interface ICommandHandler<in TCommand> where TCommand : ICommand
{
    Task HandleAsync(TCommand command, CancellationToken ct = default);
}

public interface ICommandHandler<in TCommand, TResult> where TCommand : ICommand<TResult>
{
    Task<TResult> HandleAsync(TCommand command, CancellationToken ct = default);
}

// === IMPLEMENTATION ===

public class CreateOrderCommandHandler : ICommandHandler<CreateOrderCommand, Guid>
{
    private readonly IOrderRepository _orderRepository;
    private readonly ICustomerRepository _customerRepository;
    private readonly IEventPublisher _eventPublisher;

    public CreateOrderCommandHandler(
        IOrderRepository orderRepository,
        ICustomerRepository customerRepository,
        IEventPublisher eventPublisher)
    {
        _orderRepository = orderRepository;
        _customerRepository = customerRepository;
        _eventPublisher = eventPublisher;
    }

    public async Task<Guid> HandleAsync(CreateOrderCommand command, CancellationToken ct)
    {
        // Validate
        var customer = await _customerRepository.GetByIdAsync(command.CustomerId, ct);
        if (customer == null)
            throw new CustomerNotFoundException(command.CustomerId);

        // Create domain entity
        var order = Order.Create(command.CustomerId);
        foreach (var item in command.Items)
        {
            order.AddItem(item.ProductId, item.Quantity, item.UnitPrice);
        }

        // Persist
        await _orderRepository.AddAsync(order, ct);

        // Publish domain event
        await _eventPublisher.PublishAsync(new OrderCreatedEvent(order.Id), ct);

        return order.Id;
    }
}

public class CancelOrderCommandHandler : ICommandHandler<CancelOrderCommand>
{
    private readonly IOrderRepository _orderRepository;
    private readonly IEventPublisher _eventPublisher;

    public async Task HandleAsync(CancelOrderCommand command, CancellationToken ct)
    {
        var order = await _orderRepository.GetByIdAsync(command.OrderId, ct);
        if (order == null)
            throw new OrderNotFoundException(command.OrderId);

        order.Cancel();

        await _orderRepository.UpdateAsync(order, ct);
        await _eventPublisher.PublishAsync(new OrderCancelledEvent(order.Id), ct);
    }
}
```

### Query Handlers

```csharp
public interface IQueryHandler<in TQuery, TResult> where TQuery : IQuery<TResult>
{
    Task<TResult> HandleAsync(TQuery query, CancellationToken ct = default);
}

public class GetOrderByIdQueryHandler : IQueryHandler<GetOrderByIdQuery, OrderDto?>
{
    private readonly IDbConnection _connection;

    public GetOrderByIdQueryHandler(IDbConnection connection)
    {
        _connection = connection;
    }

    public async Task<OrderDto?> HandleAsync(GetOrderByIdQuery query, CancellationToken ct)
    {
        // Direct SQL for optimized reads
        const string sql = @"
            SELECT o.Id, o.CustomerId, o.Status, o.Total, o.CreatedAt,
                   c.Name as CustomerName, c.Email as CustomerEmail
            FROM Orders o
            JOIN Customers c ON o.CustomerId = c.Id
            WHERE o.Id = @OrderId";

        return await _connection.QuerySingleOrDefaultAsync<OrderDto>(
            new CommandDefinition(sql, new { query.OrderId }, cancellationToken: ct));
    }
}

public class GetOrdersByCustomerQueryHandler
    : IQueryHandler<GetOrdersByCustomerQuery, PagedResult<OrderSummaryDto>>
{
    private readonly IDbConnection _connection;

    public async Task<PagedResult<OrderSummaryDto>> HandleAsync(
        GetOrdersByCustomerQuery query,
        CancellationToken ct)
    {
        const string sql = @"
            SELECT Id, Status, Total, CreatedAt
            FROM Orders
            WHERE CustomerId = @CustomerId
            ORDER BY CreatedAt DESC
            OFFSET @Offset ROWS FETCH NEXT @PageSize ROWS ONLY;

            SELECT COUNT(*) FROM Orders WHERE CustomerId = @CustomerId;";

        using var multi = await _connection.QueryMultipleAsync(
            new CommandDefinition(sql,
                new
                {
                    query.CustomerId,
                    Offset = (query.Page - 1) * query.PageSize,
                    query.PageSize
                },
                cancellationToken: ct));

        var items = (await multi.ReadAsync<OrderSummaryDto>()).ToList();
        var totalCount = await multi.ReadSingleAsync<int>();

        return new PagedResult<OrderSummaryDto>(items, query.Page, query.PageSize, totalCount);
    }
}
```

### Dispatcher Pattern

```csharp
public interface IDispatcher
{
    Task<TResult> SendAsync<TResult>(ICommand<TResult> command, CancellationToken ct = default);
    Task SendAsync(ICommand command, CancellationToken ct = default);
    Task<TResult> QueryAsync<TResult>(IQuery<TResult> query, CancellationToken ct = default);
}

public class Dispatcher : IDispatcher
{
    private readonly IServiceProvider _serviceProvider;

    public Dispatcher(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public async Task<TResult> SendAsync<TResult>(ICommand<TResult> command, CancellationToken ct)
    {
        var handlerType = typeof(ICommandHandler<,>).MakeGenericType(command.GetType(), typeof(TResult));
        dynamic handler = _serviceProvider.GetRequiredService(handlerType);
        return await handler.HandleAsync((dynamic)command, ct);
    }

    public async Task SendAsync(ICommand command, CancellationToken ct)
    {
        var handlerType = typeof(ICommandHandler<>).MakeGenericType(command.GetType());
        dynamic handler = _serviceProvider.GetRequiredService(handlerType);
        await handler.HandleAsync((dynamic)command, ct);
    }

    public async Task<TResult> QueryAsync<TResult>(IQuery<TResult> query, CancellationToken ct)
    {
        var handlerType = typeof(IQueryHandler<,>).MakeGenericType(query.GetType(), typeof(TResult));
        dynamic handler = _serviceProvider.GetRequiredService(handlerType);
        return await handler.HandleAsync((dynamic)query, ct);
    }
}
```

### Usage in Controllers

```csharp
[ApiController]
[Route("api/[controller]")]
public class OrdersController : ControllerBase
{
    private readonly IDispatcher _dispatcher;

    public OrdersController(IDispatcher dispatcher)
    {
        _dispatcher = dispatcher;
    }

    [HttpPost]
    public async Task<ActionResult<Guid>> CreateOrder(
        CreateOrderRequest request,
        CancellationToken ct)
    {
        var command = new CreateOrderCommand(request.CustomerId, request.Items);
        var orderId = await _dispatcher.SendAsync(command, ct);
        return CreatedAtAction(nameof(GetOrder), new { id = orderId }, orderId);
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id, CancellationToken ct)
    {
        var query = new GetOrderByIdQuery(id);
        var order = await _dispatcher.QueryAsync(query, ct);
        return order == null ? NotFound() : Ok(order);
    }

    [HttpPost("{id}/cancel")]
    public async Task<IActionResult> CancelOrder(Guid id, CancellationToken ct)
    {
        var command = new CancelOrderCommand(id);
        await _dispatcher.SendAsync(command, ct);
        return NoContent();
    }
}
```

---

## Benefits of CQS/CQRS

| Benefit | Description |
|---------|-------------|
| **Testability** | Commands and queries are isolated, easy to test |
| **Scalability** | Read and write sides can scale independently |
| **Optimization** | Read models optimized for queries, write models for business rules |
| **Clarity** | Clear intent - methods either change state or return data |
| **Maintainability** | Single responsibility, easier to modify |
| **Debugging** | Queries are safe to call repeatedly |

---

## When to Use CQRS

### Good Fit
- Complex domains with different read/write patterns
- High-read, low-write scenarios
- Systems requiring audit trails
- Event-sourced systems
- Microservices with separate read replicas

### Not Needed
- Simple CRUD applications
- Small teams/projects
- Consistent read/write patterns
- When added complexity outweighs benefits

---

## Quick Reference

```csharp
// Pure Query - Safe, no side effects
public Customer? GetCustomer(int id);
public IReadOnlyList<Order> FindOrdersByStatus(OrderStatus status);
public bool IsEmailAvailable(string email);
public int CountActiveUsers();
public decimal CalculateTotalRevenue(DateTime from, DateTime to);

// Pure Command - Changes state, returns void (or ID)
public void CreateCustomer(Customer customer);
public void UpdateOrderStatus(Guid orderId, OrderStatus status);
public void DeleteProduct(int productId);
public Guid PlaceOrder(OrderRequest request);  // ID return is acceptable
```
