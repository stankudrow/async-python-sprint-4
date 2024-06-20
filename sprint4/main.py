from os import getenv
from uvicorn import run as run_asgi

import click
from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI

from sprint4.api.internal import INTERNAL_ROUTER


load_dotenv(find_dotenv())


app = FastAPI()
app.include_router(INTERNAL_ROUTER)


APP_HOST = getenv("S4_SERVER_HOST")
APP_PORT = int(getenv("S4_SERVER_PORT"))


@click.command()
@click.option(
    "-h",
    "--host",
    type=click.STRING,
    default=APP_HOST,
    show_default=True,
    help="application host",
)
@click.option(
    "-p",
    "--port",
    type=click.INT,
    default=APP_PORT,
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
