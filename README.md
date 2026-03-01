# Robot Chatbot

## Testing

- Run all tests locally:

```bash
pytest -q
```

Current suite covers:
- Unit tests for `chat_service` (`PatternEngine`, `Agent`)
- API contract tests for `/api/v1/chat`
- Webhook contract tests (`/webhook/{token}`, dedup, token validation)
- Ingress rewrite regression checks
- Modular entrypoint checks for `app/api` and `app/webhook`

## CI

The CI workflow is in:
- `.github/workflows/ci.yml`

It runs on `pull_request` and `push`, and executes:
1. Python 3.11 setup
2. `pip install -r requirements.txt`
3. `pytest -q`

## Modular structure (current migration state)

- `app/api`
  - `factory.py`: FastAPI app factory
  - `routes.py`: `/api/v1/chat`, `/api/v1/history/{session_id}`, `/api/v1/stats`
- `app/webhook`
  - `entrypoint.py`: wrapper to expose the webhook app while preserving current runtime compatibility

`chatbot_monolith.py` now delegates API app creation to `app/api`.

## Branch protection (manual GitHub step)

Configure in repository settings:
1. Require pull request before merging
2. Require status check `pytest`