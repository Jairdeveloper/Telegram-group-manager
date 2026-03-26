param(
    [string]$BaseUrl = $env:OLLAMA_BASE_URL,
    [string]$Model = $env:LLM_MODEL
)

if (-not $BaseUrl -or $BaseUrl.Trim().Length -eq 0) {
    $BaseUrl = "http://localhost:11434"
}
if (-not $Model -or $Model.Trim().Length -eq 0) {
    $Model = "llama3"
}

Write-Host "Ollama base URL: $BaseUrl"
Write-Host "Model: $Model"

function Invoke-Post($url, $body) {
    try {
        $resp = Invoke-WebRequest -Uri $url -Method Post -Body ($body | ConvertTo-Json -Depth 5) -ContentType "application/json" -UseBasicParsing
        return @{ ok = $true; status = $resp.StatusCode; content = $resp.Content }
    } catch {
        if ($_.Exception.Response) {
            $status = $_.Exception.Response.StatusCode.value__
            return @{ ok = $false; status = $status; error = $_.Exception.Message }
        }
        return @{ ok = $false; status = $null; error = $_.Exception.Message }
    }
}

function Invoke-Get($url) {
    try {
        $resp = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing
        return @{ ok = $true; status = $resp.StatusCode; content = $resp.Content }
    } catch {
        if ($_.Exception.Response) {
            $status = $_.Exception.Response.StatusCode.value__
            return @{ ok = $false; status = $status; error = $_.Exception.Message }
        }
        return @{ ok = $false; status = $null; error = $_.Exception.Message }
    }
}

Write-Host "\n[1] GET /api/tags"
$tags = Invoke-Get "$BaseUrl/api/tags"
$tags | Format-List

Write-Host "\n[2] POST /api/chat (minimal)"
$chatBody = @{ model = $Model; messages = @(@{ role = "user"; content = "hola" }) ; stream = $false }
$chat = Invoke-Post "$BaseUrl/api/chat" $chatBody
$chat | Format-List

Write-Host "\n[3] POST /api/generate (legacy)"
$genBody = @{ model = $Model; prompt = "hola"; stream = $false }
$gen = Invoke-Post "$BaseUrl/api/generate" $genBody
$gen | Format-List

Write-Host "\n[4] POST /v1/chat/completions (OpenAI compat)"
$v1Body = @{ model = $Model; messages = @(@{ role = "user"; content = "hola" }); stream = $false; temperature = 0.2 }
$v1 = Invoke-Post "$BaseUrl/v1/chat/completions" $v1Body
$v1 | Format-List
