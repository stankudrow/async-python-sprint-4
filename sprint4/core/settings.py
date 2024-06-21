"""Project configuration module."""

from pathlib import Path
from os import getenv

import tomli
from dotenv import find_dotenv, load_dotenv
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


load_dotenv(find_dotenv())

_LOCALHOST = "localhost"

PG_USER = getenv("S4_POSTGRES_USER", "postgres")
PG_PWD = getenv("S4_POSTGRES_PASSWORD", "postgres")
PG_HOST = getenv("S4_POSTGRES_HOST", _LOCALHOST)
PG_PORT = getenv("S4_POSTGRES_PORT", 5432)
PG_DB = getenv("S4_POSTGRES_DATABASE", "postgres")


# the `pyproject-parser` package seemed disappointing for me
with open(Path(__file__).parent.parent.parent / "pyproject.toml", mode="rb") as pyprof:
    _PyProject: dict = tomli.load(pyprof)
    _PyProjectMeta: dict = _PyProject["tool"]["poetry"]


class ServerSettings(BaseSettings):
    """The main service (application) configuration."""

    # model_config = SettingsConfigDict(prefix="S4_")  # does not work (???)

    host: str = Field(validation_alias="s4_server_host", default=_LOCALHOST)
    port: int = Field(validation_alias="s4_server_port", default=8080)


class PostgresSettings(BaseSettings):
    """The database (sql -> postgres) configuration.

    The credentials should be defined in the environment file.
    This file is meant to be `.env`, containing variables with `S4_` prefix.
    """

    url: PostgresDsn = (
        f"postgresql+asyncpg://"
        f"{PG_USER}:{PG_PWD}"
        f"@{PG_HOST}:{PG_PORT}"
        f"/{PG_DB}"
    )


class Settings(BaseSettings):
    title: str = _PyProjectMeta.get("title", "App Title")
    version: str = _PyProjectMeta.get("version", "App Version")
    summary: str = _PyProjectMeta.get("summary", "App Summary")
    description: str = _PyProjectMeta.get("description", "App Description")

    server: ServerSettings = ServerSettings()
    postgres: PostgresSettings = PostgresSettings()


SETTINGS = Settings()
