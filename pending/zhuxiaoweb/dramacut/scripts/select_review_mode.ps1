<#
.SYNOPSIS
Choose whether the user will join mid-run editorial review.
.DESCRIPTION
Run in an interactive Windows PowerShell STA session. Emits one UTF-8 JSON result.
#>
[CmdletBinding()]
param([switch]$Check)

try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch { }

function Write-Selection {
    param([string]$Status, [string]$Mode = '', [string]$Reason = '')
    $result = [ordered]@{ status = $Status }
    if ($Mode) { $result.mode = $Mode }
    if ($Reason) { $result.reason = $Reason }
    ConvertTo-Json -InputObject $result -Compress
}

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    Write-Selection 'unavailable' -Reason 'not_windows'
    return
}
if (-not [System.Environment]::UserInteractive -or
    [System.Diagnostics.Process]::GetCurrentProcess().SessionId -eq 0 -or
    [System.Threading.Thread]::CurrentThread.GetApartmentState() -ne [System.Threading.ApartmentState]::STA) {
    Write-Selection 'unavailable' -Reason 'interactive_sta_required'
    return
}
try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    if (-not [System.Windows.Forms.SystemInformation]::UserInteractive) {
        Write-Selection 'unavailable' -Reason 'no_interactive_desktop'
        return
    }
} catch {
    Write-Selection 'unavailable' -Reason 'windows_forms_unavailable'
    return
}
if ($Check) {
    Write-Selection 'ready'
    return
}

$message = "是否需要你中途配合回看与专项审阅？`r`n`r`n是：生成接点/区间审阅页面与人工记录模板，等待审阅后继续。`r`n否：不生成审阅 HTML，由 Codex 检查关键帧和音频证据并记录自动审阅结果。`r`n`r`n候选计划审批仍按任务授权流程执行。"
$choice = [System.Windows.Forms.MessageBox]::Show(
    $message,
    '选择精剪审阅方式',
    [System.Windows.Forms.MessageBoxButtons]::YesNoCancel,
    [System.Windows.Forms.MessageBoxIcon]::Question
)
switch ($choice) {
    ([System.Windows.Forms.DialogResult]::Yes) { Write-Selection 'selected' -Mode 'assisted' }
    ([System.Windows.Forms.DialogResult]::No) { Write-Selection 'selected' -Mode 'autonomous' }
    default { Write-Selection 'cancelled' -Reason 'user_cancelled' }
}
