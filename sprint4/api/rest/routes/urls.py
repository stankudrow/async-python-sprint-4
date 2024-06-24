from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from sprint4.api import URL_SHORTENER_SERVICE, UrlServiceError
from sprint4.models.urls import HttpUrlAddRequest, HttpUrlFilter, HttpUrlRow


URLS_ROUTER = APIRouter(prefix="/urls", tags=["HTTP URLs"])


@URLS_ROUTER.post(
    path="/",
    summary="Batch upload URLs",
    description="Post URLs each with shortener and URL properties specified.",
)
async def add_urls(urls: list[HttpUrlAddRequest]) -> list[HttpUrlRow]:
    try:
        return await URL_SHORTENER_SERVICE.add_urls(urls)
    except UrlServiceError as e:
        raise HTTPException(status_code=409, detail=str(e))


@URLS_ROUTER.get(
    path="/all",
    summary="Get all URLs",
    description="Returns all non-paginated urls. Proceed with caution.",
)
async def get_all_urls() -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_urls(url_filter=HttpUrlFilter())


@URLS_ROUTER.get(
    path="/status/{url_id}",
    summary="Get the URL information by its id.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_id(url_id: int) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(
        url_filter=HttpUrlFilter(id=url_id)
    )


@URLS_ROUTER.get(
    path="/short-url/status/{short_url:path}",  # thanks to Starlette
    summary="Get the URL information by its short URL.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_short_url(short_url: str) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(
        url_filter=HttpUrlFilter(short_url=short_url)
    )


# changed to /full/ for nivelating the route handling orderly
@URLS_ROUTER.get(
    path="/full-url/status/{url:path}",  # thanks to Starlette
    summary="Get the URL information by its original URL.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_url(url: str) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(url_filter=HttpUrlFilter(url=url))
