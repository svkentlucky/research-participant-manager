"""Create respondents table

Revision ID: 001
Revises:
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'respondents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(2), nullable=True),
        sa.Column('zip_code', sa.String(10), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('ethnicity', sa.String(50), nullable=True),
        sa.Column('household_income', sa.String(50), nullable=True),
        sa.Column('occupation', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_respondents_email', 'respondents', ['email'], unique=True)
    op.create_index('ix_respondents_state', 'respondents', ['state'])
    op.create_index('ix_respondents_age', 'respondents', ['age'])
    op.create_index('ix_respondents_household_income', 'respondents', ['household_income'])
    op.create_index('ix_respondents_is_active', 'respondents', ['is_active'])
    op.create_index('ix_respondents_state_age', 'respondents', ['state', 'age'])
    op.create_index('ix_respondents_active_state', 'respondents', ['is_active', 'state'])


def downgrade() -> None:
    op.drop_index('ix_respondents_active_state', table_name='respondents')
    op.drop_index('ix_respondents_state_age', table_name='respondents')
    op.drop_index('ix_respondents_is_active', table_name='respondents')
    op.drop_index('ix_respondents_household_income', table_name='respondents')
    op.drop_index('ix_respondents_age', table_name='respondents')
    op.drop_index('ix_respondents_state', table_name='respondents')
    op.drop_index('ix_respondents_email', table_name='respondents')
    op.drop_table('respondents')
