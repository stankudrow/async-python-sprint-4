from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from sprint4.api.rest.routes import INTERNAL_ROUTER, URLS_ROUTER
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


@APP.exception_handler(ValidationError)
async def handler_invalid_data_model(
    request: Request,
    exc: ValidationError,
):
    return ORJSONResponse(status_code=422, content={"msg": f"ValidationError: {exc}"})
