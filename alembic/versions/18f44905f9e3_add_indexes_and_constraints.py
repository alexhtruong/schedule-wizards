"""add_constraints

Revision ID: 18f44905f9e3
Revises: d06b18856363
Create Date: 2025-05-10 11:02:39.443567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18f44905f9e3'
down_revision: Union[str, None] = 'd06b18856363'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'department',
        sa.Column('area', sa.String())
    )
    
    op.create_check_constraint(
        'ck_review_difficulty',
        'review',
        'difficulty BETWEEN 1 AND 5'
    )
    op.create_check_constraint(
        'ck_review_overall_rating',
        'review',
        'overall_rating BETWEEN 1 AND 5'
    )
    op.create_check_constraint(
        'ck_review_workload',
        'review',
        'workload_rating BETWEEN 0 AND 168'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_review_difficulty', 'review')
    op.drop_constraint('ck_review_overall_rating', 'review')
    op.drop_constraint('ck_review_workload', 'review')
    
    op.drop_column('department', 'area')
