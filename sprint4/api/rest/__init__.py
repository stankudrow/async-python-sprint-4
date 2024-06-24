# from typing import Annotated, Generator

# from fastapi import Depends

# from sprint4.core.exceptions import UrlServiceError
# from sprint4.services.url_shortener import UrlShortenerService  # noqa: F401


# URL_SHORTENER_SERVICE = UrlShortenerService()


# def url_service() -> Generator[None, None, UrlShortenerService]:
#     yield URL_SHORTENER_SERVICE


# ServiceDependency = Annotated[UrlShortenerService, Depends(url_service)]
