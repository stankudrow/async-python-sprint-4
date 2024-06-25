from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DataError, DatabaseError, NoResultFound

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

# too lazy to add the advanced middleware support and design
APP.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.example.com"])


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
