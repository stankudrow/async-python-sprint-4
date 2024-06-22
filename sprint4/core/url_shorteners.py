from pyshorteners import Shortener

from sprint4.core.ptypes import HttpUrlType


class ShortMixin:
    def shorten(self, url: HttpUrlType) -> str:
        return self._shortener.short(str(url))


class ClckRuShortener(ShortMixin):
    def __init__(self, **kwargs: dict) -> None:
        self._shortener = Shortener(**kwargs).clckru


class OsDbShortener(ShortMixin):
    def __init__(self, **kwargs: dict) -> None:
        self._shortener = Shortener(**kwargs).osdb
