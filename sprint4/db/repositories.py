"""Database repositories module."""

from datetime import datetime

from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.sql import delete, insert, select, text, update, Delete, Select, Update

from sprint4.core.exceptions import UrlRepositoryError
from sprint4.core.ptypes import KeywordsType, SettingsType
from sprint4.core.settings import SETTINGS
from sprint4.db.orms import Url
from sprint4.db.utils import get_async_engine, get_async_session
from sprint4.models.urls import HttpUrlModel, HttpUrlRow, HttpUrlFilter


_FilterableQueryType = Delete | Select | Update


def _get_conditioned_query_from_url_filter(
    query: _FilterableQueryType, url_filter: HttpUrlFilter
):
    if url_filter.id is not None:  # can be 0
        query = query.where(Url.id == url_filter.id)
    if url_filter.url:
        query = query.where(Url.url == str(url_filter.url))
    if url_filter.short_url:
        query = query.where(Url.short_url == str(url_filter.short_url))
    if url_filter.is_gone is not None:  # can be False
        query = query.where(Url.is_gone == url_filter.is_gone)
    if url_filter.visibility:
        query = query.where(Url.visibility == url_filter.visibility)
    if url_filter.client_info:
        query = query.where(Url.client_info == url_filter.client_info)
    if url_filter.clicked_at:
        query = query.where(Url.clicked_at == url_filter.clicked_at)
    if url_filter.nclicks is not None:
        query = query.where(Url.nclicks == url_filter.nclicks)
    return query


class UrlRepository:
    @classmethod
    def from_dict(cls, state: SettingsType) -> "UrlRepository":
        return cls(**state)

    def __init__(
        self,
        dsn: str,
        engine_settings: None | KeywordsType = None,
        session_settings: None | KeywordsType = None,
    ) -> None:
        self._dsn = dsn
        self._engine_settings = (
            engine_settings
            if engine_settings
            else SETTINGS.postgres.engine_settings.model_dump()
        )
        self._session_settings = (
            session_settings
            if session_settings
            else SETTINGS.postgres.session_settings.model_dump()
        )
        self._engine = get_async_engine(url=self._dsn, settings=self._engine_settings)
        self._session = get_async_session(self._engine, settings=self._session_settings)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = ",".join([f"{name}={value}" for name, value in self.to_dict()])
        return f"{cls_name}({attrs})"

    @property
    def dsn(self) -> str:
        return self._dsn

    @property
    def engine_settings(self) -> SettingsType:
        return self._engine_settings

    @property
    def session_settings(self) -> SettingsType:
        return self._session_settings

    def to_dict(self) -> KeywordsType:
        """Return the dictionary representation."""

        return {
            "dsn": self.dsn,
            "engine_settings": self.engine_settings,
            "session_settings": self.session_settings,
        }

    async def shutdown(self):
        await self._session.close()
        await self._engine.dispose()

    async def ping(self) -> None:
        """Check if the database connection is alive.

        Ping regardless an `Engine.pool_pre_ping` option being set.
        """

        async with self._session() as session:
            async with session.begin():
                await session.execute(text("SELECT 1"))

    async def add_urls(self, url_models: list[HttpUrlModel]) -> list[HttpUrlRow]:
        """Add the url models into the database.

        Args:
            url_models: list[HttpUrlModel] - the url models to insert

        Returns:
            list[HttpUrlRow] - the inserted rows
        """

        try:
            async with self._session() as session:
                query = insert(Url).returning(Url)
                async with session.begin():
                    result = await session.execute(
                        query, [url_model.model_dump() for url_model in url_models]
                    )
                    return [HttpUrlRow.model_validate(row[0]) for row in result]
        except IntegrityError as e:
            raise UrlRepositoryError(str(e)) from e

    async def get_urls(self, url_filter: HttpUrlFilter) -> list[HttpUrlRow]:
        """Get the urls by their filters.

        Args:
            url_filter: HttpUrlFilter - The fields for the WHERE clause.

        Returns:
            list[HttpUrlRow] - the selected rows
        """

        async with self._session() as session:
            query = select(Url)
            query = _get_conditioned_query_from_url_filter(
                query=query, url_filter=url_filter
            )
            async with session.begin():
                result = await session.execute(query)
            return [HttpUrlRow.model_validate(row[0]) for row in result.fetchall()]

    async def delete_url(self, url_filter: HttpUrlFilter) -> HttpUrlRow:
        """Delete the url by the filter.

        Args:
            url_filter: HttpUrlFilter - the fields for the WHERE clause

        Returns:
            HttpUrlRow - the deleted row
        """

        async with self._session() as session:
            query = delete(Url)
            query = _get_conditioned_query_from_url_filter(
                query=query, url_filter=url_filter
            )
            query = query.returning(Url)
            async with session.begin():
                response = await session.execute(query)
                return HttpUrlRow.model_validate(response.one())

    async def mark_url_gone(self, url_filter: HttpUrlFilter) -> HttpUrlRow:
        """Mark the URL gone.

        If a URL is marked as "gone", i.e. the field `is_gone` set True,
        the record remains in the database, but considered to be deleted.

        Args:
            url_filter: HttpUrlFilter - a filter for a URL to be marked "Gone"

        Raises:
            UrlRepositoryError - if the given urls cannot be marked "Gone"

        Returns:
            HttpUrlRow - the affected record model
        """

        async with self._session() as session:
            query = update(Url)
            query = _get_conditioned_query_from_url_filter(query, url_filter=url_filter)
            query = query.values(is_gone=True)
            query = query.returning(Url)
            async with session.begin():
                result = await session.execute(query)
                row = result.one()[0]
                return HttpUrlRow.model_validate(row)

    async def click_url(self, url_filter: HttpUrlFilter) -> HttpUrlRow:
        """Click the given URL.

        When a URL is clicked URL, the following attributes are set:
        * client_info -> the information about the client (if found)
        * clicked_at -> the datetime of the click on the URL (if found)

        It is like a URL being clicked, redirected to and so forth.

        Args:
            url_filter: HttpUrlFilter - a URL to be visited

        Raises:
            UrlRepositoryError - the client information is not set.

        Returns:
            HttpUrlRow - the affected record model
        """

        if not url_filter.client_info:
            msg = "the client information is not set"
            raise UrlRepositoryError(msg)
        url_filter.clicked_at = datetime.now()
        async with self._session() as session:
            ci = url_filter.client_info
            cat = url_filter.clicked_at
            # removing filter for query preparation
            url_filter.client_info = None
            url_filter.clicked_at = None
            result = await self.get_urls(url_filter=url_filter)
            if not result or len(result) != 1:
                msg = f"No result for the filter:\n{url_filter.model_dump()}"
                raise NoResultFound(msg)
            row = result[0]
            nclicks = row.nclicks + 1
            # preapre update query
            query = update(Url)
            query = _get_conditioned_query_from_url_filter(query, url_filter=url_filter)
            query = query.values(client_info=ci)
            query = query.values(clicked_at=cat)
            query = query.values(nclicks=nclicks)
            query = query.returning(Url)
            async with session.begin():
                result = await session.execute(query)
                row = result.one()[0]
                return HttpUrlRow.model_validate(row)
