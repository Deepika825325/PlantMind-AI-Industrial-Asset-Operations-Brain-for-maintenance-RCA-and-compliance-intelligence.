param(
    [string]$BaseUrl = "http://localhost:3000"
)

$ErrorActionPreference = "Stop"

$routes = @(
    @{ Name = "dashboard"; Path = "/" },
    @{ Name = "ask"; Path = "/ask" },
    @{ Name = "assets"; Path = "/assets" },
    @{ Name = "compliance"; Path = "/compliance" },
    @{ Name = "maintenance"; Path = "/maintenance" },
    @{ Name = "rca"; Path = "/rca" },
    @{ Name = "documents"; Path = "/documents" },
    @{ Name = "knowledge-graph"; Path = "/knowledge-graph" },
    @{ Name = "pid"; Path = "/pid" },
    @{ Name = "rbac"; Path = "/rbac" }
)

$chromeCandidates = @(
    "$Env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$Env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    "$Env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chrome = $chromeCandidates |
    Where-Object { Test-Path $_ } |
    Select-Object -First 1

if (-not $chrome) {
    throw "Chrome was not found. Install Chrome or capture screenshots manually."
}

New-Item `
    -ItemType Directory `
    -Force `
    -Path "docs/screenshots" |
Out-Null

foreach ($route in $routes) {
    $url = "$BaseUrl$($route.Path)"
    $output = "docs/screenshots/$($route.Name).png"

    & $chrome `
        --headless `
        --disable-gpu `
        --window-size=1440,1100 `
        "--screenshot=$output" `
        $url

    if (-not (Test-Path $output)) {
        throw "Screenshot failed for $url"
    }

    Write-Host "Captured $output"
}