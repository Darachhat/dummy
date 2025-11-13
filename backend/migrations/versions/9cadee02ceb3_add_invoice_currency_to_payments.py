"""add invoice_currency to payments

Revision ID: 9cadee02ceb3
Revises: 
Create Date: 2025-11-13 10:18:45.152670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_invoice_currency'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade():
    op.add_column('payments', sa.Column('invoice_currency', sa.String(), nullable=True))


def downgrade():
    op.drop_column('payments', 'invoice_currency')
