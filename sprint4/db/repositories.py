"""Database repositories module."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import delete, insert, select, text, Delete, Select

from sprint4.core.exceptions import UrlRepositoryError
from sprint4.core.ptypes import KeywordsType, SettingsType
from sprint4.core.settings import SETTINGS
from sprint4.db.orms import Url
from sprint4.db.utils import get_async_engine, get_async_session
from sprint4.models.urls import HttpUrlModel, HttpUrlRow, HttpUrlFilter


_FilterableQueryType = Delete | Select


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
                # TODO: update UrlHistory
            return [HttpUrlRow.model_validate(row[0]) for row in result.fetchall()]

    async def delete_urls(self, url_filters: list[HttpUrlFilter]) -> list[HttpUrlRow]:
        """Delete the urls by their filters.

        Args:
            url_filters: list[HttpUrlFilter]- the fields for the WHERE clause

        Returns:
            list[HttpUrlRow] - the deleted rows
        """

        async with self._session() as session:
            query = delete(Url)
            for url_filter in url_filters:
                query = _get_conditioned_query_from_url_filter(
                    query=query, url_filter=url_filter
                )
            query = query.returning(Url)
            async with session.begin():
                result = await session.execute(query)
                return [HttpUrlRow.model_validate(row[0]) for row in result]

    # async def mark_urls_gone(self, urls: list[HttpUrlModel]) -> list[HttpUrlRow]:
    #     """Mark URLs gone.

    #     If a URL is marked as "gone", i.e. the field `is_gone` set True,
    #     the record remains in the database, but considered to be deleted.

    #     Args:
    #         urls: list[HttpUrlModel] - URLs to be marked "Gone"

    #     Raises:
    #         UrlRepositoryError - if the given urls cannot be marked "Gone"

    #     Returns:
    #         list[HttpUrlRow] - the affected record models
    #     """

    #     async with self._session() as session:
    #         query = update(Url).returning(Url)
    #         async with session.begin():
    #             params = self._get_params_from_url_models(urls)
    #             if not (rows := await self.get_urls(params=params)):
    #                 raise UrlRepositoryError("no rows to mark as 'Gone'")
    #             new_rows: list[KeywordsType] = []
    #             while rows:
    #                 row: Url = rows.pop()
    #                 new_row = row.to_dict()
    #                 new_row["is_gone"] = True
    #                 new_rows.append(new_row)
    #             results = await session.execute(query, new_rows)
    #             return [HttpUrlRow.model_validate(row[0]) for row in results.fetchall()]

    # async def mark_urls_visited(self, urls: list[HttpUrlModel]) -> list[HttpUrlRow]:
    #     """Mark URLs visited.

    #     It is like a URL being clicked, redirected to and so forth.

    #     Args:
    #         urls: list[HttpUrlModel] - URLs to be marked "Visited"

    #     Returns:
    #         list[HttpUrlRow] - the affected record models
    #     """

    #     async with self._session() as session:
    #         query = update(Url).returning(Url)
    #         async with session.begin():
    #             params = self._get_params_from_url_models(urls)
    #             if not (rows := await self.get_urls(params=params)):
    #                 raise UrlRepositoryError("no rows to mark as 'Gone'")
    #             new_rows: list[KeywordsType] = []
    #             while rows:
    #                 row: Url = rows.pop()
    #                 new_row = row.to_dict()
    #                 new_row["is_gone"] = True
    #                 new_rows.append(new_row)
    #             results = await session.execute(query, new_rows)
    #             return [HttpUrlRow.model_validate(row[0]) for row in results.fetchall()]
