"""Service Business/Core Logic Layer."""

from sprint4.core.exceptions import UrlServiceError, UrlRepositoryError
from sprint4.core.settings import SETTINGS
from sprint4.core.url_shorteners import get_shortener
from sprint4.db.repositories import UrlRepository
from sprint4.models.internal import ServiceStatistics
from sprint4.models.urls import (
    HttpUrlAddRequest,
    HttpUrlFilter,
    HttpUrlModel,
    HttpUrlRow,
)


class UrlShortenerService:
    def __init__(self) -> None:
        self._repo = UrlRepository(
            dsn=str(SETTINGS.postgres.dsn),
            engine_settings=SETTINGS.postgres.engine_settings.model_dump(),
            session_settings=SETTINGS.postgres.session_settings.model_dump(),
        )

    async def get_stats(self) -> ServiceStatistics:
        """Return the service statistics."""

        return ServiceStatistics()

    async def ping_db(self) -> None:
        """Ping the service database."""

        return await self._repo.ping()

    async def add_urls(self, requests: list[HttpUrlAddRequest]) -> list[HttpUrlRow]:
        urls: list[HttpUrlModel] = []
        for request in requests:
            sh = get_shortener(shortener_code=request.shortener_code)
            url = request.url
            urls.append(HttpUrlModel(url=url, short_url=sh.shorten(url)))
        try:
            return await self._repo.add_urls(urls)
        except UrlRepositoryError as e:
            raise UrlServiceError(str(e)) from e

    async def get_url_stats(self, url_filter: HttpUrlFilter) -> list[HttpUrlRow]:
        return await self._repo.get_urls(url_filter)
