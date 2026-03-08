# Implementación Semana 4-5: Migración Storage JSON → Postgres

## Objetivo

Migrar el almacenamiento de `SimpleConversationStorage` (JSON en archivo) a PostgreSQL con repositorio por tenant, manteniendo compatibilidad y sin downtime.

## Estado Actual

- **Storage actual**: `chat_service/storage.py` → `SimpleConversationStorage` usa `conversations.json`
- **Sin**: SQLAlchemy, Postgres, modelos ORM
- **Settings**: `database_url` definido en `ApiSettings` pero no usado

---

## Fase 1: Setup Postgres y SQLAlchemy (Semana 4)

### Tareas

1. **Añadir dependencias**
   ```bash
   pip install sqlalchemy asyncpg psycopg2-binary alembic
   ```

2. **Configurar settings**
   - Actualizar `app/config/settings.py`:
     ```python
     class ApiSettings(BaseSettings):
         database_url: str = "postgresql://user:pass@localhost:5432/chatbot"
     ```

3. **Crear base de datos**
   ```sql
   CREATE DATABASE chatbot;
   ```

### Implementación

**`app/config/settings.py`**:
```python
class ApiSettings(BaseSettings):
    # ... existing fields
    database_url: str = "postgresql://user:pass@localhost:5432/chatbot"
```

---

## Fase 2: Modelos SQLAlchemy (Semana 4)

### Modelos a crear

**`app/database/models.py`**:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True, default="default")
    session_id = Column(String, index=True)
    user_message = Column(Text)
    bot_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})
```

---

## Fase 3: Repositorios (Semana 4-5)

### Interfaz de Repository

**`app/repositories/conversation_repository.py`**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

class ConversationRepository(ABC):
    @abstractmethod
    def save_message(self, tenant_id: str, session_id: str, user_message: str, bot_response: str, metadata: dict = None) -> None:
        pass
    
    @abstractmethod
    def get_history(self, tenant_id: str, session_id: str, limit: int = 50) -> List[dict]:
        pass
    
    @abstractmethod
    def get_sessions(self, tenant_id: str) -> List[str]:
        pass
```

### Implementación PostgreSQL

**`app/repositories/postgres_conversation_repository.py`**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Conversation, Base

class PostgresConversationRepository(ConversationRepository):
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_message(self, tenant_id: str, session_id: str, user_message: str, bot_response: str, metadata: dict = None):
        session = self.Session()
        try:
            conv = Conversation(
                tenant_id=tenant_id,
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                metadata=metadata or {}
            )
            session.add(conv)
            session.commit()
        finally:
            session.close()
    
    def get_history(self, tenant_id: str, session_id: str, limit: int = 50) -> List[dict]:
        session = self.Session()
        try:
            results = session.query(Conversation).filter(
                Conversation.tenant_id == tenant_id,
                Conversation.session_id == session_id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
            return [{"user": r.user_message, "bot": r.bot_response, "ts": r.created_at} for r in results]
        finally:
            session.close()
    
    def get_sessions(self, tenant_id: str) -> List[str]:
        session = self.Session()
        try:
            results = session.query(Conversation.session_id).filter(
                Conversation.tenant_id == tenant_id
            ).distinct().all()
            return [r.session_id for r in results]
        finally:
            session.close()
```

### Implementación Legacy (JSON)

**`app/repositories/json_conversation_repository.py`**:
```python
from chat_service.storage import SimpleConversationStorage

class JsonConversationRepository(ConversationRepository):
    def __init__(self, filename: str = "conversations.json"):
        self.storage = SimpleConversationStorage(filename)
    
    def save_message(self, tenant_id: str, session_id: str, user_message: str, bot_response: str, metadata: dict = None):
        self.storage.save(session_id, user_message, bot_response)
    
    def get_history(self, tenant_id: str, session_id: str, limit: int = 50) -> List[dict]:
        history = self.storage.get_history(session_id)
        return [{"user": h[0], "bot": h[1]} for h in history[-limit:]]
    
    def get_sessions(self, tenant_id: str) -> List[str]:
        return list(self.storage.data.keys())
```

---

## Fase 4: Factory/Registry (Semana 5)

**`app/repositories/factory.py`**:
```python
from app.config.settings import load_api_settings
from app.repositories.conversation_repository import ConversationRepository

def create_conversation_repository() -> ConversationRepository:
    settings = load_api_settings()
    
    if settings.database_url and settings.database_url.startswith("postgresql"):
        from app.repositories.postgres_conversation_repository import PostgresConversationRepository
        return PostgresConversationRepository(settings.database_url)
    
    from app.repositories.json_conversation_repository import JsonConversationRepository
    return JsonConversationRepository()
```

---

## Fase 5: Integración con API (Semana 5)

### Actualizar `app/api/routes.py`

```python
from app.repositories.factory import create_conversation_repository

conversation_repo = create_conversation_repository()

@router.post("/api/v1/chat")
async def chat(message: str, session_id: str, tenant_id: str = "default"):
    # ... existing logic
    conversation_repo.save_message(tenant_id, session_id, message, response.text)
    return {"response": response.text, "session_id": session_id}

@router.get("/api/v1/history/{session_id}")
async def history(session_id: str, tenant_id: str = "default"):
    return {
        "session_id": session_id,
        "history": conversation_repo.get_history(tenant_id, session_id)
    }
```

---

## Fase 6: Alembic Migrations (Semana 5)

### Setup

```bash
alembic init migrations
```

**`alembic.ini`**:
```ini
sqlalchemy.url = postgresql://user:pass@localhost:5432/chatbot
```

**`migrations/env.py`**:
```python
from app.database.models import Base
target_metadata = Base.metadata
```

### Migración inicial

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Fase 7: Tests (Semana 5)

### Tests de Repository

**`tests/test_postgres_repository.py`**:
```python
import pytest
from app.repositories.postgres_conversation_repository import PostgresConversationRepository

@pytest.fixture
def repo():
    return PostgresConversationRepository("postgresql://test:test@localhost:5432/test_chatbot")

def test_save_and_get_history(repo):
    repo.save_message("tenant1", "session1", "hello", "hi there")
    history = repo.get_history("tenant1", "session1")
    assert len(history) > 0
    assert history[0]["user"] == "hello"

def test_get_sessions(repo):
    repo.save_message("tenant1", "session1", "hello", "hi")
    repo.save_message("tenant1", "session2", "hello", "hi")
    sessions = repo.get_sessions("tenant1")
    assert "session1" in sessions
    assert "session2" in sessions
```

---

## Checklist de Release

- [ ] Dependencias añadidas a `requirements.txt`
- [ ] Settings con `database_url` configurado
- [ ] Modelos SQLAlchemy creados
- [ ] Repositorios implementados (PostgreSQL + JSON fallback)
- [ ] Factory actualiza correctamente según configuración
- [ ] API usa repositorio injectable
- [ ] Alembic migrations funcionando
- [ ] Tests de repository pasando
- [ ] `pytest -q` en verde
- [ ] Documentación actualizada

---

## Configuración .env

```env
# Modo PostgreSQL (producción)
DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot

# O modo JSON (desarrollo local)
# DATABASE_URL=no-db
```

---

## Rollback Strategy

Si PostgreSQL falla:
1. Configurar `DATABASE_URL=no-db` o eliminar la variable
2. El sistema usará `JsonConversationRepository` automáticamente
3. No hay downtime, solo fallback a archivo JSON
