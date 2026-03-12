import pytest

from app.enterprise.transport.handlers import handle_enterprise_command


def _call(command, args, *, actor_id=1, chat_id=10, raw_text=None):
    return handle_enterprise_command(
        actor_id=actor_id,
        chat_id=chat_id,
        command=command,
        args=args,
        raw_text=raw_text or command,
        raw_update=None,
    )


def test_fun_and_reactions_contract(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_FUN", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_REACTIONS", "1")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "1")

    fun = _call("/fun", [])
    assert fun["status"] == "ok"
    assert fun["response_text"]

    reaction = _call("/reactions", ["hola"])
    assert reaction["status"] == "ok"
    assert reaction["response_text"]


def test_gettime_contract(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_GETTIME", "1")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "1")

    result = _call("/gettime", ["UTC"])
    assert result["status"] == "ok"
    assert "UTC" in result["response_text"]


def test_anilist_contract_without_client(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_FEATURE_ANILIST", "1")
    monkeypatch.setenv("ENTERPRISE_ANILIST_URL", "")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "1")

    result = _call("/anilist", ["evangelion"])
    assert result["status"] == "ok"
    assert "Anilist no configurado" in result["response_text"]


def test_antispam_blacklist_sticker_antichannel_contract(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "1")

    antispam = _call("/antispam", ["status"])
    assert antispam["status"] == "ok"

    toggle = _call("/antispam", ["on"])
    assert toggle["status"] == "ok"

    add = _call("/blacklist", ["add", "spam"])
    assert add["status"] == "ok"

    listed = _call("/blacklist", ["list"])
    assert listed["status"] == "ok"
    assert "spam" in listed["response_text"]

    del_cmd = _call("/blacklist", ["del", "spam"])
    assert del_cmd["status"] == "ok"

    sticker_add = _call("/stickerblacklist", ["add", "file_1"])
    assert sticker_add["status"] == "ok"

    sticker_list = _call("/stickerblacklist", ["list"])
    assert sticker_list["status"] == "ok"
    assert "file_1" in sticker_list["response_text"]

    sticker_del = _call("/stickerblacklist", ["del", "file_1"])
    assert sticker_del["status"] == "ok"

    antichannel_on = _call("/antichannel", ["on"])
    assert antichannel_on["status"] == "ok"

    antichannel_status = _call("/antichannel", ["status"])
    assert antichannel_status["status"] == "ok"


def test_permissions_and_ban_commands_contract(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "1")
    monkeypatch.setenv("ENTERPRISE_OWNER_IDS", "1")

    ban = _call("/ban", ["99", "spam"], raw_text="/ban 99 spam")
    assert ban["status"] == "ok"

    unban = _call("/unban", ["99"], raw_text="/unban 99")
    assert unban["status"] == "ok"


def test_disabled_enterprise_returns_disabled(monkeypatch):
    monkeypatch.setenv("ENTERPRISE_ENABLED", "0")
    result = _call("/fun", [])
    assert result["status"] == "disabled"
