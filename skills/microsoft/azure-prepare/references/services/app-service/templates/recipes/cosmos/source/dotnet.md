# Cosmos DB Recipe — C# (.NET) — REFERENCE ONLY

## Cosmos DB SDK Setup

### NuGet Packages

```xml
<PackageReference Include="Microsoft.Azure.Cosmos" Version="3.*" />
<PackageReference Include="Azure.Identity" Version="1.13.*" />
```

### Program.cs (additions)

Add these lines — do NOT replace the existing file:

```csharp
using Azure.Identity;
using Microsoft.Azure.Cosmos;

builder.Services.AddSingleton(_ =>
{
    var endpoint = builder.Configuration["COSMOS_ENDPOINT"];
    return new CosmosClient(endpoint, new DefaultAzureCredential());
});
```

### CRUD Endpoints

Add to `Program.cs` after `app` is built:

```csharp
app.MapGet("/api/items", async (CosmosClient cosmos) =>
{
    var container = cosmos
        .GetDatabase(Environment.GetEnvironmentVariable("COSMOS_DATABASE_NAME"))
        .GetContainer(Environment.GetEnvironmentVariable("COSMOS_CONTAINER_NAME"));
    var query = container.GetItemQueryIterator<dynamic>("SELECT * FROM c");
    var results = new List<dynamic>();
    while (query.HasMoreResults)
        results.AddRange(await query.ReadNextAsync());
    return Results.Ok(results);
});
```

## Files to Modify

| File | Action |
|------|--------|
| `Program.cs` | Add CosmosClient registration + endpoints |
| `*.csproj` | Add Microsoft.Azure.Cosmos NuGet package |
