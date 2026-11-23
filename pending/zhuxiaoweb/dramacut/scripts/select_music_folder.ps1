<#
.SYNOPSIS
Ask the user to choose a music folder for this edit in a Windows folder dialog.
.DESCRIPTION
Run in the user's interactive desktop and decode stdout as UTF-8 JSON.
Windows PowerShell 5.1: powershell.exe -NoProfile -STA -File <script>
PowerShell 7 on Windows: pwsh.exe -NoProfile -STA -File <script>
The normal call blocks until the user chooses a folder or cancels. Keep the
process running while waiting for the user. -Check does not open a window.
Check the JSON status. A cancelled or unavailable dialog supplies no path.
#>
[CmdletBinding()]
param([switch]$Check)

try { [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false) } catch {
    # A non-console host can still receive the JSON as a .NET string.
}

function Write-Selection {
    param(
        [string]$Status,
        [object]$Path = $null,
        [string]$Reason = '',
        [string]$Detail = ''
    )

    $result = [ordered]@{ status = $Status; path = $Path }
    if ($Reason) { $result.reason = $Reason }
    if ($Detail) { $result.detail = $Detail }
    ConvertTo-Json -InputObject $result -Compress
}

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    Write-Selection 'unavailable' -Reason 'not_windows'
    return
}

if (-not [System.Environment]::UserInteractive -or [System.Diagnostics.Process]::GetCurrentProcess().SessionId -eq 0) {
    Write-Selection 'unavailable' -Reason 'no_interactive_desktop'
    return
}

if ([System.Threading.Thread]::CurrentThread.GetApartmentState() -ne [System.Threading.ApartmentState]::STA) {
    Write-Selection 'unavailable' -Reason 'sta_required' -Detail 'Run PowerShell with -STA in the interactive Windows session.'
    return
}

try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    if (-not [System.Windows.Forms.SystemInformation]::UserInteractive) {
        Write-Selection 'unavailable' -Reason 'no_interactive_desktop'
        return
    }
} catch {
    Write-Selection 'unavailable' -Reason 'windows_forms_unavailable' -Detail $_.Exception.Message
    return
}

if ($Check) {
    Write-Selection 'ready'
    return
}

$dialog = $null
try {
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = '请选择本次精剪的本地配乐文件夹。'
    $dialog.RootFolder = [System.Environment+SpecialFolder]::Desktop
    $dialog.SelectedPath = ''
    $dialog.ShowNewFolderButton = $false
    if ($dialog.PSObject.Properties['AutoUpgradeEnabled']) {
        # The desktop-rooted browser does not restore a recent folder.
        $dialog.AutoUpgradeEnabled = $false
    }

    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        Write-Selection 'cancelled'
        return
    }

    $selected = $dialog.SelectedPath
    if ($selected -notmatch '^(?:[A-Za-z]:[\\/]|\\\\)' -or -not [System.IO.Directory]::Exists($selected)) {
        Write-Selection 'unavailable' -Reason 'selected_folder_unavailable'
        return
    }

    Write-Selection 'selected' -Path ([System.IO.Path]::GetFullPath($selected))
} catch {
    Write-Selection 'unavailable' -Reason 'dialog_failed' -Detail $_.Exception.Message
} finally {
    if ($null -ne $dialog) { $dialog.Dispose() }
}
