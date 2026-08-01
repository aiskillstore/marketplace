# Codex Vision Bridge 代理启动脚本（Windows）
# 用法: powershell -ExecutionPolicy Bypass -File start-proxy.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

# 定位 node：优先环境变量，其次本地 node.exe，最后 PATH
$node = $env:CVB_NODE_EXE
if (-not $node) {
    $candidates = @(
        (Join-Path $here "node.exe"),
        "node"
    )
    $node = $candidates | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
}
if (-not $node) {
    Write-Host "[ERROR] 未找到 Node.js。请安装 Node.js LTS: https://nodejs.org" -ForegroundColor Red
    exit 1
}

# 设置 NODE_PATH 指向本地 node_modules（如有）
if (Test-Path (Join-Path $here "node_modules")) {
    $env:NODE_PATH = Join-Path $here "node_modules"
}

$proxyJs = Join-Path $here "ocr-proxy.js"
if (-not (Test-Path $proxyJs)) {
    Write-Host "[ERROR] 未找到 $proxyJs" -ForegroundColor Red
    exit 1
}

# 如果已有代理在运行（端口被占），直接退出
$listener = Get-NetTCPConnection -LocalPort $env:OCR_PROXY_PORT -State Listen -ErrorAction SilentlyContinue
if ($listener) {
    Write-Host "[OK] 代理已在运行 (PID $($listener[0].OwningProcess))，端口 $env:OCR_PROXY_PORT"
    exit 0
}

Start-Process -FilePath $node -ArgumentList "`"$proxyJs`"" -WindowStyle Hidden
Write-Host "[OK] 代理已启动（隐藏窗口），端口 $env:OCR_PROXY_PORT"
