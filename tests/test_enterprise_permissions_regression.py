import pytest

from app.enterprise.application.services import EnterpriseUserService
from app.enterprise.domain.entities import EnterpriseUser
from app.enterprise.domain.roles import EnterpriseRole
from app.enterprise.infrastructure.repositories import (
    InMemoryBanRepository,
    InMemoryEnterpriseUserRepository,
)


def _build_service(users):
    user_repo = InMemoryEnterpriseUserRepository()
    ban_repo = InMemoryBanRepository()
    for user in users:
        user_repo.upsert(user)
    return EnterpriseUserService(
        user_repo=user_repo,
        ban_repo=ban_repo,
        tenant_id="test-tenant",
    )


def test_non_dev_cannot_upsert_user():
    actor = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.USER)
    service = _build_service([actor])

    with pytest.raises(PermissionError):
        service.upsert_user(actor_id=1, target_id=2, role_raw="support")


def test_dev_can_upsert_user():
    actor = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.DEV)
    service = _build_service([actor])

    user = service.upsert_user(actor_id=1, target_id=2, role_raw="support")
    assert user.user_id == 2
    assert user.role == EnterpriseRole.SUPPORT


def test_only_owner_can_delete():
    actor = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.DEV)
    service = _build_service([actor])

    with pytest.raises(PermissionError):
        service.delete_user(actor_id=1, target_id=2)


def test_sudo_required_for_ban():
    actor = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.SUPPORT)
    service = _build_service([actor])

    with pytest.raises(PermissionError):
        service.ban_user(actor_id=1, target_id=2, reason="spam")


def test_owner_can_ban_and_unban():
    actor = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.OWNER)
    service = _build_service([actor])

    record = service.ban_user(actor_id=1, target_id=2, reason="spam")
    assert record.user_id == 2

    service.unban_user(actor_id=1, target_id=2, reason="ok")
