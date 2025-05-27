"""add unique constraint to course code

Revision ID: a1b2c3d4e5f6
Revises: 1e2b5b977441
Create Date: 2025-05-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '1e2b5b977441'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'uq_course_code_department',
        'course',
        ['course_code', 'department_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'uq_course_code_department',
        'course',
        type_='unique'
    )
