# PowerShell Installation Wrapper for Claude Bitbucket DevOps Skill
# This is a thin wrapper that delegates to install.sh to maintain DRY principle

Write-Host "🚀 Claude Bitbucket DevOps Skill - Windows Installer" -ForegroundColor Cyan
Write-Host ""

# Check if bash is available (Git Bash, WSL, etc.)
$bashCommand = Get-Command bash -ErrorAction SilentlyContinue

if ($null -eq $bashCommand) {
    Write-Host "❌ Error: bash not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "This installer requires bash to run the installation script." -ForegroundColor Yellow
    Write-Host "Please install Git for Windows, which includes Git Bash:" -ForegroundColor Yellow
    Write-Host "    https://git-scm.com/download/win" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installing Git, restart PowerShell and run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatively, you can run install.sh directly from Git Bash." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Found bash at: $($bashCommand.Source)" -ForegroundColor Green
Write-Host ""
Write-Host "Delegating to install.sh..." -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Execute install.sh using bash
& bash "$scriptDir/install.sh"

# Capture exit code
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ Windows installation completed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Installation failed with exit code: $exitCode" -ForegroundColor Red
}

exit $exitCode
