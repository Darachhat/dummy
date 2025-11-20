from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "add_invoice_currency"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # no-op: columns already exist in DB
    pass


def downgrade() -> None:
    # no-op
    pass
