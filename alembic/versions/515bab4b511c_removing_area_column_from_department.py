"""removing area column from department

Revision ID: 515bab4b511c
Revises: 18f44905f9e3
Create Date: 2025-05-10 23:30:30.395859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '515bab4b511c'
down_revision: Union[str, None] = '18f44905f9e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('department', 'area')


def downgrade() -> None:
    op.add_column(
        'department',
        sa.Column('area', sa.String())
    )
