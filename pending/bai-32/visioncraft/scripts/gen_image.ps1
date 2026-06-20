# =====================================================================
# VisionCraft - Agnes Image Generation Script
# =====================================================================
# Generates images via the Agnes Image 2.1 Flash API.
# Defaults: 2048x2048 (high quality 2K).
#
# USAGE
#   # Text-to-image
#   .\scripts\gen_image.ps1 -Prompt "a luminous floating city at sunrise"
#
#   # Image-to-image (transform an existing image)
#   .\scripts\gen_image.ps1 -Prompt "make it cyberpunk night, preserve composition" `
#     -ImageUrl "https://example.com/input.png"
#
#   # Convenience: aspect ratio shortcut
#   .\scripts\gen_image.ps1 -Prompt "..." -Ratio 16:9
#
#   # Return Base64 instead of URL
#   .\scripts\gen_image.ps1 -Prompt "..." -ReturnBase64
#
# REQUIREMENTS
#   Set environment variable AGNES_API_KEY before first use:
#     [System.Environment]::SetEnvironmentVariable(
#       "AGNES_API_KEY", "sk-your-key-here", "User")
# =====================================================================

param(
    # Required: text describing the image to generate (or how to transform).
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Prompt,

    # Output dimensions, e.g. "2048x2048" or "1024x768".
    # Use -Ratio for common aspect ratio shortcuts.
    [string]$Size = "2048x2048",

    # Aspect ratio shortcut. If specified, overrides -Size with a sensible default.
    [ValidateSet('1:1','16:9','9:16','4:3','3:4','3:2','2:3','21:9')]
    [string]$Ratio,

    # If provided, switches to image-to-image mode using this URL as input.
    # Supports public HTTPS URLs or "data:image/...;base64,..." Data URIs.
    [string]$ImageUrl,

    # Return Base64 data instead of a hosted URL.
    [switch]$ReturnBase64
)

# --- API key check -------------------------------------------------------
$ApiKey = $env:AGNES_API_KEY
if (-not $ApiKey) {
    Write-Host "ERROR: AGNES_API_KEY environment variable not set." -ForegroundColor Red
    Write-Host "Set it with:" -ForegroundColor Yellow
    Write-Host '  [System.Environment]::SetEnvironmentVariable("AGNES_API_KEY", "sk-your-key", "User")' -ForegroundColor Yellow
    exit 1
}

# --- Apply -Ratio shortcut -----------------------------------------------
if ($Ratio) {
    switch ($Ratio) {
        '1:1'  { $Size = '2048x2048' }
        '16:9' { $Size = '2048x1152' }
        '9:16' { $Size = '1152x2048' }
        '4:3'  { $Size = '2048x1536' }
        '3:4'  { $Size = '1536x2048' }
        '3:2'  { $Size = '2048x1365' }
        '2:3'  { $Size = '1365x2048' }
        '21:9' { $Size = '2048x878'  }
    }
}

$BaseUrl = "https://apihub.agnes-ai.com/v1/images/generations"

# --- Build request body --------------------------------------------------
$body = @{
    model  = "agnes-image-2.1-flash"
    prompt = $Prompt
    size   = $Size
}

if ($ImageUrl) {
    # Image-to-image: input goes into extra_body.image array.
    $body.extra_body = @{
        image           = @($ImageUrl)
        response_format = if ($ReturnBase64) { "b64_json" } else { "url" }
    }
} else {
    # Text-to-image
    if ($ReturnBase64) {
        $body.return_base64 = $true
    } else {
        $body.extra_body = @{ response_format = "url" }
    }
}

# --- Echo the plan -------------------------------------------------------
Write-Host "Generating image..." -ForegroundColor Cyan
Write-Host "  Prompt: $Prompt"
Write-Host "  Size:   $Size"
if ($ImageUrl) {
    Write-Host "  Mode:   Image-to-Image" -ForegroundColor Magenta
} else {
    Write-Host "  Mode:   Text-to-Image" -ForegroundColor Green
}

# --- Send request --------------------------------------------------------
try {
    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri $BaseUrl -Method Post -Headers @{
        "Authorization" = "Bearer $ApiKey"
        "Content-Type"  = "application/json"
    } -Body ([System.Text.Encoding]::UTF8.GetBytes(($body | ConvertTo-Json -Depth 10))) -TimeoutSec 360

    $elapsed = ((Get-Date) - $startTime).TotalSeconds

    if ($response.data -and $response.data.Count -gt 0) {
        $item = $response.data[0]

        if ($item.url) {
            Write-Host ""
            Write-Host "Image generated successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "MEDIA:$($item.url)"
            Write-Host ""
            Write-Host "  Size: $Size"
            Write-Host "  Time: ${elapsed}s"
        } elseif ($item.b64_json) {
            Write-Host ""
            Write-Host "Image generated (Base64)!" -ForegroundColor Green
            Write-Host "  Base64 length: $($item.b64_json.Length) chars"
            Write-Host "  Size: $Size"
            Write-Host "  Time: ${elapsed}s"
        } else {
            Write-Host "Unexpected response format." -ForegroundColor Red
            Write-Host ($response | ConvertTo-Json -Depth 5)
        }
    } else {
        Write-Host "No image data in response." -ForegroundColor Red
        Write-Host ($response | ConvertTo-Json -Depth 5)
    }
} catch {
    Write-Host ""
    Write-Host "Image generation failed!" -ForegroundColor Red
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
    Write-Host "  3. Check internet connection"
    Write-Host "  4. If 503, wait 30s and retry"
    exit 1
}
