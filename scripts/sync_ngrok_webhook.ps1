param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$NgrokApiUrl = "http://127.0.0.1:4040/api/tunnels",
    [string]$Token = ""
)

$ErrorActionPreference = "Stop"

function Get-TokenFromEnvFile {
    param([string]$EnvPath)
    if (!(Test-Path $EnvPath)) {
        return ""
    }

    $line = Get-Content $EnvPath | Where-Object { $_ -match '^TELEGRAM_BOT_TOKEN=' } | Select-Object -First 1
    if (!$line) {
        return ""
    }
    return ($line -split '=', 2)[1].Trim()
}

if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = $env:TELEGRAM_BOT_TOKEN
}
if ([string]::IsNullOrWhiteSpace($Token)) {
    $Token = Get-TokenFromEnvFile -EnvPath (Join-Path $ProjectRoot ".env")
}
if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "TELEGRAM_BOT_TOKEN not found in env var or .env file."
}

$tunnels = Invoke-RestMethod -Uri $NgrokApiUrl -Method GET
$httpsTunnel = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
if (!$httpsTunnel) {
    throw "No HTTPS ngrok tunnel found. Start ngrok first: ngrok http 8001"
}

$publicUrl = $httpsTunnel.public_url.TrimEnd("/")
$webhookUrl = "$publicUrl/webhook/$Token"
$setWebhookApi = "https://api.telegram.org/bot$Token/setWebhook"
$getWebhookApi = "https://api.telegram.org/bot$Token/getWebhookInfo"

Write-Host "Using tunnel: $publicUrl"
Write-Host "Setting webhook: $webhookUrl"

$setResult = Invoke-RestMethod -Uri $setWebhookApi -Method POST -ContentType "application/json" -Body (@{ url = $webhookUrl } | ConvertTo-Json)
Write-Host "setWebhook response: $($setResult | ConvertTo-Json -Compress)"

$info = Invoke-RestMethod -Uri $getWebhookApi -Method GET
Write-Host "getWebhookInfo response: $($info | ConvertTo-Json -Compress)"
