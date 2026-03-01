# 🧠 Brain Manager Server - Guía Completa

El **Brain Server** es un nuevo modo que convierte `get_default_brain()` en un servidor REST completo para gestionar patrones y respuestas del chatbot de forma dinámica.

---

## 📋 Inicio Rápido

### 1. Ejecutar el servidor

```bash
python chatbot_monolith.py --mode brain
```

**Salida esperada:**
```
======================================================================
🧠 BRAIN MANAGER SERVER
======================================================================
✅ Server running at http://127.0.0.1:8000
📖 Swagger docs: http://127.0.0.1:8000/docs
📋 ReDoc: http://127.0.0.1:8000/redoc

📌 Endpoints principales:
   GET    /api/v1/brain/patterns       - Listar patrones
   POST   /api/v1/brain/patterns       - Crear patrón
   GET    /api/v1/brain/patterns/{i}   - Obtener patrón
   PUT    /api/v1/brain/patterns/{i}   - Actualizar patrón
   DELETE /api/v1/brain/patterns/{i}   - Eliminar patrón
   GET    /api/v1/brain/defaults       - Listar respuestas default
   POST   /api/v1/brain/defaults       - Agregar respuesta default
   GET    /api/v1/brain/export/python  - Exportar como Python
   GET    /api/v1/brain/export/json    - Exportar como JSON
======================================================================
```

### 2. Abrir Swagger UI

Abre tu navegador en:
```
http://localhost:8000/docs
```

---

## 📡 Endpoints Disponibles

### 🔍 Health Check

```bash
GET /health
```

**Respuesta:**
```json
{
  "status": "ok",
  "service": "brain-manager"
}
```

---

### 📊 Metadatos

```bash
GET /api/v1/brain/metadata
```

**Retorna:**
```json
{
  "total_patterns": 30,
  "total_defaults": 8,
  "version": "1.0"
}
```

---

## 🎯 Gestión de Patrones (CRUD)

### Listar todos los patrones

```bash
curl -X GET "http://localhost:8000/api/v1/brain/patterns"
```

**Con paginación:**
```bash
curl -X GET "http://localhost:8000/api/v1/brain/patterns?limit=5&offset=0"
```

**Respuesta:**
```json
{
  "total": 30,
  "count": 30,
  "patterns": [
    {
      "pattern": ["hello", 0],
      "response": ["Hello!", "It's", "nice", "to", "meet", "you"]
    },
    ...
  ]
}
```

---

### Obtener un patrón específico

```bash
curl -X GET "http://localhost:8000/api/v1/brain/patterns/0"
```

**Respuesta:**
```json
{
  "index": 0,
  "pattern": ["hello", 0],
  "response": ["Hello!", "It's", "nice", "to", "meet", "you"]
}
```

---

### Crear un nuevo patrón

```bash
curl -X POST "http://localhost:8000/api/v1/brain/patterns" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": ["i", "love", [1, "thing"]],
    "response": [[1, "thing"], "is", "amazing!"]
  }'
```

**Respuesta:**
```json
{
  "status": "created",
  "index": 30,
  "pattern": ["i", "love", [1, "thing"]],
  "response": [[1, "thing"], "is", "amazing!"]
}
```

---

### Actualizar un patrón existente

```bash
curl -X PUT "http://localhost:8000/api/v1/brain/patterns/5" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": ["hey", "bot"],
    "response": ["Yes,", "what", "do", "you", "need?"]
  }'
```

**Respuesta:**
```json
{
  "status": "updated",
  "index": 5,
  "pattern": ["hey", "bot"],
  "response": ["Yes,", "what", "do", "you", "need?"]
}
```

---

### Eliminar un patrón

```bash
curl -X DELETE "http://localhost:8000/api/v1/brain/patterns/5"
```

**Respuesta:**
```json
{
  "status": "deleted",
  "index": 5
}
```

---

### Buscar patrones por palabra clave

```bash
curl -X GET "http://localhost:8000/api/v1/brain/patterns/search?q=hello"
```

**Respuesta:**
```json
{
  "query": "hello",
  "results": [
    {
      "index": 0,
      "pattern": ["hello", 0],
      "response": ["Hello!", "It's", "nice", "to", "meet", "you"]
    }
  ],
  "count": 1
}
```

---

## 💬 Gestión de Respuestas Default

### Listar respuestas default

```bash
curl -X GET "http://localhost:8000/api/v1/brain/defaults"
```

**Respuesta:**
```json
{
  "total": 8,
  "defaults": [
    ["That's", "interesting,", "tell", "me", "more"],
    ["I", "see.", "Could", "you", "elaborate?"],
    ...
  ]
}
```

---

### Agregar una respuesta default

```bash
curl -X POST "http://localhost:8000/api/v1/brain/defaults" \
  -H "Content-Type: application/json" \
  -d '{
    "response": ["Tell", "me", "more", "about", "that!"]
  }'
```

**Respuesta:**
```json
{
  "status": "created",
  "index": 8,
  "response": ["Tell", "me", "more", "about", "that!"]
}
```

---

### Eliminar una respuesta default

```bash
curl -X DELETE "http://localhost:8000/api/v1/brain/defaults/3"
```

**Respuesta:**
```json
{
  "status": "deleted",
  "index": 3
}
```

---

## 💾 Exportación

### Exportar como código Python

```bash
curl -X GET "http://localhost:8000/api/v1/brain/export/python"
```

**Respuesta:**
```json
{
  "format": "python",
  "code": "def get_default_brain() -> tuple:\n    \"\"\"Brain exportado desde servidor\"\"\"\n\n    pattern_responses = [\n        [['hello', 0], ['Hello!', \"It's\", 'nice', 'to', 'meet', 'you']],\n        ...\n    ]\n\n    default_responses = [\n        [\"That's\", \"interesting,\", \"tell\", \"me\", \"more\"],\n        ...\n    ]\n\n    return pattern_responses, default_responses\n",
  "filename": "get_default_brain.py"
}
```

---

### Exportar como JSON

```bash
curl -X GET "http://localhost:8000/api/v1/brain/export/json"
```

**Retorna el archivo completo `brain_data.json`**

---

## 🐍 Ejemplo Python - Cliente

```python
import requests
import json

BASE_URL = "http://localhost:8000"

class BrainClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def get_all_patterns(self):
        """Obtiene todos los patrones"""
        response = requests.get(f"{self.base_url}/api/v1/brain/patterns")
        return response.json()
    
    def get_pattern(self, index):
        """Obtiene un patrón específico"""
        response = requests.get(f"{self.base_url}/api/v1/brain/patterns/{index}")
        return response.json()
    
    def create_pattern(self, pattern, response):
        """Crea nuevo patrón"""
        data = {"pattern": pattern, "response": response}
        resp = requests.post(
            f"{self.base_url}/api/v1/brain/patterns",
            json=data
        )
        return resp.json()
    
    def update_pattern(self, index, pattern, response):
        """Actualiza patrón"""
        data = {"pattern": pattern, "response": response}
        resp = requests.put(
            f"{self.base_url}/api/v1/brain/patterns/{index}",
            json=data
        )
        return resp.json()
    
    def delete_pattern(self, index):
        """Elimina patrón"""
        response = requests.delete(f"{self.base_url}/api/v1/brain/patterns/{index}")
        return response.json()
    
    def search_patterns(self, keyword):
        """Busca patrones"""
        response = requests.get(
            f"{self.base_url}/api/v1/brain/patterns/search",
            params={"q": keyword}
        )
        return response.json()

# Uso
if __name__ == "__main__":
    client = BrainClient()
    
    # Listar patrones
    patterns = client.get_all_patterns()
    print(f"Total de patrones: {patterns['total']}")
    
    # Crear patrón nuevo
    new_pattern = client.create_pattern(
        pattern=["i", "am", [1, "mood"]],
        response=["That's", "great", "that", "you're", [1, "mood"]]
    )
    print(f"Patrón creado en índice: {new_pattern['index']}")
    
    # Buscar patrón
    results = client.search_patterns("hello")
    print(f"Patrones encontrados: {results['count']}")
    
    # Actualizar patrón
    updated = client.update_pattern(
        index=0,
        pattern=["hello", "there", 0],
        response=["Hello!", "Nice", "to", "see", "you"]
    )
    print(f"Patrón actualizado: {updated['status']}")
    
    # Eliminar patrón
    deleted = client.delete_pattern(5)
    print(f"Patrón eliminado: {deleted['status']}")
```

---

## 🌐 Ejemplo JavaScript - Cliente

```javascript
const BASE_URL = "http://localhost:8000";

class BrainClient {
  constructor(baseUrl = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getAllPatterns() {
    const response = await fetch(`${this.baseUrl}/api/v1/brain/patterns`);
    return response.json();
  }

  async getPattern(index) {
    const response = await fetch(`${this.baseUrl}/api/v1/brain/patterns/${index}`);
    return response.json();
  }

  async createPattern(pattern, response) {
    const res = await fetch(`${this.baseUrl}/api/v1/brain/patterns`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pattern, response })
    });
    return res.json();
  }

  async updatePattern(index, pattern, response) {
    const res = await fetch(`${this.baseUrl}/api/v1/brain/patterns/${index}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pattern, response })
    });
    return res.json();
  }

  async deletePattern(index) {
    const res = await fetch(`${this.baseUrl}/api/v1/brain/patterns/${index}`, {
      method: "DELETE"
    });
    return res.json();
  }

  async searchPatterns(keyword) {
    const response = await fetch(
      `${this.baseUrl}/api/v1/brain/patterns/search?q=${keyword}`
    );
    return response.json();
  }
}

// Uso
const client = new BrainClient();

// Ejemplo: Crear patrón nuevo
client.createPattern(
  ["i", "want", [1, "thing"]],
  [[1, "thing"], "is", "a", "great", "choice!"]
).then(result => {
  console.log("Patrón creado:", result);
});

// Ejemplo: Buscar
client.searchPatterns("hello").then(results => {
  console.log("Resultados:", results);
});
```

---

## 📦 Archivo de Persistencia

Todos los cambios se guardan automáticamente en:

```
brain_data.json
```

**Estructura:**
```json
{
  "pattern_responses": [
    {
      "pattern": ["hello", 0],
      "response": ["Hello!", "It's", "nice", "to", "meet", "you"]
    }
  ],
  "default_responses": [
    ["That's", "interesting,", "tell", "me", "more"]
  ],
  "metadata": {
    "total_patterns": 30,
    "total_defaults": 8,
    "version": "1.0"
  }
}
```

---

## 🔄 Casos de Uso

### 1. **Administración Web**
Crea un panel web que se conecte al Brain Server para editar patrones sin tocar código.

### 2. **Sincronización Multi-Instancia**
Sincroniza patrones entre múltiples instancias del chatbot.

### 3. **Entrenamiento Dinámico**
Agrega patrones nuevos basados en feedback de usuarios.

### 4. **Versionamiento**
Exporta el brain como JSON/Python y versiona en Git.

### 5. **Análisis**
Analiza patrones más usados, tasa de éxito, etc.

---

## ⚙️ Configuración

En `Settings` puedes ajustar:

```python
API_HOST = "127.0.0.1"        # Cambiar a "0.0.0.0" para acceso remoto
API_PORT = 8000               # Puerto del servidor
LOG_LEVEL = "INFO"            # INFO, DEBUG, WARNING, ERROR
```

---

## 📝 Notas

- Los cambios se persisten automáticamente en `brain_data.json`
- El servidor carga datos default si `brain_data.json` no existe
- La API es completamente RESTful y sigue estándares HTTP
- Todos los endpoints incluyen validación de entrada
- Use Swagger UI para pruebas interactivas

---

## 🎓 Próximos Pasos

1. **Ejecutar el servidor**: `python chatbot_monolith.py --mode brain`
2. **Visitar Swagger**: `http://localhost:8000/docs`
3. **Probar endpoints**: Usar la interfaz interactiva de Swagger
4. **Integrar cliente**: Usar los ejemplos Python/JavaScript

¡El Brain Server está listo para usar! 🚀
