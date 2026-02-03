# Testing Summary

## Complete User Journey Test Flow

This document summarizes the test flow for verifying the complete user journey from document upload to analytics dashboard.

### Test Files

1. **Manual Test Guide**: `frontend/TEST_FLOW_GUIDE.md`
   - Step-by-step instructions for manual testing
   - Browser DevTools verification steps
   - Troubleshooting guide

2. **Automated Test Script**: `backend/scripts/test_complete_journey.py`
   - Python script that tests all 7 steps programmatically
   - Validates backend state after each step
   - Verifies data consistency

### Test Flow Overview

Each step maps to exactly one backend endpoint:

| Step | Action | Endpoint | Frontend Route |
|------|--------|----------|----------------|
| 1 | Upload Document | `POST /api/v1/documents/upload` | `/documents/upload` |
| 2 | Create Baseline | `POST /api/v1/baselines` | `/documents/upload` (after upload) |
| 3 | Generate Draft Timeline | `POST /api/v1/timelines/draft/generate` | `/timelines/draft` |
| 4 | Commit Timeline | `POST /api/v1/timelines/draft/{id}/commit` | `/timelines/draft/{id}` |
| 5 | Track Progress | `POST /api/v1/progress/milestones/{id}/complete` | `/progress/timeline/{id}` |
| 6 | Submit PhD Doctor | `POST /api/v1/doctor/submit` | `/assessment` |
| 7 | View Analytics Dashboard | `GET /api/v1/analytics/summary` | `/dashboard` |

### Running the Tests

#### Manual Testing

1. Follow the guide in `frontend/TEST_FLOW_GUIDE.md`
2. Use browser DevTools to verify network requests
3. Check backend state after each step
4. Verify frontend state updates

#### Automated Testing

```bash
# Set database URL
export DATABASE_URL="postgresql://user:password@localhost/dbname"

# Run the test script
python backend/scripts/test_complete_journey.py
```

### Expected Results

After completing all steps:

**Frontend State:**
- `baselineStatus: 'EXISTS'`
- `timelineStatus: 'COMMITTED'`
- `doctorStatus: 'SUBMITTED'`
- `analyticsStatus: 'AVAILABLE'`

**Backend State:**
- Document record exists
- Baseline record exists and linked to document
- DraftTimeline exists (is_active = false)
- CommittedTimeline exists and linked to draft
- ProgressEvent records exist for completed milestones
- QuestionnaireDraft exists (is_submitted = true)
- JourneyAssessment exists with scores
- AnalyticsSnapshot exists with summary

### Key Validations

1. **Invariant Checks**: Each step verifies required prerequisites
2. **State Updates**: Global state updated only from API responses
3. **Data Consistency**: All records properly linked
4. **No Calculations**: Frontend displays backend-calculated data only
5. **Error Handling**: Backend error messages displayed correctly

### Troubleshooting

See `frontend/TEST_FLOW_GUIDE.md` for detailed troubleshooting steps for each test step.

### Notes

- Each step depends on the previous step completing successfully
- Invariant checks prevent invalid operations
- All calculations are performed by backend
- Error messages come from backend (no frontend guessing)
