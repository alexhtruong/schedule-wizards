"""adding department_id column to courses

Revision ID: ed3d6b28179d
Revises: 50d8ca849c2f
Create Date: 2025-05-14 19:01:21.996911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed3d6b28179d'
down_revision: Union[str, None] = '50d8ca849c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('course', sa.Column('department_id', sa.Integer(), sa.ForeignKey('department.id')))


def downgrade() -> None:
    op.drop_column('course', 'department_id')

