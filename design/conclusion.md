Conclusión única y próximo paso inmediato

Decisión única (resumen ejecutivo):
- Migrar a una arquitectura modular API-first con un Adapter de Telegram (`aiogram`), Postgres+pgvector para MVP, Ollama local + OpenAI fallback, y Redis para caching/queues. Priorizar entrega rápida del MVP (Telegram bot funcionando en 1-2 semanas) y luego modularizar el código para producción.

Por qué esta decisión:
- Máximo equilibrio entre velocidad de salida al mercado, control de costes y camino claro hacia escala y agentización.

Próximo paso inmediato (hacer ahora):
1. Añadir `telegram_adapter.py` que conecte Telegram con la API (`/api/v1/chat`) o invoque `Actor` directamente.
2. Crear `requirements.txt` y un `Dockerfile` mínimo.
3. Ejecutar `python chatbot_monolith.py --mode api` y correr el adapter en paralelo (o en Docker Compose).

Comandos rápidos para MVP (local):

- Instalar dependencias:
```
pip install -r requirements.txt
```

- Ejecutar API:
```
python chatbot_monolith.py --mode api
```

- Ejecutar adapter (en otra terminal):
```
python telegram_adapter.py
```

Entrega: ver los ficheros en `design/` para detalles técnicos y el scaffold `telegram_adapter.py` en la raíz.
