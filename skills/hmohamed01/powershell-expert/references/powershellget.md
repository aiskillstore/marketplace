# PowerShellGet & Gallery Reference

## Table of Contents
1. [Overview](#overview)
2. [Setup](#setup)
3. [Finding Modules](#finding-modules)
4. [Installing Modules](#installing-modules)
5. [Managing Modules](#managing-modules)
6. [Publishing Modules](#publishing-modules)

---

## Overview

**PowerShell Gallery** (https://www.powershellgallery.com) is the central repository for PowerShell modules, scripts, and DSC resources.

**PSResourceGet** (`Microsoft.PowerShell.PSResourceGet`) is the modern replacement for PowerShellGet:
- Ships with PowerShell 7.4+
- Faster and more reliable than legacy PowerShellGet
- Uses `*-PSResource` cmdlet naming

### Legacy vs Modern Cmdlets
| Legacy (PowerShellGet) | Modern (PSResourceGet) |
|------------------------|------------------------|
| `Find-Module` | `Find-PSResource` |
| `Install-Module` | `Install-PSResource` |
| `Update-Module` | `Update-PSResource` |
| `Uninstall-Module` | `Uninstall-PSResource` |
| `Get-InstalledModule` | `Get-InstalledPSResource` |
| `Publish-Module` | `Publish-PSResource` |

---

## Setup

### Check Installed Version
```powershell
Get-Module -Name PowerShellGet -ListAvailable
Get-Module -Name Microsoft.PowerShell.PSResourceGet -ListAvailable
```

### Install/Update PSResourceGet
```powershell
# Install modern PSResourceGet
Install-Module -Name Microsoft.PowerShell.PSResourceGet -Force

# Or update if already installed
Update-Module -Name Microsoft.PowerShell.PSResourceGet
```

### Configure Repository
```powershell
# View registered repositories
Get-PSResourceRepository

# Register PSGallery if not present
Register-PSResourceRepository -PSGallery

# Set repository priority (lower = higher priority)
Set-PSResourceRepository -Name PSGallery -Priority 50
```

---

## Finding Modules

### Basic Search
```powershell
# Search by name
Find-PSResource -Name 'Az.Compute'

# Search with wildcards
Find-PSResource -Name 'Az.*'

# Search by tag
Find-PSResource -Tag 'Azure', 'Cloud'
```

### Find-PSResource Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `-Name` | Module name (wildcards allowed) | `'PSReadLine'` |
| `-Type` | Resource type | `Module`, `Script` |
| `-Version` | Version or range | `'2.0.0'`, `'[1.0,2.0)'` |
| `-Prerelease` | Include prereleases | Switch |
| `-Tag` | Filter by tags | `'DSC', 'Azure'` |
| `-Repository` | Target repository | `'PSGallery'` |
| `-CommandName` | Find by command | `'Get-AzVM'` |
| `-DscResourceName` | Find by DSC resource | `'File'` |

### Version Range Syntax (NuGet)
| Syntax | Meaning |
|--------|---------|
| `1.0.0` | Exact version |
| `[1.0,2.0]` | >= 1.0 AND <= 2.0 |
| `[1.0,2.0)` | >= 1.0 AND < 2.0 |
| `(1.0,)` | > 1.0 |
| `[,2.0]` | <= 2.0 |

### Search Examples
```powershell
# Find all versions
Find-PSResource -Name 'Pester' -Version '*'

# Find specific version range
Find-PSResource -Name 'Az' -Version '[5.0,7.0)' -Prerelease

# Find by command name
Find-PSResource -CommandName 'Invoke-RestMethod'

# Find DSC resources
Find-PSResource -DscResourceName 'File' -Repository PSGallery

# Include dependencies
Find-PSResource -Name 'Az.Accounts' -IncludeDependencies
```

---

## Installing Modules

### Basic Installation
```powershell
# Install latest stable
Install-PSResource -Name 'Az.Compute'

# Install specific version
Install-PSResource -Name 'Pester' -Version '5.0.0'

# Install prerelease
Install-PSResource -Name 'Az' -Prerelease

# Install for current user only
Install-PSResource -Name 'PSReadLine' -Scope CurrentUser

# Install for all users (requires admin)
Install-PSResource -Name 'PSReadLine' -Scope AllUsers
```

### Install-PSResource Parameters
| Parameter | Description |
|-----------|-------------|
| `-Name` | Module name(s) |
| `-Version` | Version or range |
| `-Prerelease` | Include prerelease |
| `-Scope` | `CurrentUser` or `AllUsers` |
| `-Repository` | Source repository |
| `-TrustRepository` | Skip trust prompt |
| `-Reinstall` | Force reinstall |
| `-SkipDependencyCheck` | Don't install dependencies |
| `-NoClobber` | Don't overwrite commands |

### Trusted Repository
```powershell
# Trust PSGallery to avoid prompts
Set-PSResourceRepository -Name PSGallery -Trusted

# Or use -TrustRepository per install
Install-PSResource -Name 'Module' -TrustRepository
```

---

## Managing Modules

### List Installed Modules
```powershell
# All installed
Get-InstalledPSResource

# Filter by name
Get-InstalledPSResource -Name 'Az.*'

# Specific version
Get-InstalledPSResource -Name 'Pester' -Version '5.0.0'
```

### Update Modules
```powershell
# Update specific module
Update-PSResource -Name 'Az.Compute'

# Update all
Update-PSResource -Name '*'

# Include prerelease updates
Update-PSResource -Name 'Module' -Prerelease
```

### Uninstall Modules
```powershell
# Uninstall specific version
Uninstall-PSResource -Name 'Pester' -Version '4.0.0'

# Uninstall all versions
Uninstall-PSResource -Name 'Pester' -Version '*'

# Skip dependency check
Uninstall-PSResource -Name 'Module' -SkipDependencyCheck
```

### Save Modules (Download without install)
```powershell
# Save to path for offline use
Save-PSResource -Name 'Az.Compute' -Path 'C:\OfflineModules'

# Include dependencies
Save-PSResource -Name 'Az' -Path 'C:\OfflineModules' -IncludeXml
```

---

## Publishing Modules

### Prepare Module
```powershell
# Module manifest requirements
@{
    RootModule        = 'MyModule.psm1'
    ModuleVersion     = '1.0.0'
    GUID              = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
    Author            = 'Your Name'
    Description       = 'Module description'
    PowerShellVersion = '5.1'
    FunctionsToExport = @('Get-MyFunction', 'Set-MyFunction')
    Tags              = @('Utility', 'Automation')
    LicenseUri        = 'https://opensource.org/licenses/MIT'
    ProjectUri        = 'https://github.com/user/project'
}
```

### Publish
```powershell
# Get API key from https://www.powershellgallery.com/account/apikeys
$apiKey = 'your-api-key'

# Publish module
Publish-PSResource -Path './MyModule' -ApiKey $apiKey -Repository PSGallery

# Dry run (validate without publishing)
Publish-PSResource -Path './MyModule' -ApiKey $apiKey -WhatIf
```

---

## Common Patterns

### Install if Missing
```powershell
function Ensure-Module {
    param([string]$Name, [string]$MinVersion)

    $installed = Get-InstalledPSResource -Name $Name -ErrorAction SilentlyContinue

    if (-not $installed -or ($MinVersion -and $installed.Version -lt $MinVersion)) {
        Install-PSResource -Name $Name -Scope CurrentUser -TrustRepository
    }

    Import-Module $Name
}

Ensure-Module -Name 'Az.Compute' -MinVersion '5.0.0'
```

### Bulk Install from List
```powershell
$modules = @(
    @{ Name = 'Pester'; Version = '5.0.0' }
    @{ Name = 'PSReadLine' }
    @{ Name = 'Az.Accounts' }
)

foreach ($mod in $modules) {
    $params = @{
        Name            = $mod.Name
        Scope           = 'CurrentUser'
        TrustRepository = $true
    }
    if ($mod.Version) { $params.Version = $mod.Version }

    Install-PSResource @params
}
```

### Search Gallery for Popular Modules
```powershell
# Find most downloaded modules (sort by download count not available via cmdlet)
# Use web API or browse powershellgallery.com/stats/packages

# Find recently updated
Find-PSResource -Name '*' -Repository PSGallery |
    Sort-Object PublishedDate -Descending |
    Select-Object -First 20
```

---

## Useful Links

- **PowerShell Gallery**: https://www.powershellgallery.com
- **Gallery Status**: https://aka.ms/psgallery-status
- **Gallery Issues**: https://aka.ms/psgallery-issues
- **Module Browser**: https://learn.microsoft.com/en-us/powershell/module/
- **PSResourceGet Docs**: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.psresourceget/
