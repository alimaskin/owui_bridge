# alembic/versions/xxxxxxxxxxxx_create_transfer_state_table.py
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxxxxxxxxxx'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'transfer_state',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('last_created_at', sa.DateTime, nullable=False),
    )
    # Вставка начальной записи
    op.execute(
        "INSERT INTO transfer_state (last_created_at) VALUES ('1970-01-01T00:00:00Z')"
    )

def downgrade():
    op.drop_table('transfer_state')
