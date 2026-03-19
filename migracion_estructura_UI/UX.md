Fecha: 2026-03-19
version: v1.0-propuesta
referencia: app/manager_bot (menus, features, menu_engine, callback_router)

Resumen de la migracion:
- Reemplazar los modales de confirmacion (callback.answer con show_alert) por una actualizacion inmediata del texto del menu.
- Centralizar el refresco del menu en un helper comun para todos los features.
- Estandarizar el armado de descripciones/estados (Si/No, Off/Warn/Kick, duraciones, etc.) para reutilizacion transversal.

Arquitectura final:
1. Capa de UI (menus)
   - Cada menu se construye con un builder que recibe config y usa utilidades comunes de formato.
   - El texto del menu refleja el estado real (ej: Eliminacion: Si/No, Castigo: Ban 30m, etc.).
   - Los botones solo disparan callbacks; no muestran modales.

2. Capa de interaccion (features)
   - Cada handler actualiza config, persiste y luego refresca el menu actual.
   - El refresco se hace por un helper comun que reutiliza el MenuEngine.

3. Utilidades comunes
   - Formatters de estado y secciones (Si/No, On/Off, duracion humana, castigo).
   - Helper de refresco de menu (reconstruye menu y edita mensaje).

Componentes propuestos (nuevos/modificados):
- app/manager_bot/_menus/formatters.py
  - yes_no(value) -> "Si/No"
  - on_off(value) -> "Activado/Desactivado"
  - action_label(action, mute_sec, ban_sec)
  - duration_label(seconds)

- app/manager_bot/_menus/rendering.py
  - build_title(base_title, sections: list[str]) -> str
  - build_section(label, value) -> "{label}: {value}"

- app/manager_bot/_features/base.py (extender)
  - async def update_config_and_refresh(self, callback, bot, menu_id, updater_fn):
      * obtener config (o default)
      * updater_fn(config)
      * persistir
      * refrescar menu (menu_engine.show_menu_by_callback)
      * callback.answer() sin texto

- app/manager_bot/_transport/telegram/menu_engine.py
  - reutilizar show_menu_by_callback para refrescar UI (ya existe)

Flujo objetivo (sin modal):
1. Usuario pulsa boton.
2. Handler aplica cambios en config.
3. Se persiste config.
4. Se reconstruye menu con config actualizada.
5. Se edita el mensaje con el nuevo texto y botones.
6. callback.answer() silencioso (sin show_alert).

Ejemplo aplicado (Antispan Telegram):
- Boton "Borrar los Mensajes":
  - Antes: modal "Castigo actualizado".
  - Despues: se actualiza el texto del menu:
    "Eliminacion: Si" -> "Eliminacion: No" (o viceversa) y se redibuja el teclado.

Propuesta de fases:
Fase 1 - Infraestructura comun
- Objetivo fase:
  - Crear helpers reutilizables para refresco de menu y formateo de estados.
- Implementacion fase:
  - Crear `formatters.py` y `rendering.py`.
  - Agregar `update_config_and_refresh` en `FeatureModule`.
  - Definir convenciones de texto (Si/No, Off/Warn/Kick, etc.).

Fase 2 - Piloto en menus criticos
- Objetivo fase:
  - Validar UX sin modales en menus con alta frecuencia (antispam/antiflood).
- Implementacion fase:
  - Refactor antispam/antiflood para usar `update_config_and_refresh`.
  - Remover `callback.answer(..., show_alert=True)` en acciones de exito.
  - Ajustar titulos para reflejar estado actual (castigo, eliminacion, duraciones).

Fase 3 - Escalado al resto de menus
- Objetivo fase:
  - Unificar comportamiento UX en welcome, filters, nightmode, etc.
- Implementacion fase:
  - Migrar handlers restantes al helper comun.
  - Aplicar formatters comunes en todas las descripciones.

Fase 4 - Limpieza y estandarizacion
- Objetivo fase:
  - Eliminar duplicacion y asegurar consistencia.
- Implementacion fase:
  - Quitar helpers locales duplicados.
  - Documentar patrones de menus y estados.
  - Actualizar tests para validar que el menu renderizado refleja config.

Consideraciones adicionales:
- Mostrar modales solo para errores (ej: permisos insuficientes, parseos invalidos).
- Mantener UI reactiva: preferir edit_message_text siempre que sea posible.
- Evitar mensajes nuevos innecesarios para no ensuciar el chat.

Impacto esperado:
- UX mas clara: el usuario ve el estado actualizado en el mismo menu.
- Menos friccion: sin ventanas modales repetitivas.
- Codigo mas modular y reutilizable para nuevos menus.
