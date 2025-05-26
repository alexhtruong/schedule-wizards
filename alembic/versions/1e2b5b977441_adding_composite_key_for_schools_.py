"""adding composite key for schools between name and state

Revision ID: 1e2b5b977441
Revises: c4b2abf1b372
Create Date: 2025-05-25 19:49:14.120014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2b5b977441'
down_revision: Union[str, None] = 'c4b2abf1b372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        'uq_school_name_state',
        'school',
        ['name', 'state']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'uq_school_name_state',
        'school'
    )
