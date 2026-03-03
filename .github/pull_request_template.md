## Resumen

<!-- Describe brevemente el objetivo tecnico del PR -->

## Checklist DoD (Bloques 1-5)

- [ ] CI ejecuta `pytest -q` en `pull_request`.
- [ ] Branch protegida con:
  - [ ] Require a pull request before merging.
  - [ ] Required status check `pytest`.
- [ ] API y Webhook desacoplados en `app/api` y `app/webhook`.
- [ ] Contratos sin regresion:
  - [ ] `/api/v1/chat`
  - [ ] `/webhook/{token}` (token + dedup)
- [ ] Suite local en verde (`pytest -q`).
- [ ] README actualizado (tests, CI, estructura modular).
- [ ] Documento de migracion actualizado (`LLM/04_task.md/MIGRACION_SEMANA_2_3.md`).

## Riesgos pendientes

- [ ] Branch protection pendiente en GitHub UI.
- [ ] Dedup en memoria no distribuido cuando no hay Redis.
- [ ] Debt tecnico: migrar `datetime.utcnow()` a fecha timezone-aware.
- [ ] Otros riesgos identificados en este PR:
  - [ ] N/A

## Evidencia

<!-- Pegar salida resumida de pytest o capturas de checks -->
- `pytest -q`: <!-- ejemplo: 14 passed -->
