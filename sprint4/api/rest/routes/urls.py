
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRouter

from sprint4.api import URL_SHORTENER_SERVICE, UrlServiceError
from sprint4.models.urls import HttpUrlAddRequest, HttpUrlFilter, HttpUrlRow


URLS_ROUTER = APIRouter(prefix="/urls", tags=["HTTP URLs"])
URL_STATUSES_ROUTER = APIRouter(prefix="/statuses", tags=["URL statuses"])


def _assign_client_data_from_headers(
    request: Request, url_filter: HttpUrlFilter
) -> HttpUrlFilter:
    ip_addr, port = request.get("client")
    user_agent = request.headers.get("user-agent")
    client_info = f"<address={ip_addr}:{port};user-agent={user_agent}>"
    url_filter.client_info = client_info
    return url_filter


def _get_redirected_response(row: HttpUrlRow) -> ORJSONResponse:
    content = row.model_dump()
    return ORJSONResponse(
        content=content, status_code=307, headers={"Location": content["url"]}
    )


@URLS_ROUTER.post(
    path="/",
    summary="Batch upload URLs.",
    description="Post URLs each with shortener and URL properties specified.",
)
async def add_urls(urls: list[HttpUrlAddRequest]) -> list[HttpUrlRow]:
    try:
        return await URL_SHORTENER_SERVICE.add_urls(urls)
    except UrlServiceError as e:
        raise HTTPException(status_code=409, detail=str(e))


@URLS_ROUTER.delete(
    path="/{url_id}",
    summary="Delete the URL by its id.",
    description=(
        "Returns the deleted URL or raises NotFound error.\n"
        "If `mark_gone` query parametre is True, "
        "the URL is marked as gone, but remains in the database."
    ),
)
async def delete_url_by_id(url_id: int, mark_gone: bool = False) -> HttpUrlRow:
    url_filter = HttpUrlFilter(id=url_id)
    if mark_gone:
        result = await URL_SHORTENER_SERVICE.mark_url_gone(url_filter=url_filter)
        return ORJSONResponse(content=result.model_dump(), status_code=200)
    result = await URL_SHORTENER_SERVICE.delete_url(url_filter=url_filter)
    return ORJSONResponse(content=result.model_dump(), status_code=410)


@URL_STATUSES_ROUTER.get(
    path="/all",
    summary="Get all URL statuses",
    description="Returns all non-paginated urls. Proceed with caution.",
)
async def get_all_url_statuses() -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(url_filter=HttpUrlFilter())


@URL_STATUSES_ROUTER.get(
    path="/{url_id}",
    summary="Get the URL status by its id.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_id(url_id: int) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(
        url_filter=HttpUrlFilter(id=url_id)
    )


@URL_STATUSES_ROUTER.get(
    path="/short-url/{short_url:path}",  # thanks to Starlette
    summary="Get the URL status by its short URL.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_short_url(short_url: str) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(
        url_filter=HttpUrlFilter(short_url=short_url)
    )


# changed to /full/ for nivelating the route handling orderly
@URL_STATUSES_ROUTER.get(
    path="/full-url/{url:path}",  # thanks to Starlette
    summary="Get the URL status by its original URL.",
    description="Returns the basic information on the given and found URL.",
)
async def get_url_status_by_url(url: str) -> list[HttpUrlRow]:
    return await URL_SHORTENER_SERVICE.get_url_stats(url_filter=HttpUrlFilter(url=url))


@URLS_ROUTER.get(
    path="/{url_id}",
    summary="Get the URL by its id.",
    description="Returns the URL for the redirection.",
)
async def click_url_by_id(request: Request, url_id: int) -> HttpUrlRow:
    url_filter = HttpUrlFilter(id=url_id)
    url_filter = _assign_client_data_from_headers(
        request=request, url_filter=url_filter
    )
    row = await URL_SHORTENER_SERVICE.click_url(url_filter=url_filter)
    return _get_redirected_response(row)


@URLS_ROUTER.get(
    path="/short-url/{short_url:path}",
    summary="Get the URL by its short URL.",
    description="Returns the URL for the redirection.",
)
async def click_url_by_short_url(request: Request, short_url: str) -> HttpUrlRow:
    url_filter = HttpUrlFilter(short_url=short_url)
    url_filter = _assign_client_data_from_headers(
        request=request, url_filter=url_filter
    )
    row = await URL_SHORTENER_SERVICE.click_url(url_filter=url_filter)
    print(f"ROW = {row}")
    return _get_redirected_response(row)


@URLS_ROUTER.get(
    path="/full-url/{url:path}",
    summary="Get the URL by its original URL.",
    description="Returns the URL for the redirection.",
)
async def click_url_by_url(request: Request, url: str) -> HttpUrlRow:
    url_filter = HttpUrlFilter(url=url)
    url_filter = _assign_client_data_from_headers(
        request=request, url_filter=url_filter
    )
    row = await URL_SHORTENER_SERVICE.click_url(url_filter=url_filter)
    return _get_redirected_response(row)
