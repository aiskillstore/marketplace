<#
.SYNOPSIS
  精确截图工具 - 支持按窗口标题、进程名、屏幕区域截图

.DESCRIPTION
  多种截图策略，按优先级：
  1. Web 页面：优先用浏览器自动化截图（agent-browser skill）
  2. 应用程序窗口：按标题/进程名精确截取窗口客户区
  3. 指定屏幕区域：按坐标截取（适用于 WorkBuddy 内置浏览器面板）
  4. 全屏/活动窗口：兜底方案

.PARAMETER OutputPath
  截图输出路径（PNG格式），必填

.PARAMETER Mode
  截图模式：fullscreen | activewindow | window | region
  默认 fullscreen

.PARAMETER WindowTitle
  Mode=window 时使用，按窗口标题部分匹配查找窗口

.PARAMETER ProcessName
  Mode=window 时使用，按进程名查找窗口（不含 .exe）

.PARAMETER Region
  Mode=region 时使用，格式 "X,Y,Width,Height"

.PARAMETER ClientOnly
  截取窗口客户区（去掉标题栏和边框），默认 $true

.EXAMPLE
  powershell -File capture_screenshot.ps1 -OutputPath "s.png" -Mode window -WindowTitle "stock-watcher"
  powershell -File capture_screenshot.ps1 -OutputPath "s.png" -Mode window -ProcessName "chrome"
  powershell -File capture_screenshot.ps1 -OutputPath "s.png" -Mode region -Region "0,0,1024,768"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,

    [Parameter(Mandatory=$false)]
    [ValidateSet("fullscreen", "activewindow", "window", "region")]
    [string]$Mode = "fullscreen",

    [Parameter(Mandatory=$false)]
    [string]$WindowTitle,

    [Parameter(Mandatory=$false)]
    [string]$ProcessName,

    [Parameter(Mandatory=$false)]
    [string]$Region,

    [Parameter(Mandatory=$false)]
    [bool]$ClientOnly = $true
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ============================================
# Win32 P/Invoke via Add-Type -MemberDefinition (lightweight, avoids large env block)
# ============================================
$Win32Defs = @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public class Win32 {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT lpPoint);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsCallback lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    public delegate bool EnumWindowsCallback(IntPtr hWnd, IntPtr lParam);
}

public struct RECT {
    public int Left; public int Top; public int Right; public int Bottom;
}
public struct POINT {
    public int X; public int Y;
}
'@

try {
    Add-Type -TypeDefinition $Win32Defs -ErrorAction Stop
} catch {
    # Fallback: try without enum windows (minimal API surface for fullscreen/region modes)
    $Win32Minimal = @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public class Win32 {
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT lpPoint);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}

public struct RECT {
    public int Left; public int Top; public int Right; public int Bottom;
}
public struct POINT {
    public int X; public int Y;
}
'@
    try {
        Add-Type -TypeDefinition $Win32Minimal -ErrorAction Stop
    } catch {
        Write-Output "WARN:Win32_API_unavailable:$_"
    }
}

# ============================================
# Window enumeration via .NET Process API (avoids C# Add-Type size issues)
# ============================================
function Find-WindowByTitle {
    param([string]$TitleSubstring)
    
    $results = [System.Collections.ArrayList]::new()
    $search = $TitleSubstring.ToLower()
    
    # Use .NET's built-in Process class to find windows
    $allProcs = Get-Process | Where-Object { $_.MainWindowTitle -and $_.MainWindowTitle.Length -gt 0 }
    foreach ($proc in $allProcs) {
        if ($proc.MainWindowTitle.ToLower().Contains($search)) {
            [void]$results.Add(@{
                Handle = $proc.MainWindowHandle
                Title = $proc.MainWindowTitle
                ProcessName = $proc.ProcessName
            })
        }
    }
    return $results
}

function Find-WindowByProcessName {
    param([string]$ProcName)
    
    $results = [System.Collections.ArrayList]::new()
    $procs = Get-Process -Name $ProcName -ErrorAction SilentlyContinue
    foreach ($proc in $procs) {
        if ($proc.MainWindowHandle -and $proc.MainWindowHandle -ne [IntPtr]::Zero) {
            [void]$results.Add(@{
                Handle = $proc.MainWindowHandle
                Title = $proc.MainWindowTitle
                ProcessName = $proc.ProcessName
            })
        }
    }
    return $results
}

# ============================================
# Capture a specific window
# ============================================
function Capture-Window {
    param([IntPtr]$Hwnd, [string]$Path)
    
    if ($Hwnd -eq [IntPtr]::Zero) { return $false }
    
    # Bring to front (restore if minimized)
    if ([Win32]::IsIconic($Hwnd)) {
        [Win32]::ShowWindow($Hwnd, 9)
    }
    Start-Sleep -Milliseconds 200
    [Win32]::SetForegroundWindow($Hwnd) | Out-Null
    Start-Sleep -Milliseconds 500  # Wait for rendering
    
    if ($ClientOnly) {
        $cr = New-Object RECT
        [Win32]::GetClientRect($Hwnd, [ref]$cr)
        
        $pt = New-Object POINT
        $pt.X = 0; $pt.Y = 0
        [Win32]::ClientToScreen($Hwnd, [ref]$pt)
        
        $w = $cr.Right - $cr.Left
        $h = $cr.Bottom - $cr.Top
        
        if ($w -le 0 -or $h -le 0) { return $false }
        
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($pt.X, $pt.Y, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $g.Dispose()
    } else {
        $wr = New-Object RECT
        [Win32]::GetWindowRect($Hwnd, [ref]$wr)
        $w = $wr.Right - $wr.Left
        $h = $wr.Bottom - $wr.Top
        
        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($wr.Left, $wr.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $g.Dispose()
    }
    
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $bmp.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    return $true
}

# ============================================
# Save bitmap helper
# ============================================
function Save-Bitmap {
    param($Bitmap, [string]$Path)
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    $Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    $Bitmap.Dispose()
}

# ============================================
# Main dispatch
# ============================================
switch ($Mode) {
    "fullscreen" {
        $scr = [System.Windows.Forms.Screen]::PrimaryScreen
        $b = $scr.Bounds
        $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($b.X, $b.Y, 0, 0, $b.Size)
        $g.Dispose()
        Save-Bitmap -Bitmap $bmp -Path $OutputPath
        Write-Output "OK:fullscreen:${OutputPath}"
    }

    "activewindow" {
        $hwnd = [Win32]::GetForegroundWindow()
        if ($hwnd -eq [IntPtr]::Zero) {
            Write-Error "No foreground window found"
            exit 1
        }
        $ok = Capture-Window -Hwnd $hwnd -Path $OutputPath
        if ($ok) { Write-Output "OK:activewindow:${OutputPath}" }
        else { Write-Error "Failed to capture active window" }
    }

    "window" {
        $matches = @()
        if ($WindowTitle) {
            $matches = Find-WindowByTitle -TitleSubstring $WindowTitle
        } elseif ($ProcessName) {
            $matches = Find-WindowByProcessName -ProcName $ProcessName
        } else {
            Write-Error "Mode=window requires -WindowTitle or -ProcessName"
            exit 1
        }

        if ($matches.Count -eq 0) {
            # Debug: list visible windows
            $all = Get-Process | Where-Object { $_.MainWindowTitle } | Select-Object -First 20
            $titles = ($all | ForEach-Object { "[$($_.ProcessName)] $($_.MainWindowTitle)" }) -join " | "
            Write-Output "DEBUG:no_match for title='$WindowTitle' process='$ProcessName'"
            Write-Output "DEBUG:visible_windows=$titles"
            Write-Error "No window found matching the criteria"
            exit 1
        }

        $target = $matches[0]
        Write-Output "INFO:matched_window=[$($target.ProcessName)] $($target.Title)"
        $ok = Capture-Window -Hwnd $target.Handle -Path $OutputPath
        if ($ok) { Write-Output "OK:window:${OutputPath}" }
        else { Write-Error "Failed to capture window: $($target.Title)" }
    }

    "region" {
        if (-not $Region) {
            Write-Error "Mode=region requires -Region (format: X,Y,W,H)"
            exit 1
        }
        $p = $Region -split ','
        if ($p.Count -ne 4) {
            Write-Error "Region format: X,Y,Width,Height (got: $Region)"
            exit 1
        }
        $x = [int]$p[0]; $y = [int]$p[1]
        $w = [int]$p[2]; $h = [int]$p[3]

        $bmp = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
        $g.Dispose()
        Save-Bitmap -Bitmap $bmp -Path $OutputPath
        Write-Output "OK:region:${OutputPath}"
    }
}
