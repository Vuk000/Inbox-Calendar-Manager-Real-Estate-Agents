"""add vision neighborhood models

Revision ID: 005_add_vision_neighborhood_models
Revises: 004_drop_messages_clean_slate
Create Date: 2025-11-02 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_vision_neighborhood_models'
down_revision = '004_drop_messages_clean_slate'
branch_labels = None
depends_on = None


def upgrade():
    """Create VisionScan, NeighborhoodReport, and ApprovalQueue tables"""
    
    # Create vision_scans table
    op.create_table(
        'vision_scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('image_filename', sa.String(length=255), nullable=True),
        sa.Column('matches', sa.JSON(), nullable=True),
        sa.Column('renovations', sa.JSON(), nullable=True),
        sa.Column('vision_labels', sa.JSON(), nullable=True),
        sa.Column('rooms_detected', sa.JSON(), nullable=True),
        sa.Column('property_address', sa.String(length=255), nullable=True),
        sa.Column('property_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('processing_error', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vision_scans_id'), 'vision_scans', ['id'], unique=False)
    op.create_index(op.f('ix_vision_scans_user_id'), 'vision_scans', ['user_id'], unique=False)
    op.create_index(op.f('ix_vision_scans_created_at'), 'vision_scans', ['created_at'], unique=False)
    
    # Create neighborhood_reports table
    op.create_table(
        'neighborhood_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.String(length=500), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=False),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('fit_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('amenities_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('sentiment_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('eco_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('forecast', sa.JSON(), nullable=True),
        sa.Column('eco_roi', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('review_insights', sa.JSON(), nullable=True),
        sa.Column('similar_neighborhoods', sa.JSON(), nullable=True),
        sa.Column('market_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('processing_error', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_neighborhood_reports_id'), 'neighborhood_reports', ['id'], unique=False)
    op.create_index(op.f('ix_neighborhood_reports_user_id'), 'neighborhood_reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_neighborhood_reports_zip_code'), 'neighborhood_reports', ['zip_code'], unique=False)
    op.create_index(op.f('ix_neighborhood_reports_created_at'), 'neighborhood_reports', ['created_at'], unique=False)
    
    # Create approval_queue table
    op.create_table(
        'approval_queue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('feature_type', sa.Enum('vision_scan', 'neighborhood_report', 'ai_draft', 'lead_qualification', name='approvalfeaturetype'), nullable=False),
        sa.Column('feature_id', sa.Integer(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'expired', name='approvalstatus'), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approval_queue_id'), 'approval_queue', ['id'], unique=False)
    op.create_index(op.f('ix_approval_queue_user_id'), 'approval_queue', ['user_id'], unique=False)
    op.create_index(op.f('ix_approval_queue_feature_type'), 'approval_queue', ['feature_type'], unique=False)
    op.create_index(op.f('ix_approval_queue_status'), 'approval_queue', ['status'], unique=False)
    op.create_index(op.f('ix_approval_queue_expires_at'), 'approval_queue', ['expires_at'], unique=False)
    op.create_index(op.f('ix_approval_queue_created_at'), 'approval_queue', ['created_at'], unique=False)


def downgrade():
    """Drop VisionScan, NeighborhoodReport, and ApprovalQueue tables"""
    op.drop_index(op.f('ix_approval_queue_created_at'), table_name='approval_queue')
    op.drop_index(op.f('ix_approval_queue_expires_at'), table_name='approval_queue')
    op.drop_index(op.f('ix_approval_queue_status'), table_name='approval_queue')
    op.drop_index(op.f('ix_approval_queue_feature_type'), table_name='approval_queue')
    op.drop_index(op.f('ix_approval_queue_user_id'), table_name='approval_queue')
    op.drop_index(op.f('ix_approval_queue_id'), table_name='approval_queue')
    op.drop_table('approval_queue')
    
    op.drop_index(op.f('ix_neighborhood_reports_created_at'), table_name='neighborhood_reports')
    op.drop_index(op.f('ix_neighborhood_reports_zip_code'), table_name='neighborhood_reports')
    op.drop_index(op.f('ix_neighborhood_reports_user_id'), table_name='neighborhood_reports')
    op.drop_index(op.f('ix_neighborhood_reports_id'), table_name='neighborhood_reports')
    op.drop_table('neighborhood_reports')
    
    op.drop_index(op.f('ix_vision_scans_created_at'), table_name='vision_scans')
    op.drop_index(op.f('ix_vision_scans_user_id'), table_name='vision_scans')
    op.drop_index(op.f('ix_vision_scans_id'), table_name='vision_scans')
    op.drop_table('vision_scans')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS approvalfeaturetype')
    op.execute('DROP TYPE IF EXISTS approvalstatus')

