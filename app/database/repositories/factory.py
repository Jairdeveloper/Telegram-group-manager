"""Factory for creating conversation repositories."""
from app.config.settings import load_api_settings
from app.database.repositories.conversation_repository import ConversationRepository
from app.database.repositories.postgres_conversation_repository import PostgresConversationRepository
from app.database.repositories.json_conversation_repository import JsonConversationRepository


def create_conversation_repository() -> ConversationRepository:
    """Create a conversation repository based on settings.
    
    Returns:
        - PostgresConversationRepository if DATABASE_URL is set to PostgreSQL
        - JsonConversationRepository otherwise (fallback)
    """
    settings = load_api_settings()
    
    if settings.is_postgres_enabled():
        return PostgresConversationRepository(settings.database_url)
    
    return JsonConversationRepository()


def create_conversation_repository_from_url(database_url: str) -> ConversationRepository:
    """Create a conversation repository from a specific database URL.
    
    Args:
        database_url: PostgreSQL connection URL
        
    Returns:
        PostgresConversationRepository
    """
    if database_url.startswith("postgresql"):
        return PostgresConversationRepository(database_url)
    
    return JsonConversationRepository(database_url)
