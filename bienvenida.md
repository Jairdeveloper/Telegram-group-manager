# Propuesta de implementacion - Menu Welcome

**Objetivo**
- Implementar un menu de bienvenida con 2 niveles y comportamiento consistente con inline keyboards.
- Reutilizar la arquitectura existente (MenuEngine, CallbackRouter, FeatureModule) para que el patron sea reutilizable en otros comandos de administracion.

**UX Requerida (segun la peticion y referencias)**
1. Menu principal de welcome:
- Debe mostrar una descripcion corta de la funcionalidad.
- Debe mostrar el estado actual (on/off).
- Botones:
- Activar
- Desactivar
- Personalizar mensaje (navega al menu 2)
2. Menu 2 (personalizar mensaje):
- Botones:
- Texto (configurar mensaje de bienvenida en texto)
- Multimedia (agregar media al mensaje de bienvenida)

**Enfoque / Arquitectura Propuesta (Reutilizable)**
- Mantener el flujo actual con `MenuEngine` + `CallbackRouter` + `FeatureModule`.
- Crear un patron de menus "Settings + Customize" reutilizable:
- Cada feature define 2 menus: `feature_main` y `feature_customize`.
- Cada feature registra callbacks con prefijo `feature:*`.
- Un helper comun (por ejemplo `FeatureMenuBuilder`) arma:
- Cabecera con descripcion y estado.
- Botones de activar/desactivar.
- Boton "Personalizar" que abre el menu 2.
- Este helper puede usarse en welcome, goodbye, rules, captcha, etc.

**Cambios Propuestos En Datos (GroupConfig)**
- Agregar campos para soportar el menu solicitado:
- `welcome_enabled: bool` (ya existe)
- `welcome_text: str` (ya existe)
- `welcome_media: Optional[str]` (ya existe, pero definir que guarda file_id)
- Opcional (para futuras extensiones):
- `welcome_mode: str` (always | first_join)
- `welcome_keyboard: Optional[dict]` (inline keyboard opcional)

**Menus (Definicion)**
- Nuevo menu `welcome_main` (reemplaza o extiende `create_welcome_menu`):
- Texto:
- Titulo: "Mensaje de bienvenida"
- Descripcion: "Desde este menu puedes configurar el mensaje que se enviara al unirse un usuario."
- Estado: "Estado: Activado/Desactivado"
- Botones:
- `welcome:toggle:on`
- `welcome:toggle:off`
- `welcome:customize:open`
- `nav:back:main`
- Nuevo menu `welcome_customize`:
- Texto: "Personalizar mensaje de bienvenida"
- Estado: "Texto: SI/NO" y "Multimedia: SI/NO"
- Botones:
- `welcome:text:edit`
- `welcome:media:edit`
- `nav:back:welcome_main`

**Callbacks (Routing)**
- `welcome:toggle:on|off` -> activar/desactivar
- `welcome:customize:open` -> mostrar menu 2
- `welcome:text:edit` -> entrar a modo conversacion (texto)
- `welcome:media:edit` -> entrar a modo conversacion (media)
- `welcome:preview` (opcional) -> vista previa del mensaje

**Conversacion (Texto y Multimedia)**
- Reutilizar `ConversationState` en `app/manager_bot/_menu_service.py`.
- El flujo ya existe para `waiting_welcome_text` pero falta manejar `waiting_welcome_media` en `app/webhook/handlers.py`.
- Propuesta:
- Si estado = `waiting_welcome_text`, guardar `config.welcome_text`.
- Si estado = `waiting_welcome_media`, guardar `config.welcome_media` con file_id del mensaje.
- En ambos casos limpiar estado y re-renderizar el menu 2.

**Puntos De Integracion (Archivos Clave)**
- Menus: `app/manager_bot/_menus/welcome_menu.py`
- Feature callbacks: `app/manager_bot/_features/welcome/__init__.py`
- Conversacion: `app/manager_bot/_menu_service.py` + `app/webhook/handlers.py`
- Persistencia: `app/manager_bot/_config/group_config.py`
- Render: `app/manager_bot/_transport/telegram/menu_engine.py`

**Plan De Implementacion (Pasos)**
1. Actualizar `create_welcome_menu` para que sea el menu principal con descripcion y botones Activar/Desactivar/Personalizar.
2. Crear `create_welcome_customize_menu` (menu 2) con botones Texto y Multimedia.
3. Ajustar `WelcomeFeature.register_callbacks`:
- `welcome:customize:open` -> mostrar menu 2.
- `welcome:text:edit` -> set_state waiting_welcome_text.
- `welcome:media:edit` -> set_state waiting_welcome_media.
4. Extender `app/webhook/handlers.py` para capturar `waiting_welcome_media`.
5. Opcional: agregar helper `FeatureMenuBuilder` para reutilizar el patron en otras features.

**Reutilizacion Para Otros Comandos**
- El patron "Settings + Customize" se puede aplicar a:
- Goodbye: texto y multimedia.
- Captcha: texto y modo.
- Rules: texto y vista previa.
- Para evitar duplicacion, usar un builder comun o una clase base `SettingsFeatureModule` con:
- `get_description()`
- `get_status()`
- `get_customize_actions()`

**Riesgos Y Validaciones**
- Verificar que el envio de media devuelve `file_id` y que se guarda de forma estable.
- Asegurar que `MenuEngine` esta inicializado en el webhook.
- Confirmar que el cliente Telegram acepta `reply_markup` con `InlineKeyboardMarkup.to_dict()`.

**Resultado Esperado**
- `/welcome` o boton Welcome muestra menu principal con estado y descripcion.
- Boton "Personalizar mensaje" abre menu 2.
- Botones Texto/Multimedia inician flujo de configuracion y guardan datos.
- El patron es reutilizable para otras features de administracion.
