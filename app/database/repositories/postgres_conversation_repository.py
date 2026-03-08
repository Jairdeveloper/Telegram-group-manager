"""PostgreSQL implementation of conversation repository."""
import logging
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database.models import Conversation
from app.database.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)


class PostgresConversationRepository(ConversationRepository):
    """PostgreSQL implementation using SQLAlchemy."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self) -> Session:
        return self.Session()

    def save_message(
        self,
        tenant_id: str,
        session_id: str,
        user_message: str,
        bot_response: str,
        metadata: Optional[dict] = None
    ) -> None:
        session = self._get_session()
        try:
            conv = Conversation(
                tenant_id=tenant_id,
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                extra_data=metadata or {}
            )
            session.add(conv)
            session.commit()
        except Exception:
            logger.exception("Failed to save message to PostgreSQL")
            session.rollback()
            raise
        finally:
            session.close()

    def get_history(
        self,
        tenant_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[dict]:
        session = self._get_session()
        try:
            results = (
                session.query(Conversation)
                .filter(
                    Conversation.tenant_id == tenant_id,
                    Conversation.session_id == session_id
                )
                .order_by(Conversation.created_at.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "user": r.user_message,
                    "bot": r.bot_response,
                    "ts": r.created_at.isoformat() if r.created_at else None,
                    "metadata": r.extra_data
                }
                for r in results
            ]
        finally:
            session.close()

    def get_sessions(self, tenant_id: str) -> List[str]:
        session = self._get_session()
        try:
            results = (
                session.query(Conversation.session_id)
                .filter(Conversation.tenant_id == tenant_id)
                .distinct()
                .all()
            )
            return [r.session_id for r in results]
        finally:
            session.close()

    def delete_session(self, tenant_id: str, session_id: str) -> None:
        session = self._get_session()
        try:
            session.query(Conversation).filter(
                Conversation.tenant_id == tenant_id,
                Conversation.session_id == session_id
            ).delete()
            session.commit()
        except Exception:
            logger.exception("Failed to delete session")
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self) -> None:
        """Create all tables (for development/testing)."""
        from app.database.models import Base
        Base.metadata.create_all(self.engine)
