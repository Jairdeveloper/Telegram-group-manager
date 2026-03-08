# Debug - Fase 8: Diagnostico de Red Saliente en Windows

## Estado: ⚠️ CAUSA RAIZ OPERATIVA IDENTIFICADA (2026-03-06)

---

## Bug / Error descrito

- El bot no responde a `/e2e`
- En fases anteriores aparecia `409 Conflict`
- En la fase 7 el bot fallo en bootstrap con:
  - `telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed`

---

## Objetivo de esta fase

Determinar si el fallo restante era del codigo del bot o de la conectividad saliente del host Windows.

---

## Verificaciones ejecutadas

### 1. Resolucion DNS

Comando:

```powershell
Resolve-DnsName api.telegram.org
```

Resultado:

- `api.telegram.org -> 149.154.166.110`
- tambien hubo resolucion IPv6

Conclusion:

- DNS funciona

### 2. Prueba TCP a Telegram

Comando:

```powershell
Test-NetConnection api.telegram.org -Port 443 -InformationLevel Detailed
```

Resultado:

- `PingSucceeded = True`
- `TcpTestSucceeded = False`

Conclusion:

- el host resuelve y alcanza por ICMP
- la conexion TCP/443 falla

### 3. Comparacion con otros destinos HTTPS

Comandos:

```powershell
Test-NetConnection www.google.com -Port 443 -InformationLevel Detailed
Test-NetConnection api.github.com -Port 443 -InformationLevel Detailed
```

Resultado:

- ambos con `TcpTestSucceeded = False`

Conclusion:

- el problema no es especifico de Telegram
- la salida HTTPS/TCP del host Windows esta bloqueada o interceptada

### 4. Proxy del sistema

Comandos:

```powershell
netsh winhttp show proxy
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
```

Resultado:

- WinHTTP: acceso directo, sin proxy
- Internet Settings: sin proxy explicito ni PAC visible

Conclusion:

- no hay un proxy de sistema configurado que explique el fallo

### 5. Ruta del host

Se reviso `route print`.

Hallazgos:

- hay varias interfaces virtuales/tuneles presentes:
  - `Wintun Userspace Tunnel`
  - `TAP-Windows Adapter`
  - `OpenVPN Data Channel Offload`
  - `ZeroTier Virtual Port`
  - `Hyper-V Virtual Ethernet Adapter`
  - `VirtualBox Host-Only Ethernet Adapter`

Conclusion:

- el host tiene software de tunel/VPN/virtualizacion que puede interferir con la salida TCP normal

---

## Causa raiz de esta fase

La causa raiz actual no esta en el codigo del bot.

La evidencia apunta a un problema operativo del host Windows:

- salida TCP/443 fallida hacia Internet
- sin proxy configurado
- con multiples interfaces virtuales y tuneles instalados

Eso explica:

- `telegram.error.NetworkError`
- imposibilidad de bootstrap del bot
- `telegram_webhook_info` fallando desde el proceso local

---

## Estado consolidado del sistema

| Componente | Estado |
|-----------|--------|
| API local | ✅ OK |
| Webhook local | ✅ OK |
| E2E local sin Telegram | ✅ OK |
| Bootstrap del bot contra Telegram | ❌ FAIL por red |
| DNS | ✅ OK |
| ICMP / ping | ✅ OK |
| TCP 443 saliente | ❌ FAIL |

---

## Conclusiones

1. El codigo del proyecto ya no es el bloqueo principal.
2. El bot no puede iniciar porque el host Windows no consigue abrir conexiones TCP/443 salientes.
3. El problema es general para HTTPS, no solo para `api.telegram.org`.
4. La siguiente accion debe centrarse en red del host: firewall, antivirus, VPN, tuneles o politica corporativa.

---

## Siguientes pasos recomendados

1. Desactivar temporalmente VPN/tuneles activos:
   - OpenVPN
   - Wintun
   - ZeroTier
   - otros adaptadores virtuales no necesarios

2. Repetir:

```powershell
Test-NetConnection api.telegram.org -Port 443 -InformationLevel Detailed
Test-NetConnection api.github.com -Port 443 -InformationLevel Detailed
```

3. Si sigue fallando:
   - revisar firewall/antivirus corporativo
   - revisar inspeccion SSL/HTTPS
   - probar otra red fisica o hotspot

4. Una vez vuelva TCP/443:

```powershell
.\.venv\Scripts\python.exe -m app.telegram_ops.entrypoint
```

5. Si entonces reaparece `409 Conflict`:

```bash
curl "https://api.telegram.org/bot<TOKEN>/close"
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```
