import asyncio

import click
import uvloop
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from uvicorn import run as run_asgi

from sprint4.api.rest import INTERNAL_ROUTER, URIS_ROUTER
from sprint4.core.settings import SETTINGS

# setting uvloop instead of asyncio default one
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


app = FastAPI(
    title=SETTINGS.title,
    summary=SETTINGS.summary,
    description=SETTINGS.description,
    version=SETTINGS.version,
    default_response_class=ORJSONResponse,
)
app.include_router(INTERNAL_ROUTER)
app.include_router(URIS_ROUTER)


@click.command()
@click.option(
    "-h",
    "--host",
    type=click.STRING,
    default=SETTINGS.server.host,
    show_default=True,
    help="application host",
)
@click.option(
    "-p",
    "--port",
    type=click.INT,
    default=SETTINGS.server.port,
    show_default=True,
    help="application port",
)
def main(host: str, port: int) -> None:
    run_asgi(
        app="main:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
