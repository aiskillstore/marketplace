# Schema.org Quick Lookup Script (PowerShell)
# Opens Schema.org page for a class or property in the browser

param(
    [Parameter(Mandatory=$true)]
    [string]$Term
)

$url = "https://schema.org/$Term"

Write-Host "Opening Schema.org page for: $Term"
Write-Host "URL: $url"

Start-Process $url
