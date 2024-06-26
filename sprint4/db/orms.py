"""Database ORMs module."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text

from sprint4.models.urls import UrlVisibilityTypes


Base = declarative_base()


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    short_url: Mapped[str] = mapped_column(unique=True, nullable=False)
    is_gone: Mapped[bool] = mapped_column(default=False, nullable=False)
    visibility: Mapped[UrlVisibilityTypes] = mapped_column(
        default=UrlVisibilityTypes.public, nullable=False
    )
    client_info: Mapped[None | str] = mapped_column(Text)
    clicked_at: Mapped[None | datetime]
    nclicks: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = ", ".join([f"{col}={val}" for col, val in self.to_dict().items()])
        return f"{cls_name}({attrs})"

    def to_dict(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
