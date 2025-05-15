"""adding avg stats for courses

Revision ID: 50d8ca849c2f
Revises: 515bab4b511c
Create Date: 2025-05-14 18:26:25.001659

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50d8ca849c2f'
down_revision: Union[str, None] = '515bab4b511c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('course', sa.Column('avg_workload', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('avg_rating', sa.Float(), nullable=True))

def downgrade() -> None:
    op.drop_column('course', 'avg_workload')
    op.drop_column('course', 'avg_rating')
