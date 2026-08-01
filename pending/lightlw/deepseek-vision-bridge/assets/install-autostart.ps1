# 设置 Windows 开机自启（当前用户级，无需管理员）
# 用法: powershell -ExecutionPolicy Bypass -File install-autostart.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"

# 通过隐藏 PowerShell 窗口启动代理
$cmd = 'powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File "{0}"' -f (Join-Path $here "start-proxy.ps1")
Set-ItemProperty -Path $runKey -Name "DeepSeekVisionBridge" -Value $cmd -Type String
Write-Host "[OK] 已设置开机自启: DeepSeekVisionBridge"
Write-Host "     移除自启: Remove-ItemProperty -Path '$runKey' -Name 'DeepSeekVisionBridge'"
