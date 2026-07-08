# Auth Recipe — C# (.NET) — REFERENCE ONLY

## Microsoft Identity Web (ASP.NET Core)

### NuGet Packages

```xml
<PackageReference Include="Microsoft.Identity.Web" Version="3.*" />
```

### Program.cs (additions)

Add these lines — do NOT replace the existing file:

```csharp
using Microsoft.Identity.Web;

// Add after builder creation
builder.Services.AddMicrosoftIdentityWebApiAuthentication(builder.Configuration);
builder.Services.AddAuthorization();

// Add after app build
app.UseAuthentication();
app.UseAuthorization();

// Protected endpoint
app.MapGet("/api/me", [Authorize] (HttpContext ctx) =>
{
    var name = ctx.User.FindFirst("name")?.Value;
    return Results.Ok(new { name });
});
```

### appsettings.json

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "<tenant-id>",
    "ClientId": "<client-id>",
    "Audience": "api://<client-id>"
  }
}
```

> ⚠️ The `Audience` must match the Application ID URI of the app registration (typically `api://<client-id>`). Set `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` as app settings in Azure rather than hardcoding them.

## Files to Modify

| File | Action |
|------|--------|
| `Program.cs` | Add authentication middleware + protected endpoints |
| `appsettings.json` | Add AzureAd configuration section |
| `*.csproj` | Add Microsoft.Identity.Web NuGet package |
