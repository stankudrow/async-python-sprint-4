"""init the sprint4 db

Revision ID: 5c59b447e8f5
Revises: 
Create Date: 2024-06-16 13:57:49.196181

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c59b447e8f5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


URLS_TABLE: str = "urls"


def upgrade() -> None:
    op.create_table(
        URLS_TABLE,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table(URLS_TABLE)
