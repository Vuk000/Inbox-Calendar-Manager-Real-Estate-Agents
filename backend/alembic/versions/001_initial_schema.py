"""Initial schema with performance indexes

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes"""
    
    # Message table indexes for query optimization
    op.create_index(
        'idx_message_email_account_received',
        'messages',
        ['email_account_id', 'received_at'],
        postgresql_ops={'received_at': 'DESC'}
    )
    op.create_index(
        'idx_message_priority_read',
        'messages',
        ['priority', 'is_read']
    )
    op.create_index(
        'idx_message_category',
        'messages',
        ['category']
    )
    op.create_index(
        'idx_message_processed',
        'messages',
        ['processed_at'],
        postgresql_where=sa.text('processed_at IS NOT NULL')
    )
    
    # Task table indexes
    op.create_index(
        'idx_task_user_status_due',
        'tasks',
        ['user_id', 'status', 'due_date']
    )
    op.create_index(
        'idx_task_created_by',
        'tasks',
        ['created_by']
    )
    op.create_index(
        'idx_task_email_id',
        'tasks',
        ['email_id'],
        postgresql_where=sa.text('email_id IS NOT NULL')
    )
    
    # Draft table indexes
    op.create_index(
        'idx_draft_user_status',
        'drafts',
        ['user_id', 'status']
    )
    op.create_index(
        'idx_draft_email',
        'drafts',
        ['email_id']
    )
    
    # User table indexes
    op.create_index(
        'idx_user_email',
        'users',
        ['email'],
        unique=True
    )
    op.create_index(
        'idx_user_active',
        'users',
        ['is_active']
    )
    
    # Audit log indexes
    op.create_index(
        'idx_audit_user_timestamp',
        'audit_logs',
        ['user_id', 'timestamp'],
        postgresql_ops={'timestamp': 'DESC'}
    )
    op.create_index(
        'idx_audit_action',
        'audit_logs',
        ['action']
    )


def downgrade() -> None:
    """Remove performance indexes"""
    
    # Message indexes
    op.drop_index('idx_message_email_account_received', table_name='messages')
    op.drop_index('idx_message_priority_read', table_name='messages')
    op.drop_index('idx_message_category', table_name='messages')
    op.drop_index('idx_message_processed', table_name='messages')
    
    # Task indexes
    op.drop_index('idx_task_user_status_due', table_name='tasks')
    op.drop_index('idx_task_created_by', table_name='tasks')
    op.drop_index('idx_task_email_id', table_name='tasks')
    
    # Draft indexes
    op.drop_index('idx_draft_user_status', table_name='drafts')
    op.drop_index('idx_draft_email', table_name='drafts')
    
    # User indexes
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_active', table_name='users')
    
    # Audit log indexes
    op.drop_index('idx_audit_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_action', table_name='audit_logs')

