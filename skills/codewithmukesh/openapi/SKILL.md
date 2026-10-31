---
name: openapi
description: >
  Built-in OpenAPI support for .NET 10 applications. Covers document generation,
  transformers, TypedResults metadata, security schemes, XML comments, build-time
  generation, and multiple document support. No Swashbuckle needed.
  Load this skill when setting up API documentation, customizing OpenAPI output,
  adding security schemes to docs, or when the user mentions "OpenAPI",
  "AddOpenApi", "MapOpenApi", "document transformer", "operation transformer",
  "schema transformer", "OpenAPI 3.1", "API documentation", "Swashbuckle
  replacement", "Produces", "WithSummary", "WithDescription", "ProblemDetails",
  "Kiota", or "client generation".
---

# OpenAPI

## Core Principles

1. **Built-in, not Swashbuckle** — .NET 10 ships `Microsoft.AspNetCore.OpenApi` as the official, framework-maintained OpenAPI solution. Swashbuckle was removed from templates in .NET 9 and is no longer recommended.
2. **TypedResults drive the schema** — `TypedResults.Ok<T>()` automatically generates correct OpenAPI response schemas. `Results.Ok()` does not. Always use `TypedResults`.
3. **Transformers over workarounds** — Document, operation, and schema transformers compose cleanly. Use them for security schemes, global responses, and schema customization.
4. **Metadata on every endpoint** — Use `.WithName()`, `.WithSummary()`, `.WithTags()` on every endpoint. This metadata feeds directly into the OpenAPI spec and client generators.

## Patterns

### Basic Setup

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();  // Serves at /openapi/v1.json
}
```

### Endpoint Metadata

```csharp
group.MapPost("/", CreateOrder)
    .WithName("CreateOrder")
    .WithSummary("Create a new order")
    .WithDescription("Creates a new order for the specified customer.")
    .Produces<OrderResponse>(StatusCodes.Status201Created)
    .ProducesValidationProblem()
    .ProducesProblem(StatusCodes.Status500InternalServerError);
```

With `TypedResults`, response metadata is inferred automatically:

```csharp
static async Task<Results<Created<OrderResponse>, ValidationProblem>> CreateOrder(
    CreateOrderRequest request, ISender sender, CancellationToken ct)
{
    var result = await sender.Send(new CreateOrder.Command(request), ct);
    return result.IsSuccess
        ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
        : TypedResults.ValidationProblem(result.Errors);
}
```

### Bearer Token Security Scheme

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

internal sealed class BearerSecuritySchemeTransformer(
    IAuthenticationSchemeProvider authSchemeProvider) : IOpenApiDocumentTransformer
{
    public async Task TransformAsync(OpenApiDocument document,
        OpenApiDocumentTransformerContext context, CancellationToken ct)
    {
        var schemes = await authSchemeProvider.GetAllSchemesAsync();
        if (!schemes.Any(s => s.Name == "Bearer"))
            return;

        document.Components ??= new OpenApiComponents();
        document.Components.SecuritySchemes = new Dictionary<string, IOpenApiSecurityScheme>
        {
            ["Bearer"] = new OpenApiSecurityScheme
            {
                Type = SecuritySchemeType.Http,
                Scheme = "bearer",
                BearerFormat = "JWT",
                In = ParameterLocation.Header
            }
        };

        foreach (var operation in document.Paths.Values.SelectMany(p => p.Operations))
        {
            operation.Value.Security ??= [];
            operation.Value.Security.Add(new OpenApiSecurityRequirement
            {
                [new OpenApiSecuritySchemeReference("Bearer", document)] = []
            });
        }
    }
}
```

### Document Info Transformer

```csharp
builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, ct) =>
    {
        document.Info = new()
        {
            Title = "Checkout API",
            Version = "v1",
            Description = "API for processing orders and payments."
        };
        return Task.CompletedTask;
    });
});
```

### Multiple OpenAPI Documents

```csharp
builder.Services.AddOpenApi("v1");
builder.Services.AddOpenApi("internal", options =>
{
    options.AddDocumentTransformer<BearerSecuritySchemeTransformer>();
});

// Endpoints choose their document via WithGroupName
app.MapGet("/public", () => "Hello").WithGroupName("v1");
app.MapGet("/admin", () => "Secret").WithGroupName("internal");
```

Endpoints without `.WithGroupName()` appear in all documents.

### XML Documentation Comments (.NET 10)

Enable in the project file — the source generator extracts `<summary>`, `<param>`, `<response>` tags automatically:

```xml
<PropertyGroup>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
</PropertyGroup>
```

```csharp
/// <summary>Retrieves a project board by ID.</summary>
/// <param name="id">The project board ID.</param>
/// <response code="200">Returns the project board.</response>
/// <response code="404">Board not found.</response>
static async Task<Results<Ok<Board>, NotFound>> GetBoard(int id, AppDbContext db)
{
    var board = await db.Boards.FindAsync(id);
    return board is not null ? TypedResults.Ok(board) : TypedResults.NotFound();
}
```

XML comments on lambdas are not captured by the compiler. Use named methods.

### Schema Transformer

```csharp
options.AddSchemaTransformer((schema, context, ct) =>
{
    if (context.JsonTypeInfo.Type == typeof(decimal))
    {
        schema.Format = "decimal";
    }
    return Task.CompletedTask;
});
```

### Per-Endpoint Operation Transformer (.NET 10)

```csharp
app.MapGet("/old", () => "deprecated")
    .AddOpenApiOperationTransformer((operation, context, ct) =>
    {
        operation.Deprecated = true;
        return Task.CompletedTask;
    });
```

### Build-Time Document Generation

```xml
<PackageReference Include="Microsoft.Extensions.ApiDescription.Server" Version="*" />
<PropertyGroup>
    <OpenApiDocumentsDirectory>.</OpenApiDocumentsDirectory>
</PropertyGroup>
```

The spec file is generated in the output directory during build.

### YAML Endpoint (.NET 10)

```csharp
app.MapOpenApi("/openapi/{documentName}.yaml");
```

## Anti-patterns

### Don't Use Swashbuckle for New Projects

```csharp
// BAD — removed from .NET 9+ templates, maintenance concerns
builder.Services.AddSwaggerGen();
app.UseSwagger();
app.UseSwaggerUI();

// GOOD — built-in OpenAPI
builder.Services.AddOpenApi();
app.MapOpenApi();
```

### Don't Use WithOpenApi() in .NET 10

```csharp
// BAD — deprecated, produces ASPDEPR002 warning
app.MapGet("/", () => "hello").WithOpenApi(op => { op.Deprecated = true; return op; });

// GOOD — use per-endpoint operation transformer
app.MapGet("/", () => "hello")
    .AddOpenApiOperationTransformer((op, ctx, ct) =>
    {
        op.Deprecated = true;
        return Task.CompletedTask;
    });
```

### Don't Use Untyped Results

```csharp
// BAD — Results.Ok doesn't contribute to OpenAPI schema
static async Task<IResult> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? Results.Ok(order) : Results.NotFound();
}

// GOOD — TypedResults with union return type
static async Task<Results<Ok<Order>, NotFound>> GetOrder(Guid id, AppDbContext db)
{
    var order = await db.Orders.FindAsync(id);
    return order is not null ? TypedResults.Ok(order) : TypedResults.NotFound();
}
```

### Don't Skip WithName on Endpoints

```csharp
// BAD — client generators produce poor method names without operationId
group.MapGet("/{id:guid}", GetOrder);

// GOOD — operationId feeds into generated client method names
group.MapGet("/{id:guid}", GetOrder).WithName("GetOrder");
```

### Don't Use OpenApiAny in .NET 10

```csharp
// BAD — OpenApiAny types removed in Microsoft.OpenApi v2.x
schema.Example = new OpenApiString("2025-01-01");

// GOOD — use JsonNode from System.Text.Json.Nodes
schema.Example = JsonValue.Create("2025-01-01");
```

## Decision Guide

| Scenario | Recommendation |
|----------|---------------|
| New API project | `AddOpenApi()` + `MapOpenApi()` (built-in) |
| API documentation UI | Scalar (`MapScalarApiReference()`) |
| Security schemes in docs | Document transformer with `IOpenApiDocumentTransformer` |
| Response documentation | `TypedResults` with union return types |
| XML doc integration | `<GenerateDocumentationFile>true</GenerateDocumentationFile>` |
| Multiple API versions | Multiple `AddOpenApi("v1")` calls + `WithGroupName()` |
| Client code generation | Kiota (Microsoft recommended) or NSwag |
| Build-time spec | `Microsoft.Extensions.ApiDescription.Server` package |
| OpenAPI version | 3.1 (default in .NET 10), force 3.0 if consumers require it |
| Per-endpoint customization | `.AddOpenApiOperationTransformer()` on the endpoint |
