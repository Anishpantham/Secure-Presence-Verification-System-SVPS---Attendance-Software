"""Cross-platform device keys, one-use security challenges and iOS presence policy."""
from alembic import op
import sqlalchemy as sa
revision = '5c9d2a1e8b70'
down_revision = '3e61f3d2ac45'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('policies', sa.Column('ios_presence', sa.String(24), nullable=False, server_default='review'))
    op.add_column('devices', sa.Column('key_algorithm', sa.String(24), nullable=False, server_default='hmac-sha256'))
    op.add_column('devices', sa.Column('public_key', sa.Text(), nullable=True))
    op.add_column('devices', sa.Column('key_storage', sa.String(40), nullable=False, server_default='legacy-shared-secret'))
    op.create_table('security_challenges',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.user_id'), nullable=False),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id')),
        sa.Column('purpose', sa.String(24), nullable=False),
        sa.Column('nonce', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False))
    op.create_index('ix_security_challenges_student_id', 'security_challenges', ['student_id'])
    op.create_table('app_attest_keys',
        sa.Column('key_id', sa.String(100), primary_key=True),
        sa.Column('device_id', sa.String(36), sa.ForeignKey('devices.id'), nullable=False, unique=True),
        sa.Column('public_key', sa.LargeBinary(), nullable=False),
        sa.Column('counter', sa.BigInteger(), nullable=False),
        sa.Column('environment', sa.String(16), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))

def downgrade():
    op.drop_table('app_attest_keys')
    op.drop_index('ix_security_challenges_student_id', table_name='security_challenges')
    op.drop_table('security_challenges')
    for name in ['key_storage', 'public_key', 'key_algorithm']:
        op.drop_column('devices', name)
    op.drop_column('policies', 'ios_presence')
