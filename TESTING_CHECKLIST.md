# Phase 1 Testing Checklist

Use this checklist to validate the refactored system is working correctly.

## Pre-Testing Setup

- [ ] PostgreSQL database is running
- [ ] Redis is running (for Celery)
- [ ] Environment variables are configured (see ENV_TEMPLATE.md)
- [ ] All dependencies installed: `cd backend && pip install -r requirements.txt`
- [ ] Frontend dependencies installed: `cd frontend && npm install`

## Database Migration

- [ ] Run migration: `cd backend && alembic upgrade head`
- [ ] Verify no errors in migration output
- [ ] Check that `messages` table is dropped
- [ ] Check that `communication_logs` table exists
- [ ] Verify `tasks.communication_log_id` column exists

### SQL Verification Queries
```sql
-- Should return 0 rows (messages table dropped)
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_name = 'messages';

-- Should return > 0 (communication_logs exists)
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_name = 'communication_logs';

-- Should show communication_log_id column
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'tasks' AND column_name = 'communication_log_id';
```

## Backend Startup

- [ ] Start backend: `cd backend && python -m app.main`
- [ ] No import errors in console
- [ ] FastAPI server starts on http://localhost:8000
- [ ] Check `/docs` endpoint loads (Swagger UI)
- [ ] Check `/health` endpoint returns healthy status

## Email Integration Testing

### Gmail OAuth
- [ ] Navigate to frontend Settings → Integrations
- [ ] Click "Connect Gmail"
- [ ] Complete OAuth flow
- [ ] Email account appears in connected accounts list

### Manual Email Sync
- [ ] Trigger manual sync from UI
- [ ] Backend logs show sync starting
- [ ] Check PostgreSQL for new Contact records
- [ ] Check PostgreSQL for new CommunicationLog records with `communication_type='email'`

### SQL Verification
```sql
-- Check contacts created from emails
SELECT id, first_name, last_name, email, created_at 
FROM contacts 
ORDER BY created_at DESC 
LIMIT 10;

-- Check communication logs
SELECT id, contact_id, communication_type, subject, occurred_at 
FROM communication_logs 
WHERE communication_type = 'email'
ORDER BY occurred_at DESC 
LIMIT 10;

-- Verify linkage
SELECT 
  c.first_name,
  c.last_name,
  c.email,
  COUNT(cl.id) as email_count
FROM contacts c
LEFT JOIN communication_logs cl ON c.id = cl.contact_id
WHERE cl.communication_type = 'email'
GROUP BY c.id, c.first_name, c.last_name, c.email;
```

## Contact Management UI

### Contacts List
- [ ] Navigate to `/contacts` in frontend
- [ ] Contacts list loads without errors
- [ ] Search functionality works
- [ ] Filter by contact type works
- [ ] Filter by status works
- [ ] Relationship score displays correctly

### Contact Detail & Timeline

#### Timeline Display
- [ ] Click on a contact
- [ ] Timeline loads in <500ms
- [ ] Emails appear in chronological order
- [ ] Each timeline item shows:
  - [ ] Subject
  - [ ] Summary/preview
  - [ ] Date and time
  - [ ] Sender/direction indicator
  - [ ] Sentiment emoji (if analyzed)

#### Timeline Interactions
- [ ] Click to expand email details
- [ ] Infinite scroll loads more items
- [ ] "Load more" indicator appears when scrolling
- [ ] No duplicate items in timeline
- [ ] Timeline ends with "End of timeline" message

#### Timeline Performance
- [ ] Initial load <500ms
- [ ] Pagination is smooth
- [ ] No lag when expanding items
- [ ] Browser console shows no errors

## AI Processing

### Triage Agent
- [ ] New emails trigger AI processing (check logs)
- [ ] `urgency_score` is populated in `communication_logs`
- [ ] `sentiment_score` is populated
- [ ] `key_topics` contains extracted entities

### Manual AI Analysis
- [ ] Use `/emails/{id}/analyze` endpoint
- [ ] AI analysis completes successfully
- [ ] Scores are updated in database

## Contact Creation

### Automatic Contact Creation
- [ ] Send test email to connected account
- [ ] Email sync runs (automatic or manual)
- [ ] New contact created for sender
- [ ] Contact has correct email address
- [ ] First/last name parsed from sender name

### Duplicate Prevention
- [ ] Send multiple emails from same address
- [ ] Only one contact created
- [ ] All emails linked to same contact
- [ ] Timeline shows all emails for that contact

## API Endpoint Testing

### GET /contacts
- [ ] Returns list of contacts
- [ ] Pagination works (skip/limit)
- [ ] Search parameter filters correctly
- [ ] Response time acceptable

### GET /contacts/{id}
- [ ] Returns single contact
- [ ] Includes relationship score
- [ ] Shows last contact date
- [ ] Contact frequency calculated

### GET /contacts/{id}/timeline
- [ ] Returns communication logs
- [ ] Cursor-based pagination works
- [ ] `has_more` flag correct
- [ ] `next_cursor` provided when more items exist
- [ ] Response time <500ms

### GET /emails
- [ ] Returns email communications
- [ ] Filters by urgency work
- [ ] Search functionality works
- [ ] Pagination works

## Error Handling

### Edge Cases
- [ ] Email with no sender name (uses "Unknown")
- [ ] Email with no subject (displays correctly)
- [ ] Contact with no communications (empty timeline)
- [ ] Invalid cursor in timeline request (handled gracefully)

### Error Messages
- [ ] API errors return proper HTTP status codes
- [ ] Error messages are user-friendly
- [ ] No sensitive data in error responses
- [ ] Frontend displays errors to user

## Performance Benchmarks

- [ ] Timeline query executes in <500ms (check response_time_ms in API)
- [ ] Contact list loads in <1s for 100+ contacts
- [ ] Email sync processes 100 emails in <30s
- [ ] Database queries use proper indexes (check EXPLAIN ANALYZE)

## Celery Workers

- [ ] Start Celery worker: `celery -A app.workers.celery_app worker --loglevel=info`
- [ ] Email sync tasks execute
- [ ] AI processing tasks execute
- [ ] No task failures in logs
- [ ] Task results stored correctly

## Frontend Integration

### Components Working
- [ ] ContactsPage displays data
- [ ] ContactDetailPage loads
- [ ] Timeline component renders
- [ ] Infinite scroll triggers API calls
- [ ] Loading states show correctly

### Data Flow
- [ ] Frontend → API → Database
- [ ] Real-time updates work (WebSocket if implemented)
- [ ] State management updates correctly
- [ ] No stale data displayed

## Regression Testing

### Ensure Nothing Broke
- [ ] User authentication still works
- [ ] Other integrations not affected
- [ ] Task creation still works
- [ ] Draft system still functions
- [ ] Analytics endpoints still respond

## Final Validation

- [ ] No console errors in browser
- [ ] No Python errors in backend logs
- [ ] Database foreign keys are valid
- [ ] No orphaned records
- [ ] Backup created before migration

## Sign-Off

Once all items are checked:

- [ ] Product Owner approval
- [ ] Technical Lead approval
- [ ] Ready for production deployment

---

## Troubleshooting

### Common Issues

**Timeline not loading:**
- Check browser console for API errors
- Verify contact has communication_logs in database
- Check API endpoint returns data: `/contacts/{id}/timeline`

**Email sync not creating contacts:**
- Check Celery worker is running
- Verify email account is active in database
- Check sync logs for errors
- Ensure `get_or_create_contact_by_email` is being called

**Migration fails:**
- Check if Message model still has dependencies
- Verify database connection
- Check Alembic revision history
- Roll back and try again if needed

**Performance issues:**
- Check database indexes exist on `communication_logs`
- Verify cursor pagination is being used
- Use `EXPLAIN ANALYZE` on slow queries
- Consider adding caching layer

---

## Next Phase

After Phase 1 testing is complete:
- Phase 2: Advanced CRM features (deals, pipelines)
- Phase 3: Enhanced AI capabilities
- Phase 4: Team collaboration features

