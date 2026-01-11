# Module Health Check Script (PowerShell)
# Analyzes module structure and calculates health scores

param(
    [string]$SourceDir = "source"
)

$ErrorActionPreference = "Stop"

# Configuration
$IDEAL_MIN_CLASSES = 5
$IDEAL_MAX_CLASSES = 30
$WARNING_MAX_CLASSES = 50

Write-Host "🏥 Module Health Check" -ForegroundColor Cyan
Write-Host ("━" * 60)
Write-Host ""

# Check if source directory exists
if (-not (Test-Path $SourceDir -PathType Container)) {
    Write-Host "❌ Error: $SourceDir directory not found" -ForegroundColor Red
    exit 1
}

# Function to count items in file
function Count-Items {
    param(
        [string]$File,
        [string]$Pattern
    )

    if (Test-Path $File) {
        $matches = Select-String -Path $File -Pattern $Pattern -AllMatches
        return $matches.Count
    }
    return 0
}

# Function to calculate health score
function Get-HealthScore {
    param(
        [int]$Classes,
        [int]$Properties,
        [bool]$HasReadme
    )

    $score = 0

    # Size Balance (30 points)
    if ($Classes -ge $IDEAL_MIN_CLASSES -and $Classes -le $IDEAL_MAX_CLASSES) {
        $score += 30
    }
    elseif (($Classes -ge 1 -and $Classes -lt $IDEAL_MIN_CLASSES) -or
            ($Classes -gt $IDEAL_MAX_CLASSES -and $Classes -le $WARNING_MAX_CLASSES)) {
        $score += 15
    }

    # Documentation (20 points)
    if ($HasReadme) {
        $score += 20
    }

    # Completeness (20 points)
    if ($Classes -gt 0 -and $Properties -gt 0) {
        $score += 20
    }
    elseif ($Classes -gt 0 -or $Properties -gt 0) {
        $score += 10
    }

    # Ratio (20 points)
    if ($Classes -gt 0) {
        $ratio = ($Properties * 10) / $Classes
        if ($ratio -ge 20 -and $ratio -le 80) {
            $score += 20
        }
        elseif ($ratio -ge 10 -and $ratio -le 120) {
            $score += 10
        }
    }

    # Organization (10 points)
    $score += 10

    return $score
}

# Function to get status
function Get-Status {
    param(
        [int]$Score,
        [int]$Classes
    )

    if ($Score -ge 90) {
        return "✅ Great"
    }
    elseif ($Score -ge 80) {
        return "✅ Good"
    }
    elseif ($Score -ge 70) {
        return "✅ OK"
    }
    elseif ($Score -ge 60) {
        return "⚠️  Fair"
    }
    elseif ($Classes -ge $WARNING_MAX_CLASSES) {
        return "❌ Bloat"
    }
    else {
        return "⚠️  Small"
    }
}

# Initialize counters
$totalModules = 0
$totalClasses = 0
$totalProperties = 0
$totalScore = 0
$healthyModules = 0
$warningModules = 0
$criticalModules = 0

# Results array
$results = @()

# Get all module directories
$modules = Get-ChildItem -Path $SourceDir -Directory | Sort-Object Name

# Analyze each module
foreach ($moduleDir in $modules) {
    $moduleName = $moduleDir.Name
    $totalModules++

    # Count classes and properties
    $classesFile = Join-Path $moduleDir.FullName "classes.edn"
    $propertiesFile = Join-Path $moduleDir.FullName "properties.edn"

    $classes = Count-Items -File $classesFile -Pattern ":user\.class/"
    $properties = Count-Items -File $propertiesFile -Pattern ":user\.property/"

    # Check for README
    $readmeFile = Join-Path $moduleDir.FullName "README.md"
    $hasReadme = Test-Path $readmeFile

    # Calculate ratio
    if ($classes -gt 0) {
        $ratio = [math]::Round($properties / $classes, 1)
    }
    else {
        $ratio = "∞"
    }

    # Calculate health score
    $score = Get-HealthScore -Classes $classes -Properties $properties -HasReadme $hasReadme

    # Get status
    $status = Get-Status -Score $score -Classes $classes

    # Update counters
    $totalClasses += $classes
    $totalProperties += $properties
    $totalScore += $score

    if ($score -ge 80) {
        $healthyModules++
    }
    elseif ($score -ge 60) {
        $warningModules++
    }
    else {
        $criticalModules++
    }

    # Store result
    $results += [PSCustomObject]@{
        Module     = $moduleName
        Score      = $score
        Classes    = $classes
        Properties = $properties
        Ratio      = $ratio
        Status     = $status
    }
}

# Display results table
Write-Host ("%-15s | %5s | %5s | %5s | %6s | %s" -f "Module", "Score", "Cls", "Props", "Ratio", "Status")
Write-Host ("━" * 60)

foreach ($result in $results) {
    $scoreStr = "$($result.Score)/100"
    Write-Host ("{0,-15} | {1,9} | {2,5} | {3,5} | {4,6} | {5}" -f `
        $result.Module, $scoreStr, $result.Classes, $result.Properties, $result.Ratio, $result.Status)
}

# Summary
Write-Host ("━" * 60)
Write-Host ""
Write-Host "Summary:"
Write-Host "  Total Modules: $totalModules"
Write-Host "  Total Classes: $totalClasses"
Write-Host "  Total Properties: $totalProperties"
Write-Host ""

# Calculate overall health
if ($totalModules -gt 0) {
    $overallHealth = [math]::Floor($totalScore / $totalModules)
    Write-Host "  Overall Health: $overallHealth/100"
    Write-Host ""
    Write-Host "  ✅ Healthy Modules: $healthyModules/$totalModules" -ForegroundColor Green
    Write-Host "  ⚠️  Needs Attention: $warningModules/$totalModules" -ForegroundColor Yellow
    Write-Host "  ❌ Critical Issues: $criticalModules/$totalModules" -ForegroundColor Red
    Write-Host ""
}

# Find issues
Write-Host "Issues Found:"
Write-Host ""

# Check for bloated modules
$bloatedFound = $false
foreach ($result in $results) {
    if ($result.Classes -ge $WARNING_MAX_CLASSES) {
        $pct = [math]::Floor(($result.Classes * 100) / $totalClasses)
        Write-Host "  ❌ $($result.Module) is bloated ($($result.Classes) classes = $pct% of total)" -ForegroundColor Red
        Write-Host "     Recommendation: Split into focused modules"
        Write-Host ""
        $bloatedFound = $true
    }
}

# Check for small modules
$smallModules = @()
foreach ($result in $results) {
    # Skip common and base modules
    if ($result.Module -eq "common" -or $result.Module -eq "base") {
        continue
    }

    if ($result.Classes -le 2 -and $result.Classes -gt 0) {
        $smallModules += $result.Module
    }
}

if ($smallModules.Count -gt 0) {
    Write-Host "  ⚠️  Small modules: $($smallModules -join ', ')" -ForegroundColor Yellow
    Write-Host "     Options: Expand with related classes or merge"
    Write-Host ""
}

# Check for modules without README
$noReadme = @()
foreach ($moduleDir in $modules) {
    $readmeFile = Join-Path $moduleDir.FullName "README.md"
    if (-not (Test-Path $readmeFile)) {
        $noReadme += $moduleDir.Name
    }
}

if ($noReadme.Count -gt 0) {
    Write-Host "  ⚠️  Missing README: $($noReadme -join ', ')" -ForegroundColor Yellow
    Write-Host "     Recommendation: Add documentation"
    Write-Host ""
}

if (-not $bloatedFound -and $smallModules.Count -eq 0 -and $noReadme.Count -eq 0) {
    Write-Host "  ✅ No major issues found!" -ForegroundColor Green
    Write-Host ""
}

Write-Host ("━" * 60)
Write-Host ""
Write-Host "Run 'module-health' skill for detailed analysis and recommendations"
