"""Create users table

Revision ID: 1234567890ab
Revises:
Create Date: 2023-12-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Create unique constraint
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # Create index
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Add column to existing table (example)
    # op.add_column('users', sa.Column('phone', sa.String(), nullable=True))

    # Add foreign key (example)
    # op.create_foreign_key(
    #     'fk_posts_user_id',
    #     'posts', 'users',
    #     ['user_id'], ['id'],
    #     ondelete='CASCADE'
    # )


def downgrade() -> None:
    # Drop in reverse order
    # op.drop_constraint('fk_posts_user_id', 'posts', type_='foreignkey')
    # op.drop_column('users', 'phone')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_table('users')
