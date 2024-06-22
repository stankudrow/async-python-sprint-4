from pydantic import AnyHttpUrl, BaseModel, field_serializer


class HttpUrl(BaseModel):
    url: AnyHttpUrl
    short_url: AnyHttpUrl

    @field_serializer("url")
    def serialize_url(self, url: AnyHttpUrl, _info) -> str:
        return str(url)

    @field_serializer("short_url")
    def serialize_short_url(self, short_url: AnyHttpUrl, _info) -> str:
        return str(short_url)
