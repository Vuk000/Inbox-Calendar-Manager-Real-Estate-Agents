"""Timeline performance index

Revision ID: 003_timeline_performance
Revises: 002_project_apex
Create Date: 2025-10-22

Add composite index for communication_logs to optimize timeline queries
Target: <500ms response time for timeline endpoint
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003_timeline_performance'
down_revision = '002_project_apex'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance index for timeline queries"""
    
    # Composite index for cursor-based pagination on timeline
    # Optimizes: SELECT * FROM communication_logs WHERE contact_id = X 
    #           ORDER BY occurred_at DESC, id DESC LIMIT 20
    op.create_index(
        'idx_comm_contact_occurred_id',
        'communication_logs',
        ['contact_id', 'occurred_at', 'id'],
        postgresql_ops={'occurred_at': 'DESC', 'id': 'DESC'}
    )
    
    # Index for external_id lookups (idempotency checks)
    op.create_index(
        'idx_comm_external_user',
        'communication_logs',
        ['external_id', 'user_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes"""
    
    op.drop_index('idx_comm_external_user', table_name='communication_logs')
    op.drop_index('idx_comm_contact_occurred_id', table_name='communication_logs')

