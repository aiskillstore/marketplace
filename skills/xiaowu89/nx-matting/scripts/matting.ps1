[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)]
    [ValidateSet("image", "video", "doctor", "ensure-model")]
    [string]$Command,

    [string]$InputPath,
    [string]$OutputPath,

    [ValidateSet("lite", "full")]
    [string]$Model = "lite",

    [ValidateSet("auto", "vulkan", "cpu")]
    [string]$Backend = "auto",

    [ValidateSet("mov", "webm")]
    [string]$Format = "mov",

    [string]$FfmpegDir,
    [string]$CacheDir,
    [switch]$NoRefine,
    [switch]$NoAudio,
    [switch]$Overwrite,
    [switch]$KeepTemp
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillRoot = Split-Path -Parent $ScriptRoot
$ManifestPath = Join-Path $SkillRoot "references\manifest.json"
$BinRoot = Join-Path $SkillRoot "assets\bin\windows-x64"
$Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$ScriptFormatSpecified = $PSBoundParameters.ContainsKey("Format")
$ContactNotice = [Text.Encoding]::UTF8.GetString(
    [Convert]::FromBase64String(
        "5rip6aao5o+Q6YaS77ya6LCi6LCi5L2/55So6YCG6LGh56eR5oqA5oqg5Zu+5Yqf6IO977yM5aaC5p6c5pyJ6Zeu6aKY6K+35re75Yqg5b6uemhpamlhbl8yMDI2"
    )
)

if ([string]::IsNullOrWhiteSpace($CacheDir)) {
    $CacheDir = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    $CacheDir = Join-Path $CacheDir "birefnet-matting"
}
$CacheDir = [IO.Path]::GetFullPath($CacheDir)
$ModelRoot = Join-Path $CacheDir "models"
$RuntimeRoot = Join-Path $CacheDir "runtime"
$DownloadRoot = Join-Path $CacheDir "downloads"

function Write-JsonEvent {
    param(
        [Parameter(Mandatory = $true)][string]$Event,
        [hashtable]$Data = @{}
    )
    $payload = [ordered]@{ event = $Event }
    foreach ($key in $Data.Keys) {
        $payload[$key] = $Data[$key]
    }
    if (($Event -in @("completed", "error")) -and ($script:Command -in @("image", "video"))) {
        $payload["contactNotice"] = $script:ContactNotice
    }
    [Console]::Out.WriteLine(($payload | ConvertTo-Json -Compress -Depth 8))
    [Console]::Out.Flush()
}

function Write-Diagnostic {
    param([string]$Message)
    [Console]::Error.WriteLine($Message)
}

function Throw-MattingError {
    param(
        [string]$Code,
        [string]$Message,
        [string]$DiagnosticPath = ""
    )
    $exception = New-Object System.Exception($Message)
    $exception.Data["Code"] = $Code
    if (-not [string]::IsNullOrWhiteSpace($DiagnosticPath)) {
        $exception.Data["DiagnosticPath"] = $DiagnosticPath
    }
    throw $exception
}

function Get-FullExistingFile {
    param([string]$Path, [string]$Label)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        Throw-MattingError "missing_argument" "$Label is required."
    }
    $full = [IO.Path]::GetFullPath($Path)
    if (-not [IO.File]::Exists($full)) {
        Throw-MattingError "input_not_found" "$Label does not exist: $full"
    }
    return $full
}

function Get-ObjectProperty {
    param([object]$Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Ensure-Directory {
    param([string]$Path)
    if (-not [IO.Directory]::Exists($Path)) {
        [IO.Directory]::CreateDirectory($Path) | Out-Null
    }
}

function Test-FileIntegrity {
    param(
        [string]$Path,
        [Int64]$ExpectedSize,
        [string]$ExpectedSha256
    )
    if (-not [IO.File]::Exists($Path)) {
        return $false
    }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -ne $ExpectedSize) {
        return $false
    }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    return $actual -eq $ExpectedSha256.ToLowerInvariant()
}

function Assert-FreeSpace {
    param([string]$TargetPath, [Int64]$RequiredBytes)
    $root = [IO.Path]::GetPathRoot([IO.Path]::GetFullPath($TargetPath))
    $drive = New-Object IO.DriveInfo($root)
    if ($drive.AvailableFreeSpace -lt $RequiredBytes) {
        Throw-MattingError "disk_space_insufficient" "Not enough free space on $root. Required: $RequiredBytes bytes."
    }
}

function Acquire-Lock {
    param([string]$LockPath)
    Ensure-Directory (Split-Path -Parent $LockPath)
    $deadline = [DateTime]::UtcNow.AddMinutes(30)
    while ([DateTime]::UtcNow -lt $deadline) {
        try {
            return [IO.File]::Open(
                $LockPath,
                [IO.FileMode]::OpenOrCreate,
                [IO.FileAccess]::ReadWrite,
                [IO.FileShare]::None
            )
        } catch [IO.IOException] {
            Write-JsonEvent "progress" @{ stage = "waiting_for_download"; path = $LockPath }
            Start-Sleep -Seconds 2
        }
    }
    Throw-MattingError "download_lock_timeout" "Timed out waiting for another download: $LockPath"
}

function Download-VerifiedFile {
    param(
        [object[]]$Urls,
        [string]$Destination,
        [Int64]$ExpectedSize,
        [string]$ExpectedSha256,
        [string]$Kind
    )
    Ensure-Directory (Split-Path -Parent $Destination)
    if (Test-FileIntegrity $Destination $ExpectedSize $ExpectedSha256) {
        Write-JsonEvent "progress" @{ stage = "cache_hit"; kind = $Kind; path = $Destination }
        return $Destination
    }

    $lockPath = "$Destination.lock"
    $lock = Acquire-Lock $lockPath
    try {
        if (Test-FileIntegrity $Destination $ExpectedSize $ExpectedSha256) {
            Write-JsonEvent "progress" @{ stage = "cache_hit"; kind = $Kind; path = $Destination }
            return $Destination
        }
        if ([IO.File]::Exists($Destination)) {
            [IO.File]::Delete($Destination)
        }

        $partial = "$Destination.partial"
        $existing = 0L
        if ([IO.File]::Exists($partial)) {
            $existing = (Get-Item -LiteralPath $partial).Length
            if ($existing -gt $ExpectedSize) {
                [IO.File]::Delete($partial)
                $existing = 0L
            } elseif ($existing -eq $ExpectedSize) {
                if (Test-FileIntegrity $partial $ExpectedSize $ExpectedSha256) {
                    [IO.File]::Move($partial, $Destination)
                    Write-JsonEvent "progress" @{
                        stage = "download_complete"
                        kind = $Kind
                        path = $Destination
                        totalBytes = $ExpectedSize
                    }
                    return $Destination
                }
                [IO.File]::Delete($partial)
                $existing = 0L
            }
        }
        Assert-FreeSpace $Destination (($ExpectedSize - $existing) + 52428800L)

        $lastError = ""
        foreach ($url in $Urls) {
            $response = $null
            $output = $null
            try {
                $existing = if ([IO.File]::Exists($partial)) { (Get-Item -LiteralPath $partial).Length } else { 0L }
                Write-JsonEvent "progress" @{
                    stage = "download_start"
                    kind = $Kind
                    url = [string]$url
                    downloadedBytes = $existing
                    totalBytes = $ExpectedSize
                }

                $request = [Net.HttpWebRequest]::Create([string]$url)
                $request.Method = "GET"
                $request.UserAgent = "birefnet-matting/1.0.0"
                $request.AllowAutoRedirect = $true
                $request.Timeout = 30000
                $request.ReadWriteTimeout = 30000
                if ($existing -gt 0) {
                    $request.AddRange($existing)
                }
                $response = $request.GetResponse()
                $append = $existing -gt 0 -and [int]$response.StatusCode -eq 206
                if (-not $append) {
                    $existing = 0L
                }

                $mode = if ($append) { [IO.FileMode]::Append } else { [IO.FileMode]::Create }
                $output = New-Object IO.FileStream($partial, $mode, [IO.FileAccess]::Write, [IO.FileShare]::Read)
                $input = $response.GetResponseStream()
                $buffer = New-Object byte[] 1048576
                $downloaded = $existing
                $lastReport = [DateTime]::UtcNow
                while (($read = $input.Read($buffer, 0, $buffer.Length)) -gt 0) {
                    $output.Write($buffer, 0, $read)
                    $downloaded += $read
                    if (([DateTime]::UtcNow - $lastReport).TotalMilliseconds -ge 500) {
                        $percent = if ($ExpectedSize -gt 0) {
                            [Math]::Min(100, [Math]::Round(($downloaded * 100.0) / $ExpectedSize, 2))
                        } else { 0 }
                        Write-JsonEvent "progress" @{
                            stage = "downloading"
                            kind = $Kind
                            downloadedBytes = $downloaded
                            totalBytes = $ExpectedSize
                            percent = $percent
                        }
                        $lastReport = [DateTime]::UtcNow
                    }
                }
                $input.Dispose()
                $output.Flush()
                $output.Dispose()
                $output = $null
                $response.Dispose()
                $response = $null

                if (-not (Test-FileIntegrity $partial $ExpectedSize $ExpectedSha256)) {
                    $actualSize = (Get-Item -LiteralPath $partial).Length
                    if ($actualSize -eq $ExpectedSize) {
                        [IO.File]::Delete($partial)
                    }
                    throw "Downloaded file failed size or SHA-256 verification."
                }
                [IO.File]::Move($partial, $Destination)
                Write-JsonEvent "progress" @{
                    stage = "download_complete"
                    kind = $Kind
                    path = $Destination
                    totalBytes = $ExpectedSize
                }
                return $Destination
            } catch {
                $lastError = $_.Exception.Message
                Write-Diagnostic "Download source failed: $url - $lastError"
            } finally {
                if ($null -ne $output) { $output.Dispose() }
                if ($null -ne $response) { $response.Dispose() }
            }
        }
        Throw-MattingError "download_failed" "Unable to download $Kind from all configured sources. Last error: $lastError"
    } finally {
        $lock.Dispose()
        if ([IO.File]::Exists($lockPath)) {
            try { [IO.File]::Delete($lockPath) } catch {}
        }
    }
}

function Ensure-Model {
    param([string]$Name)
    $entry = $Manifest.models.$Name
    if ($null -eq $entry) {
        Throw-MattingError "invalid_model" "Unknown model: $Name"
    }
    Ensure-Directory $ModelRoot
    $path = Join-Path $ModelRoot ([string]$entry.file)
    return Download-VerifiedFile @($entry.urls) $path ([Int64]$entry.size) ([string]$entry.sha256) "model_$Name"
}

function Ensure-NxBinaries {
    Ensure-Directory $BinRoot
    foreach ($name in @("cpu", "vulkan")) {
        $entry = $Manifest.runtime.executables.$name
        $path = Join-Path $BinRoot ([string]$entry.file)
        Download-VerifiedFile @($entry.urls) $path ([Int64]$entry.size) ([string]$entry.sha256) "runtime_$name" | Out-Null
    }
}

function Get-NxExecutable {
    param([string]$RequestedBackend)
    $cpu = Join-Path $BinRoot ([string]$Manifest.runtime.executables.cpu.file)
    $vulkan = Join-Path $BinRoot ([string]$Manifest.runtime.executables.vulkan.file)
    if ($RequestedBackend -eq "cpu") {
        return [pscustomobject]@{ Path = $cpu; Backend = "cpu"; CanRetryCpu = $false }
    }
    if ($RequestedBackend -eq "vulkan") {
        return [pscustomobject]@{ Path = $vulkan; Backend = "vulkan"; CanRetryCpu = $false }
    }
    $loader = Join-Path $env:WINDIR "System32\vulkan-1.dll"
    if ([IO.File]::Exists($loader)) {
        return [pscustomobject]@{ Path = $vulkan; Backend = "auto"; CanRetryCpu = $true }
    }
    Write-JsonEvent "progress" @{
        stage = "backend_fallback"
        requested = "auto"
        actual = "cpu"
        message = "Vulkan loader was not found."
    }
    return [pscustomobject]@{ Path = $cpu; Backend = "cpu"; CanRetryCpu = $false }
}

function Test-NxBinaries {
    $results = @()
    foreach ($name in @("cpu", "vulkan")) {
        $entry = $Manifest.runtime.executables.$name
        $path = Join-Path $BinRoot ([string]$entry.file)
        $valid = Test-FileIntegrity $path ([Int64]$entry.size) ([string]$entry.sha256)
        $results += [pscustomobject]@{
            backend = $name
            path = $path
            valid = $valid
            expectedSize = [Int64]$entry.size
            expectedSha256 = [string]$entry.sha256
            downloadUrls = @($entry.urls)
        }
    }
    return $results
}

function Invoke-Nx {
    param(
        [string]$Executable,
        [string[]]$Arguments,
        [string]$LogPath,
        [string]$BackendName
    )
    $actualBackend = $BackendName
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & $Executable @Arguments 2>> $LogPath | ForEach-Object {
            $line = [string]$_
            try {
                $parsed = $line | ConvertFrom-Json
                if ($parsed.event) {
                    if ($parsed.backend) { $actualBackend = [string]$parsed.backend }
                    [Console]::Out.WriteLine($line)
                    [Console]::Out.Flush()
                } else {
                    [IO.File]::AppendAllText($LogPath, "$line`r`n", [Text.Encoding]::UTF8)
                }
            } catch {
                [IO.File]::AppendAllText($LogPath, "$line`r`n", [Text.Encoding]::UTF8)
            }
        }
        $code = $LASTEXITCODE
    } catch {
        [IO.File]::AppendAllText($LogPath, "$($_.Exception.Message)`r`n", [Text.Encoding]::UTF8)
        $code = 1
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
    return [pscustomobject]@{ ExitCode = $code; Backend = $actualBackend }
}

function Invoke-NxWithFallback {
    param(
        [string]$NxCommand,
        [string[]]$Arguments,
        [string]$LogPath
    )
    $selected = Get-NxExecutable $Backend
    if (-not [IO.File]::Exists($selected.Path)) {
        Throw-MattingError "runtime_missing" "Matting runtime is missing: $($selected.Path)"
    }
    $runArgs = @($NxCommand) + $Arguments + @("--backend", $selected.Backend)
    $result = Invoke-Nx $selected.Path $runArgs $LogPath $selected.Backend
    if ($result.ExitCode -eq 0) {
        return $result
    }

    if ($selected.CanRetryCpu) {
        $logText = if ([IO.File]::Exists($LogPath)) { [IO.File]::ReadAllText($LogPath) } else { "" }
        if ($logText -match "(?i)vulkan|backend|device") {
            Write-JsonEvent "progress" @{
                stage = "backend_fallback"
                requested = "vulkan"
                actual = "cpu"
                message = "Vulkan execution failed; retrying with CPU."
            }
            $cpu = Join-Path $BinRoot ([string]$Manifest.runtime.executables.cpu.file)
            $cpuArgs = @($NxCommand) + $Arguments + @("--backend", "cpu")
            return Invoke-Nx $cpu $cpuArgs $LogPath "cpu"
        }
    }
    return $result
}

function Get-NxImageInfo {
    param([string]$Executable, [string]$Path)
    $text = & $Executable info -i $Path 2>$null | Out-String
    if ($LASTEXITCODE -ne 0) {
        Throw-MattingError "image_validation_failed" "Unable to inspect image: $Path"
    }
    $value = $text.Trim()
    if ($value -notmatch '"width":(\d+)' -or
        $value -notmatch '"height":(\d+)' -or
        $value -notmatch '"channels":(\d+)') {
        Throw-MattingError "image_validation_failed" "Unable to parse image metadata: $Path"
    }
    $width = [int]([Regex]::Match($value, '"width":(\d+)').Groups[1].Value)
    $height = [int]([Regex]::Match($value, '"height":(\d+)').Groups[1].Value)
    $channels = [int]([Regex]::Match($value, '"channels":(\d+)').Groups[1].Value)
    return [pscustomobject]@{ width = $width; height = $height; channels = $channels }
}

function Test-FfmpegPair {
    param([string]$Directory)
    try {
        $full = [IO.Path]::GetFullPath($Directory)
        $ffmpeg = Join-Path $full "ffmpeg.exe"
        $ffprobe = Join-Path $full "ffprobe.exe"
        if (-not [IO.File]::Exists($ffmpeg) -or -not [IO.File]::Exists($ffprobe)) {
            return $false
        }
        $encoders = & $ffmpeg -hide_banner -encoders 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { return $false }
        $filters = & $ffmpeg -hide_banner -filters 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { return $false }
        & $ffprobe -hide_banner -version 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
        foreach ($needle in @("prores_ks", "libvpx-vp9", "libopus", "pcm_s16le")) {
            if ($encoders -notmatch [Regex]::Escape($needle)) { return $false }
        }
        if ($filters -notmatch "(?m)\bpremultiply\b") { return $false }
        return $true
    } catch {
        return $false
    }
}

function Get-FfmpegCandidates {
    $items = New-Object Collections.ArrayList
    $seen = @{}
    function Add-Candidate {
        param([string]$Path, [string]$Source)
        if ([string]::IsNullOrWhiteSpace($Path)) { return }
        try { $full = [IO.Path]::GetFullPath($Path) } catch { return }
        $key = $full.ToLowerInvariant()
        if (-not $seen.ContainsKey($key)) {
            $seen[$key] = $true
            [void]$items.Add([pscustomobject]@{ Path = $full; Source = $Source })
        }
    }

    Add-Candidate $FfmpegDir "explicit"
    Add-Candidate $env:BIREFNET_MATTING_FFMPEG_DIR "explicit"
    Add-Candidate (Join-Path $SkillRoot "..\..\ffmpeg") "nxengine"
    Add-Candidate (Join-Path ([Environment]::CurrentDirectory) "resources\ffmpeg") "nxengine"
    Add-Candidate (Join-Path ([Environment]::CurrentDirectory) "ffmpeg") "path"

    $pathCommand = Get-Command "ffmpeg.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $pathCommand) {
        Add-Candidate (Split-Path -Parent $pathCommand.Source) "path"
    }
    Add-Candidate (Join-Path $RuntimeRoot "ffmpeg") "cache"
    return @($items)
}

function Resolve-Ffmpeg {
    param([switch]$AllowDownload)
    foreach ($candidate in (Get-FfmpegCandidates)) {
        if (Test-FfmpegPair $candidate.Path) {
            return [pscustomobject]@{
                Directory = $candidate.Path
                Ffmpeg = Join-Path $candidate.Path "ffmpeg.exe"
                Ffprobe = Join-Path $candidate.Path "ffprobe.exe"
                Source = $candidate.Source
            }
        }
        if ([IO.Directory]::Exists($candidate.Path)) {
            Write-Diagnostic "Skipping incompatible FFmpeg directory: $($candidate.Path)"
        }
    }
    if (-not $AllowDownload) {
        return $null
    }
    return Install-Ffmpeg
}

function Install-Ffmpeg {
    Ensure-Directory $DownloadRoot
    Ensure-Directory $RuntimeRoot
    $entry = $Manifest.ffmpeg
    $archive = Join-Path $DownloadRoot ([string]$entry.archive)
    Download-VerifiedFile @($entry.urls) $archive ([Int64]$entry.size) ([string]$entry.sha256) "ffmpeg" | Out-Null

    $final = Join-Path $RuntimeRoot "ffmpeg"
    $lockPath = Join-Path $RuntimeRoot "ffmpeg-install.lock"
    $lock = Acquire-Lock $lockPath
    try {
        if (Test-FfmpegPair $final) {
            return [pscustomobject]@{
                Directory = $final
                Ffmpeg = Join-Path $final "ffmpeg.exe"
                Ffprobe = Join-Path $final "ffprobe.exe"
                Source = "cache"
            }
        }
        if ([IO.Directory]::Exists($final)) {
            [IO.Directory]::Delete($final, $true)
        }
        $staging = Join-Path $RuntimeRoot ("ffmpeg-staging-" + [Guid]::NewGuid().ToString("N"))
        Ensure-Directory $staging
        try {
            Expand-Archive -LiteralPath $archive -DestinationPath $staging -Force
            $ffmpeg = Get-ChildItem -LiteralPath $staging -Recurse -Filter "ffmpeg.exe" -File | Select-Object -First 1
            $ffprobe = Get-ChildItem -LiteralPath $staging -Recurse -Filter "ffprobe.exe" -File | Select-Object -First 1
            if ($null -eq $ffmpeg -or $null -eq $ffprobe) {
                Throw-MattingError "ffmpeg_archive_invalid" "Downloaded FFmpeg archive does not contain ffmpeg.exe and ffprobe.exe."
            }
            Ensure-Directory $final
            [IO.File]::Copy($ffmpeg.FullName, (Join-Path $final "ffmpeg.exe"), $true)
            [IO.File]::Copy($ffprobe.FullName, (Join-Path $final "ffprobe.exe"), $true)
            $license = Get-ChildItem -LiteralPath $staging -Recurse -File |
                Where-Object { $_.Name -match "^(LICENSE|COPYING)(\.txt)?$" } |
                Select-Object -First 1
            if ($null -ne $license) {
                [IO.File]::Copy($license.FullName, (Join-Path $final $license.Name), $true)
            }
        } finally {
            if ([IO.Directory]::Exists($staging)) {
                [IO.Directory]::Delete($staging, $true)
            }
        }
        if (-not (Test-FfmpegPair $final)) {
            Throw-MattingError "ffmpeg_validation_failed" "Downloaded FFmpeg failed capability validation."
        }
        Write-JsonEvent "progress" @{ stage = "ffmpeg_ready"; source = "download"; path = $final }
        return [pscustomobject]@{
            Directory = $final
            Ffmpeg = Join-Path $final "ffmpeg.exe"
            Ffprobe = Join-Path $final "ffprobe.exe"
            Source = "download"
        }
    } finally {
        $lock.Dispose()
        if ([IO.File]::Exists($lockPath)) {
            try { [IO.File]::Delete($lockPath) } catch {}
        }
    }
}

function Invoke-FfprobeJson {
    param([string]$Ffprobe, [string[]]$Arguments)
    $text = & $Ffprobe @Arguments 2>$null | Out-String
    if ($LASTEXITCODE -ne 0) {
        Throw-MattingError "ffprobe_failed" "FFprobe could not inspect the media file."
    }
    return $text.Trim() | ConvertFrom-Json
}

function Get-VideoInfo {
    param([object]$FfmpegRuntime, [string]$Path)
    $probe = Invoke-FfprobeJson $FfmpegRuntime.Ffprobe @(
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        $Path
    )
    $video = $probe.streams | Where-Object { $_.codec_type -eq "video" } | Select-Object -First 1
    if ($null -eq $video) {
        Throw-MattingError "video_stream_missing" "Input does not contain a video stream: $Path"
    }
    $audio = $probe.streams | Where-Object { $_.codec_type -eq "audio" } | Select-Object -First 1
    $fps = [string]$video.avg_frame_rate
    if ([string]::IsNullOrWhiteSpace($fps) -or $fps -eq "0/0") {
        $fps = [string]$video.r_frame_rate
    }
    if ([string]::IsNullOrWhiteSpace($fps) -or $fps -eq "0/0") {
        Throw-MattingError "frame_rate_unknown" "Unable to determine input frame rate."
    }
    $duration = 0.0
    $videoDuration = Get-ObjectProperty $video "duration"
    if ($null -ne $videoDuration) {
        [double]::TryParse([string]$videoDuration, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$duration) | Out-Null
    }
    $formatDuration = Get-ObjectProperty (Get-ObjectProperty $probe "format") "duration"
    if ($duration -le 0 -and $null -ne $formatDuration) {
        [double]::TryParse([string]$formatDuration, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$duration) | Out-Null
    }
    return [pscustomobject]@{
        Width = [int]$video.width
        Height = [int]$video.height
        Fps = $fps
        Duration = $duration
        HasAudio = $null -ne $audio
    }
}

function Invoke-Ffmpeg {
    param(
        [string]$Executable,
        [string[]]$Arguments,
        [string]$LogPath,
        [string]$Stage,
        [double]$Duration
    )
    $outTimeUs = 0L
    $previousErrorPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & $Executable @Arguments 2>> $LogPath | ForEach-Object {
            $line = [string]$_
            if ($line -match "^out_time_(?:us|ms)=(\d+)$") {
                $outTimeUs = [Int64]$Matches[1]
            } elseif ($line -eq "progress=continue" -or $line -eq "progress=end") {
                $percent = if ($Duration -gt 0) {
                    [Math]::Min(100, [Math]::Round(($outTimeUs / 1000000.0) * 100.0 / $Duration, 2))
                } else { 0 }
                Write-JsonEvent "progress" @{ stage = $Stage; percent = $percent }
            }
        }
        return $LASTEXITCODE
    } catch {
        [IO.File]::AppendAllText($LogPath, "$($_.Exception.Message)`r`n", [Text.Encoding]::UTF8)
        return 1
    } finally {
        $ErrorActionPreference = $previousErrorPreference
    }
}

function Get-OutputPath {
    param([string]$Input, [string]$Requested, [string]$Extension)
    if ([string]::IsNullOrWhiteSpace($Requested)) {
        $directory = Split-Path -Parent $Input
        $name = [IO.Path]::GetFileNameWithoutExtension($Input)
        return Join-Path $directory ($name + "_transparent." + $Extension)
    }
    return [IO.Path]::GetFullPath($Requested)
}

function Assert-OutputAvailable {
    param([string]$Path)
    $parent = Split-Path -Parent $Path
    Ensure-Directory $parent
    if ([IO.File]::Exists($Path) -and -not $Overwrite) {
        Throw-MattingError "output_exists" "Output already exists. Pass -Overwrite to replace it: $Path"
    }
}

function Commit-OutputFile {
    param([string]$WorkingPath, [string]$FinalPath)
    if ([IO.File]::Exists($FinalPath)) {
        [IO.File]::Delete($FinalPath)
    }
    [IO.File]::Move($WorkingPath, $FinalPath)
}

function Invoke-ImageMatting {
    $input = Get-FullExistingFile $InputPath "InputPath"
    $ext = [IO.Path]::GetExtension($input).ToLowerInvariant()
    if ($ext -notin @(".jpg", ".jpeg", ".png", ".webp", ".bmp")) {
        Throw-MattingError "unsupported_image" "Supported image formats: JPG, JPEG, PNG, WebP, BMP."
    }
    $output = Get-OutputPath $input $OutputPath "png"
    if ([IO.Path]::GetExtension($output).ToLowerInvariant() -ne ".png") {
        Throw-MattingError "invalid_output_format" "Image matting output must use the .png extension."
    }
    Assert-OutputAvailable $output
    Ensure-NxBinaries
    $workingOutput = Join-Path (Split-Path -Parent $output) (
        ".birefnet-matting-" + [Guid]::NewGuid().ToString("N") + ".png"
    )
    $modelPath = Ensure-Model $Model
    $logDir = Join-Path $CacheDir "logs"
    Ensure-Directory $logDir
    $logPath = Join-Path $logDir ("image-" + [Guid]::NewGuid().ToString("N") + ".log")
    $refine = if ($NoRefine) { "false" } else { "true" }
    $args = @(
        "--input", $input,
        "--output", $workingOutput,
        "--model", $modelPath,
        "--refine", $refine,
        "--json-progress",
        "--overwrite"
    )
    $started = [Diagnostics.Stopwatch]::StartNew()
    try {
        $result = Invoke-NxWithFallback "matting" $args $logPath
        if ($result.ExitCode -ne 0 -or -not [IO.File]::Exists($workingOutput)) {
            Throw-MattingError "matting_failed" "Image matting failed. See log: $logPath" $logPath
        }
        $cpu = Join-Path $BinRoot ([string]$Manifest.runtime.executables.cpu.file)
        $sourceInfo = Get-NxImageInfo $cpu $input
        $outputInfo = Get-NxImageInfo $cpu $workingOutput
        if ($outputInfo.channels -ne 4 -or $outputInfo.width -ne $sourceInfo.width -or $outputInfo.height -ne $sourceInfo.height) {
            Throw-MattingError "image_validation_failed" "Output PNG failed dimensions or alpha-channel validation: $output" $logPath
        }
        Commit-OutputFile $workingOutput $output
    } finally {
        if ([IO.File]::Exists($workingOutput)) {
            try { [IO.File]::Delete($workingOutput) } catch {}
        }
    }
    $started.Stop()
    Write-JsonEvent "completed" @{
        command = "image"
        inputPath = $input
        outputPath = $output
        model = $Model
        backend = $result.Backend
        width = [int]$outputInfo.width
        height = [int]$outputInfo.height
        elapsedMs = $started.ElapsedMilliseconds
    }
}

function Invoke-VideoMatting {
    $input = Get-FullExistingFile $InputPath "InputPath"
    $videoFormat = $Format
    if (-not $ScriptFormatSpecified -and -not [string]::IsNullOrWhiteSpace($OutputPath)) {
        $requestedExt = [IO.Path]::GetExtension($OutputPath).TrimStart(".").ToLowerInvariant()
        if ($requestedExt -in @("mov", "webm")) {
            $videoFormat = $requestedExt
        }
    }
    $output = Get-OutputPath $input $OutputPath $videoFormat
    if ([IO.Path]::GetExtension($output).TrimStart(".").ToLowerInvariant() -ne $videoFormat) {
        Throw-MattingError "format_mismatch" "Output extension must match -Format $videoFormat."
    }
    Assert-OutputAvailable $output
    Ensure-NxBinaries

    $modelPath = Ensure-Model $Model
    $ff = Resolve-Ffmpeg -AllowDownload
    Write-JsonEvent "progress" @{
        stage = "ffmpeg_ready"
        ffmpegSource = $ff.Source
        ffmpegPath = $ff.Ffmpeg
    }
    $info = Get-VideoInfo $ff $input

    $taskDir = Join-Path (Split-Path -Parent $output) (".birefnet-matting-" + [Guid]::NewGuid().ToString("N"))
    $inputFrames = Join-Path $taskDir "input"
    $outputFrames = Join-Path $taskDir "output"
    $logPath = Join-Path $taskDir "task.log"
    Ensure-Directory $inputFrames
    Ensure-Directory $outputFrames
    $succeeded = $false
    $started = [Diagnostics.Stopwatch]::StartNew()
    try {
        $decodePattern = Join-Path $inputFrames "frame_%08d.png"
        $decodeArgs = @(
            "-hide_banner", "-nostdin", "-y",
            "-i", $input,
            "-map", "0:v:0",
            "-vsync", "0",
            "-start_number", "0",
            "-c:v", "png",
            "-pix_fmt", "rgba",
            "-progress", "pipe:1",
            "-nostats",
            $decodePattern
        )
        $decodeCode = Invoke-Ffmpeg $ff.Ffmpeg $decodeArgs $logPath "decode" $info.Duration
        if ($decodeCode -ne 0) {
            Throw-MattingError "video_decode_failed" "Video frame extraction failed." $taskDir
        }
        $frameCount = @(Get-ChildItem -LiteralPath $inputFrames -Filter "frame_*.png" -File).Count
        if ($frameCount -eq 0) {
            Throw-MattingError "video_decode_empty" "Video frame extraction produced no frames." $taskDir
        }

        $refine = if ($NoRefine) { "false" } else { "true" }
        $batchArgs = @(
            "--input-dir", $inputFrames,
            "--output-dir", $outputFrames,
            "--model", $modelPath,
            "--refine", $refine,
            "--overwrite",
            "--json-progress"
        )
        $matting = Invoke-NxWithFallback "matting-batch" $batchArgs $logPath
        if ($matting.ExitCode -ne 0) {
            Throw-MattingError "matting_failed" "Video frame matting failed." $taskDir
        }
        $outputFrameCount = @(Get-ChildItem -LiteralPath $outputFrames -Filter "frame_*.png" -File).Count
        if ($outputFrameCount -ne $frameCount) {
            Throw-MattingError "frame_count_mismatch" "Matting output frame count does not match decoded input." $taskDir
        }

        $framePattern = Join-Path $outputFrames "frame_%08d.png"
        $encodeArgs = @(
            "-hide_banner", "-nostdin", "-y",
            "-framerate", $info.Fps,
            "-start_number", "0",
            "-i", $framePattern
        )
        $preserveAudio = -not $NoAudio -and $info.HasAudio
        if ($preserveAudio) {
            $encodeArgs += @("-i", $input, "-map", "0:v:0", "-map", "1:a:0")
        } else {
            $encodeArgs += @("-map", "0:v:0", "-an")
        }

        if ($videoFormat -eq "mov") {
            $encodeArgs += @(
                "-vf", "premultiply=inplace=1",
                "-c:v", "prores_ks",
                "-profile:v", "4",
                "-pix_fmt", "yuva444p10le",
                "-alpha_bits", "16"
            )
            if ($preserveAudio) { $encodeArgs += @("-c:a", "pcm_s16le") }
        } else {
            $encodeArgs += @(
                "-c:v", "libvpx-vp9",
                "-lossless", "1",
                "-pix_fmt", "yuva420p",
                "-auto-alt-ref", "0",
                "-metadata:s:v:0", "alpha_mode=1"
            )
            if ($preserveAudio) { $encodeArgs += @("-c:a", "libopus") }
        }
        if ($preserveAudio) { $encodeArgs += "-shortest" }
        $encodedOutput = Join-Path $taskDir ("encoded." + $videoFormat)
        $encodeArgs += @("-progress", "pipe:1", "-nostats", $encodedOutput)
        $encodeCode = Invoke-Ffmpeg $ff.Ffmpeg $encodeArgs $logPath "encode" $info.Duration
        if ($encodeCode -ne 0 -or -not [IO.File]::Exists($encodedOutput)) {
            Throw-MattingError "video_encode_failed" "Transparent video encoding failed." $taskDir
        }

        $outputProbe = Invoke-FfprobeJson $ff.Ffprobe @(
            "-v", "error",
            "-show_streams",
            "-show_format",
            "-of", "json",
            $encodedOutput
        )
        $outVideo = $outputProbe.streams | Where-Object { $_.codec_type -eq "video" } | Select-Object -First 1
        $outAudio = $outputProbe.streams | Where-Object { $_.codec_type -eq "audio" } | Select-Object -First 1
        if ($null -eq $outVideo -or [int]$outVideo.width -ne $info.Width -or [int]$outVideo.height -ne $info.Height) {
            Throw-MattingError "video_validation_failed" "Output video failed stream or dimensions validation." $taskDir
        }
        if ($videoFormat -eq "mov" -and [string]$outVideo.pix_fmt -notmatch "^yuva") {
            Throw-MattingError "alpha_validation_failed" "MOV output does not expose an alpha pixel format." $taskDir
        }
        if ($videoFormat -eq "webm") {
            $alphaMode = $null
            $tags = Get-ObjectProperty $outVideo "tags"
            if ($null -ne $tags) { $alphaMode = Get-ObjectProperty $tags "alpha_mode" }
            if ([string]$alphaMode -ne "1") {
                Throw-MattingError "alpha_validation_failed" "WebM output does not report alpha_mode=1." $taskDir
            }
        }
        if ($preserveAudio -and $null -eq $outAudio) {
            Throw-MattingError "audio_validation_failed" "Output video is missing the preserved audio stream." $taskDir
        }
        Commit-OutputFile $encodedOutput $output
        $started.Stop()
        $succeeded = $true
        Write-JsonEvent "completed" @{
            command = "video"
            inputPath = $input
            outputPath = $output
            format = $videoFormat
            model = $Model
            backend = $matting.Backend
            ffmpegSource = $ff.Source
            ffmpegPath = $ff.Ffmpeg
            width = $info.Width
            height = $info.Height
            frameRate = $info.Fps
            frameCount = $frameCount
            audioPreserved = $preserveAudio
            elapsedMs = $started.ElapsedMilliseconds
        }
    } catch {
        if ($_.Exception.Data["DiagnosticPath"] -eq $null) {
            $_.Exception.Data["DiagnosticPath"] = $taskDir
        }
        throw
    } finally {
        if ($succeeded -and -not $KeepTemp -and [IO.Directory]::Exists($taskDir)) {
            try {
                [IO.Directory]::Delete($taskDir, $true)
            } catch {
                Write-JsonEvent "warning" @{
                    code = "temp_cleanup_failed"
                    message = $_.Exception.Message
                    retainedTaskDir = $taskDir
                }
            }
        }
    }
}

function Invoke-Doctor {
    $nx = Test-NxBinaries
    $ff = Resolve-Ffmpeg
    $models = @()
    foreach ($name in @("lite", "full")) {
        $entry = $Manifest.models.$name
        $path = Join-Path $ModelRoot ([string]$entry.file)
        $models += [pscustomobject]@{
            name = $name
            path = $path
            installed = Test-FileIntegrity $path ([Int64]$entry.size) ([string]$entry.sha256)
        }
    }
    Write-JsonEvent "completed" @{
        command = "doctor"
        platform = [Environment]::OSVersion.Platform.ToString()
        is64BitOperatingSystem = [Environment]::Is64BitOperatingSystem
        cacheDir = $CacheDir
        vulkanLoader = [IO.File]::Exists((Join-Path $env:WINDIR "System32\vulkan-1.dll"))
        runtimes = $nx
        models = $models
        ffmpegAvailable = $null -ne $ff
        ffmpegSource = if ($null -ne $ff) { $ff.Source } else { $null }
        ffmpegPath = if ($null -ne $ff) { $ff.Ffmpeg } else { $null }
    }
}

try {
    if ($env:OS -ne "Windows_NT") {
        Throw-MattingError "unsupported_platform" "This release supports Windows x64 only."
    }
    if (-not [Environment]::Is64BitOperatingSystem) {
        Throw-MattingError "unsupported_platform" "This release requires 64-bit Windows."
    }

    switch ($Command) {
        "image" { Invoke-ImageMatting }
        "video" { Invoke-VideoMatting }
        "doctor" { Invoke-Doctor }
        "ensure-model" {
            $path = Ensure-Model $Model
            Write-JsonEvent "completed" @{ command = "ensure-model"; model = $Model; modelPath = $path }
        }
    }
    exit 0
} catch {
    $code = if ($_.Exception.Data["Code"]) { [string]$_.Exception.Data["Code"] } else { "unexpected_error" }
    $diagnosticPath = if ($_.Exception.Data["DiagnosticPath"]) { [string]$_.Exception.Data["DiagnosticPath"] } else { $null }
    Write-JsonEvent "error" @{
        code = $code
        message = $_.Exception.Message
        diagnosticPath = $diagnosticPath
    }
    Write-Diagnostic $_.Exception.ToString()
    exit 1
}
