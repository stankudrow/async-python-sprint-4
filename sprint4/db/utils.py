from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from sprint4.core.ptypes import KeywordsType


def get_async_engine(url: str, settings: None | KeywordsType = None) -> AsyncEngine:
    settings = settings if settings else {}
    return create_async_engine(url=url, **settings)


def get_async_session(
    engine: AsyncEngine, settings: None | KeywordsType = None
) -> AsyncSession:
    settings = settings if settings else {}
    return async_sessionmaker(bind=engine, **settings)
