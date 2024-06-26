"""Project types module."""

from typing import Any

from pydantic import AnyHttpUrl


KeywordsType = dict[str, Any]
SettingsType = KeywordsType

HttpUrlType = str | AnyHttpUrl
