param(
  [string]$Platform = "agents",
  [switch]$Force
)

$skillName = "gpt-series-reasoning-style"
$source = Split-Path -Parent $PSScriptRoot

$paths = @{
  agents    = Join-Path $env:USERPROFILE ".agents\skills\$skillName"
  codex     = Join-Path $env:USERPROFILE ".codex\skills\$skillName"
  claude    = Join-Path $env:USERPROFILE ".claude\skills\$skillName"
  cursor    = Join-Path (Get-Location) ".cursor\rules\$skillName"
  windsurf  = Join-Path (Get-Location) ".windsurf\rules\$skillName"
  cline     = Join-Path (Get-Location) ".clinerules\$skillName"
  gemini    = Join-Path $env:USERPROFILE ".gemini\skills\$skillName"
  kiro      = Join-Path $env:USERPROFILE ".kiro\skills\$skillName"
  trae      = Join-Path (Get-Location) ".trae\rules\$skillName"
  goose     = Join-Path $env:USERPROFILE ".config\goose\skills\$skillName"
  opencode  = Join-Path $env:USERPROFILE ".config\opencode\skills\$skillName"
  roo       = Join-Path (Get-Location) ".roo\rules\$skillName"
  antigravity = Join-Path $env:USERPROFILE ".agents\skills\$skillName"
}

if (-not $paths.ContainsKey($Platform)) {
  Write-Error "Unknown platform: $Platform"
  exit 1
}

$dest = $paths[$Platform]
if ((Test-Path -LiteralPath $dest) -and -not $Force) {
  Write-Error "Destination already exists: $dest. Use -Force to overwrite."
  exit 1
}

# Safety guard (C3-3): refuse to install into the skill repo itself — a
# pwd-based DEST run from the repo root would otherwise nest the repo
# inside itself via Copy-Item -Recurse.
# Must be a real descendant, not a prefix match: -like "$source*" also matches
# sibling directories that merely share a name prefix (e.g. the
# gpt-series-reasoning-style-workspace folder), which would refuse a legal
# install for a wrong reason.
$destFull = [System.IO.Path]::GetFullPath($dest).TrimEnd('\')
$sourceFull = [System.IO.Path]::GetFullPath($source).TrimEnd('\')
if ($destFull -ieq $sourceFull -or
    $destFull.StartsWith($sourceFull + [System.IO.Path]::DirectorySeparatorChar,
                         [System.StringComparison]::OrdinalIgnoreCase)) {
  Write-Error "Refusing: destination is inside the skill repo itself ($dest)"
  exit 1
}

New-Item -ItemType Directory -Path (Split-Path -Parent $dest) -Force | Out-Null
if (Test-Path -LiteralPath $dest) {
  Remove-Item -LiteralPath $dest -Recurse -Force
}
New-Item -ItemType Directory -Path $dest -Force | Out-Null
Copy-Item -Path (Join-Path $source '*') -Destination $dest -Recurse -Force
# Keep the install identical to the bash path: with -Force the '*' glob DOES
# include hidden items, so .git history / CI config would otherwise be shipped;
# site/ is the static docs page, not part of the runtime skill.
foreach ($dot in @('.git', '.github', '.gitignore', '.gitattributes', 'site')) {
  $dotPath = Join-Path $dest $dot
  if (Test-Path -LiteralPath $dotPath) {
    Remove-Item -LiteralPath $dotPath -Recurse -Force
  }
}
Get-ChildItem -Path $dest -Recurse -Directory -Filter '__pycache__' | ForEach-Object {
  Remove-Item -LiteralPath $_.FullName -Recurse -Force
}
Write-Output "Installed $skillName to $dest"
