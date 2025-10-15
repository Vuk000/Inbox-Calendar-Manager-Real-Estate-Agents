# 🎯 Cursor + Claude Development Guide for RealInbox AI

This guide shows you how to use Cursor IDE with Claude Sonnet 4.5 to continue building RealInbox AI efficiently.

---

## 🚀 Quick Start with Cursor

### 1. Open Project in Cursor

```bash
# Open the project folder in Cursor
cursor .
```

### 2. Set Up Claude API Key

1. Open Cursor Settings (Ctrl/Cmd + ,)
2. Go to "AI" section
3. Add your Anthropic API key
4. Select "Claude Sonnet 4.5" as the model

---

## 💬 Example Prompts for Next Features

### Building Email Sync Workers

**Prompt to Cursor:**
```
Create a new file backend/app/workers/email_sync.py that implements Celery background tasks for email synchronization.

Requirements:
1. Import the GmailIntegration and OutlookIntegration from app/integrations
2. Create a Celery app instance connected to Redis
3. Implement these tasks:
   - sync_gmail_account(user_id, account_id) - fetches new emails from Gmail
   - sync_outlook_account(user_id, account_id) - fetches new emails from Outlook
   - process_email_with_ai(message_id) - runs TriageAgent on a message
4. Each task should:
   - Decrypt OAuth tokens from EmailAccount model
   - Fetch emails using the integration class
   - Store emails in Message model with encryption
   - Call TriageAgent to analyze and update priority/category
   - Handle errors gracefully with retry logic
5. Add periodic tasks to run every 5 minutes for all active accounts

Use the existing models from app.models and agents from app.agents.
Follow the code style in the existing files.
```

### Building Inbox Router

**Prompt to Cursor:**
```
Create backend/app/routers/emails.py with FastAPI endpoints for email management.

Endpoints needed:
1. GET /emails - List emails with pagination and filters
   - Query params: page, limit, priority (high/medium/low), category, search
   - Return: List of messages with AI metadata (priority, category, urgency_score)
   - Sort by urgency_score descending by default
   - Include sender info, subject, preview, received date

2. GET /emails/{message_id} - Get single email with full details
   - Decrypt email body
   - Include all AI analysis results
   - Include related drafts if any

3. POST /emails/search - Semantic search using Pinecone
   - Body: { "query": "find emails about 123 Main St offer" }
   - Use VectorStore.search_similar_emails()
   - Return matching emails with similarity scores

4. POST /emails/{message_id}/analyze - Manually trigger AI triage
   - Call TriageAgent.analyze_email()
   - Update message with new analysis
   - Return updated message

Use dependencies from app.dependencies for authentication.
Follow the pattern in app/routers/auth.py.
Include proper error handling and Pydantic schemas.
```

### Building Inbox UI Component

**Prompt to Cursor:**
```
Create frontend/src/components/EmailInbox.tsx - a comprehensive email inbox interface.

Features:
1. Tabs for filtering: All, Urgent, Leads, Offers, Inspections, Negotiations
2. Search bar for semantic search
3. Email list with cards showing:
   - Priority badge (red for high, yellow for medium, gray for low)
   - Category badge with color coding
   - Sender name and email
   - Subject line
   - Preview text (first 100 chars)
   - Received time (relative: "2 hours ago")
   - Urgency score indicator
4. Click on email to view details in a modal or side panel
5. Loading states with skeleton loaders
6. Empty states with helpful messages
7. Pagination controls at bottom

Use:
- TanStack Query for data fetching
- Tailwind CSS for styling (use existing classes from index.css)
- Heroicons for icons
- The emailService from services/api.ts
- React Router for navigation

Make it responsive and beautiful like a modern email client.
```

### Building Draft Generation UI

**Prompt to Cursor:**
```
Create frontend/src/components/DraftGenerator.tsx - an AI draft generation interface.

Features:
1. Props: messageId (email to reply to)
2. "Generate Draft" button
3. Options to select number of variants (1-3)
4. Show loading state while generating
5. Display generated drafts in tabs (if multiple variants)
6. Each draft shows:
   - The generated text in a textarea (editable)
   - Confidence score
   - Word count
   - "Send", "Edit", "Regenerate" buttons
7. Edit mode: Allow user to modify text
8. Send: Confirm modal, then call API to send
9. Regenerate: Option to provide feedback on what to change

Use:
- draftService from services/api.ts
- React hooks for state management
- Toast notifications for success/error
- Tailwind for styling

Make the UI clean and intuitive for real estate agents.
```

### Building Task Board

**Prompt to Cursor:**
```
Create frontend/src/components/TaskBoard.tsx - a Kanban-style task board.

Requirements:
1. Three columns: "To Do", "In Progress", "Done"
2. Fetch tasks from API using taskService.listTasks()
3. Each task card shows:
   - Task title
   - Task type icon (showing, inspection, deadline, etc.)
   - Property address (if linked)
   - Due date with color coding (red if overdue)
   - Assignee (for team mode)
4. Drag and drop to move tasks between columns
5. Click task to open detail modal with:
   - Full description
   - Related email link
   - Calendar event info
   - Edit/delete buttons
6. "Add Task" button to create new tasks manually
7. Filter by type, property, assignee

Use:
- @dnd-kit/core for drag and drop
- TanStack Query with mutations for updates
- Tailwind for styling
- date-fns for date formatting

Follow the design pattern in DashboardPage.tsx.
```

---

## 🎨 UI Component Prompts

### Creating Reusable Components

**Badge Component:**
```
Create frontend/src/components/Badge.tsx - a reusable badge component.

Props:
- variant: "primary" | "success" | "warning" | "danger" | "gray"
- size: "sm" | "md" | "lg"
- children: React.ReactNode

Use Tailwind CSS with clsx for conditional classes.
Export as default.
```

**Modal Component:**
```
Create frontend/src/components/Modal.tsx using Headless UI Dialog.

Props:
- isOpen: boolean
- onClose: () => void
- title: string
- children: React.ReactNode
- size: "sm" | "md" | "lg" | "xl"

Features:
- Backdrop with blur
- Slide-in animation
- Close button (X icon)
- Responsive
- Escape key to close
- Click outside to close
```

---

## 🔧 Backend Enhancement Prompts

### Adding Pagination

**Prompt:**
```
Add pagination helper utility to backend/app/utils/pagination.py.

Create a function paginate(query, page, per_page) that:
1. Takes a SQLAlchemy query object
2. Applies limit and offset
3. Returns { items, total, page, per_page, pages }
4. Handles edge cases (page < 1, per_page > 100)

Use it in the emails router.
```

### Adding Webhooks

**Prompt:**
```
Create backend/app/routers/webhooks.py for receiving external webhooks.

Endpoints:
1. POST /webhooks/gmail - Gmail push notifications
2. POST /webhooks/outlook - Outlook subscription notifications
3. POST /webhooks/twilio - Twilio incoming SMS/WhatsApp

Each should:
- Verify webhook signature
- Parse payload
- Queue background job for processing
- Return 200 OK immediately
- Log to audit trail

Add security verification for each provider.
```

### Adding Email Sending

**Prompt:**
```
Add an endpoint POST /emails/{message_id}/reply in the emails router.

Body: { "content": "reply text", "draft_id": optional }

Logic:
1. Get original message
2. Get email account with decrypted tokens
3. Use GmailIntegration or OutlookIntegration to send reply
4. Set In-Reply-To and References headers for threading
5. Save sent email to database
6. If draft_id provided, mark draft as sent
7. Log to audit trail

Return the sent message data.
```

---

## 🧪 Testing Prompts

### Unit Tests

**Prompt:**
```
Create backend/tests/test_triage_agent.py with comprehensive unit tests.

Test cases:
1. test_analyze_email_offer - Test with offer email
2. test_analyze_email_lead - Test with lead inquiry
3. test_analyze_email_inspection - Test with inspection report
4. test_analyze_email_newsletter - Test with low priority
5. test_fallback_when_api_fails - Mock API error, check fallback
6. test_entity_extraction - Verify addresses, amounts extracted
7. test_priority_scoring - Check urgency score calculation

Use pytest fixtures for mock email data.
Mock the Anthropic API calls.
Assert on returned JSON structure.
```

**Prompt:**
```
Create frontend/src/components/__tests__/EmailInbox.test.tsx.

Test cases:
1. Renders loading state initially
2. Renders email list when data loaded
3. Filters work correctly (click Urgent tab)
4. Search triggers API call
5. Click email opens detail view
6. Empty state shows when no emails
7. Pagination controls work

Use React Testing Library and Mock Service Worker.
```

---

## 📊 Analytics Prompts

**Prompt:**
```
Create backend/app/services/analytics_service.py for calculating metrics.

Functions:
1. calculate_time_saved(user_id, start_date, end_date)
   - Count emails processed
   - Multiply by 0.1 hours per email
   - Return total hours

2. get_lead_conversion_funnel(user_id)
   - Count leads by stage: cold, warm, hot, closed
   - Calculate conversion rates
   - Return funnel data

3. get_email_patterns(user_id, days=30)
   - Group emails by hour of day
   - Count by category
   - Find peak times
   - Return chart data

4. generate_weekly_report(user_id)
   - All metrics above
   - Top 5 actions taken
   - Comparison to previous week

Use SQLAlchemy for queries, cache results in Redis.
```

---

## 🔐 Security Enhancement Prompts

**Prompt:**
```
Add rate limiting decorator to backend/app/security/rate_limit.py.

Create:
1. @rate_limit(max_requests=10, window_seconds=60)
2. Uses Redis to track request counts per user/IP
3. Returns 429 Too Many Requests if exceeded
4. Add X-RateLimit headers to response
5. Apply to sensitive endpoints (login, draft generation)

Use Redis with key pattern: "rate_limit:{user_id}:{endpoint}"
```

**Prompt:**
```
Add input validation middleware to FastAPI.

Requirements:
1. Validate email addresses (RFC 5322)
2. Sanitize HTML input
3. Check for SQL injection patterns
4. Validate file uploads (type, size)
5. Rate limit by IP
6. Log suspicious activity to audit trail

Apply globally in main.py.
```

---

## 🎯 Pro Tips for Cursor Development

### 1. Be Specific
❌ Bad: "Make an inbox"
✅ Good: "Create an inbox component with filters, search, and pagination using TanStack Query and Tailwind"

### 2. Reference Existing Code
✅ "Follow the pattern in backend/app/routers/auth.py"
✅ "Use the same styling as DashboardPage.tsx"

### 3. Break Down Large Tasks
Instead of: "Build the entire email management system"
Do:
1. "Create the database models"
2. "Create the API endpoints"
3. "Create the UI components"
4. "Connect them together"

### 4. Iterate
First pass: "Create a basic inbox UI"
Second pass: "Add filters and search to the inbox"
Third pass: "Add animations and loading states"

### 5. Ask for Explanations
"Explain how the TriageAgent works"
"Why did you choose this approach?"
"What are the alternatives?"

---

## 🚀 Suggested Development Order

### Week 1: Email Core
1. Email sync workers
2. Email routers (CRUD)
3. Inbox UI component
4. Email detail view

### Week 2: AI Features
5. Draft generation router
6. Draft UI component
7. Lead qualification display
8. Negotiation insights UI

### Week 3: Automation
9. Task creation from emails
10. Calendar integration
11. Task board UI
12. Reminder system

### Week 4: Polish
13. Analytics calculations
14. Charts and graphs
15. Settings page
16. Comprehensive testing

---

## 📝 Template Prompts

### New Feature Template
```
Create [file path] for [feature name].

Requirements:
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

Technical details:
- Use [library/pattern]
- Follow style in [existing file]
- Include [specific functionality]

Make it production-ready with error handling and tests.
```

### Bug Fix Template
```
Fix [bug description] in [file path].

Current behavior: [what's happening]
Expected behavior: [what should happen]
Steps to reproduce:
1. [Step 1]
2. [Step 2]

Look at [related files] for context.
```

### Refactoring Template
```
Refactor [file/function] to [improvement].

Current issues:
- [Issue 1]
- [Issue 2]

Goals:
- [Goal 1]
- [Goal 2]

Maintain backward compatibility and add tests.
```

---

## 🎓 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com
- Key concepts: Dependencies, Pydantic, async/await

### React + TypeScript
- Docs: https://react.dev
- TS Handbook: https://www.typescriptlang.org/docs/

### Tailwind CSS
- Docs: https://tailwindcss.com
- Components: https://tailwindui.com

### Anthropic Claude
- Docs: https://docs.anthropic.com
- Prompt engineering: https://docs.anthropic.com/claude/docs/prompt-engineering

---

**Happy Coding! 🚀**

Use Claude as your pair programmer - it knows the entire codebase structure and can help you build features 10x faster!

