# SQL Database — C# (.NET) — REFERENCE ONLY

## Entity Framework Core Setup

Add EF Core with Azure SQL and managed identity support to an ASP.NET Core app.

### NuGet Packages

```xml
<PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.*" />
<PackageReference Include="Azure.Identity" Version="1.13.*" />
<PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.*" />
```

### DbContext

Create `Data/AppDbContext.cs`:

```csharp
using Microsoft.EntityFrameworkCore;

namespace MyApp.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<TodoItem> TodoItems => Set<TodoItem>();
}

public class TodoItem
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public bool IsComplete { get; set; }
}
```

### Program.cs (additions)

Add these lines to `Program.cs` — do NOT replace the file:

```csharp
using Microsoft.EntityFrameworkCore;
using MyApp.Data;

// Add after builder creation
var connectionString = builder.Configuration.GetConnectionString("AZURE_SQL")
    ?? builder.Configuration["AZURE_SQL_CONNECTION_STRING"];

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));

// Add health check for SQL
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>();

// After app build — map health checks so App Service probes reflect SQL connectivity
app.MapHealthChecks("/health");
```

### API Endpoints

Add to `Program.cs` after `app` is built:

```csharp
app.MapGet("/api/todos", async (AppDbContext db) =>
    await db.TodoItems.ToListAsync());

app.MapGet("/api/todos/{id}", async (int id, AppDbContext db) =>
    await db.TodoItems.FindAsync(id) is TodoItem todo
        ? Results.Ok(todo)
        : Results.NotFound());

app.MapPost("/api/todos", async (TodoItem todo, AppDbContext db) =>
{
    db.TodoItems.Add(todo);
    await db.SaveChangesAsync();
    return Results.Created($"/api/todos/{todo.Id}", todo);
});
```

### appsettings.json

```json
{
  "ConnectionStrings": {
    "AZURE_SQL": "Server=localhost;Database=myapp;Trusted_Connection=true;"
  }
}
```

> In production, the `AZURE_SQL_CONNECTION_STRING` app setting from Azure overrides this with the managed identity connection string.

### EF Migrations (postprovision hook)

Create `infra/scripts/setup-db.sh`:

```bash
#!/bin/bash
dotnet ef database update --project src/api
```

## Files to Add

| File | Action |
|------|--------|
| `Data/AppDbContext.cs` | Create — DbContext + entity models |
| `Program.cs` | Modify — add DbContext registration + endpoints |
| `appsettings.json` | Modify — add ConnectionStrings section |

## Common Patterns

- Always use `AddHealthChecks().AddDbContextCheck<>()` for SQL health monitoring
- Use `AsNoTracking()` for read-only queries to improve performance
- Apply migrations via postprovision hook, not at app startup
