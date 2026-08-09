# Generated from the signed PersonWise CLI release model.
# Embedded minisign trust root: RWQxXCGcBkNBLF/3q1BbM7xZmDxbaY53bjJYcruIuTbK5DYVm+Nm1ztO
$ErrorActionPreference = "Stop"
$action = if ($args.Count -eq 1) { $args[0] } else { "" }
if ($action -notin @("--approve-install", "--approve-upgrade", "--approve-rollback")) {
  [Console]::Error.WriteLine('{"schema_version":"1","ok":false,"error":{"code":"INSTALL_APPROVAL_REQUIRED","message":"Explicit user approval is required before installing, upgrading, or rolling back the PersonWise executable.","retryable":false,"action":"obtain_user_approval"},"request_id":"bootstrap-local"}')
  exit 2
}
if (-not [Environment]::Is64BitOperatingSystem) { throw "Unsupported Windows target" }
$nativeSignatureRequired = $false
if ($nativeSignatureRequired -and "deferred-founder-approved" -ne "verified") {
  [Console]::Error.WriteLine('{"schema_version":"1","ok":false,"error":{"code":"NATIVE_SIGNATURE_REQUIRED","message":"This release candidate has not completed Authenticode signing.","retryable":false,"action":"use_verified_release"},"request_id":"bootstrap-local"}')
  exit 9
}
if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) { throw "LOCALAPPDATA is unavailable" }
$targetDir = Join-Path $env:LOCALAPPDATA "PersonWise\bin"
$targetPath = Join-Path $targetDir "personwise.exe"
[IO.Directory]::CreateDirectory($targetDir) | Out-Null
$targetDirInfo = Get-Item -LiteralPath $targetDir -Force
if (($targetDirInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Install directory must not be a reparse point" }
$upgradeHashes = @("151375f65df8b82e63ccba55119ad96badfc11437737452f67b1a274f229b4a5", "20a0dd088b2b19629899ee775b6bdf5189fe55ddd15765891ce76673169d53bb", "2a74bb17410e230a4c5b50e4f7c1407bc198873dac025d56b6294428967fb97c", "6840175ff4e73c136afa55f20f66efb1322d77b03c739cd7b85f03c1c6944b91", "872e3b54d2d0262f682e319e45ad5b3daa1dcd1a3048d3cf12232694c5778cb6", "8bec4b1137ce49e6e4692550a1e1454997a3a0097386e9ce690e7d053795f435", "aa1c88ecf4e1fc0ea44c2e6a9d137c6f8361223737b3ddcbc00e82eb85e67b78", "bcdbc700dfce751967327db0084dd2b30b743c567f758ea662f879ab48b2f8d2")
$rollbackHashes = @()
$currentDigest = ""
if (Test-Path -LiteralPath $targetPath) {
  $existing = Get-Item -LiteralPath $targetPath -Force
  if ($action -eq "--approve-install" -or $existing.PSIsContainer -or (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) { throw "Install target is occupied by an unrecognized installation and was not changed" }
  $currentDigest = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $allowedHashes = if ($action -eq "--approve-upgrade") { $upgradeHashes } else { $rollbackHashes }
  if ($allowedHashes -notcontains $currentDigest) { throw "Existing executable is not recognized by the signed release history and was not changed" }
} elseif ($action -ne "--approve-install") {
  throw "An approved upgrade or rollback requires a recognized existing installation"
}
$workDir = Join-Path $targetDir (".personwise-install." + [Guid]::NewGuid().ToString("N"))
[IO.Directory]::CreateDirectory($workDir) | Out-Null
try {
  $archive = Join-Path $workDir "personwise_1.1.6_windows_amd64.zip"
  Add-Type -AssemblyName System.Net.Http
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $handler = [Net.Http.HttpClientHandler]::new()
  $handler.AllowAutoRedirect = $false
  $client = [Net.Http.HttpClient]::new($handler)
  $client.Timeout = [TimeSpan]::FromSeconds(300)
  $request = [Net.Http.HttpRequestMessage]::new([Net.Http.HttpMethod]::Get, "https://releases.personwise.ai/cli/v1.1.6/personwise_1.1.6_windows_amd64.zip")
  $response = $client.SendAsync($request, [Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
  try {
    if (-not $response.IsSuccessStatusCode) { throw "Artifact download failed" }
    $declaredLength = $response.Content.Headers.ContentLength
    if ($null -ne $declaredLength -and ($declaredLength -ne 3217769 -or $declaredLength -gt 26214400)) { throw "Artifact size mismatch" }
    $inputStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $outputStream = [IO.File]::Open($archive, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
      $buffer = New-Object byte[] 65536
      [long]$total = 0
      while (($read = $inputStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $total += $read
        if ($total -gt 3217769 -or $total -gt 26214400) { throw "Artifact size limit exceeded during download" }
        $outputStream.Write($buffer, 0, $read)
      }
      if ($total -ne 3217769) { throw "Artifact size mismatch" }
      $outputStream.Flush($true)
    } finally {
      $outputStream.Dispose()
      $inputStream.Dispose()
    }
  } finally {
    $response.Dispose()
    $request.Dispose()
    $client.Dispose()
    $handler.Dispose()
  }
  $file = Get-Item -LiteralPath $archive
  if ($file.Length -ne 3217769 -or $file.Length -gt 26214400) { throw "Artifact size mismatch" }
  $digest = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($digest -ne "87a9ac7e0759d4cc944a02b97e12772584388d46f2e9cd1e63e965465a4c36c2") { throw "Artifact checksum mismatch" }
  $extractDir = Join-Path $workDir "extracted"
  Expand-Archive -LiteralPath $archive -DestinationPath $extractDir
  $entries = @(Get-ChildItem -LiteralPath $extractDir -Force -Recurse)
  $binaryEntry = Get-Item -LiteralPath (Join-Path $extractDir "personwise.exe") -Force
  $licenseEntry = Get-Item -LiteralPath (Join-Path $extractDir "LICENSE") -Force
  $noticesEntry = Get-Item -LiteralPath (Join-Path $extractDir "THIRD_PARTY_NOTICES.md") -Force
  if ($entries.Count -ne 3 -or $binaryEntry.PSIsContainer -or $licenseEntry.PSIsContainer -or $noticesEntry.PSIsContainer -or (($binaryEntry.Attributes -bor $licenseEntry.Attributes -bor $noticesEntry.Attributes) -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Archive contents invalid" }
  $candidate = Join-Path $extractDir "personwise.exe"
  $candidateDigest = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($candidateDigest -ne "785e53606d6dfd6d5a76093cce402834f1bc18cb298df3d9c175fe157a98380f") { throw "Release executable checksum mismatch" }
  if ("deferred-founder-approved" -eq "verified") {
    $signature = Get-AuthenticodeSignature -LiteralPath $candidate
    if ($signature.Status -ne "Valid" -or $signature.SignerCertificate.Thumbprint -ne "") { throw "Authenticode verification failed" }
  }
  $currentTargetDirInfo = Get-Item -LiteralPath $targetDir -Force
  if ($currentTargetDirInfo.FullName -ne $targetDirInfo.FullName -or (($currentTargetDirInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) { throw "Install directory changed during verification" }
  if ($action -eq "--approve-install") {
    [IO.File]::Move($candidate, $targetPath)
  } else {
    $existing = Get-Item -LiteralPath $targetPath -Force
    if ($existing.PSIsContainer -or (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) -or (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $currentDigest) { throw "Existing installation changed during verification and was not replaced" }
    $backup = Join-Path $workDir "previous-personwise.exe"
    [IO.File]::Replace($candidate, $targetPath, $backup, $true)
    Remove-Item -LiteralPath $backup -Force
  }
  [ordered]@{schema_version="1"; ok=$true; data=[ordered]@{path=[IO.Path]::GetFullPath($targetPath); software_version="1.1.6"; cli_contract_version="1.0"; action=$action}; request_id="bootstrap-local"} | ConvertTo-Json -Compress
} finally {
  if (Test-Path -LiteralPath $workDir) { Remove-Item -LiteralPath $workDir -Recurse -Force }
}
