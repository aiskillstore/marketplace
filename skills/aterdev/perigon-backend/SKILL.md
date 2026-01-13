---
name: perigon-backend
description: Perigon ASP.NET Core + EF Core + Aspire conventions
---
## When to use
- Backend work across src/Definition, src/Modules, src/Services, and src/AppHost (entities, DTOs, managers, controllers, EF, hosting).

## Usage
- Architecture: Definition (entities/EF/Share/ServiceDefaults) -> Modules (Managers + DTOs) -> Services (controllers). Use Code First with <Nullable>enable.
- Entities: inherit EntityBase (Id, CreatedAt, UpdatedAt, IsDeleted); Id uses Guid v7 client-generated. Strings need max length; decimals set precision (10,2 or 18,6); enums require [Description]; prefer DateTimeOffset/DateOnly/TimeOnly.
- Database: favor SQL Server (commercial) or PostgreSQL; use foreign keys within a domain; avoid string-delimited lists (use arrays/JSON). Migrations via scripts/EFMigrations.ps1; files under Definition/EntityFramework/Migrations.
- Data access: DbContexts live in Definition/EntityFramework/AppDbContext; default TenantDbFactory/UniversalDbFactory for creation. Prefer Queryable with Select projections; AsNoTracking by default; use EFCore.BulkExtensions for bulk ops.
- Managers: place in src/Modules/{Mod}/Managers; inherit ManagerBase (generic when tied to entity) for DI. Do not return ActionResult or touch HttpContext; avoid manager-to-manager refs. Use base ops (FindAsync, ExistAsync, ListAsync, PageListAsync, InsertAsync, UpdateAsync, DeleteAsync, BulkInsertAsync, ExecuteInTransactionAsync). Throw BusinessException for business errors; keep third-party calls/helpers in share/services.
- DTOs: store under src/Modules/{Mod}/Models/{Entity}Dtos with Detail/Add/Update/Item/Filter shapes; map via Mapster.
- Controllers: under src/Services/*/Controllers; inherit RestControllerBase. Use HTTP verb attributes and method names AddAsync/UpdateAsync/DeleteAsync/GetDetailAsync/FilterAsync. Return ActionResult<T>; use Problem/NotFound for errors; avoid ApiResponse wrappers; keep business logic in Manager; handle auth/permission/validation here.
- Aspire/AppHost: AppHost orchestrates infra/services; ensure Docker/Podman running. Configure via appsettings*.json. Avoid build/run commands unless requested; check editor diagnostics after changes.
