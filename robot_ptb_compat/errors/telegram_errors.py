"""Re-export de errores de PTB."""

try:
    from telegram.error import (
        TelegramError,
        BadRequest,
        Forbidden,
        InvalidToken,
        NetworkError,
        TimedOut,
        Conflict,
        RetryAfter,
        ChatMigrated,
        PassportDecryptionError,
        EndPointNotFound,
    )

    __all__ = [
        "TelegramError",
        "BadRequest",
        "Forbidden",
        "InvalidToken",
        "NetworkError",
        "TimedOut",
        "Conflict",
        "RetryAfter",
        "ChatMigrated",
        "PassportDecryptionError",
        "EndPointNotFound",
    ]
except ImportError:
    TelegramError = Exception
    
    class BadRequest(Exception):
        pass
    
    class Forbidden(Exception):
        pass
    
    class InvalidToken(Exception):
        pass
    
    class NetworkError(Exception):
        pass
    
    class TimedOut(Exception):
        pass
    
    class Conflict(Exception):
        pass
    
    class RetryAfter(Exception):
        def __init__(self, retry_after: int):
            self.retry_after = retry_after
            super().__init__(f"Retry after {retry_after} seconds")
    
    class ChatMigrated(Exception):
        def __init__(self, new_chat_id: int):
            self.new_chat_id = new_chat_id
            super().__init__(f"Chat migrated to {new_chat_id}")
    
    class PassportDecryptionError(Exception):
        pass
    
    class EndPointNotFound(Exception):
        pass

    __all__ = [
        "TelegramError",
        "BadRequest",
        "Forbidden",
        "InvalidToken",
        "NetworkError",
        "TimedOut",
        "Conflict",
        "RetryAfter",
        "ChatMigrated",
        "PassportDecryptionError",
        "EndPointNotFound",
    ]
