# Frontend-Backend Integration Summary

## Architecture Overview

The system follows a **strict separation of concerns** where:
- **Backend** = Orchestration, business logic, validation, intelligence
- **Frontend** = UI rendering, state mirroring, API communication

This architecture ensures **zero logic duplication** and **single source of truth**.

---

## Where Orchestration Lives

### Backend Orchestrators

All business logic and orchestration lives **exclusively in the backend**:

#### 1. **BaselineOrchestrator** (`backend/app/orchestrators/baseline_orchestrator.py`)
- **Location:** Backend only
- **Responsibilities:**
  - Validates document exists (if provided)
  - Ensures no baseline already exists for user
  - Creates immutable Baseline record
  - Writes DecisionTrace for audit
  - Handles idempotency via `request_id`
- **Frontend Role:** None - frontend only calls the API

#### 2. **TimelineOrchestrator** (`backend/app/orchestrators/timeline_orchestrator.py`)
- **Location:** Backend only
- **Responsibilities:**
  - Validates baseline exists
  - Calls `TimelineIntelligenceEngine` for stage/milestone detection
  - Estimates durations and maps dependencies
  - Creates DraftTimeline with stages and milestones
  - Commits timeline (creates immutable CommittedTimeline)
  - Writes DecisionTrace for audit
- **Frontend Role:** None - frontend only calls the API

#### 3. **PhDDoctorOrchestrator** (`backend/app/orchestrators/phd_doctor_orchestrator.py`)
- **Location:** Backend only
- **Responsibilities:**
  - Processes questionnaire responses
  - Calls `JourneyHealthEngine` for assessment
  - Generates recommendations and action items
  - Calculates health scores and dimensions
  - Writes DecisionTrace for audit
- **Frontend Role:** None - frontend only collects responses and submits

#### 4. **AnalyticsOrchestrator** (`backend/app/orchestrators/analytics_orchestrator.py`)
- **Location:** Backend only
- **Responsibilities:**
  - Aggregates timeline and progress data
  - Calculates completion percentages
  - Computes delay metrics
  - Generates journey health summary
  - Writes DecisionTrace for audit
- **Frontend Role:** None - frontend only displays results

#### 5. **Services** (Backend)
- **DocumentService:** Text extraction, normalization, language detection
- **ProgressService:** Milestone completion tracking, delay calculation
- **No frontend equivalent** - all processing happens in backend

---

## Where Frontend Stops

### Frontend Responsibilities (Limited Scope)

The frontend has **strictly defined boundaries**:

#### 1. **UI Rendering Only**
```typescript
// Frontend renders what backend provides
const Dashboard = () => {
  const { data } = useAnalyticsSummary();
  return <div>{data.milestone_completion_percentage}%</div>;
};
```
- ✅ Renders backend data
- ❌ Does NOT calculate percentages
- ❌ Does NOT compute delays
- ❌ Does NOT make business decisions

#### 2. **State Mirroring**
```typescript
// Frontend state mirrors backend state exactly
const state = useGlobalStateStore();
// state.baselineStatus: 'NONE' | 'EXISTS' (from backend)
// state.timelineStatus: 'NONE' | 'DRAFT' | 'COMMITTED' (from backend)
```
- ✅ Stores backend state values
- ✅ Updates only after successful API calls
- ❌ Does NOT compute state
- ❌ Does NOT infer state from data

#### 3. **API Communication**
```typescript
// Frontend calls backend, waits for response
const response = await uploadDocument(file, userId);
// Backend returns document_id
setUploadedDocumentId(response.document_id);
```
- ✅ Makes API calls
- ✅ Waits for backend response (no optimistic updates)
- ✅ Passes data through without validation
- ❌ Does NOT validate business rules
- ❌ Does NOT make decisions

#### 4. **Route Guards (State Checks Only)**
```typescript
// Guards check state, but don't compute it
guardTimelineGenerationRequiresBaseline(state);
// Throws error if baselineStatus !== 'EXISTS'
```
- ✅ Checks backend state before allowing actions
- ✅ Prevents invalid navigation
- ❌ Does NOT compute state
- ❌ Does NOT make business decisions

---

## Why No Logic Duplication Exists

### 1. **Single Source of Truth: Backend**

All business logic lives in **one place** - the backend:

```
Frontend Request → Backend Orchestrator → Business Logic → Response
```

**Example: Timeline Generation**
- ❌ Frontend does NOT detect stages
- ❌ Frontend does NOT extract milestones
- ❌ Frontend does NOT estimate durations
- ✅ Backend `TimelineOrchestrator` does ALL of this
- ✅ Frontend only displays the result

### 2. **Frontend State is a Mirror**

Frontend state **mirrors** backend state, it doesn't compute it:

```typescript
// After successful API call
const response = await createBaseline(...);
setBaselineStatus('EXISTS'); // Mirror backend state

// Frontend does NOT do this:
// if (response.baseline) { setBaselineStatus('EXISTS'); } // ❌ NO LOGIC
```

**State Updates:**
- ✅ Updated only after backend confirms success
- ✅ Values come directly from backend
- ❌ Never computed or inferred

### 3. **No Frontend Intelligence**

Frontend has **zero intelligence** - it's a pure presentation layer:

**What Frontend Does:**
- ✅ Renders UI
- ✅ Collects user input
- ✅ Calls backend APIs
- ✅ Displays backend responses

**What Frontend Does NOT Do:**
- ❌ Calculate progress percentages
- ❌ Compute delay metrics
- ❌ Generate recommendations
- ❌ Make business decisions
- ❌ Validate business rules
- ❌ Infer state from data

### 4. **Backend Validates Everything**

All validation happens in backend:

```typescript
// Frontend: Just passes data through
await createBaseline({
  program_name: "PhD in CS",
  institution: "University",
  // ... other fields
});

// Backend: Validates everything
class BaselineOrchestrator:
    def create(self, ...):
        # Validates document exists
        # Validates no baseline exists
        # Validates all fields
        # Creates baseline
```

**Frontend Guards:**
- Route guards check **state** (not data)
- State comes from backend
- Guards prevent UI actions, but backend is final validator

### 5. **No Computed Fields**

Frontend never computes derived values:

```typescript
// ❌ WRONG - Frontend computing
const completionPercentage = (completed / total) * 100;

// ✅ CORRECT - Backend provides
const { milestone_completion_percentage } = await getAnalyticsSummary();
// Backend calculated this, frontend just displays it
```

---

## System Alignment Status

### ✅ Aligned Components

1. **Document Upload**
   - ✅ Frontend calls `POST /api/v1/documents/upload`
   - ✅ Backend `DocumentService` processes file
   - ✅ No frontend logic

2. **API Client Layer**
   - ✅ Centralized API client (`Frontend/src/api/client.ts`)
   - ✅ No business logic in client
   - ✅ Pure HTTP abstraction

3. **State Management**
   - ✅ Global state mirrors backend state only
   - ✅ No computed flags
   - ✅ Updates only after API success

4. **Route Guards**
   - ✅ Check backend state only
   - ✅ No business logic
   - ✅ Prevent invalid navigation

### ⚠️ Partially Aligned Components

1. **WellBeingCheckIn.tsx**
   - ⚠️ Uses mock data (`mockAutoData`, `mockPreviousRCI`)
   - ⚠️ Computes progress (`getCurrentSectionProgress`, `getTotalProgress`)
   - ✅ Should fetch from backend instead

2. **ResearchTimeline.tsx**
   - ✅ Document upload wired correctly
   - ⚠️ Generates UI-only timeline events (acceptable for display)
   - ❌ Missing baseline creation
   - ❌ Missing timeline generation

### ❌ Missing Components

1. **Baseline Creation**
   - ❌ No service (`baseline.service.ts`)
   - ❌ No page wired to backend
   - ❌ No state update after creation

2. **Timeline Generation**
   - ❌ No service (`timeline.service.ts`)
   - ❌ No page
   - ❌ No state update after generation

3. **Timeline Commit**
   - ❌ No commit functionality
   - ❌ No state update after commit

4. **Progress Tracking**
   - ❌ No service (`progress.service.ts`)
   - ❌ No page
   - ❌ No backend integration

5. **PhD Doctor Submission**
   - ❌ No service (`assessment.service.ts`)
   - ⚠️ Uses mock data
   - ❌ No state update after submission

6. **Analytics Dashboard**
   - ❌ No service (`analytics.service.ts`)
   - ❌ Placeholder page (not wired)
   - ❌ No backend integration

---

## Integration Flow Example

### Complete Flow: Upload → Baseline → Timeline → Commit

```
1. User uploads document
   Frontend: POST /api/v1/documents/upload
   Backend: DocumentService.upload_document()
   Response: { document_id: "..." }
   Frontend: Stores document_id (no logic)

2. User creates baseline
   Frontend: POST /api/v1/baselines { document_id, ... }
   Backend: BaselineOrchestrator.create()
   - Validates document exists
   - Validates no baseline exists
   - Creates Baseline record
   - Writes DecisionTrace
   Response: { baseline_id: "..." }
   Frontend: setBaselineStatus('EXISTS') (mirror state)

3. User generates timeline
   Frontend: POST /api/v1/timelines/draft/generate { baseline_id }
   Backend: TimelineOrchestrator.generate()
   - Validates baseline exists
   - Calls TimelineIntelligenceEngine
   - Detects stages, extracts milestones
   - Estimates durations, maps dependencies
   - Creates DraftTimeline
   - Writes DecisionTrace
   Response: { draft_timeline_id: "..." }
   Frontend: setTimelineStatus('DRAFT') (mirror state)

4. User commits timeline
   Frontend: POST /api/v1/timelines/draft/{id}/commit
   Backend: TimelineOrchestrator.commit()
   - Validates draft exists
   - Creates CommittedTimeline (immutable)
   - Marks draft as inactive
   - Writes DecisionTrace
   Response: { committed_timeline_id: "..." }
   Frontend: 
     setTimelineStatus('COMMITTED') (mirror state)
     setAnalyticsStatus('AVAILABLE') (mirror state)
```

**Key Points:**
- ✅ All intelligence in backend
- ✅ Frontend only passes data and mirrors state
- ✅ No logic duplication
- ✅ Single source of truth

---

## Architecture Principles

### 1. **Backend is Source of Truth**
- All business logic in backend
- All validation in backend
- All calculations in backend
- Frontend is presentation layer only

### 2. **Frontend is Stateless (Almost)**
- Frontend state mirrors backend state
- No computed fields
- No derived values
- Updates only after backend confirms

### 3. **No Logic Duplication**
- Business rules exist only in backend
- Frontend never reimplements backend logic
- Frontend never validates business rules
- Frontend never makes business decisions

### 4. **Clear Boundaries**
- Frontend: UI, state mirroring, API calls
- Backend: Orchestration, logic, validation, intelligence
- Never cross boundaries

---

## Conclusion

### System Alignment: ⚠️ **Partially Aligned**

**Strengths:**
- ✅ Architecture is correctly designed
- ✅ Document upload fully integrated
- ✅ State management mirrors backend
- ✅ Route guards check backend state
- ✅ API client has no business logic

**Gaps:**
- ❌ Missing services for 6 of 7 steps
- ❌ Missing pages for 5 of 7 steps
- ⚠️ Some mock data still present
- ⚠️ Some frontend logic still exists

**Next Steps:**
1. Create missing services
2. Wire missing pages
3. Remove mock data
4. Remove frontend logic
5. Add state updates after API calls

**Architecture is sound** - implementation needs completion.
