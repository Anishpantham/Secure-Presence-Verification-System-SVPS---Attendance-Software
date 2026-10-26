"""Mandatory QR/acoustic policy v2; historical attempts remain unchanged."""
from alembic import op
import sqlalchemy as sa
revision = '9bd32a88f101'
down_revision = '7a2d13ce4f90'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('attendance_sessions', sa.Column('presence_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('attendance_sessions', sa.Column('presence_epoch', sa.Integer(), nullable=False, server_default='0'))
    op.create_table('presence_qr',
        sa.Column('id', sa.String(36), primary_key=True), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('attendance_sessions.id'), nullable=False),
        sa.Column('classroom_id', sa.String(36), sa.ForeignKey('classrooms.id'), nullable=False),
        sa.Column('epoch', sa.Integer(), nullable=False), sa.Column('token', sa.String(300), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_presence_qr_session_id', 'presence_qr', ['session_id'])
    op.create_table('presence_proofs',
        sa.Column('challenge_id', sa.String(36), sa.ForeignKey('challenges.id'), primary_key=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.user_id'), nullable=False),
        sa.Column('qr_id', sa.String(36), sa.ForeignKey('presence_qr.id'), nullable=False),
        sa.Column('qr_verified_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ready_at', sa.DateTime(timezone=True)), sa.Column('audio_hash', sa.String(64)),
        sa.Column('audio_started_at', sa.DateTime(timezone=True)), sa.Column('audio_expires_at', sa.DateTime(timezone=True)),
        sa.Column('audio_verified_at', sa.DateTime(timezone=True)),
        sa.Column('audio_consumed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('audio_request_hash', sa.String(64)), sa.UniqueConstraint('qr_id', 'student_id'))
    op.create_index('ix_presence_proofs_student_id', 'presence_proofs', ['student_id'])
    # Explicit migration: old GPS-only auto policy is retired. Existing stricter review/retry is preserved.
    op.execute("UPDATE policies SET ios_presence = 'dynamic' WHERE ios_presence = 'gps_only'")


def downgrade():
    op.execute("UPDATE policies SET ios_presence = 'review' WHERE ios_presence = 'dynamic'")
    op.drop_table('presence_proofs')
    op.drop_table('presence_qr')
    op.drop_column('attendance_sessions', 'presence_epoch')
    op.drop_column('attendance_sessions', 'presence_enabled')
