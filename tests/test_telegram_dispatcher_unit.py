from app.telegram.dispatcher import dispatch_telegram_update


def test_dispatcher_classifies_ops_command():
    result = dispatch_telegram_update(
        {"update_id": 1, "message": {"chat": {"id": 123}, "text": "/e2e"}}
    )

    assert result.kind == "ops_command"
    assert result.chat_id == 123
    assert result.command == "/e2e"
    assert result.args == ()


def test_dispatcher_classifies_chat_message():
    result = dispatch_telegram_update(
        {"update_id": 2, "message": {"chat": {"id": 123}, "text": "hola"}}
    )

    assert result.kind == "chat_message"
    assert result.chat_id == 123
    assert result.text == "hola"


def test_dispatcher_marks_update_without_message_as_unsupported():
    result = dispatch_telegram_update({"update_id": 3})

    assert result.kind == "unsupported"
    assert result.reason == "missing_message"


def test_dispatcher_marks_unknown_command_as_unsupported():
    result = dispatch_telegram_update(
        {"update_id": 4, "message": {"chat": {"id": 123}, "text": "/unknown arg1"}}
    )

    assert result.kind == "unsupported"
    assert result.command == "/unknown"
    assert result.args == ("arg1",)
    assert result.reason == "unsupported_command"
