param(
  [Parameter(Mandatory=$true)][string]$DataDir,
  [int]$WindowMinutes = 10
)

$ErrorActionPreference = "Stop"

$remindersPath = Join-Path $DataDir "reminders.csv"
$notifiedPath = Join-Path $DataDir "notified.log"

if (-not (Test-Path $remindersPath)) {
  Write-Host "reminders.csv not found"
  exit 1
}

$now = Get-Date
$windowEnd = $now.AddMinutes($WindowMinutes)

$notified = @{}
if (Test-Path $notifiedPath) {
  Get-Content $notifiedPath | ForEach-Object {
    if ($_ -and -not $notified.ContainsKey($_)) { $notified[$_] = $true }
  }
}

$rows = Import-Csv $remindersPath
$toNotify = @()

foreach ($row in $rows) {
  if (-not $row.reminder_time) { continue }
  try {
    $rt = [datetime]::ParseExact($row.reminder_time, "yyyy-MM-dd HH:mm", $null)
  } catch {
    continue
  }
  if ($rt -ge $now -and $rt -le $windowEnd) {
    $key = "$($row.reminder_time)|$($row.title)"
    if (-not $notified.ContainsKey($key)) {
      $toNotify += [PSCustomObject]@{ key = $key; title = $row.title; time = $row.reminder_time }
      $notified[$key] = $true
    }
  }
}

if ($toNotify.Count -eq 0) {
  Write-Host "No reminders"
  exit 0
}

Add-Type -AssemblyName System.Windows.Forms
foreach ($item in $toNotify) {
  [System.Windows.Forms.MessageBox]::Show("$($item.title)`n$($item.time)", "Schedule Reminder") | Out-Null
  Add-Content -Path $notifiedPath -Value $item.key
}

Write-Host "Notified $($toNotify.Count) reminder(s)"
