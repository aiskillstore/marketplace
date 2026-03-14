param(
  [string]$AppPath = "D:\DBdesigner",
  [string]$BindHost = "127.0.0.1",
  [int]$Port = 3000,
  [string]$WorkspacePath = "",
  [switch]$OpenBrowser = $true
)

$ErrorActionPreference = "Stop"

function Test-DbdesignerUrl {
  param([string]$Url)

  try {
    $null = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
    return $true
  } catch {
    return $false
  }
}

if (-not (Test-Path -LiteralPath $AppPath)) {
  throw "DBdesigner directory not found: $AppPath"
}

$serverFile = Join-Path $AppPath "server.js"
if (-not (Test-Path -LiteralPath $serverFile)) {
  throw "server.js not found under: $AppPath"
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
  throw "Node.js is not available in PATH. Install Node 18+ first."
}

$url = "http://${BindHost}:${Port}"
$workspacePathToUse = if ([string]::IsNullOrWhiteSpace($WorkspacePath)) {
  (Get-Location).Path
} else {
  $WorkspacePath
}
$workspaceNameToUse = if ([string]::IsNullOrWhiteSpace($workspacePathToUse)) {
  ""
} else {
  Split-Path -Path $workspacePathToUse -Leaf
}
$launchUrl = $url
if (-not [string]::IsNullOrWhiteSpace($workspacePathToUse)) {
  $encodedWorkspacePath = [System.Uri]::EscapeDataString($workspacePathToUse)
  $encodedWorkspaceName = [System.Uri]::EscapeDataString($workspaceNameToUse)
  $launchUrl = "${url}/?workspacePath=${encodedWorkspacePath}&workspaceName=${encodedWorkspaceName}"
}
$startedProcess = $null
$reusedExisting = Test-DbdesignerUrl -Url $url

if (-not $reusedExisting) {
  $startedProcess = Start-Process -FilePath $node.Source -ArgumentList @("server.js") -WorkingDirectory $AppPath -PassThru -WindowStyle Normal

  $deadline = (Get-Date).AddSeconds(20)
  do {
    Start-Sleep -Milliseconds 500

    if ($startedProcess.HasExited) {
      throw "DBdesigner server exited early with code $($startedProcess.ExitCode)."
    }
  } until ((Test-DbdesignerUrl -Url $url) -or (Get-Date) -ge $deadline)

  if (-not (Test-DbdesignerUrl -Url $url)) {
    throw "DBdesigner server did not become ready within 20 seconds: $url"
  }
}

if ($OpenBrowser) {
  Start-Process $launchUrl | Out-Null
}

[pscustomobject]@{
  appPath = $AppPath
  url = $url
  launchUrl = $launchUrl
  workspacePath = $workspacePathToUse
  reusedExisting = $reusedExisting
  status = if ($reusedExisting) { "reused" } else { "started" }
  statusMessage = if ($reusedExisting) { "DB Craft service already running; reusing existing service." } else { "DB Craft service was not running; started a new service." }
  pid = if ($startedProcess) { $startedProcess.Id } else { $null }
}
