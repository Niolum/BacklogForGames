"""add email confirmations table

Revision ID: 771594397690
Revises: bbdaef3f7431
Create Date: 2026-09-27 11:18:58.222562+00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '771594397690'
down_revision: str | Sequence[str] | None = 'bbdaef3f7431'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE SEQUENCE backlog_app.email_confirmations_id_seq'))
    op.create_table(
        'email_confirmations',
        sa.Column(
            'id',
            sa.Integer(),
            server_default=sa.text("nextval('backlog_app.email_confirmations_id_seq'::regclass)"),
            nullable=False,
        ),
        sa.Column('user_id', sa.Integer(), nullable=False, comment='User'),
        sa.Column('token', sa.Text(), nullable=False, comment='Confirmation token'),
        sa.Column(
            'expires_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='Token expiration time',
        ),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True, comment='Token use time'),
        sa.ForeignKeyConstraint(['user_id'], ['backlog_app.users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='backlog_app',
    )
    op.execute(
        sa.text(
            'ALTER SEQUENCE backlog_app.email_confirmations_id_seq OWNED BY backlog_app.email_confirmations.id',
        ),
    )
    op.create_index(
        op.f('ix_backlog_app_email_confirmations_token'),
        'email_confirmations',
        ['token'],
        unique=True,
        schema='backlog_app',
    )
    op.create_index(
        op.f('ix_backlog_app_email_confirmations_user_id'),
        'email_confirmations',
        ['user_id'],
        unique=False,
        schema='backlog_app',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_backlog_app_email_confirmations_user_id'),
        table_name='email_confirmations',
        schema='backlog_app',
    )
    op.drop_index(
        op.f('ix_backlog_app_email_confirmations_token'),
        table_name='email_confirmations',
        schema='backlog_app',
    )
    op.drop_table('email_confirmations', schema='backlog_app')
