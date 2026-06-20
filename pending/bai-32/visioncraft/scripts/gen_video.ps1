# =====================================================================
# VisionCraft - Agnes Video Generation Script
# =====================================================================
# Generates videos via the Agnes Video V2.0 API.
# Defaults: 1920x1080 @ 60fps, 241 frames (~4.0s ultra-smooth).
#
# USAGE
#   # Text-to-video
#   .\scripts\gen_video.ps1 -Prompt "a cat walking on the beach at sunset"
#
#   # Image-to-video
#   .\scripts\gen_video.ps1 -Prompt "the woman turns to camera" `
#     -Image "https://example.com/photo.png"
#
#   # Multi-image (multiple references)
#   .\scripts\gen_video.ps1 -Prompt "transformation scene" `
#     -Image "https://a.png","https://b.png"
#
#   # Keyframes animation (smooth A->B morph)
#   .\scripts\gen_video.ps1 -Prompt "smooth cinematic transition" `
#     -Image "https://a.png","https://b.png" -Mode keyframes
#
#   # Convenience: aspect ratio + duration shortcuts
#   .\scripts\gen_video.ps1 -Prompt "..." -Ratio 9:16 -Seconds 8
#
#   # Reproducible result
#   .\scripts\gen_video.ps1 -Prompt "..." -Seed 42
#
# REQUIREMENTS
#   Set environment variable AGNES_API_KEY before first use:
#     [System.Environment]::SetEnvironmentVariable(
#       "AGNES_API_KEY", "sk-your-key-here", "User")
# =====================================================================

[CmdletBinding(DefaultParameterSetName='Direct')]
param(
    # Required: text describing the video to generate.
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Prompt,

    # Optional: input image URL(s).
    #   1 image  -> image-to-video
    #   2+ images -> multi-image (default) or keyframes (use -Mode keyframes)
    [string[]]$Image,

    # 'multi-image' (default) or 'keyframes'. Only meaningful when 2+ images
    # are passed. Keyframes mode generates smooth transitions between images.
    [ValidateSet('multi-image','keyframes')]
    [string]$Mode = 'multi-image',

    # Aspect ratio shortcut. If specified, sets Width/Height for you.
    # Maps to standard 1080p resolutions.
    [ValidateSet('16:9','9:16','1:1','4:3','3:4')]
    [string]$Ratio,

    # Duration shortcut in seconds. Auto-calculates NumFrames given FrameRate.
    # Final NumFrames is rounded to satisfy 8n+1 and capped at 441.
    [double]$Seconds,

    # Direct dimension parameters (used if -Ratio not specified).
    [int]$Width = 1920,
    [int]$Height = 1080,

    # Frame count. Must satisfy 8n+1 and be <=441.
    # 81 / 121 / 161 / 241 / 441 are valid.
    [int]$NumFrames = 241,

    # Frames per second, 1-60. Higher = smoother but shorter at fixed NumFrames.
    [ValidateRange(1,60)]
    [int]$FrameRate = 60,

    # Optional: things you don't want to appear in the video.
    [string]$NegativePrompt,

    # Optional: random seed for reproducibility.
    [int]$Seed
)

# --- API key check -------------------------------------------------------
$ApiKey = $env:AGNES_API_KEY
if (-not $ApiKey) {
    Write-Host "ERROR: AGNES_API_KEY environment variable not set." -ForegroundColor Red
    Write-Host "Set it with:" -ForegroundColor Yellow
    Write-Host '  [System.Environment]::SetEnvironmentVariable("AGNES_API_KEY", "sk-your-key", "User")' -ForegroundColor Yellow
    exit 1
}

# --- Apply -Ratio shortcut (overrides Width/Height) ----------------------
if ($Ratio) {
    switch ($Ratio) {
        '16:9' { $Width = 1920; $Height = 1080 }
        '9:16' { $Width = 1080; $Height = 1920 }
        '1:1'  { $Width = 1024; $Height = 1024 }
        '4:3'  { $Width = 1440; $Height = 1080 }
        '3:4'  { $Width = 1080; $Height = 1440 }
    }
}

# --- Apply -Seconds shortcut (compute valid NumFrames) -------------------
if ($PSBoundParameters.ContainsKey('Seconds')) {
    $targetFrames = [math]::Round($Seconds * $FrameRate)
    # Round up to satisfy 8n+1
    $n = [math]::Ceiling(($targetFrames - 1) / 8.0)
    $NumFrames = [int]($n * 8 + 1)
    if ($NumFrames -gt 441) { $NumFrames = 441 }
    if ($NumFrames -lt 9)   { $NumFrames = 9 }
}

# --- Build request body --------------------------------------------------
$body = [ordered]@{
    model      = 'agnes-video-v2.0'
    prompt     = $Prompt
    width      = $Width
    height     = $Height
    num_frames = $NumFrames
    frame_rate = $FrameRate
}

if ($NegativePrompt) { $body.negative_prompt = $NegativePrompt }
if ($PSBoundParameters.ContainsKey('Seed')) { $body.seed = $Seed }

$displayMode = 'Text-to-Video'
if ($Image -and $Image.Count -gt 0) {
    if ($Image.Count -eq 1) {
        # Single image -> top-level "image" string
        $body.image = $Image[0]
        $displayMode = 'Image-to-Video'
    } else {
        # 2+ images -> extra_body.image array
        $extra = [ordered]@{ image = $Image }
        if ($Mode -eq 'keyframes') {
            $extra.mode  = 'keyframes'
            $displayMode = 'Keyframes Animation'
        } else {
            $displayMode = 'Multi-image Video'
        }
        $body.extra_body = $extra
    }
}

# --- Echo the plan -------------------------------------------------------
$durationSec = [math]::Round($NumFrames / $FrameRate, 1)

Write-Host "Creating video generation task..." -ForegroundColor Cyan
Write-Host "  Prompt: $Prompt"
Write-Host "  Resolution: ${Width}x${Height}"
Write-Host "  Frames: $NumFrames @ ${FrameRate}fps (~${durationSec}s)"
if ($PSBoundParameters.ContainsKey('Seed')) { Write-Host "  Seed: $Seed" }
Write-Host "  Mode: $displayMode" -ForegroundColor Magenta

$jsonStr   = $body | ConvertTo-Json -Depth 10 -Compress
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($jsonStr)

$authHeader = "Bearer $ApiKey"
$headers    = @{ Authorization = $authHeader; "Content-Type" = "application/json" }

# --- Step 1: Create task -------------------------------------------------
try {
    Write-Host "  Sending request..." -ForegroundColor Gray

    $webResponse = Invoke-WebRequest `
        -Uri "https://apihub.agnes-ai.com/v1/videos" `
        -Method Post `
        -Headers $headers `
        -Body $bodyBytes `
        -TimeoutSec 120 `
        -UseBasicParsing
    $response = $webResponse.Content | ConvertFrom-Json

    $videoId = $response.video_id.ToString()
    $taskId  = $response.task_id.ToString()
    $status  = if ($response.status -is [string]) { $response.status } else { $response.status.ToString() }

    Write-Host ""
    Write-Host "Task created!" -ForegroundColor Green
    Write-Host "  video_id: $videoId"
    Write-Host "  task_id:  $taskId"
    Write-Host "  Status:   $status"
    if ($response.seconds) { Write-Host "  Estimated duration: $($response.seconds)s" }
    if ($response.size) {
        $sizeVal = if ($response.size -is [string]) { $response.size } else { ($response.size | Out-String).Trim() }
        Write-Host "  Estimated resolution: $sizeVal"
    }
}
catch {
    Write-Host ""
    Write-Host "Failed to create video task!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red

    if ($_.Exception.Response) {
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            $errorResponse = $reader.ReadToEnd()
            Write-Host "API Response: $errorResponse" -ForegroundColor DarkYellow
        } catch { }
    }

    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check AGNES_API_KEY is valid"
    Write-Host "  2. Verify the prompt is non-empty"
    Write-Host "  3. num_frames must satisfy 8n+1 and be <=441"
    Write-Host "  4. frame_rate must be between 1 and 60"
    Write-Host "  5. If 503, wait 30s and retry"
    exit 1
}

# --- Step 2: Poll for completion -----------------------------------------
Write-Host ""
Write-Host "Polling for results (every 5s, up to 15 minutes)..." -ForegroundColor Yellow

$maxAttempts = 180   # 180 * 5s = 15 minutes
$attempt     = 0
$finalUrl    = $null
$result      = $null

while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 5
    $attempt++

    try {
        $encoded  = [System.Net.WebUtility]::UrlEncode($videoId)
        $queryUrl = "https://apihub.agnes-ai.com/agnesapi?video_id=$encoded"

        $queryResponse = Invoke-WebRequest `
            -Uri $queryUrl `
            -Headers @{ Authorization = $authHeader } `
            -TimeoutSec 30 `
            -UseBasicParsing
        $result = $queryResponse.Content | ConvertFrom-Json

        $currentStatus = $result.status
        $progress      = if ($result.progress) { "$($result.progress)%" } else { "N/A" }

        Write-Host "  [$attempt] Status: $currentStatus | Progress: $progress" -NoNewline

        if ($currentStatus -eq "completed") {
            Write-Host " Done!" -ForegroundColor Green
            $finalUrl = $result.remixed_from_video_id
            break
        } elseif ($currentStatus -eq "failed") {
            Write-Host " Failed!" -ForegroundColor Red
            $errorMsg = if ($result.error) { $result.error | ConvertTo-Json -Depth 5 } else { "Unknown error" }
            Write-Host "  Error: $errorMsg" -ForegroundColor Red
            exit 1
        } elseif ($currentStatus -eq "queued" -or $currentStatus -eq "in_progress") {
            Write-Host "..." -ForegroundColor Gray
        } else {
            Write-Host " (unknown: $currentStatus)" -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "  [$attempt] Poll error: $($_.Exception.Message)" -ForegroundColor DarkRed
    }
}

# --- Output --------------------------------------------------------------
if ($finalUrl) {
    Write-Host ""
    Write-Host "Video generated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "MEDIA:$finalUrl"
    Write-Host ""
    $finalSize = if ($result.size -is [string]) { $result.size } else { ($result.size | Out-String).Trim() }
    Write-Host "  Resolution: $finalSize"
    Write-Host "  Duration:   $($result.seconds)s"
} else {
    # Timeout: never silent. Surface video_id so the user can re-query later.
    Write-Host ""
    Write-Host "Still processing after 15 minutes - the task is not abandoned, just slow." -ForegroundColor Yellow
    Write-Host "  Re-query later with this video_id:" -ForegroundColor Yellow
    Write-Host "    $videoId"
    Write-Host "  Manual check (PowerShell):"
    Write-Host "    Invoke-WebRequest -Uri ""https://apihub.agnes-ai.com/agnesapi?video_id=$videoId"" -Headers @{ Authorization = ""Bearer `$env:AGNES_API_KEY"" } -UseBasicParsing | Select-Object -Expand Content"
    exit 2
}
