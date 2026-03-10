import pytest
from app.auth.provider import AuthProvider
from app.auth.models import User, UserRole
from app.database.repositories import InMemoryUserRepository, User as RepoUser


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def auth_provider(user_repo):
    provider = AuthProvider(user_repo)
    return provider


@pytest.fixture
def test_user(user_repo):
    user = RepoUser(
        user_id="usr_test123",
        tenant_id="tenant_1",
        email="test@example.com",
        username="testuser",
        hashed_password=AuthProvider.hash_password("password123"),
        role="user",
        status="active"
    )
    user_repo.save(user)
    return user


class TestAuthProvider:
    def test_hash_password(self):
        password = "testpassword"
        hashed = AuthProvider.hash_password(password)
        assert hashed == AuthProvider.hash_password(password)
        assert hashed != AuthProvider.hash_password("otherpassword")

    def test_authenticate_success(self, auth_provider, test_user):
        user = auth_provider.authenticate("testuser", "password123", "tenant_1")
        assert user is not None
        assert user.username == "testuser"
        assert user.tenant_id == "tenant_1"

    def test_authenticate_wrong_password(self, auth_provider, test_user):
        user = auth_provider.authenticate("testuser", "wrongpassword", "tenant_1")
        assert user is None

    def test_authenticate_invalid_user(self, auth_provider):
        user = auth_provider.authenticate("nonexistent", "password", "tenant_1")
        assert user is None

    def test_authenticate_inactive_user(self, auth_provider, user_repo):
        user = RepoUser(
            user_id="usr_inactive",
            tenant_id="tenant_1",
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=AuthProvider.hash_password("password"),
            role="user",
            status="suspended"
        )
        user_repo.save(user)
        
        result = auth_provider.authenticate("inactiveuser", "password", "tenant_1")
        assert result is None

    def test_create_session(self, auth_provider, test_user):
        session_id = auth_provider.create_session(
            user=test_user,
            ip="192.168.1.1",
            user_agent="test-agent"
        )
        assert session_id is not None
        assert len(session_id) > 20

    def test_verify_session(self, auth_provider, test_user):
        session_id = auth_provider.create_session(test_user)
        session = auth_provider.verify_session(session_id)
        
        assert session is not None
        assert session.user_id == test_user.user_id
        assert session.tenant_id == test_user.tenant_id

    def test_verify_invalid_session(self, auth_provider):
        session = auth_provider.verify_session("invalid_session_id")
        assert session is None

    def test_revoke_session(self, auth_provider, test_user):
        session_id = auth_provider.create_session(test_user)
        assert auth_provider.verify_session(session_id) is not None
        
        auth_provider.revoke_session(session_id)
        assert auth_provider.verify_session(session_id) is None

    def test_create_api_key(self, auth_provider):
        api_key, key_value = auth_provider.create_api_key(
            tenant_id="tenant_1",
            name="Test Key",
            permissions=["read", "write"],
            expires_days=30
        )
        
        assert api_key is not None
        assert key_value.startswith("sk_")
        assert api_key.name == "Test Key"
        assert api_key.permissions == ["read", "write"]

    def test_verify_api_key(self, auth_provider):
        api_key, key_value = auth_provider.create_api_key(
            tenant_id="tenant_1",
            name="Test Key",
            permissions=["read"]
        )
        
        verified = auth_provider.verify_api_key(key_value)
        assert verified is not None
        assert verified.key_id == api_key.key_id

    def test_revoke_api_key(self, auth_provider, user_repo):
        auth_provider.set_user_repo(user_repo)
        
        api_key, key_value = auth_provider.create_api_key(
            tenant_id="tenant_1",
            name="Revokable Key",
            permissions=["read"]
        )
        
        assert auth_provider.verify_api_key(key_value) is not None
        
        auth_provider.revoke_api_key(api_key.key_id, "tenant_1")
        
        assert auth_provider.verify_api_key(key_value) is None

    def test_rate_limiting(self, auth_provider, user_repo):
        auth_provider.set_user_repo(user_repo)
        
        for i in range(5):
            auth_provider._track_failed_login("ratelimited")
        
        assert auth_provider.is_rate_limited("ratelimited") is True
        assert auth_provider.is_rate_limited("notratelimited") is False


class TestAuthModels:
    def test_user_role_enum(self):
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.USER.value == "user"
        assert UserRole.API_USER.value == "api_user"
