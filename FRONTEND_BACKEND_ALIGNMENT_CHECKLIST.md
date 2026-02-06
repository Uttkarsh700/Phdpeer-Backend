# Frontend-Backend Alignment Checklist

This document lists all frontend assumptions that must be aligned with the backend implementation.

---

## 🔐 Authentication & Authorization

### ✅ Assumptions to Align

- [ ] **Authentication State Storage**
  - **Location**: `src/components/layout/Layout.tsx`, `src/pages/Auth.tsx`, `src/pages/Dashboard.tsx`, `src/components/auth/LoginModal.tsx`
  - **Current**: Uses `sessionStorage.getItem("isAuthenticated")`, `sessionStorage.getItem("userId")`, `sessionStorage.getItem("frensei_access")`
  - **Backend Must Provide**: 
    - Authentication endpoint: `POST /api/v1/auth/login`
    - Authentication endpoint: `POST /api/v1/auth/register`
    - Token-based auth (JWT or session tokens)
    - User ID in response
    - Gateway access validation

- [ ] **Route Protection**
  - **Location**: `src/components/layout/Layout.tsx` (lines 19-37)
  - **Current**: Checks `sessionStorage` for protected routes
  - **Backend Must Provide**: 
    - Protected route validation endpoint
    - User role/permission checking
    - Session validation

- [ ] **Login/Register Flow**
  - **Location**: `src/pages/Auth.tsx` (line 24)
  - **Current**: Mock authentication with TODO comment
  - **Backend Must Provide**: 
    - `POST /api/v1/auth/login` with email/password
    - `POST /api/v1/auth/register` with email/password/displayName
    - Response: `{ userId: string, token: string, isAuthenticated: boolean }`

---

## 📊 Collaboration Events & Ledger

### ✅ Assumptions to Align

- [ ] **Fetch Collaboration Events**
  - **Location**: `src/pages/CollaborationLedger.tsx` (line 52)
  - **Current**: `localStorage.getItem("collaboration_events")`
  - **Backend Must Provide**: 
    - `GET /api/v1/collaboration/events`
    - Response: `CollaborationEvent[]` with structure:
      ```typescript
      {
        id: string;
        created_by: string;
        event_type: string;
        summary: string;
        event_date: string;
        status: 'pending' | 'verified' | 'rejected';
        created_at: string;
        participants: Array<{ user_id: string; role: string }>;
        verifications: Array<{ user_id: string; verified: boolean; timestamp: string }>;
      }
      ```

- [ ] **Create Collaboration Event**
  - **Location**: `src/components/ledger/AddEventModal.tsx` (line 100)
  - **Current**: Creates event object and stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/events`
    - Request body: `{ event_type, summary, event_date, participants }`
    - Response: Created `CollaborationEvent` object

- [ ] **Update Event Verification**
  - **Location**: `src/components/ledger/EventCard.tsx` (line 73)
  - **Current**: Updates verification in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/events/:id/verify`
    - Request body: `{ verified: boolean }`
    - Response: Updated event with verification

- [ ] **Journey Reconstruction (AI Minutes-to-Timeline)**
  - **Location**: `src/components/ledger/ReconstructJourneyModal.tsx` (line 44)
  - **Current**: Mock extraction, returns hardcoded event
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/journey/reconstruct`
    - Request body: `{ journey_text: string }`
    - Response: `{ events: CollaborationEvent[], error?: string }`
    - **Note**: This requires NLP/AI processing on backend

- [ ] **Timeline Integration**
  - **Location**: `src/components/ledger/TimelineIntegrationModal.tsx` (line 99)
  - **Current**: Creates events from timeline and stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/events/bulk`
    - Request body: `{ events: TimelineEvent[] }`
    - Response: Created events array

---

## 👥 Team & Role Management

### ✅ Assumptions to Align

- [ ] **Fetch Project Members**
  - **Location**: `src/components/ledger/AddEventModal.tsx` (line 54), `src/components/ledger/RoleManagementModal.tsx` (line 29)
  - **Current**: `localStorage.getItem("project_members")`
  - **Backend Must Provide**: 
    - `GET /api/v1/collaboration/members`
    - Response: `Array<{ id: string, user_id: string, display_name: string, role: 'collaborator' | 'overseer' | 'viewer' }>`

- [ ] **Add Team Member**
  - **Location**: `src/components/ledger/RoleManagementModal.tsx` (line 57)
  - **Current**: Creates member object and stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/members`
    - Request body: `{ display_name: string, role: string }`
    - Response: Created member object

- [ ] **Remove Team Member**
  - **Location**: `src/components/ledger/RoleManagementModal.tsx` (line 34)
  - **Current**: Removes from `localStorage`
  - **Backend Must Provide**: 
    - `DELETE /api/v1/collaboration/members/:id`
    - Response: Success confirmation

---

## 🎯 Goals Management

### ✅ Assumptions to Align

- [ ] **Fetch Goals**
  - **Location**: `src/components/profile/GoalsModule.tsx` (line 38)
  - **Current**: `localStorage.getItem("goals")`
  - **Backend Must Provide**: 
    - `GET /api/v1/goals`
    - Response: `Goal[]` with structure:
      ```typescript
      {
        id: string;
        user_id: string;
        title: string;
        description?: string;
        priority: 'low' | 'medium' | 'high';
        completed: boolean;
        due_date?: string;
        created_at: string;
        updated_at: string;
      }
      ```

- [ ] **Create Goal**
  - **Location**: `src/components/profile/GoalsModule.tsx` (line 52)
  - **Current**: Creates goal and stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/goals`
    - Request body: `{ title: string, priority: string, due_date?: string }`
    - Response: Created goal object

- [ ] **Toggle Goal Completion**
  - **Location**: `src/components/profile/GoalsModule.tsx` (line 99)
  - **Current**: Updates completion status in `localStorage`
  - **Backend Must Provide**: 
    - `PATCH /api/v1/goals/:id`
    - Request body: `{ completed: boolean }`
    - Response: Updated goal object

- [ ] **Delete Goal**
  - **Location**: `src/components/profile/GoalsModule.tsx` (line 122)
  - **Current**: Removes from `localStorage`
  - **Backend Must Provide**: 
    - `DELETE /api/v1/goals/:id`
    - Response: Success confirmation

---

## 💚 Wellness Check-in

### ✅ Assumptions to Align

- [ ] **Mock Auto Data**
  - **Location**: `src/pages/WellBeingCheckIn.tsx` (lines 26-36)
  - **Current**: Hardcoded mock data:
    ```typescript
    const mockAutoData = {
      milestoneCompletion: 75,
      avgDelay: 12,
      supervisorResponseTime: 3,
      meetingCadence: 14,
      opportunitiesAdded: 8,
    };
    const mockPreviousRCI = 62;
    ```
  - **Backend Must Provide**: 
    - `GET /api/v1/wellness/auto-data`
    - Response: `{ milestoneCompletion, avgDelay, supervisorResponseTime, meetingCadence, opportunitiesAdded }`
    - `GET /api/v1/wellness/previous-rci`
    - Response: `{ previousRCI: number }`

- [ ] **Wellness Calculation**
  - **Location**: `src/lib/wellnessCalculations.ts`
  - **Current**: Frontend calculates RCI, RI, DI, D1-D8 dimensions
  - **Backend Must Provide**: 
    - `POST /api/v1/wellness/calculate`
    - Request body: `{ sectionScores: SectionScores, autoData: AutoData, previousRCI?: number }`
    - Response: `CalculationResults` with all indices
    - **Note**: Backend should perform calculations, not frontend

- [ ] **Submit Wellness Assessment**
  - **Location**: `src/pages/WellBeingCheckIn.tsx` (line 78)
  - **Current**: Calculates locally, no backend submission
  - **Backend Must Provide**: 
    - `POST /api/v1/wellness/submit`
    - Request body: `{ responses: Record<string, number>, sectionScores: SectionScores }`
    - Response: `{ results: CalculationResults, assessmentId: string }`

---

## 📝 Writing Evolution

### ✅ Assumptions to Align

- [ ] **Fetch Writing Profile**
  - **Location**: `src/pages/WritingEvolution.tsx` (line 37), `src/pages/WritingEvolutionCertificate.tsx` (line 39)
  - **Current**: `loadProfile()` from `localStorage` (via `writingEvolutionTypes.ts`)
  - **Backend Must Provide**: 
    - `GET /api/v1/writing/profile`
    - Response: `WritingProfile` with baseline and submissions

- [ ] **Create Baseline**
  - **Location**: `src/pages/WritingEvolutionBaseline.tsx` (line 68)
  - **Current**: Generates mock evaluation, stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/writing/baseline`
    - Request body: `{ text: string, discipline: string, researchType: string, stage: string, language: string, method: 'upload' | 'write', files?: File[] }`
    - Response: `{ baseline: BaselineEvaluation, profileId: string }`
    - **Note**: Backend must perform writing analysis (not frontend mock)

- [ ] **Submit Checkpoint**
  - **Location**: `src/pages/WritingEvolutionCheckpoint.tsx` (line 47)
  - **Current**: Generates **mock** evolution run results:
    ```typescript
    const mockScore = Math.floor(Math.random() * 30) + 70; // 70-100
    const mockTrend = mockScore >= 85 ? 'improving' : mockScore >= 75 ? 'stable' : 'volatile';
    const mockSignals = [...];
    const mockGuidance = [...];
    const mockChanges = {...};
    ```
  - **Backend Must Provide**: 
    - `POST /api/v1/writing/checkpoint`
    - Request body: `{ file: File, milestoneType: string, date: Date, aiAssisted: boolean, externalEditing: boolean, coauthorInput: boolean }`
    - Response: `{ sample: WritingSample, run: EvolutionRun }` with **real** continuity analysis
    - **Note**: Backend must perform actual writing continuity analysis (not random scores)

- [ ] **Fetch Evolution Report**
  - **Location**: `src/pages/WritingEvolutionReport.tsx` (line 59)
  - **Current**: Loads from `localStorage.getItem("evolution_runs")` and `localStorage.getItem("writing_samples")`
  - **Backend Must Provide**: 
    - `GET /api/v1/writing/reports/:id`
    - Response: `{ run: EvolutionRun, sample: WritingSample }`

- [ ] **Fetch All Evolution Runs**
  - **Location**: `src/pages/WritingEvolutionReport.tsx` (line 61)
  - **Current**: Loads from `localStorage`
  - **Backend Must Provide**: 
    - `GET /api/v1/writing/runs`
    - Response: `EvolutionRun[]`

---

## 📅 Research Timeline

### ✅ Assumptions to Align

- [ ] **Timeline Generation**
  - **Location**: `src/pages/ResearchTimeline.tsx` (lines 403-517)
  - **Current**: **Client-side only** - detects field from filename, generates timeline events locally
  - **Backend Must Provide**: 
    - `POST /api/v1/timeline/generate`
    - Request body: `{ file: File }`
    - Response: `{ field: string, events: TimelineEvent[] }`
    - **Note**: Backend must perform document analysis (not frontend filename detection)

- [ ] **Opportunity Pool (Hardcoded)**
  - **Location**: `src/pages/ResearchTimeline.tsx` (lines 523-534)
  - **Current**: Hardcoded array of opportunity strings
  - **Backend Must Provide**: 
    - `GET /api/v1/timeline/opportunities`
    - Response: `Array<{ title: string, type: string, deadline?: string, match?: number }>`
    - **Note**: Backend should fetch real opportunities from external APIs/databases

- [ ] **Field Detection**
  - **Location**: `src/pages/ResearchTimeline.tsx` (lines 403-429)
  - **Current**: Keyword matching on filename
  - **Backend Must Provide**: 
    - Field detection via document analysis (not filename)
    - Response should include confidence score

---

## 👤 Profile & Dashboard

### ✅ Assumptions to Align

- [ ] **Profile Strength Data (Mock)**
  - **Location**: `src/pages/ProfileStrength.tsx` (line 19)
  - **Current**: Hardcoded `userData` object with mock values
  - **Backend Must Provide**: 
    - `GET /api/v1/profile/strength`
    - Response: `{ name, program, year, academicStage, continuityStatus, lastMeeting, fundingRemaining, monthlyBurn, isBurnedOut, upcomingGrants, upcomingConferences, needsCoAuthor, recommendedSkills }`

- [ ] **Profile Wheel Data**
  - **Location**: `src/pages/ProfileStrength.tsx` (lines 42-49)
  - **Current**: Hardcoded wheel data with scores
  - **Backend Must Provide**: 
    - `GET /api/v1/profile/wheel`
    - Response: `Array<{ id: string, name: string, score: number, color: string }>`
    - **Note**: Scores should be calculated from real data

- [ ] **Add to Timeline from Profile Wheel**
  - **Location**: `src/components/profile/ProfileWheel.tsx` (line 199)
  - **Current**: Creates event and stores in `localStorage`
  - **Backend Must Provide**: 
    - `POST /api/v1/collaboration/events` (same as collaboration events)

- [ ] **AI Nudge Panel**
  - **Location**: `src/components/profile/AINudgePanel.tsx` (line 24)
  - **Current**: Analyzes events from `localStorage` to generate nudges
  - **Backend Must Provide**: 
    - `GET /api/v1/profile/nudges`
    - Response: `Array<{ id: string, title: string, message: string, priority: string, color: string }>`
    - **Note**: Backend should perform AI analysis (not frontend keyword extraction)

- [ ] **Journey Timeline (Mock Papers)**
  - **Location**: `src/components/profile/JourneyTimeline.tsx` (line 18)
  - **Current**: Hardcoded `mockPapers` array
  - **Backend Must Provide**: 
    - `GET /api/v1/profile/journey`
    - Response: `Array<{ title: string, date: string, status: string, type: string }>`

---

## 🏛️ University Dashboard

### ✅ Assumptions to Align

- [ ] **All Dashboard Data (Hardcoded)**
  - **Location**: `src/pages/UniversityDashboard.tsx` (lines 14-70)
  - **Current**: All data is hardcoded:
    - `activityFeed` (line 14)
    - `metrics` (line 39)
    - `heatmapData` (line 47)
    - `fundingData` (line 58)
    - `publications` (line 65)
  - **Backend Must Provide**: 
    - `GET /api/v1/university/dashboard`
    - Response: `{ metrics, heatmapData, fundingData, publications, activityFeed }`
    - **Note**: All metrics should be calculated from real researcher data

- [ ] **Activity Feed Updates**
  - **Location**: `src/pages/UniversityDashboard.tsx` (lines 22-37)
  - **Current**: Randomly generates activities from hardcoded array every 5 seconds
  - **Backend Must Provide**: 
    - `GET /api/v1/university/activity-feed` (real-time or polling)
    - Response: `Array<{ id: string, text: string, timestamp: string }>`

---

## 🌐 Peer Network

### ✅ Assumptions to Align

- [ ] **All Network Data (Hardcoded)**
  - **Location**: `src/pages/PeerNetwork.tsx` (lines 13-86)
  - **Current**: All data is hardcoded:
    - `industryProjects` (line 13)
    - `entrepreneurshipOpps` (line 21)
    - `gigListings` (line 27)
    - `peerMatches` (line 33)
    - `pendingInvitations` (line 39)
    - `aiUpdates` (line 44)
    - `grantOpportunities` (line 53)
  - **Backend Must Provide**: 
    - `GET /api/v1/network/industry-projects`
    - `GET /api/v1/network/entrepreneurship-opportunities`
    - `GET /api/v1/network/gig-listings`
    - `GET /api/v1/network/peer-matches`
    - `GET /api/v1/network/pending-invitations`
    - `GET /api/v1/network/ai-updates`
    - `GET /api/v1/network/grant-opportunities`
    - Response: Appropriate data structures for each

- [ ] **Apply to Project**
  - **Location**: `src/pages/PeerNetwork.tsx` (line 117)
  - **Current**: Simulates application with `setTimeout`
  - **Backend Must Provide**: 
    - `POST /api/v1/network/projects/:id/apply`
    - Response: `{ success: boolean, applicationId: string }`

- [ ] **Find Peer**
  - **Location**: `src/pages/PeerNetwork.tsx` (line 146)
  - **Current**: Simulates peer finding with stages
  - **Backend Must Provide**: 
    - `POST /api/v1/network/find-peer`
    - Response: `{ peer: PeerMatch, matchScore: number }`
    - **Note**: Backend should perform actual matching algorithm

---

## 📊 Dashboard (Main)

### ✅ Assumptions to Align

- [ ] **Dashboard Placeholder**
  - **Location**: `src/pages/Dashboard.tsx` (line 39)
  - **Current**: Placeholder text "This is a placeholder dashboard. More features coming soon!"
  - **Backend Must Provide**: 
    - `GET /api/v1/dashboard/summary`
    - Response: Dashboard summary data

---

## 🔧 Frontend-Computed State (Should Be Backend)

### ✅ Calculations to Move to Backend

- [ ] **Wellness Indices Calculation**
  - **Location**: `src/lib/wellnessCalculations.ts`
  - **Current**: Frontend calculates D1-D8, RI, DI, RCI, bands
  - **Backend Must Provide**: 
    - All calculations should be performed on backend
    - Frontend should only display results

- [ ] **Writing Evolution Analysis**
  - **Location**: `src/pages/WritingEvolutionCheckpoint.tsx` (lines 51-74)
  - **Current**: Generates random mock scores and trends
  - **Backend Must Provide**: 
    - Real continuity score calculation
    - Real trend analysis
    - Real signal detection
    - Real guidance generation

- [ ] **Timeline Event Generation**
  - **Location**: `src/pages/ResearchTimeline.tsx` (lines 432-517)
  - **Current**: Client-side generation based on field config
  - **Backend Must Provide**: 
    - Document analysis
    - Timeline generation
    - Event suggestion

- [ ] **Profile Wheel Score Calculation**
  - **Location**: `src/pages/ProfileStrength.tsx` (lines 42-49)
  - **Current**: Hardcoded scores
  - **Backend Must Provide**: 
    - Real score calculation from user data
    - Dynamic score updates

---

## 📦 Data Storage Keys (localStorage/sessionStorage)

### ✅ Storage Keys to Replace with API Calls

- [ ] `collaboration_events` → `GET /api/v1/collaboration/events`
- [ ] `project_members` → `GET /api/v1/collaboration/members`
- [ ] `goals` → `GET /api/v1/goals`
- [ ] `evolution_runs` → `GET /api/v1/writing/runs`
- [ ] `writing_samples` → `GET /api/v1/writing/samples`
- [ ] `isAuthenticated` → Backend session/token validation
- [ ] `userId` → Backend user context
- [ ] `frensei_access` → Backend gateway validation

---

## 🎯 Summary

### Critical Backend Requirements

1. **Authentication System**: JWT/session tokens, user management
2. **Collaboration Events API**: Full CRUD operations
3. **Wellness Calculation Engine**: Backend must calculate all indices
4. **Writing Analysis Engine**: Real continuity analysis (not mocks)
5. **Timeline Generation**: Document analysis and event generation
6. **Profile Data Aggregation**: Real-time calculation of profile metrics
7. **Opportunity Matching**: Real data from external sources
8. **AI/NLP Services**: Journey reconstruction, nudge generation, writing analysis

### Data Flow Changes

- **Before**: Frontend → localStorage → Display
- **After**: Frontend → API → Backend → Database → Response → Display

### Mock Data Locations

- All hardcoded arrays in `PeerNetwork.tsx`
- All hardcoded objects in `UniversityDashboard.tsx`
- Mock calculations in `WritingEvolutionCheckpoint.tsx`
- Mock auto data in `WellBeingCheckIn.tsx`
- Hardcoded profile data in `ProfileStrength.tsx`

---

## ✅ Next Steps

1. Create API client layer in frontend
2. Replace all `localStorage`/`sessionStorage` operations with API calls
3. Move all calculations to backend
4. Replace all hardcoded data with API endpoints
5. Implement error handling for API failures
6. Add loading states for async operations
7. Update TypeScript types to match backend responses
