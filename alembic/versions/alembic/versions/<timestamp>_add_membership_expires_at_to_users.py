"""add membership_expires_at to users

Revision ID: add_membership_expires_at
Revises: <previous_revision_id>
Create Date: YYYY-MM-DD HH:MM:SS.ssssss

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_membership_expires_at'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('membership_expires_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('users', 'membership_expires_at')