$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Security

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class JobAppCred {
  [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
  public struct CREDENTIAL {
    public uint Flags;
    public uint Type;
    public string TargetName;
    public string Comment;
    public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
    public uint CredentialBlobSize;
    public IntPtr CredentialBlob;
    public uint Persist;
    public uint AttributeCount;
    public IntPtr Attributes;
    public string TargetAlias;
    public string UserName;
  }

  [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  public static extern bool CredRead(string target, uint type, uint flags, out IntPtr credentialPtr);

  [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  public static extern bool CredWrite([In] ref CREDENTIAL userCredential, uint flags);

  [DllImport("advapi32.dll", SetLastError = true)]
  public static extern void CredFree(IntPtr credentialPtr);
}
"@

function Read-Request {
  $stdin = New-Object System.IO.StreamReader([Console]::OpenStandardInput(), [Text.Encoding]::UTF8)
  $metaLine = $stdin.ReadLine()
  if (-not $metaLine) { throw 'Missing profile-store request.' }
  $meta = $metaLine | ConvertFrom-Json
  $plaintext = $stdin.ReadToEnd()
  return @{ Meta = $meta; Plaintext = $plaintext }
}

function Get-WrappingKey([string]$Target, [string]$UserName, [bool]$Create) {
  $ptr = [IntPtr]::Zero
  if ([JobAppCred]::CredRead($Target, 1, 0, [ref]$ptr)) {
    try {
      $cred = [Runtime.InteropServices.Marshal]::PtrToStructure($ptr, [type][JobAppCred+CREDENTIAL])
      $bytes = New-Object byte[] $cred.CredentialBlobSize
      [Runtime.InteropServices.Marshal]::Copy($cred.CredentialBlob, $bytes, 0, $cred.CredentialBlobSize)
      return $bytes
    } finally {
      [JobAppCred]::CredFree($ptr)
    }
  }
  if (-not $Create) { return $null }
  $key = New-Object byte[] 32
  [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($key)
  $blobPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal($key.Length)
  try {
    [Runtime.InteropServices.Marshal]::Copy($key, 0, $blobPtr, $key.Length)
    $cred = New-Object JobAppCred+CREDENTIAL
    $cred.Type = 1
    $cred.TargetName = $Target
    $cred.UserName = $UserName
    $cred.CredentialBlob = $blobPtr
    $cred.CredentialBlobSize = [uint32]$key.Length
    $cred.Persist = 2
    if (-not [JobAppCred]::CredWrite([ref]$cred, 0)) {
      throw 'write-failed'
    }
  } finally {
    [Runtime.InteropServices.Marshal]::FreeHGlobal($blobPtr)
  }
  return $key
}

function Protect-Profile([byte[]]$Key, [string]$Plaintext, [string]$Path) {
  $plainBytes = [Text.Encoding]::UTF8.GetBytes($Plaintext)
  $aes = [Security.Cryptography.Aes]::Create()
  try {
    $aes.Key = $Key
    $aes.GenerateIV()
    $encryptor = $aes.CreateEncryptor()
    $cipher = $encryptor.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
    $payload = New-Object byte[] ($aes.IV.Length + $cipher.Length)
    [Array]::Copy($aes.IV, 0, $payload, 0, $aes.IV.Length)
    [Array]::Copy($cipher, 0, $payload, $aes.IV.Length, $cipher.Length)
    $protected = [Security.Cryptography.ProtectedData]::Protect($payload, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
      New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    [IO.File]::WriteAllBytes($Path, $protected)
  } finally {
    $aes.Dispose()
  }
}

function Unprotect-Profile([byte[]]$Key, [string]$Path) {
  $protected = [IO.File]::ReadAllBytes($Path)
  $payload = [Security.Cryptography.ProtectedData]::Unprotect($protected, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
  $aes = [Security.Cryptography.Aes]::Create()
  try {
    $aes.Key = $Key
    $iv = New-Object byte[] $aes.IV.Length
    [Array]::Copy($payload, 0, $iv, 0, $iv.Length)
    $aes.IV = $iv
    $cipher = New-Object byte[] ($payload.Length - $iv.Length)
    [Array]::Copy($payload, $iv.Length, $cipher, 0, $cipher.Length)
    $decryptor = $aes.CreateDecryptor()
    $plainBytes = $decryptor.TransformFinalBlock($cipher, 0, $cipher.Length)
    return [Text.Encoding]::UTF8.GetString($plainBytes)
  } finally {
    $aes.Dispose()
  }
}

try {
  $request = Read-Request
  $meta = $request.Meta
  $target = [string]$meta.service
  $account = [string]$meta.account
  $path = [string]$meta.path
  if ($meta.op -eq 'set') {
    $key = Get-WrappingKey $target $account $true
    Protect-Profile $key $request.Plaintext $path
  } elseif ($meta.op -eq 'get') {
    $key = Get-WrappingKey $target $account $false
    if (-not $key -or -not (Test-Path -LiteralPath $path)) { throw 'missing' }
    $text = Unprotect-Profile $key $path
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [Console]::OutputEncoding = $utf8
    [Console]::Out.Write($text)
  } else {
    throw 'unsupported'
  }
} catch {
  [Console]::Error.WriteLine('Windows profile storage failed.')
  exit 1
}
