# Casos de Uso - Configuración de Destinatarios de Reportes

## Casos de Uso

### Caso 1: Configurar envío al fundador

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de reportes
2. Selecciona "📤 Destinatario: 🚫 Ninguno"
3. Selecciona "👑 Enviar al fundador"
4. El sistema guarda la configuración
5. A partir de ahora, los reportes se enviarán al fundador

**Resultado esperado:**
- El menú muestra "📤 Destinatario: 👑 Fundador"
- Los nuevos reportes tienen `recipients = [founder_id]`

---

### Caso 2: Configurar envío al grupo staff

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de reportes
2. Selecciona "📤 Destinatario: 🚫 Ninguno"
3. Selecciona "👥 Enviar al grupo Staff"
4. El sistema guarda la configuración

**Resultado esperado:**
- El menú muestra "📤 Destinatario: 👥 Grupo Staff"
- Los nuevos reportes tienen `recipients = [staff_ids]`

---

### Caso 3: Desactivar destinatarios

**Actor:** Administrador del grupo

**Flujo:**
1. El administrador accede al menú de reportes
2. Selecciona "📤 Destinatario: 👑 Fundador"
3. Selecciona "❌ Desactivar"
4. El sistema guarda la configuración

**Resultado esperado:**
- Los nuevos reportes tienen `recipients = []` (aunque la configuración sea "fundador")
- El menú muestra estado "❌ Desactivado"

---

### Caso 4: Crear reporte con destinatarios

**Actor:** Usuario del grupo

**Flujo:**
1. El usuario ejecuta `/report @usuario spam`
2. El sistema crea el reporte
3. El sistema consulta la configuración de destinatarios
4. El sistema guarda los destinatarios en el reporte
5. El sistema notifica a los destinatarios configurados

**Resultado esperado:**
- Reporte creado con `recipients` según configuración
- Notificaciones enviadas solo a los destinatarios configurados

---

## Ejemplos de Configuración

### Configuración 1: Grupo sin founder

```python
config.report_destination = "fundador"
# founder_id = None
# staff_ids = [200, 300]

# Resultado:
recipients = []  # No se envía a nadie (no hay founder)
```

### Configuración 2: Grupo con founder y staff

```python
config.report_destination = "fundador"
# founder_id = 100
# staff_ids = [200, 300]

# Resultado:
recipients = [100]  # Solo al founder
```

### Configuración 3: Grupo con staff

```python
config.report_destination = "grupo_staff"
# founder_id = 100
# staff_ids = [200, 300]

# Resultado:
recipients = [200, 300]  # Solo al staff
```

---

## Diagramas de Flujo

### Flujo de creación de reporte

```
Usuario ejecuta /report
        ↓
ReportsFeature.create_report()
        ↓
ReportsConfigService.get_destination_recipients()
        ↓
┌───────────────────────────────────────┐
│  ¿report_destination_enabled?         │
│  Si → Continuar                        │
│  No → recipients = []                  │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│  Según report_destination:             │
│  - ninguno:   recipients = []        │
│  - fundador:  recipients = [founder_id]│
│  - grupo_staff: recipients = staff_ids│
└───────────────────────────────────────┘
        ↓
Report.recipients = recipients
        ↓
ReportRepository.save() → BD
        ↓
Notificaciones a recipients
```

### Flujo de configuración

```
Admin accede al menú de reportes
        ↓
Selecciona "📤 Destinatario"
        ↓
reports:config:dest callback
        ↓
Muestra menú de destinos
        ↓
Admin selecciona opción
        ↓
reports:config:set:{tipo} callback
        ↓
ReportsConfigService.set_destination()
        ↓
Guarda en ConfigStorage
        ↓
Confirma al usuario
```

---

## Notas de Implementación

1. La configuración se guarda por chat_id
2. Los destinatarios se calculan al momento de crear el reporte
3. Si el founder_id no existe, se retorna lista vacía
4. Si staff_ids está vacío, se retorna lista vacía
5. La funcionalidad puede desactivarse sin perder la configuración