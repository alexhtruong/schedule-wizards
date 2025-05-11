"""translating database ER diagram to actual tables

Revision ID: d06b18856363
Revises: e91d0c24f7d0
Create Date: 2025-05-05 13:48:09.935196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd06b18856363'
down_revision: Union[str, None] = 'e91d0c24f7d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('global_inventory')
    
    op.create_table(
        'school',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False)
    )

    op.create_table(
        'department',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('abbrev', sa.String(), nullable=False),
        sa.Column('school_id', sa.Integer(), sa.ForeignKey('school.id'), nullable=False)
    )

    op.create_table(
        'professor',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('avg_rating', sa.Float()),
        sa.Column('classes_taught', sa.Integer()),
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('department.id'), nullable=False),
        sa.Column('total_reviews', sa.Integer()),
        sa.Column('avg_difficulty', sa.Integer()),
        sa.Column('avg_workload', sa.Integer()),
    )

    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True)
    )

    op.create_table(
        'professor_tags',
        sa.Column('professor_id', sa.Integer(), sa.ForeignKey('professor.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id'), primary_key=True)
    )

    op.create_table(
        'course',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('course_code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False)
    )

    op.create_table(
        'student',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('major', sa.String()),
        sa.Column('dept_id', sa.Integer(), sa.ForeignKey('department.id')),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('review_count', sa.Integer(), default=0)
    )

    op.create_table(
        'review',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('course.id'), nullable=False),
        sa.Column('term', sa.String(), nullable=False),
        sa.Column('difficulty', sa.Integer()),
        sa.Column('overall_rating', sa.Integer()),
        sa.Column('workload_rating', sa.Integer()),
        sa.Column('comments', sa.String()),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('student.id'), nullable=False)
    )

    op.create_table(
        'review_tags',
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('review.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id'), primary_key=True)
    )

    op.create_table(
        'professors_courses',
        sa.Column('professor_id', sa.Integer(), sa.ForeignKey('professor.id'), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('course.id'), primary_key=True),
    )

    op.create_table(
        'department_courses',
        sa.Column('department_id', sa.Integer(), sa.ForeignKey('department.id'), primary_key=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('course.id'), primary_key=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('department_courses')
    op.drop_table('professors_courses')
    op.drop_table('review')
    op.drop_table('student')
    op.drop_table('course')
    op.drop_table('professor')
    op.drop_table('department')
    op.drop_table('school')
    op.drop_table('review_tags')
    op.drop_table('professor_tags')
    op.drop_table('tag')
