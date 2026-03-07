````curl.exe "https://api.telegram.org/bot8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw/getWebhookInfo"
{"ok":true,"result":{"url":"https://sulkiest-unworkmanlike-shondra.ngrok-free.app/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw","has_custom_certificate":false,"pending_update_count":11,"last_error_date":1772869235,"last_error_message":"Wrong response from the webhook: 404 Not Found","max_connections":40,"ip_address":"3.124.142.205"}}
````

curl.exe http://127.0.0.1:4040/api/tunnels
{"tunnels":[{"name":"command_line","ID":"8389c87a810dc6edde1ec057ef726c45","uri":"/api/tunnels/command_line","public_url":"https://sulkiest-unworkmanlike-shondra.ngrok-free.dev","proto":"https","config":{"addr":"http://localhost:8001","inspect":true},"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}}],"uri":"/api/tunnels"}

curl.exe http://127.0.0.1:8000/health
{"status":"ok","version":"2.1"}

curl.exe http://127.0.0.1:8001/health
{"status":"ok"}

curl.exe -X POST "https://sulkiest-unworkmanlike-shondra.ngrok-free.app/webhook/8588716358:AAGw3RX94SyEeM1UxM-3sGPPs83n3IM2qJw" ^
¿Más?   -H "Content-Type: application/json" ^
¿Más?   -d "{\"update_id\":99999,\"message\":{\"chat\":{\"id\":999},\"text\":\"test\"}}"
<!DOCTYPE html>
<html class="h-full" lang="en-US" dir="ltr">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="preload" href="https://assets.ngrok.com/fonts/euclid-square/EuclidSquare-Regular-WebS.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/euclid-square/EuclidSquare-RegularItalic-WebS.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/euclid-square/EuclidSquare-Medium-WebS.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/euclid-square/EuclidSquare-MediumItalic-WebS.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/ibm-plex-mono/IBMPlexMono-Text.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/ibm-plex-mono/IBMPlexMono-TextItalic.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/ibm-plex-mono/IBMPlexMono-SemiBold.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <link rel="preload" href="https://assets.ngrok.com/fonts/ibm-plex-mono/IBMPlexMono-SemiBoldItalic.woff" as="font" type="font/woff" crossorigin="anonymous" />
    <meta name="author" content="ngrok">
    <meta name="description" content="ngrok is the fastest way to put anything on the internet with a single command.">
    <link href="https://ngrok.com/assets/favicon.ico" rel="shortcut icon" type="image/x-icon">
    <meta name="robots" content="noindex, nofollow">
    <link id="style" rel="stylesheet" href="https://cdn.ngrok.com/static/css/error.css">
    <noscript>The endpoint sulkiest-unworkmanlike-shondra.ngrok-free.app is offline. (ERR_NGROK_3200)</noscript>
    <script id="script" src="https://cdn.ngrok.com/static/js/error.js" type="text/javascript"></script>
  </head>
  <body class="h-full" id="ngrok">
    <div id="root" data-payload="eyJjZG5CYXNlIjoiaHR0cHM6Ly9jZG4ubmdyb2suY29tLyIsImNvZGUiOiIzMjAwIiwibWVzc2FnZSI6IlRoZSBlbmRwb2ludCBzdWxraWVzdC11bndvcmttYW5saWtlLXNob25kcmEubmdyb2stZnJlZS5hcHAgaXMgb2ZmbGluZS4iLCJ0aXRsZSI6Ik5vdCBGb3VuZCJ9"></div>
  </body>
</html>

type logs\ops_events.jsonl

INFO", "update_id": 82, "chat_id": 12345}
{"ts_utc": "2026-03-07T05:54:54.837346+00:00", "component": "webhook", "event": "webhook.received", "level": "INFO", "update_id": 83, "chat_id": 12345, "process_async": false}
{"ts_utc": "2026-03-07T05:54:54.911877+00:00", "component": "telegram", "event": "telegram.dispatch.chat_message", "level": "INFO", "update_id": 83, "chat_id": 12345}
{"ts_utc": "2026-03-07T05:54:54.942863+00:00", "component": "webhook", "event": "webhook.process_start", "level": "INFO", "update_id": 83, "chat_id": 12345, "text_len": 4, "dispatch_kind": "chat_message"}
{"ts_utc": "2026-03-07T05:54:54.962255+00:00", "component": "webhook", "event": "webhook.chat_service.ok", "level": "INFO", "update_id": 83, "chat_id": 12345, "reply_len": 10}
{"ts_utc": "2026-03-07T05:54:54.986331+00:00", "component": "webhook", "event": "webhook.telegram_send.error", "level": "ERROR", "update_id": 83, "chat_id": 12345}
{"ts_utc": "2026-03-07T05:54:55.009451+00:00", "component": "webhook", "event": "webhook.received", "level": "INFO", "update_id": 84, "chat_id": 12345, "process_async": false}
{"ts_utc": "2026-03-07T05:54:55.031199+00:00", "component": "telegram", "event": "telegram.dispatch.ops_command", "level": "INFO", "update_id": 84, "chat_id": 12345}
{"ts_utc": "2026-03-07T05:54:55.047641+00:00", "component": "webhook", "event": "webhook.process_start", "level": "INFO", "update_id": 84, "chat_id": 12345, "text_len": 5, "dispatch_kind": "ops_command"}
{"ts_utc": "2026-03-07T05:54:55.062828+00:00", "component": "webhook", "event": "webhook.ops_service.ok", "level": "INFO", "update_id": 84, "chat_id": 12345, "command": "/logs", "ops_status": "ok", "reply_len": 9}
{"ts_utc": "2026-03-07T05:54:55.080453+00:00", "component": "webhook", "event": "webhook.telegram_send.ok", "level": "INFO", "update_id": 84, "chat_id": 12345}