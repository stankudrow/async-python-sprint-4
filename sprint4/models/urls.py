from datetime import datetime
from enum import Enum

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, NonNegativeInt, field_serializer

from sprint4.core.url_shorteners import ShortenersEnum


class UrlVisibilityTypes(str, Enum):
    public = "public"
    private = "private"


class HttpUrlBase(BaseModel):
    url: AnyHttpUrl
    visibility: UrlVisibilityTypes = UrlVisibilityTypes.public

    @field_serializer("url")
    def serialize_url(self, url: AnyHttpUrl, _info) -> str:
        return str(url)

    @field_serializer("visibility")
    def serialize_visibility(self, visibility: UrlVisibilityTypes, _info) -> str:
        return visibility.value


class HttpUrlModel(HttpUrlBase):
    short_url: AnyHttpUrl

    @field_serializer("short_url")
    def serialize_short_url(self, short_url: AnyHttpUrl, _info) -> str:
        return str(short_url)


class HttpUrlRow(HttpUrlModel):
    model_config = ConfigDict(from_attributes=True)

    id: NonNegativeInt
    is_gone: bool = False
    client_info: None | str
    clicked_at: None | datetime
    nclicks: NonNegativeInt


class HttpUrlFilter(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: None | NonNegativeInt = None
    url: None | AnyHttpUrl = None
    short_url: None | AnyHttpUrl = None
    is_gone: None | bool = None
    visibility: None | UrlVisibilityTypes = None
    client_info: None | str = None
    clicked_at: None | datetime = None
    nclicks: None | int = None

    @field_serializer("url")
    def serialize_url(self, url: AnyHttpUrl, _info) -> None | str:
        return str(url) if url else url

    @field_serializer("short_url")
    def serialize_short_url(self, short_url: AnyHttpUrl, _info) -> None | str:
        return str(short_url) if short_url else short_url

    @field_serializer("visibility")
    def serialize_visibility(
        self, visibility: None | UrlVisibilityTypes, _info
    ) -> None | str:
        return visibility.value if visibility else visibility


class HttpUrlAddRequest(HttpUrlBase):
    shortener_code: ShortenersEnum = ShortenersEnum.clckru
