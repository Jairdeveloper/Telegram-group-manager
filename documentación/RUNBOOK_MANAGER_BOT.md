# Runbook - Manager Bot: Sistema de Menús Interactivos

## Resumen

Este runbook describe cómo utilizar las funcionalidades del sistema de menús interactivos del Manager Bot.

---

## 1. Comando /config

### Descripción
El comando `/config` abre el menú principal de configuración del bot.

### Uso
```
/config
```

### Resultado
Se muestra un menú inline keyboard con las siguientes opciones:
- 📋 **Información** - Información del grupo
- 🛡️ **Moderación** - Opciones de moderación
- 🔰 **Antispam** - Configuración antispam
- 🔍 **Filtros** - Filtros de contenido
- 👋 **Bienvenida** - Mensajes de bienvenida
- ⏰ **Modo Noche** - Configuración de horario
- 📎 **Media** - Moderación de medios

---

## 2. Navegación en Menús

### Botones de Navegación
| Botón | Función |
|-------|---------|
| 🔙 Atrás | Volver al menú anterior |
| 🏠 Inicio | Volver al menú principal |
| ℹ️ Info | Muestra información |

### Flujo de Navegación
1. Usuario envía `/config`
2. Aparece el menú principal
3. Usuario presiona un botón (ej: "Moderación")
4. Se muestra el submenú correspondiente
5. Usuario puede navegar hacia atrás o al inicio

---

## 3. Configuración de Moderación

### Menú de Moderación
Acceso: `/config` → **Moderación**

| Opción | Descripción |
|--------|-------------|
| 🚫 Anti-Canal | Bloquea mensajes de canales |
| 🔗 Anti-Link | Controla enlaces |
| 🖼️ Anti-Media | Filtra tipos de medios |
| ⛔ Palabras Bloqueadas | Lista de palabras prohibidas |
| 🌙 Modo Noche | Restringe mensajes por horario |

### Anti-Canal
```
/config → Moderación → Anti-Canal
```
- **Activar**: Toggle en ON
- **Desactivar**: Toggle en OFF

### Anti-Link
```
/config → Moderación → Anti-Link
```
- **Activar**: Toggle en ON
- **Configurar**: Elegir tipo de enlaces a bloquear
  - Dominios específicos
  - URLs cortas
  - Todos los enlaces

### Modo Noche
```
/config → Moderación → Modo Noche
```
- **Activar**: Toggle en ON
- **Horario**: Definir hora de inicio y fin
- **Días**: Seleccionar días activos

---

## 4. Configuración Antispam

### Menú Antispam
Acceso: `/config` → **Antispam**

| Opción | Descripción |
|--------|-------------|
| 🔰 Activar | Activa/desactiva el antispam |
| 👁️ SpamWatch | Integración con SpamWatch API |
| 📜 Sibyl | Integración con Sibyl Bot |
| 🎚️ Sensibilidad | Nivel de detección (Bajo/Medio/Alto) |

### Configurar Sensibilidad
```
/config → Antispam → Sensibilidad
```
- **Bajo**: Solo detecta spam obvio
- **Medio**: Balance entre seguridad y falsos positivos
- **Alto**: Detecta todo lo sospechoso (puede bloquear usuarios legítimos)

---

## 5. Filtros de Contenido

### Menú de Filtros
Acceso: `/config` → **Filtros**

| Opción | Descripción |
|--------|-------------|
| ➕ Añadir | Agregar nuevo filtro |
| 📋 Lista | Ver filtros activos |
| 🗑️ Palabras Bloqueadas | Lista de palabras prohibidas |
| 🚫 Sticker Blacklist | Lista de stickers bloqueados |

### Añadir un Filtro
```
/config → Filtros → Añadir
```
1. Seleccionar tipo de filtro
2. Ingresar patrón o palabra
3. Confirmar

### Tipos de Filtros
- **Palabras**: Texto específico a detectar
- **Patrones**: Expresiones regulares
- **Stickers**: ID de stickers a bloquear

---

## 6. Mensajes de Bienvenida

### Menú de Bienvenida
Acceso: `/config` → **Bienvenida**

| Opción | Descripción |
|--------|-------------|
| ✋ Activar | Activa/desactiva bienvenida |
| 📝 Texto | Configurar mensaje de bienvenida |
| 👋 Despedida | Configurar mensaje de despedida |
| 🖼️ Media | Imagen/video de bienvenida |

### Configurar Mensaje
```
/config → Bienvenida → Texto
```
1. Escribir el mensaje
2. Usar variables:
   - `{user}` - Nombre del usuario
   - `{title}` - Nombre del grupo
   - `{count}` - Número de miembros
3. Confirmar

### Variables Disponibles
| Variable | Descripción |
|----------|-------------|
| `{user}` | Nombre del usuario |
| `{user_mention}` | Mención del usuario |
| `{title}` | Nombre del grupo |
| `{count}` | Cantidad de miembros |
| `{date}` | Fecha actual |

---

## 7. Moderación de Medios

### Menú Media
Acceso: `/config` → **Media**

| Opción | Descripción |
|--------|-------------|
| 🖼️ Imágenes | Permitir/bloquear imágenes |
| 🎬 Videos | Permitir/bloquear videos |
| 🎵 Audio | Permitir/bloquear audio |
| 📄 Documentos | Permitir/bloquear documentos |

---

## 8. Variables de Entorno

### Configuración del Sistema

| Variable | Descripción | Default |
|----------|-------------|---------|
| `MENU_STORAGE_TYPE` | Tipo de almacenamiento | `memory` |
| `DATABASE_URL` | URL de PostgreSQL | - |
| `REDIS_URL` | URL de Redis | - |
| `RATE_LIMIT_CALLS` | Calls permitidos | `30` |
| `RATE_LIMIT_WINDOW` | Ventana de tiempo (seg) | `60` |

### Ejemplo
```bash
# Production
MENU_STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379
RATE_LIMIT_CALLS=30
RATE_LIMIT_WINDOW=60
```

---

## 9. Rate Limiting

### Descripción
El sistema limita el número de callbacks por usuario para prevenir abuso.

### Límites
- **30 callbacks** por minuto por usuario

### Usuario Bloqueado
Si un usuario excede el límite:
```
⚠️ Demasiadas solicitudes. Intenta más tarde.
```

---

## 10. Estados de Conversación

### Descripción
El sistema mantiene estados de conversación para inputs de texto largos.

### Flujos Soportados
| Estado | Descripción |
|--------|-------------|
| `waiting_welcome_text` | Editando mensaje de bienvenida |
| `waiting_goodbye_text` | Editando mensaje de despedida |
| `waiting_filter_pattern` | Agregando nuevo filtro |
| `waiting_blocked_word` | Agregando palabra bloqueada |
| `waiting_whitelist_domain` | Agregando dominio permitido |
| `waiting_rules_text` | Editando reglas |
| `waiting_captcha_answer` | Resolviendo captcha |

---

## 11. Troubleshooting

### El menú no aparece
1. Verificar que el bot tenga permisos
2. Verificar que el usuario sea administrador
3. Revisar logs: `webhook.menu.display`

### El callback no responde
1. Verificar rate limiting
2. Revisar logs: `webhook.callback_query.*`

### Error al guardar configuración
1. Verificar conexión a Redis/Postgres
2. Revisar permisos de la base de datos

### El bot no responde a /config
1. Verificar que el comando esté registrado
2. Revisar logs de `enterprise_command`

---

## 12. Comandos Rápidos

| Comando | Descripción |
|---------|-------------|
| `/config` | Abrir menú de configuración |
| `/antispam` | Configurar antispam |
| `/antichannel` | Configurar anticanal |
| `/filter` | Ver filtros |
| `/welcome` | Ver bienvenida |
| `/rules` | Ver reglas |
| `/setwelcome [texto]` | Establecer bienvenida |
| `/setrules [texto]` | Establecer reglas |

---

## 13. Métricas

### Prometheus Metrics

| Métrica | Descripción |
|---------|-------------|
| `telegram_webhook_requests_total` | Total de requests |
| `telegram_webhook_process_seconds` | Tiempo de procesamiento |
| `webhook_callback_query_ok` | Callbacks procesados |
| `webhook_menu_display` | Menús mostrados |

---

*Documento generado el 2026-03-12*
*Versión: 1.0*
