"""drop professor_tags table

Revision ID: d7d2b7250947
Revises: d28956519f4c
Create Date: 2025-05-15 16:10:21.928920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7d2b7250947'
down_revision: Union[str, None] = 'd28956519f4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('professor_tags')


def downgrade() -> None:
    """Downgrade schema."""
    pass
