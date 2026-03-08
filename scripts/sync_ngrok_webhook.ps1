param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$NgrokApiUrl = "http://127.0.0.1:4040/api/tunnels",
    [string]$BotToken = "",
    [string]$WebhookToken = ""
)

$ErrorActionPreference = "Stop"

function Get-TokenFromEnvFile {
    param([string]$EnvPath, [string]$TokenName)
    if (!(Test-Path $EnvPath)) {
        return ""
    }

    $line = Get-Content $EnvPath | Where-Object { $_ -match "^$TokenName=" } | Select-Object -First 1
    if (!$line) {
        return ""
    }
    return ($line -split '=', 2)[1].Trim()
}

if ([string]::IsNullOrWhiteSpace($BotToken)) {
    $BotToken = $env:TELEGRAM_BOT_TOKEN
}
if ([string]::IsNullOrWhiteSpace($BotToken)) {
    $BotToken = Get-TokenFromEnvFile -EnvPath (Join-Path $ProjectRoot ".env") -TokenName "TELEGRAM_BOT_TOKEN"
}
if ([string]::IsNullOrWhiteSpace($BotToken)) {
    throw "TELEGRAM_BOT_TOKEN not found in env var or .env file."
}

if ([string]::IsNullOrWhiteSpace($WebhookToken)) {
    $WebhookToken = $env:WEBHOOK_TOKEN
}
if ([string]::IsNullOrWhiteSpace($WebhookToken)) {
    $WebhookToken = Get-TokenFromEnvFile -EnvPath (Join-Path $ProjectRoot ".env") -TokenName "WEBHOOK_TOKEN"
}
if ([string]::IsNullOrWhiteSpace($WebhookToken)) {
    Write-Host "WARNING: WEBHOOK_TOKEN not found. Using TELEGRAM_BOT_TOKEN as fallback (not recommended for production)."
    $WebhookToken = $BotToken
}

$tunnels = Invoke-RestMethod -Uri $NgrokApiUrl -Method GET
$httpsTunnel = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
if (!$httpsTunnel) {
    throw "No HTTPS ngrok tunnel found. Start ngrok first: ngrok http 8001"
}

$publicUrl = $httpsTunnel.public_url.TrimEnd("/")
$webhookUrl = "$publicUrl/webhook/$WebhookToken"
$setWebhookApi = "https://api.telegram.org/bot$BotToken/setWebhook"
$getWebhookApi = "https://api.telegram.org/bot$BotToken/getWebhookInfo"

Write-Host "Using tunnel: $publicUrl"
Write-Host "Setting webhook: $webhookUrl"
Write-Host "Bot token: $($BotToken.Substring(0, [Math]::Min(10, $BotToken.Length)))..."

$setResult = Invoke-RestMethod -Uri $setWebhookApi -Method POST -ContentType "application/json" -Body (@{ url = $webhookUrl } | ConvertTo-Json)
Write-Host "setWebhook response: $($setResult | ConvertTo-Json -Compress)"

$info = Invoke-RestMethod -Uri $getWebhookApi -Method GET
Write-Host "getWebhookInfo response: $($info | ConvertTo-Json -Compress)"
