"""Version info para robot-ptb-compat."""

from typing import NamedTuple

__version__ = "0.1.0"


class Version(NamedTuple):
    """Versión de la librería."""
    major: int
    minor: int
    micro: int
    releaselevel: str = "alpha"
    serial: int = 0

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.micro}"
        if self.releaselevel != "final":
            version = f"{version}{self.releaselevel[0]}{self.serial}"
        return version


__version_info__ = Version(major=0, minor=1, micro=0, releaselevel="alpha", serial=0)

PTB_VERSION = "22.6.0"
PTB_BOT_API_VERSION = "9.3"
