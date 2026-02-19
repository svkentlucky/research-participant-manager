"""Create studies table

Revision ID: 002
Revises: 001
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'studies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('client_name', sa.String(255), nullable=False),
        sa.Column('methodology', sa.String(50), nullable=False),
        sa.Column('target_count', sa.Integer(), nullable=False),
        sa.Column('incentive_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_studies_client_name', 'studies', ['client_name'])
    op.create_index('ix_studies_status', 'studies', ['status'])
    op.create_index('ix_studies_status_start', 'studies', ['status', 'start_date'])


def downgrade() -> None:
    op.drop_index('ix_studies_status_start', table_name='studies')
    op.drop_index('ix_studies_status', table_name='studies')
    op.drop_index('ix_studies_client_name', table_name='studies')
    op.drop_table('studies')
