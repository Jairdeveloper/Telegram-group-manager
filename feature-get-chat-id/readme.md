# Feature: Obtener `chat_id` desde un update de Telegram

Este pequeño recurso explica cómo usar el script `scripts/get_chat_id.py` para extraer el `chat_id` de un payload (update) de Telegram, y además describe un flujo de trabajo Git sencillo (para principiantes) usando las ramas `dev`, `feature/*` y `main`.

## Uso del script

- Lectura desde archivo:

```bash
python scripts/get_chat_id.py sample_update.json
```

- Lectura desde stdin (útil para piping):

```bash
cat sample_update.json | python scripts/get_chat_id.py
```

El script imprimirá una línea como:

```
CHAT_ID: 123456789
```

## Formato esperado
El script busca `message` o `edited_message` en la raíz del JSON y extrae `message["chat"]["id"]`.

Ejemplo mínimo de `sample_update.json`:

```json
{
  "update_id": 99999,
  "message": {
    "message_id": 1,
    "from": {"id": 111, "is_bot": false, "first_name": "You"},
    "chat": {"id": 123456789, "type": "private"},
    "date": 1234567890,
    "text": "hola"
  }
}
```

## Flujo Git (para principiantes)

Objetivo: mantener `main` como la rama estable/lista para producción, `dev` como integración y ramas `feature/<nombre>` para desarrollar nuevas funcionalidades.

1. Preparación local (una única vez):

```bash
git clone <repo-url>
cd <repo>
# Obtener ramas remotas
git fetch origin
```

2. Crear una rama feature desde `dev`:

```bash
# Asegúrate de estar en dev y actualizada
git checkout dev
#subir rama a remoto
git push -u origin dev
git pull origin dev
# Crear la rama de feature
git checkout -b feature/get-chat-id
```

3. Trabajar en la feature:

- Hacer cambios pequeños y commits limpios.

```bash
git add scripts/get_chat_id.py feature-get-chat-id/readme.md
git commit -m "feat: add helper to extract chat_id from telegram update"
```

4. Publicar la rama y abrir un Pull Request (PR):

```bash
git push -u origin feature/get-chat-id
# Luego, en la plataforma (GitHub/GitLab), abre un PR hacia la rama `dev`.
```

5. Revisión y merge a `dev`:

- Pide revisión, corrige comentarios, y una vez aprobado, haz merge en `dev` (usualmente mediante la interfaz web).
- Alternativamente, si tienes permiso y quieres hacerlo por CLI:

```bash
# desde dev actualizada
git checkout dev
git pull origin dev
git merge --no-ff feature/get-chat-id
git push origin dev
```

6. Política para pasar a `main` (release):

- Cuando `dev` esté estable y listo para release, crea una rama `release/vX.Y` desde `dev`, prueba, y luego mergea a `main`.
- Taggea la versión y despliega desde `main`.

Ejemplo rápido:

```bash
# desde dev
git checkout dev
git pull origin dev
git checkout -b release/v0.1.0
# pruebas y ajustes
git push -u origin release/v0.1.0
# en web: merge release -> main
# luego en local
git checkout main
git pull origin main
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

7. Hotfix (corrección urgente):

- Crear rama desde `main`: `hotfix/issue-123`, arreglar, merge a `main` y `dev`.

## Buenas prácticas (sencillas)

- Commits pequeños y mensajes claros.
- Abrir PRs hacia `dev`, no hacia `main` directamente.
- Mantener ramas de feature cortas-living (merge pronto).
- Ejecutar pruebas locales antes de pedir revisión.

---

Si quieres, puedo añadir un ejemplo de pipeline CI sencillo (GitHub Actions) para ejecutar tests y lint automáticamente al abrir PRs.