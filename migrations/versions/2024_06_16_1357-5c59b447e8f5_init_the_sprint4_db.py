"""init the sprint4 database

Revision ID: 5c59b447e8f5
Revises: 
Create Date: 2024-06-16 13:57:49.196181
"""

from enum import Enum
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c59b447e8f5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# tables
URLS_TABLE: str = "urls"

# columns
SHORT_URL_COL = "short_url"

# indexes
IDX_SUFFIX = "idx"
SHORT_URL_INDEX = f"{SHORT_URL_COL}_{IDX_SUFFIX}"


# data
class UrlVisibilityTypes(str, Enum):
    public = "public"
    private = "private"


def upgrade() -> None:
    op.create_table(
        URLS_TABLE,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("url", sa.Text, nullable=False, comment="URL"),
        sa.Column(
            SHORT_URL_COL,
            sa.String,
            unique=True,
            nullable=False,
            comment="Shortened URL",
        ),
        sa.Column(
            "is_gone",
            sa.Boolean,
            default=False,
            server_default="False",
            nullable=False,
            comment="The mark for deletion",
        ),
        sa.Column(
            "visibility",
            sa.Enum(UrlVisibilityTypes),
            default=UrlVisibilityTypes.public,
            server_default=UrlVisibilityTypes.public,
            nullable=False,
            comment="The kind of URL by visibility: public, private, etc.",
        ),
    )
    op.create_index(
        index_name=SHORT_URL_INDEX,
        table_name=URLS_TABLE,
        columns=[SHORT_URL_COL],
        unique=True,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        index_name=SHORT_URL_INDEX,
        table_name=URLS_TABLE,
        if_exists=True,
    )
    op.drop_table(URLS_TABLE)
