"""trip status enum

Revision ID: df9e00f0406e
Revises: 84db2609dc52
Create Date: 2026-03-10 11:55:14.654597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df9e00f0406e'
down_revision: Union[str, Sequence[str], None] = '84db2609dc52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum('pending', 'processing', 'completed', 'failed', name='tripstatus').create(op.get_bind())
    op.alter_column('trips', 'status',
               existing_type=sa.VARCHAR(),
               type_=sa.Enum('pending', 'processing', 'completed', 'failed', name='tripstatus'),
               nullable=False,
               postgresql_using='status::tripstatus')


def downgrade() -> None:
    op.alter_column('trips', 'status',
               existing_type=sa.Enum('pending', 'processing', 'completed', 'failed', name='tripstatus'),
               type_=sa.VARCHAR(),
               nullable=True)
    sa.Enum(name='tripstatus').drop(op.get_bind())
