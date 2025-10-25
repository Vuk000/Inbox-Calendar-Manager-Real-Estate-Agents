# Database Migration Guide

This guide explains how to manage database migrations for RealInbox AI using Alembic.

---

## Current Migration Status

✅ **All migrations applied** (as of October 25, 2025)

Current version: `004_drop_messages_clean_slate`

Migration history:
1. `001_initial` - Initial schema with performance indexes
2. `002_project_apex` - CRM schema (Teams, Contacts, Communications, Transactions)
3. `003_timeline_performance_index` - Timeline query optimization
4. `004_drop_messages_clean_slate` - Remove deprecated Message model

---

## Quick Reference

### Check Current Version

```bash
cd backend
alembic current
```

### View Migration History

```bash
alembic history
```

### Apply All Pending Migrations

```bash
alembic upgrade head
```

### Rollback One Migration

```bash
alembic downgrade -1
```

### Rollback to Specific Version

```bash
alembic downgrade 002_project_apex
```

---

## Understanding Our Migrations

### Migration 001: Initial Schema

**Purpose**: Set up performance indexes for the original schema  
**Tables Affected**: messages, tasks, drafts, users, audit_logs  
**Note**: Some indexes reference `messages` table which is now deprecated

### Migration 002: Project Apex CRM

**Purpose**: Add complete CRM functionality  
**Created Tables**:
- `teams` - Team/brokerage management
- `team_members` - Team membership
- `contacts` - Unified contact records
- `communication_logs` - All communications (replaces messages)
- `transactions` - Deal pipeline
- `notes` - Contact notes
- `ai_actions` - Human-in-the-loop AI
- `landing_pages` - Lead generation

**Key Features**:
- Relationship scoring
- Communication frequency tracking
- AI insights on contacts
- Transaction pipeline with stages

### Migration 003: Timeline Performance

**Purpose**: Optimize contact timeline queries (target <500ms)  
**Indexes Created**:
- `idx_comm_contact_occurred_id` - For cursor-based pagination
- `idx_comm_external_user` - For idempotency checks

**Performance Impact**: ~80% faster timeline queries

### Migration 004: Clean Slate

**Purpose**: Remove deprecated Message model, establish Contact + CommunicationLog as single source of truth  
**Changes**:
- Drops `messages` table entirely
- Removes `message_id` from `communication_logs`
- Updates `tasks` to use `communication_log_id`

**⚠️ WARNING**: This is a **destructive migration**. Any data in the `messages` table will be lost. Ensure you've migrated all message data to `communication_logs` before running.

---

## Creating New Migrations

### Auto-generate from Model Changes

1. Make changes to SQLAlchemy models in `app/models/`

2. Generate migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

3. Review generated file in `alembic/versions/`

4. Edit if needed (autogenerate isn't perfect)

5. Test migration:
```bash
# Apply
alembic upgrade head

# Test rollback
alembic downgrade -1

# Reapply
alembic upgrade head
```

### Manual Migration

For complex changes:

```bash
alembic revision -m "Description of changes"
```

Edit the generated file manually.

---

## Migration Best Practices

### 1. Always Review Auto-generated Migrations

Alembic's autogenerate is helpful but not perfect. Check:
- Foreign key constraints are correct
- Indexes are appropriate
- No unintended changes

### 2. Make Migrations Reversible

Always implement `downgrade()` function. This allows rollbacks.

### 3. Test Migrations on Development Data

```bash
# Backup database first
cp inbox_manager_dev.db inbox_manager_dev.db.backup

# Test migration
alembic upgrade head

# Test rollback
alembic downgrade -1

# Verify data integrity
```

### 4. Use Descriptive Names

Good: `003_add_contact_tags_array`  
Bad: `003_update_contacts`

### 5. One Logical Change Per Migration

Don't mix unrelated schema changes in one migration.

---

## Common Migration Issues

### Issue: "Target database is not up to date"

**Cause**: Database has been manually modified  
**Fix**:
```bash
# Stamp database with current version
alembic stamp head
```

### Issue: "Can't locate revision identifier"

**Cause**: Migration file missing or revision ID mismatch  
**Fix**: Check `alembic/versions/` for all migration files. Verify `down_revision` chain is correct.

### Issue: "Table already exists"

**Cause**: Running migration on existing database  
**Fix**: Either:
- Drop tables and start fresh (DEV ONLY)
- Manually stamp to skip that migration
- Use `IF NOT EXISTS` in migration

### Issue: Migration Fails Midway

**Cause**: Data incompatibility or constraint violation  
**Fix**:
```bash
# Rollback
alembic downgrade -1

# Fix data issues
# Re-run migration
alembic upgrade +1
```

---

## Environment-Specific Migrations

### Development (SQLite)

```bash
# .env
DATABASE_URL=sqlite:///./inbox_manager_dev.db
```

### Production (PostgreSQL)

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/realinbox_prod
```

**Note**: Some features differ between SQLite and PostgreSQL:
- SQLite doesn't support `ALTER COLUMN` directly
- PostgreSQL has better index types
- Always test migrations on the target database type

---

## Migration Checklist

Before deploying migrations to production:

- [ ] Tested on development database
- [ ] Tested upgrade path
- [ ] Tested downgrade path
- [ ] Reviewed for data loss risks
- [ ] Backup plan in place
- [ ] Downtime window estimated
- [ ] Team notified

---

## Emergency Rollback

If a migration causes issues in production:

```bash
# 1. Immediately rollback
alembic downgrade -1

# 2. Verify application works
# 3. Investigate issue
# 4. Fix migration
# 5. Test thoroughly
# 6. Redeploy
```

---

## Database Backup Strategy

### Before Migrations

```bash
# SQLite
cp inbox_manager_dev.db backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL
pg_dump realinbox_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore from Backup

```bash
# SQLite
cp backup_20251025_120000.db inbox_manager_dev.db

# PostgreSQL
psql realinbox_db < backup_20251025_120000.sql
```

---

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Migration Guide](https://docs.sqlalchemy.org/en/14/core/metadata.html)
- Project issue tracker for migration-related bugs

---

**Last Updated**: October 25, 2025

