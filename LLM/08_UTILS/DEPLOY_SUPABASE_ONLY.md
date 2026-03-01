# Despliegue: Usar solo Supabase (nota sobre limitaciones)

Esta sección explica las opciones para "mantener todo en Supabase" y las limitaciones prácticas para una app Python/ FastAPI.

Resumen rápido
 - Supabase es excelente como backend de datos (Postgres, Auth, Storage) y para funciones Edge (Deno/TypeScript).
 - Actualmente Supabase Edge Functions no ejecutan Python (están basadas en Deno/Edge runtime), por lo que no pueden hospedar directamente un servicio FastAPI.

Opciones para aproximarse a "todo en Supabase":

Opción A — Supabase solo para datos; app en contenedor externo (recomendado)
  - Usar Supabase para Postgres (pgvector) y Auth.
  - Hospedar la app FastAPI en Render / Fly / Railway / GH Actions runner; conectar a Supabase vía `DATABASE_URL`.
  - Ventaja: arquitectura clara y robusta.

Opción B — Usar Edge Functions de Supabase para partes pequeñas
  - Mantener la lógica pesadas (FastAPI) en un contenedor y mover endpoints ligeros/rápidos a Edge Functions (JS/TS) si conviene.
  - Ejemplo: un endpoint que valida un token o ejecuta una transformación simple puede ser Edge Function.

Opción C — (Self-host) desplegar contenedor junto a Supabase (no nativo)
  - Si tu proveedor lo permite, crear una VM/Compute y ejecutar tanto Supabase Local (self-host) y tu contenedor; esto no aplica para Supabase Cloud gestionada.

Pasos recomendados (flujo práctico)
 1. Crear proyecto Supabase y habilitar `pgvector`.
 2. Mantener la app FastAPI en un contenedor y desplegar en Render/Fly/Railway.
 3. Proteger las claves y usar `SUPABASE_KEY` service role desde el backend.
 4. Si necesitas funciones edge, implementarlas en `supabase/functions` (JS/TS) y desplegarlas con `supabase` CLI.

Conclusión
 - Si tu aplicación principal es Python/FastAPI, la mejor práctica es usar Supabase para datos y usar un proveedor de contenedores para la app. "Todo en Supabase" solo es factible si reescribes la lógica como funciones Edge (Deno/TS).
