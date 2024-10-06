"""Add event_status table

Revision ID: ab07af433014
Revises: xxxxxxxxxxxx
Create Date: 2024-10-06 19:21:46.319288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab07af433014'
down_revision: Union[str, None] = 'xxxxxxxxxxxx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'event_status',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('event_id', sa.String, unique=True, nullable=False),
        sa.Column('event_data', sa.JSON, nullable=False),
        sa.Column('status', sa.String, nullable=False, server_default='new'),
        sa.Column('attempts', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_error', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    )

    # Создание индексов
    op.create_index('ix_event_status_status', 'event_status', ['status'], unique=False)
    op.create_index('ix_event_status_attempts', 'event_status', ['attempts'], unique=False)


def downgrade() -> None:
    # Удаление индексов
    op.drop_index('ix_event_status_attempts', table_name='event_status')
    op.drop_index('ix_event_status_status', table_name='event_status')
    # Удаление таблицы
    op.drop_table('event_status')
