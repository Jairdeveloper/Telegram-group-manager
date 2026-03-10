"""User repository interface and implementation."""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import hashlib
import secrets


class User:
    def __init__(
        self,
        user_id: str,
        tenant_id: str,
        email: str,
        username: str,
        hashed_password: str,
        role: str = "user",
        status: str = "active",
        created_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        mfa_enabled: bool = False
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.email = email
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.mfa_enabled = mfa_enabled


class ApiKeyModel:
    def __init__(
        self,
        key_id: str,
        tenant_id: str,
        name: str,
        key_hash: str,
        permissions: List[str],
        expires_at: Optional[datetime] = None,
        last_used: Optional[datetime] = None,
        created_at: Optional[datetime] = None
    ):
        self.key_id = key_id
        self.tenant_id = tenant_id
        self.name = name
        self.key_hash = key_hash
        self.permissions = permissions
        self.expires_at = expires_at
        self.last_used = last_used
        self.created_at = created_at or datetime.utcnow()


class UserRepository(ABC):
    """Abstract base class for user storage."""

    @abstractmethod
    def get_by_username(self, username: str, tenant_id: str) -> Optional[User]:
        """Get user by username and tenant."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str, tenant_id: str) -> Optional[User]:
        """Get user by ID and tenant."""
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        """Save a user."""
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        """Update a user."""
        pass

    @abstractmethod
    def delete(self, user_id: str, tenant_id: str) -> bool:
        """Delete a user."""
        pass

    @abstractmethod
    def list_users(self, tenant_id: str) -> List[User]:
        """List all users for a tenant."""
        pass

    @abstractmethod
    def get_api_key_by_hash(self, key_hash: str, tenant_id: str = None) -> Optional[ApiKeyModel]:
        """Get API key by hash."""
        pass

    @abstractmethod
    def save_api_key(self, api_key: ApiKeyModel) -> None:
        """Save an API key."""
        pass

    @abstractmethod
    def update_api_key(self, api_key: ApiKeyModel) -> None:
        """Update an API key."""
        pass

    @abstractmethod
    def delete_api_key(self, key_id: str, tenant_id: str) -> bool:
        """Delete an API key."""
        pass

    @abstractmethod
    def list_api_keys(self, tenant_id: str) -> List[ApiKeyModel]:
        """List all API keys for a tenant."""
        pass


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository."""

    def __init__(self):
        self._users: dict = {}
        self._api_keys: dict = {}

    def get_by_username(self, username: str, tenant_id: str) -> Optional[User]:
        key = f"{tenant_id}:{username}"
        return self._users.get(key)

    def get_by_id(self, user_id: str, tenant_id: str) -> Optional[User]:
        for user in self._users.values():
            if user.user_id == user_id and user.tenant_id == tenant_id:
                return user
        return None

    def save(self, user: User) -> None:
        key = f"{user.tenant_id}:{user.username}"
        self._users[key] = user

    def update(self, user: User) -> None:
        key = f"{user.tenant_id}:{user.username}"
        if key in self._users:
            self._users[key] = user

    def delete(self, user_id: str, tenant_id: str) -> bool:
        for key, user in list(self._users.items()):
            if user.user_id == user_id and user.tenant_id == tenant_id:
                del self._users[key]
                return True
        return False

    def list_users(self, tenant_id: str) -> List[User]:
        return [u for u in self._users.values() if u.tenant_id == tenant_id]

    def get_api_key_by_hash(self, key_hash: str, tenant_id: str = None) -> Optional[ApiKeyModel]:
        for key in self._api_keys.values():
            if key.key_hash == key_hash:
                if tenant_id is None or key.tenant_id == tenant_id:
                    return key
        return None

    def save_api_key(self, api_key: ApiKeyModel) -> None:
        self._api_keys[api_key.key_id] = api_key

    def update_api_key(self, api_key: ApiKeyModel) -> None:
        if api_key.key_id in self._api_keys:
            self._api_keys[api_key.key_id] = api_key

    def delete_api_key(self, key_id: str, tenant_id: str) -> bool:
        key = self._api_keys.get(key_id)
        if key and key.tenant_id == tenant_id:
            del self._api_keys[key_id]
            return True
        return False

    def list_api_keys(self, tenant_id: str) -> List[ApiKeyModel]:
        return [k for k in self._api_keys.values() if k.tenant_id == tenant_id]


_user_repo_instance: Optional[UserRepository] = None


def get_user_repository() -> UserRepository:
    global _user_repo_instance
    if _user_repo_instance is None:
        _user_repo_instance = InMemoryUserRepository()
    return _user_repo_instance


def set_user_repository(repo: UserRepository) -> None:
    global _user_repo_instance
    _user_repo_instance = repo
