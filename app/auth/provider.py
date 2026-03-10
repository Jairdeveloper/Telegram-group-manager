from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import secrets
from app.auth.models import User, UserRole, ApiKey, AuthSession
from app.database.repositories import UserRepository


class AuthProvider:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo
        self._sessions: Dict[str, AuthSession] = {}
        self._login_attempts: Dict[str, List[datetime]] = {}
    
    def set_user_repo(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str, tenant_id: str) -> Optional[User]:
        if not self.user_repo:
            return None
        
        user = self.user_repo.get_by_username(username, tenant_id)
        if not user:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            self._track_failed_login(username)
            return None
        
        if user.status != "active":
            return None
        
        user.last_login = datetime.utcnow()
        self.user_repo.update(user)
        
        return user
    
    def _track_failed_login(self, username: str) -> None:
        now = datetime.utcnow()
        if username not in self._login_attempts:
            self._login_attempts[username] = []
        self._login_attempts[username].append(now)
        self._login_attempts[username] = [
            ts for ts in self._login_attempts[username]
            if now - ts < timedelta(minutes=15)
        ]
    
    def is_rate_limited(self, username: str) -> bool:
        attempts = self._login_attempts.get(username, [])
        return len(attempts) >= 5

    def create_session(
        self, 
        user: User, 
        ip: str = "0.0.0.0", 
        user_agent: str = "unknown",
        expires_hours: int = 24
    ) -> str:
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        session = AuthSession(
            session_id=session_id,
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            role=user.role,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=expires_at
        )
        self._sessions[session_id] = session
        return session_id
    
    def verify_session(self, session_id: str) -> Optional[AuthSession]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        if datetime.utcnow() > session.expires_at:
            del self._sessions[session_id]
            return None
        
        return session
    
    def refresh_session(self, session_id: str) -> Optional[str]:
        session = self.verify_session(session_id)
        if not session:
            return None
        
        del self._sessions[session_id]
        return self.create_session(
            user=User(
                user_id=session.user_id,
                tenant_id=session.tenant_id,
                email="",
                username="",
                hashed_password="",
                role=session.role
            ),
            ip=session.ip_address,
            user_agent=session.user_agent
        )
    
    def revoke_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def revoke_all_user_sessions(self, user_id: str) -> int:
        sessions_to_remove = [
            sid for sid, s in self._sessions.items()
            if s.user_id == user_id
        ]
        for sid in sessions_to_remove:
            del self._sessions[sid]
        return len(sessions_to_remove)

    def create_api_key(
        self, 
        tenant_id: str, 
        name: str, 
        permissions: List[str],
        expires_days: Optional[int] = None
    ) -> tuple[ApiKey, str]:
        key_id = secrets.token_hex(8)
        key_value = f"sk_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(key_value)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key = ApiKey(
            key_id=key_id,
            tenant_id=tenant_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at,
            last_used=None
        )
        
        if self.user_repo:
            self.user_repo.save_api_key(api_key)
        
        return api_key, key_value
    
    def verify_api_key(self, key_value: str) -> Optional[ApiKey]:
        if not self.user_repo:
            return None
        
        key_hash = self._hash_key(key_value)
        api_key = self.user_repo.get_api_key_by_hash(key_hash)
        
        if not api_key:
            return None
        
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        api_key.last_used = datetime.utcnow()
        self.user_repo.update_api_key(api_key)
        
        return api_key
    
    def revoke_api_key(self, key_id: str, tenant_id: str) -> bool:
        if not self.user_repo:
            return False
        return self.user_repo.delete_api_key(key_id, tenant_id)
    
    def list_api_keys(self, tenant_id: str) -> List[ApiKey]:
        if not self.user_repo:
            return []
        return self.user_repo.list_api_keys(tenant_id)

    @staticmethod
    def _hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, hashed: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_active_sessions_count(self, tenant_id: str) -> int:
        return sum(1 for s in self._sessions.values() if s.tenant_id == tenant_id)


auth_provider = AuthProvider()
