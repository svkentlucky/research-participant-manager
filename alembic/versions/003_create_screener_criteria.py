"""Create screener_criteria table

Revision ID: 003
Revises: 002
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'screener_criteria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(50), nullable=False),
        sa.Column('operator', sa.String(20), nullable=False),
        sa.Column('value', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['study_id'], ['studies.id'], ondelete='CASCADE')
    )

    # Create index on study_id for fast lookups
    op.create_index('ix_screener_criteria_study_id', 'screener_criteria', ['study_id'])


def downgrade() -> None:
    op.drop_index('ix_screener_criteria_study_id', table_name='screener_criteria')
    op.drop_table('screener_criteria')
