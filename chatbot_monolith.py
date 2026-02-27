#!/usr/bin/env python3
"""
DESCRIPCIÓN:
-----------
Este es un archivo monolítico que contiene TODO el código del chatbot modulado.
Incluye: configuración, NLP, persistencia, embeddings, LLM, y API REST.

Para ejecutar:
    python chatbot_monolith.py --mode cli      (Modo CLI interactivo)
    python chatbot_monolith.py --mode api      (Modo API REST)

DEPENDENCIAS NECESARIAS:
    pip install fastapi uvicorn sqlalchemy pydantic-settings sentence-transformers

OPCIONAL (para LLM):
    pip install openai requests
"""

import os
import sys
import re
import json
import logging
import argparse
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from contextlib import contextmanager

# =============================================================================
# PARTE 1: CONFIGURACIÓN Y LOGGING
# =============================================================================

class Settings:
    """Configuración centralizada"""
    
    APP_NAME = "ChatBot Evolution"
    APP_VERSION = "2.1"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    SQLALCHEMY_ECHO = False
    
    # NLP
    PATTERN_TIMEOUT = 5.0
    MIN_CONFIDENCE = 0.5
    
    # Embeddings
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    ENABLE_EMBEDDINGS = True
    
    # LLM Fallback
    USE_LLM_FALLBACK = True
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "mistral"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 150
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API
    # Allow overriding host via env `API_HOST` (use 0.0.0.0 in containers)
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_WORKERS = 4


settings = Settings()


def get_logger(name: str) -> logging.Logger:
    """Factory para obtener loggers configurados"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger


logger = get_logger(__name__)


# =============================================================================
# PARTE 2-4: Externalized chat service (Agent, PatternEngine, Tokenizer, PronounTranslator)
# =============================================================================

# Extracted to package `chat_service` for reuse and testability
from chat_service.agent import Agent, Response
from chat_service.pattern_engine import PatternEngine, Tokenizer, PronounTranslator


# =============================================================================
# PARTE 3: RESPUESTA ESTRUCTURADA
# =============================================================================

@dataclass
class Response:
    """Respuesta estructurada del Actor"""
    text: str
    confidence: float = 1.0
    pattern_matched: bool = False
    source: str = "default"
    metadata: dict = field(default_factory=dict)


# =============================================================================
# PARTE 4: ACTOR ORQUESTADOR
# =============================================================================

class Actor:
    """Orquestador: procesa entrada, matchea patrones, genera respuestas"""
    
    def __init__(
        self,
        pattern_responses: List[Tuple[List, List]],
        default_responses: List[List[str]],
    ):
        self.pattern_responses = pattern_responses
        self.default_responses = default_responses
        
        self.pattern_engine = PatternEngine()
        self.pronoun_translator = PronounTranslator()
        self.tokenizer = Tokenizer()
        
        self.username = ""
        self.username_tag = "Username"
        self.default_response_index = 0
    
    def process(self, user_input: str) -> Response:
        """Procesa entrada del usuario y genera respuesta"""
        tokens = self.tokenizer.tokenize(user_input)
        input_text = self.tokenizer.detokenize(tokens)
        
        # Intenta matching
        matched_pattern = None
        binding_list = None
        response_template = None
        
        for pattern, response_tmpl in self.pattern_responses:
            bl = self.pattern_engine.match(pattern, input_text)
            if bl is not None:
                matched_pattern = pattern
                binding_list = bl
                response_template = response_tmpl
                break
        
        # Genera respuesta
        if binding_list is None:
            response = self._generate_default_response()
            response.source = "default"
        else:
            translated_bindings = self.pronoun_translator.translate(binding_list)
            response_text = self._build_reply(response_template, translated_bindings)
            response = Response(
                text=response_text,
                confidence=0.9,
                pattern_matched=True,
                source="pattern",
                metadata={"pattern": matched_pattern, "bindings": translated_bindings},
            )
        
        return response
    
    def _generate_default_response(self) -> Response:
        """Genera respuesta default (cíclica)"""
        resp = self.default_responses[self.default_response_index]
        text = " ".join(resp)
        self.default_response_index = (self.default_response_index + 1) % len(self.default_responses)
        return Response(text=text, source="default")
    
    def _build_reply(self, response_template: List, binding_list: List[List[str]]) -> str:
        """Construye respuesta reemplazando placeholders con bindings"""
        binding_dict = {}
        
        for binding in binding_list:
            if isinstance(binding, list) and len(binding) > 0:
                key = binding[0]
                values = binding[1:]
                
                if key == self.username_tag and values:
                    if self.username and self.username != values[0]:
                        response = [values[0], "eh?", "what", "ever", "happened", "to", self.username]
                        return " ".join(response)
                    self.username = values[0]
                
                binding_dict[key] = values
        
        reply = []
        for elem in response_template:
            if isinstance(elem, list) and len(elem) > 1:
                binding_key = elem[1]
                if binding_key in binding_dict:
                    reply.extend(binding_dict[binding_key])
            else:
                reply.append(str(elem))
        
        return " ".join(reply)


# =============================================================================
# PARTE 5: PERSISTENCIA (OPCIONAL - SIMPLE JSON)
# =============================================================================

class SimpleConversationStorage:
    """Almacenamiento simple de conversaciones en JSON"""
    
    def __init__(self, filename: str = "conversations.json"):
        self.filename = filename
        self.data = self._load()
    
    def _load(self) -> dict:
        """Carga conversaciones desde archivo"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self, session_id: str, user_input: str, bot_response: str):
        """Guarda interacción"""
        if session_id not in self.data:
            self.data[session_id] = []
        
        self.data[session_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user": user_input,
            "bot": bot_response,
        })
        
        self._persist()
    
    def _persist(self):
        """Guarda a archivo"""
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2, default=str)
    
    def get_history(self, session_id: str) -> list:
        """Obtiene historial de sesión"""
        return self.data.get(session_id, [])


# =============================================================================
# PARTE 6: BÚSQUEDA SEMÁNTICA (OPCIONAL - CON SENTENCE TRANSFORMERS)
# =============================================================================

class EmbeddingService:
    """Servicio de embeddings semánticos (opcional)"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled and settings.ENABLE_EMBEDDINGS
        self.model = None
        
        if self.enabled:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
            except ImportError:
                logger.warning("sentence-transformers not installed. Embeddings disabled.")
                self.enabled = False
    
    def embed(self, text: str) -> Optional[List[float]]:
        """Genera embedding para texto"""
        if not self.enabled or not self.model:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None


# =============================================================================
# PARTE 7: LLM FALLBACK (OPCIONAL - OPENAI + OLLAMA)
# =============================================================================

class LLMProvider:
    """Interfaz abstracta para LLM"""
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """Provider para OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.available = False
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.available = True
                logger.info("OpenAI provider initialized")
            except ImportError:
                logger.warning("openai package not installed")
    
    def generate(self, prompt: str) -> Optional[str]:
        """Genera respuesta con GPT"""
        if not self.available:
            return None
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return None


class OllamaProvider(LLMProvider):
    """Provider para Ollama local"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.available = False
        
        try:
            import requests
            self.requests = requests
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                self.available = True
                logger.info(f"Ollama provider initialized at {self.base_url}")
        except:
            logger.warning(f"Ollama not available at {self.base_url}")
    
    def generate(self, prompt: str) -> Optional[str]:
        """Genera respuesta con modelo local"""
        if not self.available:
            return None
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30,
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        
        return None


class LLMFallback:
    """Gestor de fallback a LLM"""
    
    def __init__(self):
        self.provider: Optional[LLMProvider] = None
        
        if not settings.USE_LLM_FALLBACK:
            return
        
        # Intenta OpenAI primero
        if settings.OPENAI_API_KEY:
            self.provider = OpenAIProvider()
            if self.provider.available:
                return
        
        # Fallback a Ollama
        self.provider = OllamaProvider()
    
    def generate(self, prompt: str) -> Optional[str]:
        """Genera respuesta si provider disponible"""
        if not self.provider:
            return None
        
        return self.provider.generate(prompt)


# =============================================================================
# PARTE 8: CLI - MODO INTERACTIVO
# =============================================================================

def get_default_brain() -> tuple:
    """Retorna brain mejorado con 40+ patrones"""
    
    default_responses = [
        ["That's", "interesting,", "tell", "me", "more"],
        ["I", "see.", "Could", "you", "elaborate?"],
        ["That's", "a", "great", "point"],
        ["I", "understand.", "What", "else?"],
        ["In", "other", "words,", "you're", "saying...?"],
        ["Can", "you", "give", "me", "an", "example?"],
        ["That", "makes", "sense"],
        ["I", "appreciate", "your", "thoughts"],
    ]
    
    pattern_responses = [
        # SALUDOS
        [["hello", 0], ["Hello!", "It's", "nice", "to", "meet", "you"]],
        [["hi", 0], ["Hi", "there!", "How", "can", "I", "help?"]],
        [["hey", 0], ["Hey!", "What's", "on", "your", "mind?"]],
        [["good", "morning"], ["Good", "morning!", "Ready", "to", "chat?"]],
        [["good", "afternoon"], ["Good", "afternoon!", "How", "are", "you?"]],
        [["good", "evening"], ["Good", "evening!", "Nice", "to", "see", "you"]],
        
        # DESPEDIDAS
        [["goodbye", 0], ["Goodbye!", "It", "was", "great", "talking", "to", "you"]],
        [["bye", 0], ["See", "you", "later!", "Take", "care"]],
        
        # PRESENTACIÓN
        [[0, "my", "name", "is", [1, "name"], 0], 
         ["Pleased", "to", "meet", "you,", [1, "name"], "!"]],
        
        # CÓMO ESTÁS
        [["how", "are", "you"], ["I'm", "doing", "great,", "thanks", "for", "asking!"]],
        [["how", "are", "you", "doing"], ["Doing", "well!", "What", "about", "you?"]],
        
        # ESTADO DEL USUARIO
        [["i", "am", [1, "feeling"], 0],
         ["I'm", "sorry", "to", "hear", "you're", [1, "feeling"]]],
        
        # PREFERENCIAS
        [["i", "like", [1, "thing"], 0],
         [[1, "thing"], "is", "great!", "Why", "do", "you", "enjoy", [1, "thing"], "?"]],
        
        [["i", "hate", [1, "thing"], 0],
         ["I", "see.", "It", "sounds", "like", [1, "thing"], "isn't", "for", "you"]],
        
        # RELACIONES
        [[[1, "subject"], "loves", [0, "object"]],
         ["That's", "beautiful!"]],
        [[[1, "person"], "is", "my", "friend"],
         ["That's", "lovely!"]],
        
        # NECESIDADES
        [["i", "need", [1, "object"], 0],
         ["Why", "do", "you", "need", [1, "object"], "?"]],
        
        [["help", "me"],
         ["Of", "course!", "I'm", "here", "to", "help"]],
        
        # PREGUNTAS
        [["what", "is", [1, "topic"], 0],
         ["That's", "an", "interesting", "question", "about", [1, "topic"]]],
        
        # AGRADECIMIENTO
        [["thanks", 0], ["You're", "welcome!", "Happy", "to", "help"]],
        [["thank", "you"], ["My", "pleasure!"]],
        
        # CONFIRMACIÓN
        [["yes", 0], ["Great!"]],
        [["no", 0], ["I", "understand"]],
        
        # INFORMACIÓN DEL BOT
        [["who", "are", "you"],
         ["I'm", "an", "AI", "chatbot", "created", "to", "chat"]],
        [["what", "can", "you", "do"],
         ["I", "can", "have", "conversations", "and", "help", "with", "ideas"]],
    ]
    
    return pattern_responses, default_responses


def run_cli():
    """Modo CLI interactivo"""
    logger.info("Starting ChatBot CLI (Monolithic Version)")
    
    # Inicializa componentes
    pattern_responses, default_responses = get_default_brain()
    actor = Actor(pattern_responses, default_responses)
    storage = SimpleConversationStorage()
    session_id = str(uuid.uuid4())[:8]
    
    print("\n" + "=" * 70)
    print("ChatBot Evolution - Monolithic Mode (CLI)")
    print("=" * 70)
    print("Type 'quit' o '(quit)' to exit\n")
    
    try:
        while True:
            try:
                user_input = input("> ").strip()
            except EOFError:
                print("\n(EOF) Type '(quit)' to exit")
                continue
            
            if not user_input:
                continue
            
            if user_input.lower() in ("(quit)", "quit", "exit"):
                print("Bye!")
                break
            
            response = actor.process(user_input)
            print(f"Bot: {response.text}")
            
            # Guarda conversación
            storage.save(session_id, user_input, response.text)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted. Bye!")


# =============================================================================
# PARTE 9: API REST (OPCIONAL - CON FASTAPI)
# =============================================================================

def run_api():
    """Modo API REST"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
    except ImportError:
        print("ERROR: FastAPI no instalado. Instala con: pip install fastapi uvicorn")
        sys.exit(1)
    
    logger.info("Starting ChatBot API (Monolithic Version)")
    
    # Inicializa componentes
    pattern_responses, default_responses = get_default_brain()
    actor = Actor(pattern_responses, default_responses)
    storage = SimpleConversationStorage()
    
    # Crea app FastAPI
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Monolithic Chatbot with NLP, Embeddings, and LLM Fallback"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health():
        """Health check"""
        return {"status": "ok", "version": settings.APP_VERSION}
    
    @app.post("/api/v1/chat")
    async def chat(message: str, session_id: Optional[str] = None):
        """Endpoint principal de chat"""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="message required")
        
        response = actor.process(message)
        storage.save(session_id, message, response.text)
        
        return {
            "session_id": session_id,
            "message": message,
            "response": response.text,
            "confidence": response.confidence,
            "source": response.source,
            "pattern_matched": response.pattern_matched,
        }
    
    @app.get("/api/v1/history/{session_id}")
    async def history(session_id: str):
        """Obtiene historial de sesión"""
        return {"session_id": session_id, "history": storage.get_history(session_id)}
    
    @app.get("/api/v1/stats")
    async def stats():
        """Estadísticas del chatbot"""
        return {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "total_sessions": len(storage.data),
            "total_messages": sum(len(msgs) for msgs in storage.data.values()),
        }
    
    # Inicia servidor
    print(f"\n✅ API running at http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📖 Swagger docs: http://{settings.API_HOST}:{settings.API_PORT}/docs\n")
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )


# =============================================================================
# PARTE 10: MAIN ENTRY POINT
# =============================================================================

def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(
        description="ChatBot Evolution - Monolithic Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python chatbot_monolith.py --mode cli       CLI mode
  python chatbot_monolith.py --mode api       API REST mode
  python chatbot_monolith.py --help           Show help
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Modo de ejecución (default: cli)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "cli":
            run_cli()
        elif args.mode == "api":
            run_api()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
