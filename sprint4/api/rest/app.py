from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DataError, DatabaseError, NoResultFound

from sprint4.api.rest import BLACKLIST_IPS
from sprint4.api.rest.routes import INTERNAL_ROUTER, URLS_ROUTER, URL_STATUSES_ROUTER
from sprint4.core.settings import SETTINGS


APP = FastAPI(
    title=SETTINGS.title,
    summary=SETTINGS.summary,
    description=SETTINGS.description,
    version=SETTINGS.version,
    default_response_class=ORJSONResponse,
)
APP.include_router(INTERNAL_ROUTER)
APP.include_router(URLS_ROUTER)
APP.include_router(URL_STATUSES_ROUTER)


@APP.exception_handler(ValidationError)
async def handle_invalid_data_model(
    request: Request,
    exc: ValidationError,
):
    return ORJSONResponse(status_code=422, content={"msg": f"ValidationError: {exc}"})


@APP.exception_handler(DataError)
async def handle_invalid_data_from_db(
    request: Request,
    exc: DataError,
):
    return ORJSONResponse(status_code=422, content={"msg": f"DataError: {exc}"})


@APP.exception_handler(NoResultFound)
async def handle_not_found_entity(
    request: Request,
    exc: NoResultFound,
):
    return ORJSONResponse(status_code=404, content={"msg": f"NotFoundError: {exc}"})


@APP.exception_handler(DatabaseError)
async def handle_database_error(
    request: Request,
    exc: DatabaseError,
):
    return ORJSONResponse(status_code=418, content={"msg": f"DatabaseError: {exc}"})


@APP.middleware("http")
async def filter_hosts(request: Request, call_next):
    ip, _ = request.get("client")
    if ip in BLACKLIST_IPS:
        msg = f"the IP={ip} is in the black list"
        return ORJSONResponse(content=msg, status_code=400)
    return await call_next(request)
