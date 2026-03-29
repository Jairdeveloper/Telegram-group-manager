# Habilitando LLM para mejor inferencia

El bot ahora tiene **habilitado el LLM** para entender mejor el lenguaje natural.

## Cambio realizado

En `app/webhook/handlers.py`:
```python
# Antes
parser = ActionParser(llm_enabled=False)

# Ahora
parser = ActionParser(llm_enabled=True)
```

## Cómo funciona

El parser ahora:
1. **Primero**: Intenta rule-based (patrones simples)
2. **Si no coincide**: Usa el LLM para inferir la intención

## Requisitos para que funcione

### Opción 1: Ollama (local, recomendado para desarrollo)

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar Ollama
ollama serve

# Descargar modelo
ollama pull llama3
```

### Opción 2: OpenAI (producción)

Configurar variables de entorno:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-tu-api-key-aqui
```

O en el archivo `.env`:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-tu-api-key-aqui
```

## Pruebas

Con LLM habilitado, el bot puede entender frases como:
- "Quiero poner un mensaje de bienvenida"
- "Cambia el welcome"
- "Setup welcome message"
- "Ponle la bienvenida"
- "Quítale el antiflood"
- "Activa lo del spam"

## Fallback

Si el LLM no está disponible, el sistema vuelve al parser rule-based.

## Notas

- El LLM es más lento que el parser rule-based
- Tiene un costo si usas OpenAI
- Para desarrollo local, Ollama es gratuito
