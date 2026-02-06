# Frontend Screen Wiring Progress

## Status: Document Upload Complete ✅

### ✅ Screen 1: Document Upload

**File:** `Frontend/src/pages/ResearchTimeline.tsx`  
**Endpoint:** `POST /api/v1/documents/upload`  
**Service:** `Frontend/src/services/document.service.ts`  
**Backend Endpoint:** `backend/app/api/v1/endpoints/documents.py` (created)

**Changes Made:**
1. ✅ Created `document.service.ts` with `uploadDocument()` function
2. ✅ Created backend endpoint `documents.py` with `/upload` route
3. ✅ Updated `ResearchTimeline.tsx` to:
   - Call `uploadDocument()` instead of mock setTimeout
   - Wait for backend response (no optimistic success)
   - Store `uploadedDocumentId` for baseline creation
   - Handle errors from backend
   - Show loading state while waiting
4. ✅ Created `devHelpers.ts` for user ID (temporary - replace with auth context)

**Behavior:**
- User selects file → UI shows loading
- Frontend calls `POST /api/v1/documents/upload` with FormData
- UI waits for backend response
- On success: stores `document_id`, shows success toast
- On error: shows error toast, resets file input
- No optimistic success - UI only updates after backend confirms

**Next:** Wire Baseline Creation screen
