from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from sprint4.api import URL_SHORTENER_SERVICE
from sprint4.models import ServiceStatistics

INTERNAL_ROUTER = APIRouter(tags=["internal"])


@INTERNAL_ROUTER.get(
    path="/stats",
    summary="Service live statistics",
    description="Returns the service live status in the `Service-Ping` header.",
)
async def get_statistics() -> ServiceStatistics:
    stats = await URL_SHORTENER_SERVICE.get_stats()
    return JSONResponse(
        content=stats.model_dump_json(), headers={"Service-Ping": "Pong"}
    )


@INTERNAL_ROUTER.get(
    path="/db/ping",
    summary="Database ping status",
    description="Returns the service database live status in the `DB-Ping` header.",
)
async def ping_database() -> None:
    try:
        await URL_SHORTENER_SERVICE.ping_db()
        return JSONResponse(content={"ping": "pong"}, headers={"DB-Ping": "Pong"})
    except Exception:
        raise HTTPException(status_code=418, headers={"DB-Ping": "Failed"})
