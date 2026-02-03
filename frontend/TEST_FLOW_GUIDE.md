# Complete User Journey Test Flow

This guide provides step-by-step instructions for testing the complete user journey from document upload to analytics dashboard.

## Overview

Each step maps to exactly one backend endpoint:

1. **Upload Document** → `POST /api/v1/documents/upload`
2. **Create Baseline** → `POST /api/v1/baselines`
3. **Generate Draft Timeline** → `POST /api/v1/timelines/draft/generate`
4. **Commit Timeline** → `POST /api/v1/timelines/draft/{id}/commit`
5. **Track Progress** → `POST /api/v1/progress/milestones/{id}/complete`
6. **Submit PhD Doctor** → `POST /api/v1/doctor/submit`
7. **View Analytics Dashboard** → `GET /api/v1/analytics/summary`

## Prerequisites

- Backend server running on `http://localhost:8000` (or configured `VITE_API_BASE_URL`)
- Frontend server running on `http://localhost:3000`
- Database initialized and accessible
- Test user account (or ability to create one)

## Test Flow

### Step 1: Upload Document

**Endpoint:** `POST /api/v1/documents/upload`

**Frontend Route:** `/documents/upload`

**Actions:**
1. Navigate to `http://localhost:3000/documents/upload`
2. Select a PDF or DOCX file (e.g., PhD program requirements document)
3. Enter document title: "PhD Program Requirements"
4. Enter description: "Official PhD program requirements document"
5. Select document type: "requirements"
6. Click "Upload Document"

**Expected Results:**
- ✅ File uploads successfully
- ✅ Progress bar shows upload progress
- ✅ Document ID is returned
- ✅ No errors displayed
- ✅ Form remains visible (baseline creation is next step)

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/documents/upload` with status 200
- Response contains `{ documentId: "..." }`

**Verify Backend State:**
- Document record created in database
- File stored in uploads directory
- Document text extracted and stored

---

### Step 2: Create Baseline

**Endpoint:** `POST /api/v1/baselines`

**Frontend Route:** `/documents/upload` (same page, after document upload)

**Actions:**
1. After document upload succeeds, baseline form appears
2. Fill in baseline form:
   - Program Name: "PhD in Computer Science"
   - Institution: "Test University"
   - Field of Study: "Computer Science"
   - Start Date: Select today's date
   - Expected End Date: Select date 4 years from now (optional)
   - Research Area: "Machine Learning" (optional)
3. Click "Create Baseline"

**Expected Results:**
- ✅ Baseline created successfully
- ✅ Global state updated: `baselineStatus: 'EXISTS'`
- ✅ Navigation redirects to appropriate screen (based on state)
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/baselines` with status 200
- Response contains `{ baselineId: "..." }`
- Global state store shows `baselineStatus: 'EXISTS'`

**Verify Backend State:**
- Baseline record created in database
- Baseline linked to document
- Baseline linked to user

---

### Step 3: Generate Draft Timeline

**Endpoint:** `POST /api/v1/timelines/draft/generate`

**Frontend Route:** `/timelines/draft` or `/timelines/draft/{draftId}`

**Actions:**
1. Navigate to timeline generation page (should auto-redirect after baseline creation)
2. If no draft exists, timeline generation should trigger automatically
3. Wait for timeline generation to complete (may take a few seconds)

**Expected Results:**
- ✅ Timeline generation starts automatically (if no draft exists)
- ✅ Loading indicator shows "Generating timeline..."
- ✅ Draft timeline created with stages and milestones
- ✅ Timeline displayed with:
  - Stages (e.g., "Coursework", "Literature Review", "Research Phase")
  - Milestones within each stage
  - DRAFT status badge visible
- ✅ Global state updated: `timelineStatus: 'DRAFT'`
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/timelines/draft/generate` with status 200
- Response contains timeline with stages and milestones
- Global state store shows `timelineStatus: 'DRAFT'`

**Verify Backend State:**
- DraftTimeline record created
- TimelineStage records created
- TimelineMilestone records created
- All linked to baseline and user

---

### Step 4: Commit Timeline

**Endpoint:** `POST /api/v1/timelines/draft/{draftId}/commit`

**Frontend Route:** `/timelines/draft/{draftId}`

**Actions:**
1. On the draft timeline page, click "Commit Timeline" button
2. In the commit modal:
   - Review the warning about immutability
   - Optionally modify title: "My Committed PhD Timeline"
   - Optionally modify description
3. Click "Confirm Commit"

**Expected Results:**
- ✅ Commit confirmation modal appears
- ✅ Commit succeeds
- ✅ Global state updated: `timelineStatus: 'COMMITTED'`
- ✅ Navigation redirects to committed timeline page
- ✅ Committed timeline is read-only
- ✅ Draft timeline is frozen (is_active = false)
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/timelines/draft/{draftId}/commit` with status 200
- Response contains `{ committedTimelineId: "..." }`
- Global state store shows `timelineStatus: 'COMMITTED'`

**Verify Backend State:**
- CommittedTimeline record created
- DraftTimeline.is_active set to false
- CommittedTimeline linked to DraftTimeline
- All stages and milestones copied to committed timeline

---

### Step 5: Track Progress

**Endpoint:** `POST /api/v1/progress/milestones/{milestoneId}/complete`

**Frontend Route:** `/progress/timeline/{timelineId}`

**Actions:**
1. Navigate to progress tracking page (should be accessible after commit)
2. View committed milestones
3. Click checkbox next to a milestone to mark it as completed
4. Optionally mark multiple milestones as completed

**Expected Results:**
- ✅ Progress tracking page loads with committed milestones
- ✅ Milestones displayed with completion checkboxes
- ✅ Clicking checkbox marks milestone as completed
- ✅ Delay indicators update (if milestone is overdue)
- ✅ Progress percentage updates
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/progress/milestones/{milestoneId}/complete` with status 200
- Response contains `{ eventId: "..." }`
- Subsequent GET requests show updated progress data

**Verify Backend State:**
- ProgressEvent record created for each completion
- Milestone.is_completed set to true
- Delay calculations updated
- Progress metrics recalculated

---

### Step 6: Submit PhD Doctor Questionnaire

**Endpoint:** `POST /api/v1/doctor/submit`

**Frontend Route:** `/assessment` or `/doctor`

**Actions:**
1. Navigate to PhD Doctor questionnaire page
2. Fill out questionnaire dimensions:
   - Research Quality: Answer all questions (1-10 scale)
   - Timeline Adherence: Answer all questions
   - Work-Life Balance: Answer all questions
   - (Other dimensions as configured)
3. Review progress indicator (should show completion percentage)
4. Click "Submit Assessment"

**Expected Results:**
- ✅ Questionnaire form loads with all dimensions
- ✅ Auto-save works (draft saved periodically)
- ✅ Progress indicator shows completion status
- ✅ Submit button enabled when all questions answered
- ✅ Submission succeeds
- ✅ JourneyAssessment summary displayed
- ✅ UI locks after submission (read-only)
- ✅ Global state updated: `doctorStatus: 'SUBMITTED'`
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `POST /api/v1/doctor/save-draft` (auto-save calls)
- Network tab shows `POST /api/v1/doctor/submit` with status 200
- Response contains JourneyAssessment with scores and recommendations
- Global state store shows `doctorStatus: 'SUBMITTED'`

**Verify Backend State:**
- QuestionnaireDraft.is_submitted set to true
- JourneyAssessment record created
- Health scores calculated and stored
- Recommendations generated and stored

---

### Step 7: View Analytics Dashboard

**Endpoint:** `GET /api/v1/analytics/summary`

**Frontend Route:** `/dashboard` or `/analytics`

**Actions:**
1. Navigate to analytics dashboard page
2. Wait for analytics summary to load

**Expected Results:**
- ✅ Dashboard loads successfully
- ✅ Analytics summary displays:
  - Timeline status (on_track, delayed, or completed)
  - Progress percentage
  - Milestone completion stats (total, completed, pending)
  - Delay indicators (total delays, overdue milestones, etc.)
  - Journey health summary (overall score, dimension scores)
  - Longitudinal summary (timeline overview, progress events, etc.)
- ✅ All data is read-only (no calculations performed in frontend)
- ✅ No errors displayed

**Verify in Browser DevTools:**
- Network tab shows `GET /api/v1/analytics/summary?user_id=...` with status 200
- Response contains complete analytics summary
- Global state store shows `analyticsStatus: 'AVAILABLE'`

**Verify Backend State:**
- AnalyticsSnapshot record created (or retrieved from cache)
- Summary contains all required metrics
- Health scores from JourneyAssessment included
- Progress data from ProgressEvents included

---

## End-to-End Validation

After completing all steps, verify:

### Frontend State
- ✅ `baselineStatus: 'EXISTS'`
- ✅ `timelineStatus: 'COMMITTED'`
- ✅ `doctorStatus: 'SUBMITTED'`
- ✅ `analyticsStatus: 'AVAILABLE'`

### Backend State
- ✅ Document record exists
- ✅ Baseline record exists and linked to document
- ✅ DraftTimeline exists (is_active = false)
- ✅ CommittedTimeline exists and linked to draft
- ✅ ProgressEvent records exist for completed milestones
- ✅ QuestionnaireDraft exists (is_submitted = true)
- ✅ JourneyAssessment exists with scores
- ✅ AnalyticsSnapshot exists with summary

### Data Consistency
- ✅ All records linked to same user_id
- ✅ CommittedTimeline has stages and milestones
- ✅ Progress events reference correct milestones
- ✅ Analytics summary references correct timeline
- ✅ Journey health scores are valid (0-100 range)

---

## Troubleshooting

### Step 1 Fails: Document Upload
- **Check:** File size limits, file type restrictions
- **Check:** Backend upload directory permissions
- **Check:** Network connectivity

### Step 2 Fails: Baseline Creation
- **Check:** Document ID is valid
- **Check:** Required fields are provided
- **Check:** Date format is correct

### Step 3 Fails: Timeline Generation
- **Check:** Baseline exists (invariant check)
- **Check:** Baseline has valid document
- **Check:** Timeline orchestrator is working
- **Check:** Backend logs for errors

### Step 4 Fails: Timeline Commit
- **Check:** Draft timeline exists (invariant check)
- **Check:** Draft timeline is active
- **Check:** User has permission to commit

### Step 5 Fails: Progress Tracking
- **Check:** Committed timeline exists (invariant check)
- **Check:** Milestone ID is valid
- **Check:** Progress service is working

### Step 6 Fails: PhD Doctor Submission
- **Check:** All questions are answered
- **Check:** Response values are in valid range (1-10)
- **Check:** Questionnaire version exists

### Step 7 Fails: Analytics Dashboard
- **Check:** Committed timeline exists (invariant check)
- **Check:** Analytics orchestrator is working
- **Check:** Progress events exist
- **Check:** JourneyAssessment exists

---

## Automated Testing

See `backend/scripts/test_complete_journey.py` for an automated test script that verifies all steps programmatically.

---

## Notes

- Each step depends on the previous step completing successfully
- Invariant checks prevent invalid operations (e.g., generating timeline without baseline)
- Global state is updated only from API responses (no optimistic updates)
- All calculations are performed by backend (frontend only displays data)
- Error messages come from backend (no frontend guessing)
