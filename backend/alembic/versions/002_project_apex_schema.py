"""Project Apex CRM Schema Migration

Revision ID: 002_project_apex
Revises: 001_initial_schema
Create Date: 2025-10-17

This migration adds the complete CRM schema for Project Apex:
- Teams and team members
- Contacts with relationship scoring
- Communication logs
- Transactions with pipeline management
- Notes
- AI Actions for human-in-the-loop
- Landing pages for lead generation
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_project_apex'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply schema changes"""
    
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('owner_id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_owner_id'), 'teams', ['owner_id'], unique=True)
    
    # Create team_members table
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)
    op.create_index(op.f('ix_team_members_team_id'), 'team_members', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_members_user_id'), 'team_members', ['user_id'], unique=False)
    
    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('secondary_phone', sa.String(length=50), nullable=True),
        sa.Column('address_line1', sa.String(length=500), nullable=True),
        sa.Column('address_line2', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('contact_type', sa.String(length=50), nullable=True),
        sa.Column('contact_status', sa.String(length=50), nullable=True),
        sa.Column('lead_source', sa.String(length=100), nullable=True),
        sa.Column('relationship_score', sa.Float(), nullable=True),
        sa.Column('last_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contact_frequency', sa.Integer(), nullable=True),
        sa.Column('ai_insights', sa.JSON(), nullable=True),
        sa.Column('preferred_contact_method', sa.String(length=50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('facebook_url', sa.String(length=500), nullable=True),
        sa.Column('twitter_handle', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_shared_with_team', sa.Boolean(), nullable=True),
        sa.Column('shared_by', sa.Integer(), nullable=True),
        sa.Column('shared_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['shared_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_contact_status'), 'contacts', ['contact_status'], unique=False)
    op.create_index(op.f('ix_contacts_contact_type'), 'contacts', ['contact_type'], unique=False)
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=False)
    op.create_index(op.f('ix_contacts_first_name'), 'contacts', ['first_name'], unique=False)
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_last_name'), 'contacts', ['last_name'], unique=False)
    op.create_index(op.f('ix_contacts_phone'), 'contacts', ['phone'], unique=False)
    op.create_index(op.f('ix_contacts_team_id'), 'contacts', ['team_id'], unique=False)
    op.create_index(op.f('ix_contacts_user_id'), 'contacts', ['user_id'], unique=False)
    op.create_index('idx_contact_name', 'contacts', ['first_name', 'last_name'], unique=False)
    op.create_index('idx_contact_type', 'contacts', ['contact_type'], unique=False)
    op.create_index('idx_contact_user_status', 'contacts', ['user_id', 'contact_status'], unique=False)
    
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('transaction_type', sa.Enum('BUYER', 'SELLER', 'BOTH', 'LEASE', 'REFERRAL', name='transactiontype'), nullable=False),
        sa.Column('stage', sa.Enum('LEAD', 'ACTIVE', 'PENDING', 'UNDER_CONTRACT', 'CLOSED_WON', 'CLOSED_LOST', 'ARCHIVED', name='transactionstage'), nullable=False),
        sa.Column('pipeline_position', sa.Integer(), nullable=True),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=True),
        sa.Column('estimated_value', sa.Float(), nullable=True),
        sa.Column('commission_percentage', sa.Float(), nullable=True),
        sa.Column('estimated_commission', sa.Float(), nullable=True),
        sa.Column('actual_sale_price', sa.Float(), nullable=True),
        sa.Column('actual_commission', sa.Float(), nullable=True),
        sa.Column('checklist_template', sa.String(length=50), nullable=True),
        sa.Column('checklist_items', sa.JSON(), nullable=True),
        sa.Column('timeline_events', sa.JSON(), nullable=True),
        sa.Column('lead_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('contract_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('inspection_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('appraisal_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closing_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('probability', sa.Float(), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=True),
        sa.Column('public_timeline_uuid', sa.String(length=36), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('outcome_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('public_timeline_uuid')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_public_timeline_uuid'), 'transactions', ['public_timeline_uuid'], unique=True)
    op.create_index(op.f('ix_transactions_team_id'), 'transactions', ['team_id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index('idx_transaction_contact', 'transactions', ['contact_id'], unique=False)
    op.create_index('idx_transaction_stage', 'transactions', ['stage'], unique=False)
    op.create_index('idx_transaction_user_stage', 'transactions', ['user_id', 'stage'], unique=False)
    
    # Create communication_logs table
    op.create_table('communication_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('communication_type', sa.Enum('EMAIL', 'SMS', 'WHATSAPP', 'PHONE_CALL', 'MEETING', 'NOTE', 'TWITTER_DM', 'FACEBOOK_MESSENGER', name='communicationtype'), nullable=False),
        sa.Column('direction', sa.Enum('INBOUND', 'OUTBOUND', 'INTERNAL', name='communicationdirection'), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('from_address', sa.String(length=255), nullable=True),
        sa.Column('to_address', sa.String(length=255), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('urgency_score', sa.Float(), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=True),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('property_id', sa.Integer(), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('has_attachments', sa.Boolean(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communication_logs_communication_type'), 'communication_logs', ['communication_type'], unique=False)
    op.create_index(op.f('ix_communication_logs_contact_id'), 'communication_logs', ['contact_id'], unique=False)
    op.create_index(op.f('ix_communication_logs_id'), 'communication_logs', ['id'], unique=False)
    op.create_index(op.f('ix_communication_logs_message_id'), 'communication_logs', ['message_id'], unique=False)
    op.create_index(op.f('ix_communication_logs_occurred_at'), 'communication_logs', ['occurred_at'], unique=False)
    op.create_index(op.f('ix_communication_logs_property_id'), 'communication_logs', ['property_id'], unique=False)
    op.create_index(op.f('ix_communication_logs_transaction_id'), 'communication_logs', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_communication_logs_user_id'), 'communication_logs', ['user_id'], unique=False)
    op.create_index('idx_comm_contact_date', 'communication_logs', ['contact_id', 'occurred_at'], unique=False)
    op.create_index('idx_comm_type_direction', 'communication_logs', ['communication_type', 'direction'], unique=False)
    op.create_index('idx_comm_user_date', 'communication_logs', ['user_id', 'occurred_at'], unique=False)
    
    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('property_id', sa.Integer(), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_pinned', sa.Boolean(), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_contact_id'), 'notes', ['contact_id'], unique=False)
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=False)
    op.create_index(op.f('ix_notes_property_id'), 'notes', ['property_id'], unique=False)
    op.create_index(op.f('ix_notes_transaction_id'), 'notes', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_notes_user_id'), 'notes', ['user_id'], unique=False)
    
    # Create ai_actions table
    op.create_table('ai_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.Enum('MERGE_CONTACTS', 'UPDATE_CONTACT', 'CREATE_TRANSACTION', 'UPDATE_TRANSACTION', 'LINK_CONTACT_PROPERTY', 'SUGGEST_FOLLOW_UP', name='aiactiontype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'REJECTED', 'EXPIRED', 'EXECUTED', name='aiactionstatus'), nullable=False),
        sa.Column('proposed_data', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_actions_action_type'), 'ai_actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_ai_actions_id'), 'ai_actions', ['id'], unique=False)
    op.create_index(op.f('ix_ai_actions_status'), 'ai_actions', ['status'], unique=False)
    op.create_index(op.f('ix_ai_actions_user_id'), 'ai_actions', ['user_id'], unique=False)
    
    # Create landing_pages table
    op.create_table('landing_pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('template', sa.String(length=100), nullable=True),
        sa.Column('seo_title', sa.String(length=255), nullable=True),
        sa.Column('seo_description', sa.Text(), nullable=True),
        sa.Column('seo_keywords', sa.JSON(), nullable=True),
        sa.Column('hero_image', sa.String(length=500), nullable=True),
        sa.Column('hero_title', sa.String(length=500), nullable=True),
        sa.Column('hero_subtitle', sa.Text(), nullable=True),
        sa.Column('cta_text', sa.String(length=100), nullable=True),
        sa.Column('cta_button_color', sa.String(length=50), nullable=True),
        sa.Column('form_fields', sa.JSON(), nullable=True),
        sa.Column('sections', sa.JSON(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('leads_count', sa.Integer(), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('analytics', sa.JSON(), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('custom_js', sa.Text(), nullable=True),
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('thank_you_message', sa.Text(), nullable=True),
        sa.Column('redirect_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_landing_pages_id'), 'landing_pages', ['id'], unique=False)
    op.create_index(op.f('ix_landing_pages_user_id'), 'landing_pages', ['user_id'], unique=False)
    op.create_index('idx_landing_page_published', 'landing_pages', ['is_published'], unique=False)
    op.create_index('idx_landing_page_slug', 'landing_pages', ['slug'], unique=False)
    
    # Add new foreign keys to existing tables
    op.add_column('tasks', sa.Column('transaction_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('contact_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_tasks_contact_id'), 'tasks', ['contact_id'], unique=False)
    op.create_index(op.f('ix_tasks_transaction_id'), 'tasks', ['transaction_id'], unique=False)
    op.create_foreign_key('fk_tasks_transaction', 'tasks', 'transactions', ['transaction_id'], ['id'])
    op.create_foreign_key('fk_tasks_contact', 'tasks', 'contacts', ['contact_id'], ['id'])
    
    # Drop legacy tables - migration to CRM schema complete
    # Note: Messages and Drafts tables are kept for backward compatibility
    # The models still exist but are considered deprecated
    # Communication data should now use CommunicationLog table


def downgrade() -> None:
    """Revert schema changes"""
    
    # Drop foreign keys from tasks
    op.drop_constraint('fk_tasks_contact', 'tasks', type_='foreignkey')
    op.drop_constraint('fk_tasks_transaction', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_transaction_id'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_contact_id'), table_name='tasks')
    op.drop_column('tasks', 'contact_id')
    op.drop_column('tasks', 'transaction_id')
    
    # Drop new tables in reverse order
    op.drop_index('idx_landing_page_slug', table_name='landing_pages')
    op.drop_index('idx_landing_page_published', table_name='landing_pages')
    op.drop_index(op.f('ix_landing_pages_user_id'), table_name='landing_pages')
    op.drop_index(op.f('ix_landing_pages_id'), table_name='landing_pages')
    op.drop_table('landing_pages')
    
    op.drop_index(op.f('ix_ai_actions_user_id'), table_name='ai_actions')
    op.drop_index(op.f('ix_ai_actions_status'), table_name='ai_actions')
    op.drop_index(op.f('ix_ai_actions_id'), table_name='ai_actions')
    op.drop_index(op.f('ix_ai_actions_action_type'), table_name='ai_actions')
    op.drop_table('ai_actions')
    
    op.drop_index(op.f('ix_notes_user_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_transaction_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_property_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_index(op.f('ix_notes_contact_id'), table_name='notes')
    op.drop_table('notes')
    
    op.drop_index('idx_comm_user_date', table_name='communication_logs')
    op.drop_index('idx_comm_type_direction', table_name='communication_logs')
    op.drop_index('idx_comm_contact_date', table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_user_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_transaction_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_property_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_occurred_at'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_message_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_contact_id'), table_name='communication_logs')
    op.drop_index(op.f('ix_communication_logs_communication_type'), table_name='communication_logs')
    op.drop_table('communication_logs')
    
    op.drop_index('idx_transaction_user_stage', table_name='transactions')
    op.drop_index('idx_transaction_stage', table_name='transactions')
    op.drop_index('idx_transaction_contact', table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_team_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_public_timeline_uuid'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    
    op.drop_index('idx_contact_user_status', table_name='contacts')
    op.drop_index('idx_contact_type', table_name='contacts')
    op.drop_index('idx_contact_name', table_name='contacts')
    op.drop_index(op.f('ix_contacts_user_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_team_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_phone'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_last_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_first_name'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_contact_type'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_contact_status'), table_name='contacts')
    op.drop_table('contacts')
    
    op.drop_index(op.f('ix_team_members_user_id'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_team_id'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')
    
    op.drop_index(op.f('ix_teams_owner_id'), table_name='teams')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')

