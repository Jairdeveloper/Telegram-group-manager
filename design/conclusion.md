ConclusiÃ³n Ãºnica y prÃ³ximo paso inmediato

DecisiÃ³n Ãºnica (resumen ejecutivo):
- Migrar a una arquitectura modular API-first con un Adapter de Telegram (`aiogram`), Postgres+pgvector para MVP, Ollama local + OpenAI fallback, y Redis para caching/queues. Priorizar entrega rÃ¡pida del MVP (Telegram bot funcionando en 1-2 semanas) y luego modularizar el cÃ³digo para producciÃ³n.

Por quÃ© esta decisiÃ³n:
- MÃ¡ximo equilibrio entre velocidad de salida al mercado, control de costes y camino claro hacia escala y agentizaciÃ³n.

PrÃ³ximo paso inmediato (hacer ahora):
1. AÃ±adir `telegram_adapter.py` que conecte Telegram con la API (`/api/v1/chat`) o invoque `Actor` directamente.
2. Crear `requirements.txt` y un `Dockerfile` mÃ­nimo.
3. Ejecutar `uvicorn app.api.entrypoint:app --host 0.0.0.0 --port 8000` y correr el adapter en paralelo (o en Docker Compose).

Comandos rÃ¡pidos para MVP (local):

- Instalar dependencias:
```
pip install -r requirements.txt
```

- Ejecutar API:
```
uvicorn app.api.entrypoint:app --host 0.0.0.0 --port 8000
```

- Ejecutar adapter (en otra terminal):
```
python telegram_adapter.py
```

Entrega: ver los ficheros en `design/` para detalles tÃ©cnicos y el scaffold `telegram_adapter.py` en la raÃ­z.


