# Frensei Data Flow Architecture

## Overview
This document maps the data flows across all Frensei modules and identifies inputs needed for consistency.

---

## Module Data Flows

### 1. Research Timeline → Collaboration Ledger
**Flow Direction**: Timeline events can inform collaboration events

**Data Inputs Required**:
- Research proposal document (PDF/DOCX)
- Detected research field
- Timeline milestones (dates, phases, deliverables)

**Outputs Generated**:
- Structured timeline with phases and milestones
- Gantt chart visualization
- Key deadline dates

**Integration Points**:
- Timeline milestones (e.g., "Draft submission") should auto-create pending collaboration events
- Major deadlines should suggest collaboration verification prompts
- Supervisor feedback dates from timeline can pre-populate ledger events

**Current State**: ❌ Not integrated
**Recommended**: Timeline milestone dates → Auto-suggest Collaboration Ledger events

---

### 2. Collaboration Ledger → PhD Doctor (WellBeing)
**Flow Direction**: Collaboration health impacts wellness metrics

**Data Inputs Required**:
- Event frequency (meetings, feedback sessions)
- Verification status (pending vs verified events)
- Supervisor interaction patterns
- Delay events and explanations

**Outputs Generated**:
- Supervision cadence score
- Communication health indicator
- Collaboration risk assessment
- Recommendation adjustments based on team dynamics

**Integration Points**:
- Low verification rates → Flag as "Supervision Concern" in PhD Doctor
- Long gaps between meetings → Reduce supervision score
- High rejection rates → Increase risk level
- Frequent delay explanations → Flag timeline pressure

**Current State**: ❌ Not integrated
**Recommended**: 
```javascript
// Example integration
const supervisionCadence = calculateFromLedger({
  meetingFrequency: ledgerEvents.filter(e => e.type === 'meeting').length,
  averageGapDays: getAverageGapBetweenMeetings(),
  pendingVerifications: ledgerEvents.filter(e => e.status === 'pending').length
});
```

---

### 3. PhD Doctor → Collaboration Ledger
**Flow Direction**: Wellness check-in responses inform collaboration needs

**Data Inputs Required**:
- Supervision quality scores (1-5 Likert scale)
- Mental health indicators
- Timeline pressure responses
- Support satisfaction ratings

**Outputs Generated**:
- Recommended meeting frequency
- Suggested intervention events
- Communication improvement prompts

**Integration Points**:
- Low supervision scores → Auto-suggest "Schedule Meeting" event
- High stress responses → Prompt "Delay Explained" or "Support Discussion" event
- Negative wellbeing trends → Alert Overseers (supervisors) in Ledger

**Current State**: ❌ Not integrated
**Recommended**: PhD Doctor results → Generate suggested Collaboration Ledger events

---

### 4. Peer Network → Collaboration Ledger
**Flow Direction**: External collaborations tracked in ledger

**Data Inputs Required**:
- Peer connections and roles
- Co-authorship relationships
- External collaborator profiles

**Outputs Generated**:
- Suggested participants for events
- Co-author verification invitations
- External collaboration tracking

**Integration Points**:
- Peers from Network → Available as Collaboration Ledger participants
- Co-authors identified → Auto-add as "Collaborator" role
- Industry mentors → Auto-add as "Overseer" role

**Current State**: ❌ Not integrated
**Recommended**: Peer Network profiles → Populate Collaboration Ledger participant list

---

### 5. Timeline + Ledger + PhD Doctor → Institutional Dashboard
**Flow Direction**: All modules feed university-level analytics

**Data Aggregated**:
- Timeline completion rates
- Collaboration verification patterns
- Wellbeing risk scores
- Supervisor engagement metrics

**Outputs Generated**:
- Department-wide risk heatmaps
- Supervision quality benchmarks
- Intervention recommendations
- Funding allocation priorities

**Integration Points**:
- Multiple students with low supervision cadence → Flag department
- Persistent unverified events → Highlight supervisor
- Widespread wellbeing decline → Institutional alert

**Current State**: ❌ Not integrated
**Recommended**: Aggregated dashboard pulling from all student modules

---

## Data Consistency Requirements

### User Identity
**Required Across All Modules**:
- `user_id` (from auth.users)
- Display name
- Email
- Role in research (PhD student, supervisor, co-author)

**Implementation Status**: ✅ Partially implemented
- Collaboration Ledger uses `project_members` table
- PhD Doctor uses anonymous session data
- Timeline uses file metadata only

**Action Needed**: Create unified `user_profiles` table:
```sql
CREATE TABLE public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  display_name TEXT NOT NULL,
  email TEXT,
  research_field TEXT,
  institution TEXT,
  role TEXT, -- 'phd_student', 'supervisor', 'postdoc', etc.
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

### Shared Event Schema
**Required for Integration**:
- Standardized date format (ISO 8601)
- Common event type taxonomy
- Shared participant references

**Current Issues**:
- Timeline uses custom milestone structure
- Ledger uses collaboration_events table
- PhD Doctor uses wellbeing_responses table
- No unified event bus

**Action Needed**: Create event bridge table:
```sql
CREATE TABLE public.unified_events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  source_module TEXT, -- 'timeline', 'ledger', 'phd_doctor'
  event_type TEXT,
  event_date DATE,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

### Research Field Consistency
**Current State**:
- Timeline detects field from proposal keywords
- PhD Doctor has hardcoded field in wellbeing questions
- Collaboration Ledger has no field awareness
- Peer Network would need field matching

**Action Needed**: 
1. Store detected field in user_profiles
2. Use field to:
   - Customize PhD Doctor questions
   - Match Peer Network recommendations
   - Filter Institutional Dashboard views
   - Tag Collaboration Ledger events

---

## Priority Integration Roadmap

### Phase 1: User Profile Foundation (Highest Priority)
1. Create `user_profiles` table
2. Migrate existing user data
3. Link all modules to profiles

### Phase 2: Timeline → Ledger Bridge
1. Extract milestone dates from Timeline
2. Auto-suggest Ledger events for major deadlines
3. Link Timeline phases to Ledger event types

### Phase 3: Ledger → PhD Doctor Integration
1. Calculate supervision metrics from Ledger
2. Adjust PhD Doctor scores based on collaboration health
3. Generate intervention recommendations

### Phase 4: Cross-Module Event Bus
1. Create unified_events table
2. Stream events from all modules
3. Enable Institutional Dashboard aggregation

### Phase 5: Peer Network Integration
1. Import Peer Network profiles as Ledger participants
2. Track external collaborations
3. Enable co-author verification workflows

---

## Data Privacy & Security Notes

### Role-Based Access
- **Collaborators**: See events they participate in
- **Overseers**: See all events (no write access)
- **Viewers**: Read-only access
- **Students**: Own their data across all modules
- **Institutions**: Aggregated, anonymized analytics only

### Sensitive Data
- PhD Doctor responses: Encrypted, not shared with institutions
- Collaboration Ledger: Visible to participants only
- Timeline: Private by default, shareable on demand

### GDPR Compliance
- All user data exportable
- Right to deletion supported
- Audit logs for institutional access
- Consent management for data sharing

---

## API Endpoints Needed

### Cross-Module Queries
```typescript
// Get user's complete research health
GET /api/research-health/:userId
Response: {
  timeline: { completionRate, upcomingMilestones },
  collaboration: { verificationRate, supervisionCadence },
  wellbeing: { riskLevel, recommendations },
  network: { activeConnections, opportunitiesMatched }
}

// Trigger cross-module event
POST /api/events/suggest
Body: { 
  sourceModule: "timeline",
  eventType: "milestone_deadline",
  suggestTo: "collaboration_ledger"
}
```

---

## Summary

**Current Integration Status**: 0/5 modules connected

**Critical Dependencies**:
1. User profile unification
2. Shared event schema
3. Date format standardization
4. Research field consistency

**Next Steps**:
1. Implement user_profiles table
2. Build Timeline → Ledger bridge
3. Calculate Ledger → PhD Doctor metrics
4. Design unified event bus
