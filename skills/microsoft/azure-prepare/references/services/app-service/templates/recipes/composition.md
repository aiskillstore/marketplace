# Composition Algorithm — REFERENCE ONLY

Step-by-step algorithm for composing a base App Service template with an integration recipe.

> **This is the authoritative process. Follow it exactly.**

## Algorithm

```
INPUT:
  - language:    dotnet | typescript | javascript | python | java
  - scenario:    web-api | web-app
  - integration: none | sql | cosmos | auth | redis
  - iac:         bicep | terraform

OUTPUT:
  - Complete project directory ready for `azd up`
```

### Step 1: Fetch Base Template

```bash
# Determine template by scenario + language
IF scenario == 'web-api':
  TEMPLATE = web_api_templates[language]    # See web-api.md
ELSE IF scenario == 'web-app':
  TEMPLATE = web_app_templates[language]    # See web-app.md

# Non-interactive init
ENV_NAME="$(basename "$PWD" | tr '[:upper:]' '[:lower:]' | tr ' _' '-')-dev"
# PowerShell: $ENV_NAME = "$(Split-Path -Leaf (Get-Location) | ForEach-Object { $_.ToLower() -replace '[ _]','-' })-dev"
azd init -t $TEMPLATE -e "$ENV_NAME" --no-prompt
```

### Step 2: Check if Recipe Needed

```
IF integration IN [none]:
  → DONE. Base template is complete.

IF integration IN [sql, cosmos, redis, auth]:
  → Full recipe. Continue to Step 3.
```

### Step 3: Add IaC Module (for full recipes only)

**Bicep:**
1. Read recipe's `README.md` for the Bicep module file
2. Copy module into `infra/app/`
3. Add module reference in `infra/main.bicep`:
   ```bicep
   module sqlServer './app/sql.bicep' = {
     name: 'sqlServer'
     scope: rg
     params: {
       name: name
       location: location
       tags: tags
       appServicePrincipalId: web.outputs.SERVICE_WEB_IDENTITY_PRINCIPAL_ID
     }
   }
   ```
4. If VNET_ENABLED, add the network module for private endpoints

**Terraform:**
1. Copy recipe `.tf` files into `infra/`
2. Merge app settings into web app resource block
3. Networking uses `count = var.vnet_enabled ? 1 : 0`

### Step 4: Add App Settings

Read the recipe's `README.md` for required app settings. Add them to the web app config.

> **CRITICAL: Managed Identity Configuration**
>
> For service bindings, prefer User Assigned Managed Identity (UAMI).
> Always include connection settings that reference managed identity, not passwords:
>
> ⚠️ **Connection-string format is language-specific.** The example below is **.NET / ADO.NET** format. For other stacks, use the per-language env vars documented in `recipes/sql/source/{language}.md`:
>
> | Language | Env var(s) | Format |
> |---|---|---|
> | .NET | `AZURE_SQL_CONNECTION_STRING` | `Server=...;Authentication=Active Directory Managed Identity;User Id=<clientId>;` (ADO.NET) |
> | Python | `AZURE_SQL_SERVER`, `AZURE_SQL_DATABASE`, `AZURE_CLIENT_ID` | Code obtains MI access token and passes via ODBC `attrs_before` |
> | Node.js | `DATABASE_URL` | `sqlserver://<host>:1433;database=<db>;authentication=ActiveDirectoryMsi;clientId=<clientId>` (Prisma) |

> ```bicep
> appSettings: [
>   { name: 'AZURE_SQL_CONNECTION_STRING', value: 'Server=${sqlServer.properties.fullyQualifiedDomainName};Database=${dbName};Authentication=Active Directory Managed Identity;User Id=${managedIdentity.properties.clientId};' }
> ]
> ```

### Step 5: Add Source Code Integration

1. Read `recipes/{integration}/source/{language}.md`
2. Add the integration code (service client, middleware, configuration)
3. Add package dependencies (NuGet, npm, pip, Maven)

> ⛔ **Do NOT replace the main entry point file** (Program.cs, app.py, index.js).
> Recipes ADD integration code alongside the existing application code.

### Step 6: Update azure.yaml (if needed)

Some recipes require hooks:
```yaml
hooks:
  postprovision:
    posix:
      shell: sh
      run: ./infra/scripts/setup-db.sh
    windows:
      shell: pwsh
      run: ./infra/scripts/setup-db.ps1
```

### Step 7: Validate and Deploy

**Required Environment Setup:**
```bash
azd env set AZURE_LOCATION eastus2
```

**Deployment (two-phase recommended):**
```bash
azd provision --no-prompt     # Create resources + RBAC assignments
sleep 60                       # Wait for RBAC propagation
azd deploy --no-prompt        # Deploy code (RBAC now active)
```

> **CRITICAL: Never store database passwords in app settings.**
> The correct approach is managed identity with passwordless connections.

## Critical Rules

1. **NEVER synthesize Bicep or Terraform from scratch** — always start from base template IaC
2. **Do not restructure or replace base IaC files** — only ADD recipe modules alongside them
3. **ALWAYS use recipe RBAC role GUIDs** — never let the LLM guess role IDs
4. **ALWAYS use `--no-prompt`** — the agent must never elicit user input during azd commands
5. **ALWAYS include a health check endpoint** at `/health`
6. **ALWAYS use managed identity** — no connection strings with passwords
7. **ALWAYS tag the App Service** with `azd-service-name` matching `azure.yaml`
