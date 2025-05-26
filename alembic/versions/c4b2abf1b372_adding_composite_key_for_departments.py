"""adding composite key for departments

Revision ID: c4b2abf1b372
Revises: d7d2b7250947
Create Date: 2025-05-25 19:34:45.434800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4b2abf1b372'
down_revision: Union[str, None] = 'd7d2b7250947'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        'department_name_school_unique',
        'department',
        ['name', 'school_id']
    )
    op.create_unique_constraint(
        'department_abbrev_school_unique', 
        'department',
        ['abbrev', 'school_id']
    )


def downgrade() -> None:
    op.drop_constraint(
        'department_name_school_unique',
        'department',
        type_='unique'
    )
    op.drop_constraint(
        'department_abbrev_school_unique',
        'department',
        type_='unique'
    )
