"""Recover exact enrollment submissions after a lost HTTP response."""
from alembic import op
import sqlalchemy as sa
revision = '7a2d13ce4f90'
down_revision = '5c9d2a1e8b70'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('challenges', sa.Column('enrollment_request_hash', sa.String(64), nullable=True))

def downgrade():
    op.drop_column('challenges', 'enrollment_request_hash')
