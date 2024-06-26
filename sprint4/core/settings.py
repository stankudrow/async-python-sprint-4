"""Project configuration module."""

from pathlib import Path
from os import getenv
from typing import Callable

import orjson
import tomli
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, PostgresDsn, field_serializer
from pydantic_settings import BaseSettings


load_dotenv(find_dotenv())

_LOCALHOST = "localhost"

PG_USER = getenv("S4_POSTGRES_USER", "postgres")
PG_PWD = getenv("S4_POSTGRES_PASSWORD", "postgres")
PG_HOST = getenv("S4_POSTGRES_HOST", _LOCALHOST)
PG_PORT = getenv("S4_POSTGRES_PORT", 5432)
PG_DB = getenv("S4_POSTGRES_DATABASE", "postgres")


# The `pyproject-parser` package seemed disappointing for me.
# So parsing the `pyproject.toml` "manually".
with open(Path(__file__).parent.parent.parent / "pyproject.toml", mode="rb") as pyprof:
    _PyProject: dict = tomli.load(pyprof)
    _MainSection: dict = _PyProject["tool"]["poetry"]
    _AppMetaSection: dict = _PyProject["tool"]["app_meta"]


class ServerSettings(BaseSettings):
    """The main service (application) configuration."""

    # model_config = SettingsConfigDict(prefix="S4_")  # does not work (???)

    host: str = Field(validation_alias="s4_server_host", default=_LOCALHOST)
    port: int = Field(validation_alias="s4_server_port", default=8080)


class PostgresEngineConfig(BaseModel):
    echo: bool = True
    echo_pool: bool = True
    hide_parameters: bool = True
    json_deserializer: Callable = orjson.loads
    json_serializer: Callable = orjson.dumps
    pool_pre_ping: bool = True


class PostgresSessionConfig(BaseModel):
    autobegin: bool = False
    autoflush: bool = True
    expire_on_commit: bool = False


class PostgresSettings(BaseSettings):
    """The database (sql -> postgres) configuration.

    The credentials should be defined in the environment file.
    This file is meant to be `.env`, containing variables with `S4_` prefix.
    """

    dsn: PostgresDsn = (
        f"postgresql+asyncpg://"
        f"{PG_USER}:{PG_PWD}"
        f"@{PG_HOST}:{PG_PORT}"
        f"/{PG_DB}"
    )
    engine_settings: PostgresEngineConfig = PostgresEngineConfig()
    session_settings: PostgresSessionConfig = PostgresSessionConfig()

    @field_serializer("dsn")
    def serialise_dsn(self, dsn, _info) -> str:
        return str(dsn)


class Settings(BaseSettings):
    title: str = _AppMetaSection.get("title", "App Title")
    version: str = _MainSection.get("version", "App Version")
    summary: str = _AppMetaSection.get("summary", "App Summary")
    description: str = _MainSection.get("description", "App Description")

    server: ServerSettings = ServerSettings()
    postgres: PostgresSettings = PostgresSettings()


SETTINGS = Settings()
