param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string[]]$Hosts = @("api.telegram.org", "api.github.com", "www.google.com"),
    [switch]$RunBootstrap = $true
)

$ErrorActionPreference = "Stop"

function Test-OutboundHttps {
    param([string]$HostName)

    $dnsRecords = @()
    try {
        $dnsRecords = Resolve-DnsName $HostName -ErrorAction Stop |
            Where-Object { $_.Type -in @("A", "AAAA") } |
            Select-Object -ExpandProperty IPAddress
    } catch {
        $dnsRecords = @()
    }

    $netResult = Test-NetConnection $HostName -Port 443 -InformationLevel Detailed -WarningAction SilentlyContinue

    return [PSCustomObject]@{
        HostName      = $HostName
        DnsOk         = ($dnsRecords.Count -gt 0)
        DnsAddresses  = ($dnsRecords -join ", ")
        PingSucceeded = [bool]$netResult.PingSucceeded
        Tcp443Ok      = [bool]$netResult.TcpTestSucceeded
        RemoteAddress = "$($netResult.RemoteAddress)"
    }
}

function Get-VirtualInterfaceHints {
    $routeOutput = route print
    $patterns = @(
        "Wintun",
        "TAP-Windows Adapter",
        "OpenVPN",
        "ZeroTier",
        "Hyper-V Virtual Ethernet Adapter",
        "VirtualBox Host-Only Ethernet Adapter"
    )

    foreach ($line in $routeOutput) {
        foreach ($pattern in $patterns) {
            if ($line -like "*$pattern*") {
                $line.Trim()
                break
            }
        }
    }
}

function Invoke-BootstrapCheck {
    param([string]$ProjectRoot)

    $pythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $pythonPath)) {
        return [PSCustomObject]@{
            Executed = $false
            ExitCode = -1
            Summary  = ".venv python not found"
        }
    }

    Push-Location $ProjectRoot
    try {
        $previousErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $output = & $pythonPath -m app.telegram_ops.entrypoint 2>&1 | ForEach-Object { "$_" }
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
        Pop-Location
    }

    $networkLine = $output | Where-Object {
        $_ -match "NetworkError" -or $_ -match "ConnectError" -or $_ -match "bootstrap failed"
    } | Select-Object -Last 1

    if (!$networkLine) {
        $networkLine = ($output | Select-Object -Last 1)
    }

    return [PSCustomObject]@{
        Executed = $true
        ExitCode = $exitCode
        Summary  = "$networkLine"
    }
}

$proxyInfo = netsh winhttp show proxy
$internetSettings = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" |
    Select-Object ProxyEnable, ProxyServer, AutoConfigURL
$results = $Hosts | ForEach-Object { Test-OutboundHttps -HostName $_ }
$virtualInterfaces = @(Get-VirtualInterfaceHints)

Write-Host "=== Outbound HTTPS Diagnostic ==="
Write-Host "ProjectRoot: $ProjectRoot"
Write-Host "Timestamp: $(Get-Date -Format s)"
Write-Host ""
Write-Host "Host checks:"

foreach ($result in $results) {
    Write-Host "- Host: $($result.HostName)"
    Write-Host "  DNS: $($result.DnsOk) [$($result.DnsAddresses)]"
    Write-Host "  Ping: $($result.PingSucceeded)"
    Write-Host "  TCP/443: $($result.Tcp443Ok)"
    Write-Host "  RemoteAddress: $($result.RemoteAddress)"
}

Write-Host ""
Write-Host "WinHTTP proxy:"
$proxyInfo | ForEach-Object { Write-Host "  $_" }

Write-Host ""
Write-Host "Internet Settings:"
Write-Host "  ProxyEnable: $($internetSettings.ProxyEnable)"
Write-Host "  ProxyServer: $($internetSettings.ProxyServer)"
Write-Host "  AutoConfigURL: $($internetSettings.AutoConfigURL)"

Write-Host ""
Write-Host "Virtual interface hints:"
if ($virtualInterfaces.Count -eq 0) {
    Write-Host "  None detected in route print output."
} else {
    $virtualInterfaces | ForEach-Object { Write-Host "  $_" }
}

if ($RunBootstrap) {
    Write-Host ""
    Write-Host "Bootstrap check:"
    $bootstrap = Invoke-BootstrapCheck -ProjectRoot $ProjectRoot
    Write-Host "  Executed: $($bootstrap.Executed)"
    Write-Host "  ExitCode: $($bootstrap.ExitCode)"
    Write-Host "  Summary: $($bootstrap.Summary)"
}

$allTcpOk = ($results | Where-Object { -not $_.Tcp443Ok }).Count -eq 0
if ($allTcpOk) {
    Write-Host ""
    Write-Host "Conclusion: outbound TCP/443 succeeded for all tested hosts."
    exit 0
}

Write-Host ""
Write-Host "Conclusion: outbound TCP/443 is failing for one or more tested hosts."
exit 1
