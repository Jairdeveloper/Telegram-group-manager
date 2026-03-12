import random

import pytest

from app.enterprise.application.services import (
    EnterpriseModerationService,
    EnterpriseUtilityService,
    EnterpriseUserService,
)
from app.enterprise.domain.entities import EnterpriseUser
from app.enterprise.domain.roles import EnterpriseRole
from app.enterprise.infrastructure.moderation_repositories import (
    InMemoryAntiChannelRepository,
    InMemoryAntiSpamRepository,
    InMemoryBlacklistRepository,
    InMemoryStickerBlacklistRepository,
)
from app.enterprise.infrastructure.repositories import (
    InMemoryBanRepository,
    InMemoryEnterpriseUserRepository,
)


def _build_user_service(users):
    user_repo = InMemoryEnterpriseUserRepository()
    ban_repo = InMemoryBanRepository()
    for user in users:
        user_repo.upsert(user)
    return EnterpriseUserService(
        user_repo=user_repo,
        ban_repo=ban_repo,
        tenant_id="test-tenant",
    )


def _build_moderation_service(user_service):
    return EnterpriseModerationService(
        user_service=user_service,
        antispam_repo=InMemoryAntiSpamRepository(),
        blacklist_repo=InMemoryBlacklistRepository(),
        sticker_blacklist_repo=InMemoryStickerBlacklistRepository(),
        antichannel_repo=InMemoryAntiChannelRepository(),
        tenant_id="test-tenant",
    )


def test_antispam_set_get():
    admin = EnterpriseUser(user_id=10, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    user_service = _build_user_service([admin])
    moderation_service = _build_moderation_service(user_service)

    config = moderation_service.set_antispam(
        actor_id=10,
        chat_id=99,
        enabled=True,
        spamwatch_enabled=True,
        sibyl_enabled=False,
    )

    assert config.enabled is True
    assert config.spamwatch_enabled is True
    assert config.sibyl_enabled is False

    fetched = moderation_service.get_antispam(99)
    assert fetched is not None
    assert fetched.enabled is True


def test_blacklist_rejects_invalid_regex():
    admin = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    moderation_service = _build_moderation_service(_build_user_service([admin]))

    with pytest.raises(ValueError):
        moderation_service.add_blacklist(1, 200, "([invalid")


def test_blacklist_blocks_message():
    admin = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    user = EnterpriseUser(user_id=2, tenant_id="test-tenant", role=EnterpriseRole.USER)
    user_service = _build_user_service([admin, user])
    moderation_service = _build_moderation_service(user_service)

    moderation_service.add_blacklist(1, 300, "spam")
    decision = moderation_service.evaluate_message(
        actor_id=2,
        chat_id=300,
        text="spam detected",
        sticker_file_id=None,
        sender_chat_type=None,
    )

    assert decision.status == "blocked"
    assert decision.reason == "blacklist"


def test_sticker_blacklist_blocks():
    admin = EnterpriseUser(user_id=10, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    user = EnterpriseUser(user_id=11, tenant_id="test-tenant", role=EnterpriseRole.USER)
    user_service = _build_user_service([admin, user])
    moderation_service = _build_moderation_service(user_service)

    moderation_service.add_sticker_blacklist(10, 400, "file_123")
    decision = moderation_service.evaluate_message(
        actor_id=11,
        chat_id=400,
        text="",
        sticker_file_id="file_123",
        sender_chat_type=None,
    )

    assert decision.status == "blocked"
    assert decision.reason == "sticker_blacklist"


def test_antichannel_blocks_channel_sender():
    admin = EnterpriseUser(user_id=10, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    user = EnterpriseUser(user_id=11, tenant_id="test-tenant", role=EnterpriseRole.USER)
    user_service = _build_user_service([admin, user])
    moderation_service = _build_moderation_service(user_service)

    moderation_service.set_antichannel(10, 500, enabled=True)
    decision = moderation_service.evaluate_message(
        actor_id=11,
        chat_id=500,
        text="hola",
        sticker_file_id=None,
        sender_chat_type="channel",
    )

    assert decision.status == "blocked"
    assert decision.reason == "antichannel"


def test_whitelist_role_is_exempt():
    admin = EnterpriseUser(user_id=1, tenant_id="test-tenant", role=EnterpriseRole.SUDO)
    whitelisted = EnterpriseUser(user_id=2, tenant_id="test-tenant", role=EnterpriseRole.WHITELIST)
    user_service = _build_user_service([admin, whitelisted])
    moderation_service = _build_moderation_service(user_service)

    moderation_service.add_blacklist(1, 600, "spam")
    decision = moderation_service.evaluate_message(
        actor_id=2,
        chat_id=600,
        text="spam detected",
        sticker_file_id=None,
        sender_chat_type=None,
    )

    assert decision.status == "allowed"


def test_utility_service_outputs():
    random.seed(0)
    service = EnterpriseUtilityService(
        feature_flags={"fun": True, "reactions": True, "anilist": True, "wallpaper": True, "gettime": True},
        default_timezone="UTC",
        anilist_client=None,
    )

    assert "Sugerencia" in service.wallpaper_suggestion()
    assert service.get_time("Invalid/Zone").startswith("Zona horaria invalida")
    assert service.anilist_search("eva") == "Anilist no configurado."
    assert service.reaction_for_text("hola") in {"Hola!", "Hey!", "Buenas!"}
    assert service.random_fun()
