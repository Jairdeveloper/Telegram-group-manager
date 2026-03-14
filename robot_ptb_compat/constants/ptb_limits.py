"""Re-export de límites y constantes de PTB."""

from typing import Final

try:
    from telegram import constants as ptb_constants
except ImportError:
    ptb_constants = None

BOT_API_VERSION: Final[str] = "9.3"
BOT_API_VERSION_INFO: Final[tuple] = (9, 3)

MAX_MESSAGE_LENGTH: Final[int] = 4096
MAX_CAPTION_LENGTH: Final[int] = 1024
MAX_COMMANDS: Final[int] = 100
MAX_COMMAND_LENGTH: Final[int] = 32
MAX_DESCRIPTION_LENGTH: Final[int] = 256

MESSAGES_PER_SECOND: Final[int] = 30
MESSAGES_PER_SECOND_PER_CHAT: Final[int] = 1
MESSAGES_PER_MINUTE_PER_GROUP: Final[int] = 20

MAX_CALLBACK_DATA_LENGTH: Final[int] = 64
MAX_KEYBOARD_BUTTONS: Final[int] = 100
MAX_BUTTONS_PER_ROW: Final[int] = 8

FILESIZE_DOWNLOAD: Final[int] = 20 * 1024 * 1024
FILESIZE_UPLOAD: Final[int] = 50 * 1024 * 1024
PHOTOSIZE_UPLOAD: Final[int] = 10 * 1024 * 1024

if ptb_constants is not None:
    try:
        BOT_API_VERSION = ptb_constants.BOT_API_VERSION
        BOT_API_VERSION_INFO = ptb_constants.BOT_API_VERSION_INFO
    except AttributeError:
        pass

    try:
        MAX_MESSAGE_LENGTH = ptb_constants.MessageLimit.MAX_MESSAGE_LENGTH
        MAX_CAPTION_LENGTH = ptb_constants.MessageLimit.MAX_CAPTION_LENGTH
    except AttributeError:
        pass

    try:
        MESSAGES_PER_SECOND = ptb_constants.FloodLimit.MESSAGES_PER_SECOND
        MESSAGES_PER_SECOND_PER_CHAT = ptb_constants.FloodLimit.MESSAGES_PER_SECOND_PER_CHAT
    except AttributeError:
        pass

    try:
        MAX_CALLBACK_DATA_LENGTH = ptb_constants.InlineKeyboardButtonLimit.MAX_CALLBACK_DATA
    except AttributeError:
        pass

    try:
        FILESIZE_DOWNLOAD = ptb_constants.FileSizeLimit.FILESIZE_DOWNLOAD
        FILESIZE_UPLOAD = ptb_constants.FileSizeLimit.FILESIZE_UPLOAD
    except AttributeError:
        pass

__all__ = [
    "BOT_API_VERSION",
    "BOT_API_VERSION_INFO",
    "MAX_MESSAGE_LENGTH",
    "MAX_CAPTION_LENGTH",
    "MAX_COMMANDS",
    "MAX_COMMAND_LENGTH",
    "MAX_DESCRIPTION_LENGTH",
    "MESSAGES_PER_SECOND",
    "MESSAGES_PER_SECOND_PER_CHAT",
    "MESSAGES_PER_MINUTE_PER_GROUP",
    "MAX_CALLBACK_DATA_LENGTH",
    "MAX_KEYBOARD_BUTTONS",
    "MAX_BUTTONS_PER_ROW",
    "FILESIZE_DOWNLOAD",
    "FILESIZE_UPLOAD",
    "PHOTOSIZE_UPLOAD",
]
