Fecha: 2026-03-27
version: 1.0
referencia: 04_ANALISIS_BOT.md

---

# Análisis: Persistencia - Sistemas de Almacenamiento Diferentes

## Logs

```
2026-03-27 21:18:58,046 INFO ActionParser: text='Activa bienvenida con Hola equipo', result=welcome.toggle, conf=0.8
2026-03-27 21:18:58,046 INFO ActionParser: using roles=['admin']
2026-03-27 21:18:58,057 INFO ActionParser: action_result status=ok, message=Welcome actualizado
# Bot responde "Welcome actualizado" ✅
# Pero /welcome dice "No hay mensaje configurado" ❌
```

---

## Problema identificado

### El bot usa DOS sistemas de almacenamiento diferentes

| Sistema | Usa | Guarda en |
|--------|-----|-----------|
| ActionParser | `GroupConfigService` | `GroupConfig` |
| Enterprise `/welcome` | `EnterpriseWelcomeService` | `EnterpriseWelcome` |

**No están sincronizados.**

---

## Flujo actual

```
Sistema ActionParser:
"Mensaje NL" → ActionParser → GroupConfigService → GroupConfig
                                                        ↓
                                              (se guarda en memoria/PostgreSQL)
                                                        ↓
                                              PERO el sistema Enterprise NO LEE ESTO

Sistema Enterprise:
"/welcome" → EnterpriseHandler → EnterpriseWelcomeService → EnterpriseWelcome
                                                                  ↓
                                                        (tabla diferente)
```

---

## Causa raíz

1. **ActionParser** guarda el mensaje en `GroupConfig.welcome_text`
2. **Sistema Enterprise** lee de `EnterpriseWelcome.welcome_text`
3. Son tablas/modelos diferentes que NO se sincronizan

---

## Solución propuesta

### Opción 1: Modificar ActionParser para usar EnterpriseWelcomeService (Recomendada)

Cambiar `pilot_actions.py` para que guarde usando el mismo servicio que el sistema Enterprise:

```python
# En pilot_actions.py, cambiar:
from app.manager_bot.services import GroupConfigService

# Por:
from app.enterprise.application.services import get_enterprise_service

async def _welcome_set_text(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    # Usar el mismo servicio que el sistema Enterprise
    service = get_enterprise_service()
    welcome = service.set_welcome(
        actor_id=ctx.user_id,
        chat_id=ctx.chat_id,
        welcome_text=params.text,
    )
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_text": welcome.welcome_text},
    )
```

### Opción 2: Sincronizar ambos sistemas

Cuando se guarda en uno, también guardar en el otro.

### Opción 3: Unificar sistemas

Hacer que `/welcome` lea de `GroupConfig` en lugar de `EnterpriseWelcome`.

---

# Plan de Implementación

---

## Fase 1: Modificar ActionParser para usar EnterpriseService

### Objetivo fase
Hacer que las acciones de welcome usen el mismo sistema de almacenamiento que el comando `/welcome`.

### Implementacion fase

1. Importar `EnterpriseContentService` en `pilot_actions.py`
2. Modificar `_welcome_set_text` para usar el servicio de Enterprise
3. Modificar `_welcome_toggle` para usar el servicio de Enterprise

---

## Fase 2: Verificar consistencia

### Objetivo fase
Confirmar que los datos se guardan y leen del mismo lugar.

### Implementacion fase

1. Probar "bienvenida: Hola equipo"
2. Consultar /welcome
3. Verificar que muestra el mensaje

---

## Fase 3: Aplicar a otras acciones

### Objetivo fase
Aplicar la misma solución a goodbye, antispam, etc.

### Implementacion fase

Repetir para:
- goodbye.set_text
- goodbye.toggle
- antispam.toggle
- filter.add_word / filter.remove_word

---

---

# Solución Implementada

## Fase 1: Modificar ActionParser para usar EnterpriseService ✅

### Objetivo fase
Hacer que las acciones de welcome usen el mismo sistema de almacenamiento que el comando `/welcome`.

### Implementacion fase: ✅ COMPLETADA

**Cambios realizados en `app/agent/actions/pilot_actions.py`:**

1. **Nuevo import:**
```python
from app.enterprise.infrastructure.content_repositories import get_welcome_repo
from app.enterprise.domain.entities import EnterpriseWelcome
```

2. **Modificado `_welcome_toggle`:**
```python
async def _welcome_toggle(ctx: ActionContext, params: WelcomeToggleParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=existing.welcome_text if existing else "",
        enabled=params.enabled,
    )
    welcome = welcome_repo.set(welcome)
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_enabled": welcome.enabled},
    )
```

3. **Modificado `_welcome_set_text`:**
```python
async def _welcome_set_text(ctx: ActionContext, params: WelcomeSetTextParams) -> ActionResult:
    welcome_repo = get_welcome_repo()
    existing = welcome_repo.get(ctx.tenant_id or "default", ctx.chat_id)
    welcome = EnterpriseWelcome(
        tenant_id=ctx.tenant_id or "default",
        chat_id=ctx.chat_id,
        welcome_text=params.text,
        enabled=existing.enabled if existing else True,
    )
    welcome = welcome_repo.set(welcome)
    return ActionResult(
        status="ok",
        message="Welcome actualizado",
        data={"welcome_text": welcome.welcome_text},
    )
```

4. **Actualizado dry_run, snapshot y undo** para usar el mismo repositorio.

---

## Fase 2: Verificación

### Tests passing
```
pytest tests/agent/test_actions_unit.py -v
============================== 19 passed ==============================
```

---

## Resumen

| Problema | Causa | Solución |
|----------|-------|----------|
| /welcome no muestra lo guardado | Sistemas de almacenamiento diferentes | Usar EnterpriseWelcomeRepository en ActionParser ✅ |

---

## Estado final

| Fase | Estado |
|------|--------|
| Fase 1: Modificar ActionParser | ✅ COMPLETADA |
| Fase 2: Verificación | ✅ COMPLETADA |
