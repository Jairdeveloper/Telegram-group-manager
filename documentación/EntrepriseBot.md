# EnterpriseALRobot - Documentación del Bot

## Visión General del Proyecto

EnterpriseALRobot es un bot de Telegram construido sobre la biblioteca `python-telegram-bot`. El proyecto está basado en el concepto de "Kigyo" (un proyecto de AnimeKaizoku/Eagle Union) y utiliza una arquitectura modular.

### Tecnologías y Librerías Principales

- **python-telegram-bot**: Biblioteca principal para la API de Telegram
- **SQLAlchemy/SQLite**: Base de datos para persistencia
- **Redis**: Cache y almacenamiento rápido
- **SpamWatch API**: Protección contra spam
- **SibylSystem**: Sistema de bans distribuidos

### Estructura de Permisos

El bot implementa una jerarquía de usuarios:
- **OWNER_ID**: Dueño del bot
- **DEV_USERS**: Desarrolladores
- **SUDO_USERS**: Administradores globales
- **SUPPORT_USERS**: Usuarios de soporte
- **WHITELIST_USERS**: Lista blanca
- **SARDEGNA_USERS**: Grupo especial de inmunidad

---

## Módulos del Bot

### Administración de Grupos

| Módulo | Descripción |
|--------|-------------|
| **admin.py** | Gestión de administradores: promoción, descenso, permisos de grupo |
| **bans.py** | Sistema de baneo: ban, tempban, kick, baneo de canales |
| **muting.py** | Silenciamiento: mute, tmute, unmute, restricciones de chat |
| **purge.py** | Eliminación masiva de mensajes con confirmación |
| **locks.py** | Bloqueo de contenido: audio, voz, documentos, videos, URLs, bots, etc. |
| **antiflood.py** | Protección contra floods: límites configurables por chat |

### Bienvenida y Mensajes

| Módulo | Descripción |
|--------|-------------|
| **welcome.py** | Mensajes de bienvenida personalizados, CAPTCHA, botones de verificación |
| **rules.py** | Sistema de reglas de grupo consultables por usuarios |

### Notas y Almacenamiento

| Módulo | Descripción |
|--------|-------------|
| **notes.py** | Guardado y recuperación de notas, stickers, archivos, imágenes |
| **cust_filters.py** | Filtros personalizados para respuestas automáticas |

### Sistema de Federaciones

| Módulo | Descripción |
|--------|-------------|
| **feds.py** | Federaciones de grupos: bans federados, múltiples grupos bajo una fed |

### Protección Anti-Spam

| Módulo | Descripción |
|--------|-------------|
| **antispam.py** | GBAN (Global Ban): baneo global, sincronización con SpamWatch y SibylSystem |
| **antiflood.py** | Detección y restricción por flood |
| **blacklist.py** | Lista negra de palabras/patrones |
| **sticker_blacklist.py** | Bloqueo de stickers específicos |
| **blacklistusers.py** | Baneo global de usuarios |
| **antichannel.py** | Prevención de usuarios anónimos |
| **antilinkedchannel.py** | Desvinculación de canales vinculados |

### Sistema de Warnings

| Módulo | Descripción |
|--------|-------------|
| **warns.py** | Sistema de advertencias: warn, unwarn, límites configurables, acciones automáticas |

### Utilidades

| Módulo | Descripción |
|--------|-------------|
| **notes.py** | Notas guardadas con multimedia |
| **paste.py** | Subida de código a paste services |
| **paste.py** | Convertidor de moneda |
| **gettime.py** | Información de zonas horarias |
| **speed_test.py** | Test de velocidad de internet |
| **wallpaper.py** | Búsqueda de wallpapers |

### Entretenimiento

| Módulo | Descripción |
|--------|-------------|
| **fun.py** | Comandos divertids: runs, slap, insultos, dice, etc. |
| **weebify.py** | Conversión de texto a estilo anime |
| **reactions.py** | Reacciones automáticas a mensajes |
| **anilist.py** | Información de anime/manga desde AniList API |

### Información de Usuario

| Módulo | Descripción |
|--------|-------------|
| **userinfo.py** | Información de perfil de usuario |
| **users.py** | Base de datos de usuarios |
| **afk.py** | Sistema Away From Keyboard |

### Sistema de Backup

| Módulo | Descripción |
|--------|-------------|
| **backups.py** | Exportación e importación de datos de grupo |

### Moderación Avanzada

| Módulo | Descripción |
|--------|-------------|
| **reporting.py** | Sistema de reportes a administradores |
| **log_channel.py** | Canales de logs para todas las acciones |
| **cleaner.py** | Limpieza de mensajes del bot |
| **disable.py** | Habilitar/deshabilitar comandos |

### Comandos Especiales

| Módulo | Descripción |
|--------|-------------|
| **modules.py** | Listado de módulos cargados |
| **language.py** | Sistema de idiomas/multilingual |
| **connection.py** | Gestión de chats conectados |
| **announce.py** | Anuncios a múltiples grupos |
| **debug.py** | Herramientas de depuración |
| **eval.py** | Evaluación de código Python (solo owner) |
| **shell.py** | Ejecución de comandos shell (solo owner) |

---

## Sistema de Base de Datos (SQL)

Los módulos SQL proporcionan persistencia:

- **users_sql.py**: Usuarios
- **notes_sql.py**: Notas
- **rules_sql.py**: Reglas
- **feds_sql.py**: Federaciones
- **antispam_sql.py**: Banes globales
- **blacklist_sql.py**: Listas negras
- **locks_sql.py**: Bloqueos
- **welcome_sql.py**: Bienvenidas
- **warns_sql.py**: Warnings
- **afk_sql.py**: Estado AFK

---

## Helper Functions

Módulos auxiliares en `helper_funcs/`:

- **chat_status.py**: Verificaciones de estado de admin
- **decorators.py**: Decoradores (@kigcmd, @rate_limit, etc.)
- **extraction.py**: Extracción de usuarios y argumentos
- **string_handling.py**: Manejo de texto y parsing
- **filters.py**: Filtros personalizados
- **handlers.py**: Manejadores de mensajes
- **misc.py**: Utilidades varias
- **anonymous.py**: Manejo de usuarios anónimos

---

## Configuración

El bot se configura mediante `config.ini` con opciones como:
- TOKEN del bot
- IDs de administrador
- Configuración de base de datos (PostgreSQL)
- Redis
- APIs externas (Cash API, Time API, Wall API, Last.fm, etc.)
