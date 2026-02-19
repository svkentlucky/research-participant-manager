"""Create study_assignments table

Revision ID: 004
Revises: 003
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'study_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_id', sa.Integer(), nullable=False),
        sa.Column('respondent_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='invited'),
        sa.Column('invited_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['study_id'], ['studies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['respondent_id'], ['respondents.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('study_id', 'respondent_id', name='uq_study_respondent')
    )

    # Create indexes
    op.create_index('ix_study_assignments_study_id', 'study_assignments', ['study_id'])
    op.create_index('ix_study_assignments_respondent_id', 'study_assignments', ['respondent_id'])
    op.create_index('ix_study_assignments_status', 'study_assignments', ['status'])


def downgrade() -> None:
    op.drop_index('ix_study_assignments_status', table_name='study_assignments')
    op.drop_index('ix_study_assignments_respondent_id', table_name='study_assignments')
    op.drop_index('ix_study_assignments_study_id', table_name='study_assignments')
    op.drop_table('study_assignments')
