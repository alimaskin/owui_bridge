"""Initial migration

Revision ID: 03c9aa7a7171
Revises: 
Create Date: 2024-10-07 08:16:44.130736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03c9aa7a7171'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    print("Running upgrade migration df27dccb688e")
    try:
        op.create_table(
            'transfer_state',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('last_created_at', sa.DateTime, nullable=False),
        )
        op.execute(
            "INSERT INTO transfer_state (last_created_at) VALUES ('1970-01-01T00:00:00Z')"
        )
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

def downgrade():
    op.drop_table('transfer_state')
