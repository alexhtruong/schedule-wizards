"""remove_student_id_from_reviews

Revision ID: d28956519f4c
Revises: ed3d6b28179d
Create Date: 2025-05-14 19:46:55.775031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd28956519f4c'
down_revision: Union[str, None] = 'ed3d6b28179d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop foreign key constraint if it exists
    op.drop_constraint('review_student_id_fkey', 'review', type_='foreignkey')
    
    # Remove the student_id column
    op.drop_column('review', 'student_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the student_id column
    op.add_column('review',
        sa.Column('student_id', sa.INTEGER(), nullable=True)
    )
    
    # Add back the foreign key constraint
    op.create_foreign_key(
        'review_student_id_fkey',
        'review', 'user',
        ['student_id'], ['id']
    )
