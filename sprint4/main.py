import asyncio

import click
import uvloop
from uvicorn import run as run_asgi

from sprint4.core.settings import SETTINGS
from sprint4.api.rest.app import APP

# setting uvloop instead of asyncio default one
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


app = APP


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
