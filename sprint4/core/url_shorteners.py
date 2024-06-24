from enum import Enum

from pyshorteners import Shortener

from sprint4.core.ptypes import HttpUrlType


class ShortenerError(Exception):
    """Generic (HTTP) URL Shortener Error."""


class ShortenersEnum(str, Enum):
    clckru = "clckru"
    osdb = "osdb"


class ShortenerMixin:
    def shorten(self, url: HttpUrlType) -> str:
        return self._shortener.short(str(url))


class ClckRuShortener(ShortenerMixin):
    def __init__(self, **kwargs: dict) -> None:
        self._shortener = Shortener(**kwargs).clckru


class OsDbShortener(ShortenerMixin):
    def __init__(self, **kwargs: dict) -> None:
        self._shortener = Shortener(**kwargs).osdb


def get_shortener(shortener_code: str, **kwargs) -> ClckRuShortener | OsDbShortener:
    """Return a Shortener class by its string code value."""

    try:
        code = ShortenersEnum(shortener_code)
    except ValueError as e:
        msg = f"unknown shortener code: {shortener_code!r}"
        raise ShortenerError(msg) from e

    if code == ShortenersEnum.clckru:
        return ClckRuShortener(**kwargs)
    if code == ShortenersEnum.osdb:
        return OsDbShortener(**kwargs)
