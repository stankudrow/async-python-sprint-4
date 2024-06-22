"""Database ORMs module."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Text


Base = declarative_base()


class URLs(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    short_url: Mapped[str] = mapped_column(unique=True, nullable=False)
