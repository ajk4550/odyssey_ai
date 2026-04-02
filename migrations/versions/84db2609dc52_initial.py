"""initial

Revision ID: 84db2609dc52
Revises: 
Create Date: 2026-03-10 11:33:22.358751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '84db2609dc52'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'trips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_input', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_trips_id'), 'trips', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_trips_id'), table_name='trips')
    op.drop_table('trips')
