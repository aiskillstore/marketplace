<#
.SYNOPSIS
    Search PowerShell Gallery for modules, scripts, or DSC resources.

.DESCRIPTION
    Enhanced search wrapper for Find-PSResource with formatted output
    and common search patterns.

.PARAMETER Name
    Module name pattern. Supports wildcards (*).

.PARAMETER Tag
    Filter by tags (comma-separated).

.PARAMETER Command
    Find modules containing a specific command.

.PARAMETER DscResource
    Find modules containing a specific DSC resource.

.PARAMETER Type
    Resource type: Module, Script, or All.

.PARAMETER Prerelease
    Include prerelease versions.

.PARAMETER First
    Number of results to return. Default: 20.

.EXAMPLE
    .\Search-Gallery.ps1 -Name 'Az.*'
    Search for all Azure modules.

.EXAMPLE
    .\Search-Gallery.ps1 -Tag 'Azure', 'Cloud' -First 10
    Search by tags.

.EXAMPLE
    .\Search-Gallery.ps1 -Command 'Invoke-RestMethod'
    Find modules containing a specific command.
#>

[CmdletBinding(DefaultParameterSetName = 'ByName')]
param(
    [Parameter(ParameterSetName = 'ByName', Position = 0)]
    [string]$Name = '*',

    [Parameter(ParameterSetName = 'ByName')]
    [string[]]$Tag,

    [Parameter(ParameterSetName = 'ByCommand', Mandatory)]
    [string]$Command,

    [Parameter(ParameterSetName = 'ByDsc', Mandatory)]
    [string]$DscResource,

    [ValidateSet('Module', 'Script', 'All')]
    [string]$Type = 'Module',

    [switch]$Prerelease,

    [int]$First = 20
)

# Ensure PSResourceGet is available
$psrg = Get-Module -Name Microsoft.PowerShell.PSResourceGet -ListAvailable
if (-not $psrg) {
    Write-Warning "Microsoft.PowerShell.PSResourceGet not found. Using legacy Find-Module."
    $useLegacy = $true
}

# Build search parameters
$searchParams = @{
    Repository = 'PSGallery'
}

if ($Prerelease) {
    $searchParams.Prerelease = $true
}

# Execute search based on parameter set
$results = switch ($PSCmdlet.ParameterSetName) {
    'ByName' {
        $searchParams.Name = $Name
        if ($Tag) { $searchParams.Tag = $Tag }
        if ($Type -ne 'All') { $searchParams.Type = $Type }

        if ($useLegacy) {
            Find-Module @searchParams -ErrorAction SilentlyContinue |
                Select-Object -First $First
        } else {
            Find-PSResource @searchParams -ErrorAction SilentlyContinue |
                Select-Object -First $First
        }
    }
    'ByCommand' {
        if ($useLegacy) {
            Find-Module -Command $Command -Repository PSGallery -ErrorAction SilentlyContinue |
                Select-Object -First $First
        } else {
            Find-PSResource -CommandName $Command -Repository PSGallery -ErrorAction SilentlyContinue |
                Select-Object -First $First
        }
    }
    'ByDsc' {
        if ($useLegacy) {
            Find-Module -DscResource $DscResource -Repository PSGallery -ErrorAction SilentlyContinue |
                Select-Object -First $First
        } else {
            Find-PSResource -DscResourceName $DscResource -Repository PSGallery -ErrorAction SilentlyContinue |
                Select-Object -First $First
        }
    }
}

if (-not $results) {
    Write-Host "No results found." -ForegroundColor Yellow
    return
}

# Format output
$results | ForEach-Object {
    [PSCustomObject]@{
        Name        = $_.Name
        Version     = $_.Version
        Description = if ($_.Description.Length -gt 80) {
            $_.Description.Substring(0, 77) + '...'
        } else {
            $_.Description
        }
        Author      = $_.Author
        Downloads   = if ($_.AdditionalMetadata.downloadCount) {
            $_.AdditionalMetadata.downloadCount
        } else {
            'N/A'
        }
    }
} | Format-Table -AutoSize -Wrap

Write-Host "`nTotal: $($results.Count) results" -ForegroundColor Cyan
Write-Host "Install: Install-PSResource -Name '<ModuleName>' -Scope CurrentUser" -ForegroundColor DarkGray
