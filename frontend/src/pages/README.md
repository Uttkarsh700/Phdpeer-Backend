# Frontend Pages

This directory contains all page components for the PhD Timeline Intelligence Platform.

## Implemented Pages

### 1. Document Upload Page (`/documents/upload`)

**File:** `DocumentUploadPage.tsx`

**Features:**
- File upload (PDF/DOCX) with validation
- Progress bar during upload
- Document metadata form (title, description, type)
- Optional baseline creation with context form
- Automatic navigation after success

**Form Fields:**
- **Document:**
  - File selection (PDF/DOCX only)
  - Title (required)
  - Description (optional)
  - Document type (dropdown)
  
- **Baseline Context** (optional):
  - Program name (required if enabled)
  - Institution (required if enabled)
  - Field of study (required if enabled)
  - Start date (required if enabled)
  - Expected end date (optional)
  - Research area (optional)

**Flow:**
1. Select file → Auto-populate title
2. Fill document metadata
3. Toggle "Create Baseline" if needed
4. Fill baseline context
5. Submit → Upload document → Create baseline (if enabled) → Navigate

**API Calls:**
- `documentService.upload()` - Upload document with progress tracking
- `baselineService.create()` - Create baseline (if enabled)

---

### 2. Draft Timeline Page (`/timelines/draft/:draftId`)

**File:** `DraftTimelinePage.tsx`

**Features:**
- View draft timeline with all stages and milestones
- Edit mode toggle (UI only - API endpoints for editing not yet implemented)
- Commit timeline action with modal confirmation
- Stage cards with order, duration, and status
- Milestone cards with completion status and critical flags
- Baseline information display
- Visual hierarchy with stage numbers

**Components:**
- Header with title, description, version, stats
- Baseline info banner
- Edit mode notice (placeholder for future functionality)
- Stage cards with:
  - Stage order number (circular badge)
  - Title and description
  - Duration in months
  - Status badge (PENDING, IN_PROGRESS, COMPLETED)
  - List of milestones
- Milestone cards with:
  - Checkbox (completed state)
  - Title and description
  - Target date
  - Critical flag
  - Completion date (if completed)

**Commit Modal:**
- Title input (pre-filled from draft)
- Description input
- Warning about immutability
- Confirmation action

**API Calls:**
- `timelineService.getDraftWithDetails()` - Load timeline with stages/milestones
- `timelineService.commit()` - Commit timeline to create immutable version

---

### 3. Committed Timeline Page (`/timelines/committed/:committedId`)

**File:** `CommittedTimelinePage.tsx`

**Features:**
- Read-only view of committed timeline
- All stage and milestone details
- Immutability notice banner
- Link to progress tracking
- Completion status display
- Version information

**Display:**
- Header with COMMITTED badge
- Immutability notice (green banner)
- Baseline information
- Stage cards (same layout as draft, read-only)
- Milestone cards with completion dates
- Timeline notes section

**Actions:**
- View Progress button → Navigate to `/progress/timeline/:timelineId`

**API Calls:**
- `timelineService.getCommittedWithDetails()` - Load committed timeline with full details

---

### 4. Baseline Detail Page (`/baselines/:baselineId`)

**File:** `BaselineDetailPage.tsx`

**Features:**
- View baseline details
- Create timeline from baseline
- Display all baseline fields
- Formatted dates and timestamps

**Display:**
- Program name, institution, field of study
- Start date, expected end date
- Research area
- Requirements summary
- Notes
- Created/updated timestamps

**Actions:**
- "Create Timeline" button → Calls `timelineService.createDraft()` → Navigate to draft page

**API Calls:**
- `baselineService.getById()` - Load baseline details
- `timelineService.createDraft()` - Create new draft timeline

---

### 5. Timelines List Page (`/timelines`)

**File:** `TimelinesPage.tsx`

**Features:**
- List all draft and committed timelines
- Tab navigation between drafts and committed
- Click card to navigate to detail page
- Status badges (DRAFT, COMMITTED, ACTIVE)
- Empty states with helpful messages

**Tabs:**
- **Draft Timelines:** Shows all draft timelines with edit access
- **Committed Timelines:** Shows all immutable committed versions

**Timeline Cards:**
- Title and description
- Status badges
- Version number (drafts)
- Commit date (committed)
- Target completion date (committed)
- Creation date

**API Calls:**
- `timelineService.getUserDrafts()` - Load user's draft timelines
- `timelineService.getUserCommitted()` - Load user's committed timelines

---

## Placeholder Pages

The following pages are placeholders (simple headers) awaiting implementation:

- `DashboardPage.tsx` - Main dashboard
- `DocumentsPage.tsx` - Document list
- `DocumentDetailPage.tsx` - Document details
- `BaselinesPage.tsx` - Baseline list
- `BaselineCreatePage.tsx` - Create baseline without document
- `ProgressPage.tsx` - Progress overview
- `TimelineProgressPage.tsx` - Timeline-specific progress
- `HealthDashboardPage.tsx` - Journey health dashboard
- `AssessmentPage.tsx` - Take health assessment
- `AssessmentHistoryPage.tsx` - View assessment history
- `AssessmentDetailPage.tsx` - Assessment details
- `NotFoundPage.tsx` - 404 error page

---

## Design Principles

All implemented pages follow these principles:

### 1. **Clarity Over Design**
- Simple, clean layouts
- Clear typography hierarchy
- Consistent spacing and alignment
- No complex animations or effects

### 2. **Functional Components**
- React functional components with hooks
- TypeScript for type safety
- Local state management (useState)
- Side effects with useEffect

### 3. **Form Patterns**
- Controlled inputs
- Inline validation
- Clear error messages
- Loading states
- Success feedback
- Disabled states during submission

### 4. **Visual Feedback**
- Loading spinners
- Progress bars (file upload)
- Success/error banners
- Disabled button states
- Hover effects
- Status badges

### 5. **Navigation**
- React Router hooks (useNavigate, useParams)
- Automatic redirects after actions
- Back buttons
- Breadcrumb context in headers

### 6. **Tailwind CSS Classes**
- Utility-first styling
- Consistent color palette (blue, green, yellow, red, gray)
- Responsive design patterns
- Focus states for accessibility

---

## Common Patterns

### Loading State
```tsx
if (loading) {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
```

### Error State
```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <p className="text-sm text-red-800">{error}</p>
  </div>
)}
```

### Success State
```tsx
{success && (
  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
    <p className="text-sm text-green-800">Success message</p>
  </div>
)}
```

### Modal Pattern
```tsx
{showModal && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
      {/* Modal content */}
    </div>
  </div>
)}
```

---

## Testing the Pages

### 1. Start the Development Server
```bash
cd frontend
npm run dev
```

### 2. Navigate to Pages
- Upload Document: http://localhost:3000/documents/upload
- View Timelines: http://localhost:3000/timelines
- Draft Timeline: http://localhost:3000/timelines/draft/:draftId
- Committed Timeline: http://localhost:3000/timelines/committed/:committedId
- Baseline Detail: http://localhost:3000/baselines/:baselineId

### 3. Test Flows

**Document Upload → Baseline → Timeline:**
1. Go to `/documents/upload`
2. Upload a PDF/DOCX
3. Enable "Create Baseline"
4. Fill baseline form
5. Submit → Redirects to baseline detail
6. Click "Create Timeline" → Timeline generated
7. View draft timeline
8. Click "Commit Timeline"
9. Fill commit form
10. Submit → Redirects to committed timeline

---

## Next Steps

### Immediate Enhancements
1. Add form validation library (React Hook Form)
2. Add toast notifications (react-hot-toast)
3. Implement edit functionality for drafts
4. Add delete confirmations
5. Add pagination for lists

### Future Pages
1. Progress tracking page with charts
2. Health assessment questionnaire
3. Dashboard with overview widgets
4. Document list with search/filter
5. Baseline list with sorting

### State Management
Consider adding Zustand stores for:
- User authentication
- Global loading state
- Toast notifications
- Cache for API responses
