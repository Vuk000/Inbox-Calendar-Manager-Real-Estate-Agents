# V0 Prompt for AgentFlow Missing Pages

Please generate the following pages for a Next.js 16 (App Router) real estate CRM application called **AgentFlow**. The app uses the existing design system with shadcn/ui components, Tailwind CSS, and the color scheme/styling already established.

---

## CRITICAL DESIGN REQUIREMENTS

1. **Match Existing Design System:**
   - Use the existing AgentFlow color palette (vibrant electric blue primary, bright teal secondary, coral accent)
   - Apply glassmorphism effects with `.glass-card` class for all cards
   - Use `.glow-border` class for primary buttons
   - Maintain consistent spacing, typography, and component styling
   - Follow the existing navigation structure in `app/dashboard/layout.tsx`

2. **Technology Stack:**
   - Next.js 16 with App Router
   - TypeScript
   - shadcn/ui components (already configured)
   - Tailwind CSS with existing theme
   - Lucide React icons
   - Client components where needed (use "use client" directive)

3. **Page Locations:**
   - Create pages under `app/dashboard/` directory
   - Follow Next.js App Router conventions
   - Each page should have a `page.tsx` file

---

## PAGES TO CREATE

### 1. INBOX PAGE (`app/dashboard/inbox/page.tsx`)

**Purpose:** Email inbox management with AI triage, priority filtering, and email detail view.

**Features:**
- **Stats Cards (Top Row):**
  - Total Emails count
  - Unread count
  - Urgent count
  - Today's emails count
  - Use `glass-card` styling with icons

- **Email List (Left/Main Panel):**
  - Filterable email list with tabs: All, Unread, Urgent, Starred, AI-Suggested
  - Search bar with search icon
  - Each email item shows:
    - Sender avatar and name
    - Subject line (bold if unread)
    - Preview snippet (2 lines max)
    - Timestamp (relative: "5 min ago", "2 hours ago")
    - Priority badge (High/Medium/Low with color coding)
    - AI category badge (Hot Lead, Follow-up, Routine, etc.)
    - Star icon (toggleable)
  - Hover effect on email items
  - Selected email highlighted

- **Email Detail Panel (Right Side on Desktop):**
  - Full email content
  - Sender details with avatar
  - Action buttons: Reply, Forward, Archive, Delete, Star
  - "Generate AI Reply" button with sparkles icon (primary, glow-border)
  - Responsive: slide-in panel on mobile

- **Empty State:**
  - Centered message when no emails selected
  - Illustration or icon
  - "Select an email to view details" text

**Mock Data Structure:**
```typescript
interface Email {
  id: number
  sender_name: string
  sender_email: string
  subject: string
  snippet: string
  body: string
  timestamp: string
  is_read: boolean
  is_starred: boolean
  priority: 'high' | 'medium' | 'low'
  ai_category: string
}
```

---

### 2. DRAFTS PAGE (`app/dashboard/drafts/page.tsx`)

**Purpose:** Manage AI-generated email drafts with variants and editing.

**Features:**
- **Header:**
  - "Email Drafts" title
  - "Generate New Draft" button (primary, glow-border)
  - Search bar

- **Drafts List:**
  - Grid of draft cards (2-3 columns on desktop)
  - Each draft card shows:
    - Original email subject/context
    - Draft preview (first 3 lines)
    - "Variant 1 of 3" badge
    - Edit and Send buttons
    - Delete icon
    - Timestamp created
  - Use `glass-card` with hover effects

- **Draft Detail Modal/Panel:**
  - Full draft content (editable textarea)
  - Variant selector tabs (if multiple variants)
  - Tone indicator badge (Professional, Friendly, Formal)
  - Action buttons:
    - Save Changes
    - Send Email (primary button)
    - Generate More Variants
    - Discard

- **Empty State:**
  - "No drafts yet"
  - "Generate your first AI draft" message
  - Create Draft button

**Mock Data Structure:**
```typescript
interface Draft {
  id: number
  original_message_id: number
  subject: string
  content: string
  variant_number: number
  total_variants: number
  tone: string
  created_at: string
  status: 'draft' | 'sent'
}
```

---

### 3. TASKS PAGE (`app/dashboard/tasks/page.tsx`)

**Purpose:** Task management with kanban-style board and status tracking.

**Features:**
- **Header:**
  - "Tasks" title
  - View toggle: Board View / List View
  - "Create Task" button (primary, glow-border)
  - Filter dropdown (All, My Tasks, Team Tasks)

- **Kanban Board View:**
  - 4 columns: To Do, In Progress, Review, Completed
  - Each column has:
    - Title with count badge
    - Scrollable task cards
    - "Add Task" button at bottom
  - Task cards show:
    - Task title
    - Description snippet
    - Due date with calendar icon
    - Priority badge
    - Assignee avatar(s)
    - Tags/labels
    - Contact/property linked (if applicable)
  - Drag-and-drop appearance (even if not functional yet)

- **List View (Alternative):**
  - Table-style list with columns: Task, Status, Priority, Due Date, Assignee
  - Checkbox for completion
  - Row click to view details

- **Task Detail Modal:**
  - Task title (editable)
  - Description (editable textarea)
  - Status dropdown
  - Priority selector
  - Due date picker
  - Assignee selector
  - Tags input
  - Linked contact/property selector
  - Delete Task button (destructive)
  - Save Changes button

**Mock Data Structure:**
```typescript
interface Task {
  id: number
  title: string
  description: string
  status: 'todo' | 'in_progress' | 'review' | 'completed'
  priority: 'high' | 'medium' | 'low'
  due_date: string
  assignee_name?: string
  tags: string[]
  linked_contact_id?: number
}
```

---

### 4. CALENDAR PAGE (`app/dashboard/calendar/page.tsx`)

**Purpose:** Meeting and event calendar with scheduling.

**Features:**
- **Header:**
  - Month/Year display with prev/next arrows
  - View toggle: Month, Week, Day
  - "Schedule Meeting" button (primary, glow-border)
  - Today button

- **Calendar Grid (Month View):**
  - Standard calendar layout (7 days × 5-6 weeks)
  - Each day cell shows:
    - Day number
    - Event dots/pills (color-coded by type)
    - Today highlighted
    - Click to view day details

- **Upcoming Meetings Sidebar:**
  - List of next 5 meetings
  - Each meeting shows:
    - Title
    - Time range
    - Attendees (avatars)
    - Meeting type badge (Showing, Call, Closing, etc.)
    - Video call icon if virtual
  - "View All" link

- **Meeting Detail Modal:**
  - Meeting title
  - Date and time
  - Duration
  - Attendees list
  - Location/Video link
  - Description
  - Linked contact/property
  - Action buttons: Edit, Cancel, Join Call

- **Schedule Meeting Modal:**
  - Title input
  - Date picker
  - Time picker (start/end)
  - Attendees (contact selector)
  - Meeting type dropdown
  - Location/Video link input
  - Notes textarea
  - Create Meeting button

**Mock Data Structure:**
```typescript
interface Meeting {
  id: number
  title: string
  start_time: string
  end_time: string
  attendees: string[]
  type: string
  location?: string
  virtual_link?: string
  description?: string
}
```

---

### 5. ANALYTICS PAGE (`app/dashboard/analytics/page.tsx`)

**Purpose:** Business metrics, reports, and performance analytics.

**Features:**
- **Header:**
  - "Analytics & Reports" title
  - Date range selector (Last 7 days, 30 days, 3 months, Custom)
  - Export Report button

- **Key Metrics Row (4 Cards):**
  - Total Revenue (with $ icon)
  - Active Deals (with trending icon)
  - Response Rate (% with up/down indicator)
  - Conversion Rate (% with chart icon)
  - Each card: glass-card, large number, trend indicator, "vs last period"

- **Charts Section:**
  - **Revenue Chart (Line/Area Chart):**
    - Monthly revenue trend
    - Use recharts library
    - Gradient fill under line
    - Grid background
  
  - **Email Performance (Bar Chart):**
    - Emails sent, opened, replied
    - Grouped bars
    - Legend
  
  - **Lead Pipeline (Funnel Chart or Horizontal Bar):**
    - Stages: New Lead → Qualified → Showing → Offer → Closed
    - Count at each stage
    - Conversion rates between stages
  
  - **Activity Heatmap (Calendar-style):**
    - Email activity by day/hour
    - Color intensity for activity level

- **Reports Table:**
  - List of generated reports
  - Columns: Report Name, Date Range, Created At, Actions
  - Download button per report

**Mock Data:**
Use recharts-compatible data structures with realistic numbers.

---

### 6. SETTINGS PAGE (`app/dashboard/settings/page.tsx`)

**Purpose:** User profile, integrations, preferences, and subscription management.

**Features:**
- **Tabs Navigation (Left Sidebar or Top):**
  - Profile
  - Integrations
  - Preferences
  - Billing & Subscription
  - Security
  - Notifications

- **Profile Tab:**
  - Avatar upload (large circular avatar with edit icon)
  - Full Name input
  - Email (read-only, verified badge)
  - Phone input
  - Job Title input
  - Brokerage/Company input
  - Bio textarea
  - Save Changes button

- **Integrations Tab:**
  - **Email Accounts:**
    - Connected accounts list (Gmail, Outlook)
    - Each shows: email address, status (Active/Disconnected), sync status
    - Connect/Disconnect buttons
    - "Add Email Account" button
  
  - **Calendar Integration:**
    - Google Calendar connect button
    - Sync settings
  
  - **Social Media:**
    - Facebook, Twitter/X integration status
    - Connect buttons

- **Preferences Tab:**
  - Theme toggle (Light/Dark/System)
  - Language selector
  - Timezone selector
  - Email notification preferences (checkboxes)
  - AI assistance level (slider or radio)

- **Billing & Subscription Tab:**
  - Current plan card (glass-card, glow-border if premium)
  - Plan name and price
  - Features included
  - Usage meters (AI actions used/limit, contacts limit)
  - Upgrade/Change Plan button
  - Payment method (card ending in ****1234)
  - Billing history table

- **Security Tab:**
  - Change Password section (old password, new password, confirm)
  - Two-Factor Authentication toggle
  - Active Sessions list
  - Sign out all devices button

- **Notifications Tab:**
  - Email notifications (checkboxes for different types)
  - Push notifications toggle
  - Notification frequency selector
  - Digest preferences

---

### 7. PROPERTIES PAGE (`app/dashboard/properties/page.tsx`)

**Purpose:** Real estate property listings management.

**Features:**
- **Header:**
  - "Properties" title
  - "Add Property" button (primary, glow-border)
  - Search bar
  - View toggle: Grid / List

- **Filters:**
  - Status dropdown (All, Active, Sold, Pending, Archived)
  - Property type (House, Condo, Land, Commercial)
  - Price range slider
  - Sort by (Newest, Price, Size)

- **Properties Grid:**
  - Card grid (2-3 columns)
  - Each property card shows:
    - Main image (placeholder or icon)
    - Address
    - Price (large, bold)
    - Beds/Baths/SqFt icons with numbers
    - Property type badge
    - Status badge (Active/Sold/Pending)
    - Linked contact count (if any)
    - Quick actions: View, Edit, Archive

- **Property Detail Modal:**
  - Image gallery (placeholder images)
  - Address and price
  - Property details table (beds, baths, sqft, lot size, year built)
  - Description textarea
  - MLS ID
  - Listing agent
  - Linked contacts list
  - Linked transactions
  - Action buttons: Edit, Share, Archive

- **Add/Edit Property Form:**
  - Address inputs (street, city, state, zip)
  - Price input
  - Property type selector
  - Beds/baths/sqft inputs
  - Description textarea
  - MLS ID input
  - Status selector
  - Image upload area (placeholder)
  - Save Property button

**Mock Data Structure:**
```typescript
interface Property {
  id: number
  address: string
  city: string
  state: string
  zip: string
  price: number
  beds: number
  baths: number
  sqft: number
  property_type: string
  status: 'active' | 'sold' | 'pending' | 'archived'
  description: string
  mls_id?: string
  images: string[]
}
```

---

## DESIGN CONSISTENCY CHECKLIST

For each page, ensure:

✅ All cards use `glass-card` className
✅ Primary action buttons use `glow-border` className
✅ Icons from lucide-react
✅ Consistent spacing (p-6, space-y-6, gap-4, gap-6)
✅ Responsive design (mobile-first)
✅ Loading states with skeleton or spinner
✅ Empty states with helpful messaging
✅ Proper TypeScript types
✅ "use client" directive where needed (interactive components)
✅ Accessible (labels, aria-attributes)
✅ Color-coded badges (destructive for high priority, secondary for medium, outline for low)
✅ Hover effects on interactive elements
✅ Consistent typography hierarchy

---

## COMPONENT REUSE

Use these existing shadcn/ui components:
- Card, CardHeader, CardTitle, CardDescription, CardContent
- Button (variants: default, outline, ghost, destructive)
- Input, Textarea, Label
- Select, SelectTrigger, SelectValue, SelectContent, SelectItem
- Badge
- Avatar, AvatarImage, AvatarFallback
- DropdownMenu (for actions)
- Tabs, TabsList, TabsTrigger, TabsContent
- Dialog or Sheet (for modals)

---

## MOCK DATA

Generate realistic mock data for each page. Use:
- Real estate agent names
- California cities and addresses
- Realistic email subjects and content
- Professional business context
- Dates within last 30 days
- Logical status progressions

---

## OUTPUT

Please create:
1. All 7 page files with complete implementations
2. Mock data arrays within each page file
3. All necessary components as separate files if reusable
4. Proper TypeScript interfaces
5. Responsive layouts that work on mobile, tablet, desktop

Match the quality and style of the existing Dashboard and Contacts pages. The pages should look cohesive and professional, ready for a real estate CRM product.

