from fastapi.routing import APIRouter

from sprint4.models.internal import (
    ServiceStatistics as Stats,
)


INTERNAL_ROUTER = APIRouter(tags=["internal"])


@INTERNAL_ROUTER.get("/stats")
def statistics() -> Stats:
    return Stats()


@INTERNAL_ROUTER.get("/ping")
def ping_database() -> None:
    raise NotImplementedError
