Fecha: 2026-03-26
version: 1.0
referencia: 01_PLAN_IMPLEMENTACION_MIGRACION_ARQUITECTURA_AGENTEIA_COMPLETADO.md

Resumen del plan

Ampliar el sistema de acciones existente para que el bot responda a consultas en lenguaje natural para administrar grupos. El bot interpretará peticiones como "Configura un mensaje de bienvenida simple" y ejecutará las acciones necesarias mediante el Action Registry.

Objetivo

Permitir a los administradores y moderadores configurar funciones del grupo mediante instrucciones en lenguaje natural, sin necesidad de usar menús interactivos o comandos.

Arquitectura objetivo

- `app/agent/actions/parser.py`: расширение con más patrones NL
- `app/agent/actions/pilot_actions.py`: расширение con nuevas acciones
- `app/manager_bot/services/group_config_service.py`: расширение según sea necesario
- `app/agent/actions/templates.py`: расширеинe plantillas de respuesta

Fases de implementación

Fase:
Fase 1 - Expansion del Action Parser NL
Objetivo fase:
Ampliar el parser basado en reglas para reconocer más patrones de lenguaje natural y mapearlos a acciones.
Implementacion fase:
- Agregar patrones para todas las acciones del grupo:
  - Bienvenida: activar, desactivar, establecer texto
  - Antispam: activar, desactivar, configurar excepciones
  - Antiflood: activar, configurar limite y accion
  - Antilink: activar, desactivar
  - Antichannel: activar, desactivar
  - Captcha: activar, configurar modo y tiempo
  - Filtros: agregar palabras bloqueadas, eliminar filtros
  - Modo nocturno: activar, configurar horarios
  - Bienvenida/Despedida: configurar mensaje de despedida
- Agregar sinónimos y variaciones regionales (español Latinoamerica)
- Implementar extracción de parámetros complejos (duraciones, acciones)

Archivos modificados:
- `app/agent/actions/parser.py`

Validacion

Para validar manualmente:
- Enviar "ponle captcha de botones" y verificar que mapea a captcha.toggle con modo button
- Enviar "activa el modo noche de 10pm a 6am" y verificar parseo de horarios
- Probar variaciones como "desactiva antispam", "apaga el anti spam", "quita el antiflood"

Fase:
Fase 2 - Registro de acciones completas
Objetivo fase:
Registrar todas las acciones de configuración de grupo en el Action Registry.
Implementacion fase:
- Crear modelos de parámetros para cada acción usando Pydantic
- Implementar funciones execute, snapshot, undo, dry_run para cada acción:
  - `welcome.toggle`, `welcome.set_text`, `welcome.set_media`
  - `goodbye.toggle`, `goodbye.set_text`, `goodbye.set_media`
  - `antispam.toggle`, `antispam.configure`
  - `antiflood.toggle`, `antiflood.configure`
  - `antilink.toggle`, `antichannel.toggle`
  - `captcha.toggle`, `captcha.configure`
  - `blocked_words.add`, `blocked_words.remove`, `blocked_words.list`
  - `nightmode.toggle`, `nightmode.configure`
  - `filtro.configure`
  - `multimedia.configure`
- Configurar permisos (admin/moderator) por acción
- Definir acciones que requieren confirmación

Archivos modificados/creados:
- `app/agent/actions/group_actions.py` (nuevo archivo con todas las acciones)

Validacion

Para validar manualmente:
- Verificar que todas las acciones se registran correctamente
- Probar ejecución de cada acción y verificar cambios en GroupConfig

Fase:
Fase 3 - Mejor templates de respuesta
Objetivo fase:
Personalizar los mensajes de respuesta según la acción ejecutada.
Implementacion fase:
- Crear templates específicos por categoría de acción
- Incluir valores actuales y nuevos en previsualizaciones
- Agregar emojis y formato legible para confirmaciones
- Soportar múltiples idiomas de respuesta

Archivos modificados:
- `app/agent/actions/templates.py`

Validacion

Para validar manualmente:
- Probar "activa la bienvenida" y verificar mensaje: "✅ Mensaje de bienvenida activado"
- Probar dry-run de cambio de texto y verificar mostra: "Texto actual: X → Nuevo: Y"

Fase:
Fase 4 - Fallback y errores helpful
Objetivo fase:
Manejar gracefully casos donde no se puede Parsear o ejecutar una acción.
Implementacion fase:
- Agregar respuestas de fallback cuando no se reconoce la intención
-Sugerir acciones relacionadas basadas en palabras clave
- Proporcionar ayuda contextual cuando falta información
- Implementar modo "sugiere comando" cuando el LLM no está habilitado

Archivos modificados:
- `app/agent/actions/parser.py`
- `app/agent/actions/templates.py`
- `app/agent/core.py`

Validacion

Para validar manualmente:
- Enviar "quiero algo de seguridad" y verificar sugerencia de acciones relacionadas
- Enviar "configura lo del modo noche" sin horario y verificar request de параметр

Fase:
Fase 5 - Testing de integración
Objetivo fase:
Verificar el flujo completo desde NL hasta la ejecución.
Implementacion fase:
- Crear tests de integración para los flujos principales:
  - Activar/desactivar funcionalidades
  - Configurar con parámetros completos
  - dry-run y confirmación
  - Rollback de acciones
- Verificar que el webhook procesa correctamente mensajes NL

Archivos creados:
- `tests/agent/test_actions_integration.py`

Validacion

Ejecutar: pytest tests/agent/test_actions_integration.py

Ejemplos de interacción esperados

Usuario: "Configura un mensaje de bienvenida simple"
Bot: Ejecuta welcome.set_text con texto "Bienvenido al grupo"
Mensaje: "✅ Mensaje de bienvenida configurado"

Usuario: "Activa el antispam"
Bot: Ejecuta antispam.toggle con enabled=True
Mensaje: "✅ Antispam activado"

Usuario: "Ponle captcha de botones a los nuevos"
Bot: Ejecuta captcha.toggle + captcha.configure con modo button
Mensaje: "✅ Captcha configurado en modo botones"

Usuario: "Agrega 'spam' a palabras bloqueadas"
Bot: Ejecuta blocked_words.add con palabra "spam"
Mensaje: "✅ 'spam' agregado a palabras bloqueadas"

Usuario: "Cuantas advertencias max?"
Bot: Consulta max_warnings y responde
Mensaje: "El maximo actual es 3 advertencias"

Archivo de notas técnicas

Dependencias existentes:
- ActionRegistry y ActionExecutor (Fase 1)
- ActionParser con soporte LLM fallback
- GroupConfigService
- ActionPermissionPolicy

Flags de configuración:
- AGENT_ACTIONS_ENABLED
- ACTION_PARSER_LLM_ENABLED
