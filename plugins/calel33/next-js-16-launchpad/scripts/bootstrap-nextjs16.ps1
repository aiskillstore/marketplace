<#!
.SYNOPSIS
  Bootstraps or upgrades a project to the Next.js 16 recommended stack.
.DESCRIPTION
  Validates Node.js 20.9+, applies the official codemod (optional), installs latest next/react packages,
  and runs create-next-app with TypeScript, ESLint, Tailwind, App Router, Turbopack, and @/* alias defaults.
.PARAMETER ProjectName
  Target directory for create-next-app (defaults to "next16-app").
.PARAMETER SkipCodemod
  Skip running the upgrade codemod (set when starting from scratch).
#>
param(
  [string]$ProjectName = "next16-app",
  [switch]$SkipCodemod
)

$ErrorActionPreference = "Stop"

function Require-Command {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "Command '$Name' is required but not installed."
  }
}

Require-Command node
Require-Command npm
Require-Command npx

$nodeVersion = (node -v).TrimStart('v')
try {
  $parsed = [version]$nodeVersion
} catch {
  throw "Unable to parse Node.js version '$nodeVersion'."
}

if ($parsed.Major -lt 20 -or ($parsed.Major -eq 20 -and $parsed.Minor -lt 9)) {
  throw "Next.js 16 requires Node.js 20.9+. Detected v$nodeVersion."
}

if (-not $SkipCodemod) {
  Write-Host "Running Next.js codemod upgrade..." -ForegroundColor Cyan
  npx @next/codemod@canary upgrade latest
}

Write-Host "Installing latest Next.js + React packages..." -ForegroundColor Cyan
npm install next@latest react@latest react-dom@latest --save

Write-Host "Scaffolding project '$ProjectName' with Next.js 16 defaults..." -ForegroundColor Cyan
npx create-next-app@latest $ProjectName `
  --ts `
  --eslint `
  --tailwind `
  --app `
  --turbopack `
  --src-dir false `
  --import-alias "@/*" `
  --use-npm `
  --yes

Write-Host "Next.js 16 project ready." -ForegroundColor Green
