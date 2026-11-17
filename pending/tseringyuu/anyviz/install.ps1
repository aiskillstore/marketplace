$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0

$Repository = "TseringYuu/anyviz"
$ArchiveUrl = "https://github.com/$Repository/archive/refs/heads/main.zip"
$AnyvizUserHome = if ($env:ANYVIZ_HOME) { $env:ANYVIZ_HOME } else { $env:USERPROFILE }
$SourceRoot = $env:ANYVIZ_SOURCE_DIR
$DetectCommands = $env:ANYVIZ_DETECT_COMMANDS -ne "0"
$TempRoot = $null
$script:InstallCount = 0

function Fail([string]$Message) {
    throw "anyviz: $Message"
}

function Install-AnyvizSkill([string]$AgentName, [string]$Target) {
    $parent = Split-Path -Parent $Target
    $token = [Guid]::NewGuid().ToString("N")
    $staging = Join-Path $parent ".anyviz-install-$token"
    $backup = Join-Path $parent ".anyviz-backup-$token"
    $preservedBackup = $null

    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    New-Item -ItemType Directory -Force -Path $staging | Out-Null

    try {
        Copy-Item (Join-Path $SourceRoot "SKILL.md") (Join-Path $staging "SKILL.md")

        foreach ($directory in @("aesthetics", "adapters", "guides", "templates", "scripts", "examples")) {
            $sourceDirectory = Join-Path $SourceRoot $directory
            if (Test-Path $sourceDirectory) {
                Copy-Item $sourceDirectory (Join-Path $staging $directory) -Recurse
            }
        }

        $assetTarget = Join-Path $staging "assets"
        New-Item -ItemType Directory -Force -Path $assetTarget | Out-Null
        foreach ($asset in @("banner.svg", "wordmark.svg")) {
            $sourceAsset = Join-Path (Join-Path $SourceRoot "assets") $asset
            if (Test-Path $sourceAsset) {
                Copy-Item $sourceAsset (Join-Path $assetTarget $asset)
            }
        }
        "https://github.com/$Repository" | Set-Content -Encoding ASCII (Join-Path $staging ".anyviz-source")

        if (Test-Path $Target) {
            $targetItem = Get-Item $Target -Force
            if (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                Remove-Item $staging -Recurse -Force
                Write-Host "linked     $AgentName  $Target"
                return
            }

            if (Test-Path (Join-Path $Target ".anyviz-source")) {
                Move-Item $Target $backup
            }
            else {
                $preservedBackup = Join-Path $parent ("anyviz.backup-" + (Get-Date -Format "yyyyMMddHHmmss"))
                while (Test-Path $preservedBackup) {
                    $preservedBackup += "-1"
                }
                Move-Item $Target $preservedBackup
                Write-Host "backed up $AgentName  $preservedBackup"
            }
        }

        try {
            Move-Item $staging $Target
        }
        catch {
            if (Test-Path $staging) {
                Remove-Item $staging -Recurse -Force
            }
            if (Test-Path $backup) {
                Move-Item $backup $Target
            }
            elseif ($preservedBackup -and (Test-Path $preservedBackup)) {
                Move-Item $preservedBackup $Target
            }
            throw
        }
        if (Test-Path $backup) {
            Remove-Item $backup -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        if (Test-Path $staging) {
            Remove-Item $staging -Recurse -Force
        }
        Fail "installation failed for $AgentName`: $($_.Exception.Message)"
    }

    $script:InstallCount += 1
    Write-Host "installed  $AgentName  $Target"
}

function Install-IfDetected(
    [string]$AgentName,
    [string]$Marker,
    [string]$Target,
    [string]$CommandName
) {
    $commandFound = $false
    if ($DetectCommands -and $CommandName) {
        $commandFound = $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
    }
    if ((Test-Path $Marker) -or $commandFound) {
        Install-AnyvizSkill $AgentName $Target
    }
}

if (-not $AnyvizUserHome) {
    Fail "cannot determine user home directory"
}

try {
    if ($SourceRoot) {
        if (-not (Test-Path (Join-Path $SourceRoot "SKILL.md"))) {
            Fail "SKILL.md not found in $SourceRoot"
        }
    }
    else {
        $TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("anyviz-" + [Guid]::NewGuid().ToString("N"))
        $archivePath = Join-Path $TempRoot "anyviz.zip"
        $extractRoot = Join-Path $TempRoot "extract"
        New-Item -ItemType Directory -Force -Path $extractRoot | Out-Null

        Invoke-WebRequest -UseBasicParsing -Uri $ArchiveUrl -OutFile $archivePath
        Expand-Archive -Path $archivePath -DestinationPath $extractRoot -Force
        $sourceDirectory = Get-ChildItem -Path $extractRoot -Directory | Select-Object -First 1
        if (-not $sourceDirectory) {
            Fail "archive extraction failed"
        }
        $SourceRoot = $sourceDirectory.FullName
        if (-not (Test-Path (Join-Path $SourceRoot "SKILL.md"))) {
            Fail "archive extraction failed"
        }
    }

    # Shared Agent Skills path for Codex, Cursor, OpenCode, OpenClaw, Cline,
    # Kimi Code CLI, Warp, Zed, and other compatible agents.
    Install-AnyvizSkill "Universal agents" (Join-Path $AnyvizUserHome ".agents/skills/anyviz")

    $agents = @(
        @("Claude Code", ".claude", ".claude/skills/anyviz", "claude"),
        @("Hermes Agent", ".hermes", ".hermes/skills/anyviz", "hermes"),
        @("Gemini CLI", ".gemini", ".gemini/skills/anyviz", "gemini"),
        @("GitHub Copilot", ".copilot", ".copilot/skills/anyviz", "copilot"),
        @("Windsurf", ".codeium/windsurf", ".codeium/windsurf/skills/anyviz", "windsurf"),
        @("Goose", ".config/goose", ".config/goose/skills/anyviz", "goose"),
        @("Continue", ".continue", ".continue/skills/anyviz", "cn"),
        @("Kiro CLI", ".kiro", ".kiro/skills/anyviz", "kiro-cli"),
        @("OpenHands", ".openhands", ".openhands/skills/anyviz", "openhands"),
        @("Qwen Code", ".qwen", ".qwen/skills/anyviz", "qwen"),
        @("Roo Code", ".roo", ".roo/skills/anyviz", "roo"),
        @("Trae", ".trae", ".trae/skills/anyviz", "trae"),
        @("Droid", ".factory", ".factory/skills/anyviz", "droid"),
        @("Junie", ".junie", ".junie/skills/anyviz", "junie"),
        @("Kilo Code", ".kilocode", ".kilocode/skills/anyviz", "kilo")
    )

    foreach ($agent in $agents) {
        Install-IfDetected $agent[0] (Join-Path $AnyvizUserHome $agent[1]) (Join-Path $AnyvizUserHome $agent[2]) $agent[3]
    }

    Write-Host "anyviz ready in $script:InstallCount skill root(s). Restart agents that were already running."
}
finally {
    if ($TempRoot -and (Test-Path $TempRoot)) {
        Remove-Item $TempRoot -Recurse -Force
    }
}
