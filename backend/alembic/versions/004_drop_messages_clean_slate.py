"""drop messages table clean slate

Revision ID: 004_drop_messages_clean_slate
Revises: 003_timeline_performance_index
Create Date: 2025-10-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_drop_messages_clean_slate'
down_revision = '003_timeline_performance'
branch_labels = None
depends_on = None


def upgrade():
    """
    Drop the deprecated messages table and clean up communication_logs.
    This establishes Contact + CommunicationLog as the single source of truth.
    """
    # Drop foreign key constraint from communication_logs.message_id
    op.drop_constraint('communication_logs_message_id_fkey', 'communication_logs', type_='foreignkey')
    
    # Drop the message_id column from communication_logs (deprecated field)
    op.drop_column('communication_logs', 'message_id')
    
    # Update tasks table: replace message_id with communication_log_id
    op.drop_constraint('tasks_message_id_fkey', 'tasks', type_='foreignkey')
    op.alter_column('tasks', 'message_id', new_column_name='communication_log_id')
    op.create_foreign_key('tasks_communication_log_id_fkey', 'tasks', 'communication_logs', ['communication_log_id'], ['id'])
    
    # Drop the messages table entirely
    op.drop_table('messages')
    
    # Ensure optimal indexes exist on communication_logs for timeline queries
    # These should already exist from migration 002, but verify/create if missing
    try:
        op.create_index('idx_comm_contact_date', 'communication_logs', ['contact_id', 'occurred_at'], unique=False)
    except:
        pass  # Index already exists
    
    try:
        op.create_index('idx_comm_user_date', 'communication_logs', ['user_id', 'occurred_at'], unique=False)
    except:
        pass  # Index already exists


def downgrade():
    """
    Recreate messages table structure (for emergency rollback only).
    Note: Data will NOT be restored - this is a clean slate migration.
    """
    # Recreate messages table structure
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_account_id', sa.Integer(), nullable=True),
        sa.Column('social_account_id', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('thread_id', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('sender_email', sa.String(length=255), nullable=True),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('recipient_emails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('cc_emails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bcc_emails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('encrypted_body', sa.Text(), nullable=False),
        sa.Column('body_preview', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('is_starred', sa.Boolean(), nullable=True),
        sa.Column('is_draft', sa.Boolean(), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.Column('attachment_count', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('urgency_score', sa.Float(), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('entities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('suggested_actions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate indexes
    op.create_index('ix_messages_external_id', 'messages', ['external_id'], unique=False)
    op.create_index('ix_messages_sender_email', 'messages', ['sender_email'], unique=False)
    
    # Add message_id column back to communication_logs
    op.add_column('communication_logs', sa.Column('message_id', sa.Integer(), nullable=True))
    
    # Recreate foreign key
    op.create_foreign_key('communication_logs_message_id_fkey', 'communication_logs', 'messages', ['message_id'], ['id'])
    
    # Revert tasks table: replace communication_log_id with message_id
    op.drop_constraint('tasks_communication_log_id_fkey', 'tasks', type_='foreignkey')
    op.alter_column('tasks', 'communication_log_id', new_column_name='message_id')
    op.create_foreign_key('tasks_message_id_fkey', 'tasks', 'messages', ['message_id'], ['id'])

