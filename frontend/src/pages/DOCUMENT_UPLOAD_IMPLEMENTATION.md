# Document Upload Page Implementation

## Overview

The document upload page allows users to upload documents and create baselines. It follows a strict flow with no optimistic UI - all state updates happen after API responses.

## Behavior Flow

1. **User uploads document** → File is validated and uploaded via API
2. **User fills baseline form** → Required fields: program name, institution, field of study, start date
3. **Submit form** → Two sequential API calls:
   - `POST /api/v1/documents/upload` - Upload document
   - `POST /api/v1/baselines` - Create baseline
4. **On success**:
   - Update global state: `setBaselineStatus('EXISTS')`
   - Navigate to appropriate screen based on updated state
5. **On error**: Show error message, don't update state

## Key Features

✅ **No optimistic UI** - Waits for actual API responses  
✅ **State updates from API** - Only updates state after successful API call  
✅ **State-based navigation** - Uses `getRouteFromState()` to determine next screen  
✅ **Error handling** - Shows errors without updating state  
✅ **Progress tracking** - Shows upload progress during file upload  

## Code Structure

```typescript
// 1. Upload document (wait for response)
const { documentId } = await documentService.upload(...);

// 2. Create baseline (wait for response)
const result = await baselineService.create({...});

// 3. Update global state (only after success)
setBaselineStatus('EXISTS');

// 4. Navigate based on state
const state = useGlobalStateStore.getState();
const validRoute = getRouteFromState(state);
navigate(validRoute, { replace: true });
```

## State Updates

The page updates global state **only** after successful API responses:

- `baselineStatus: 'NONE'` → `'EXISTS'` (after baseline creation succeeds)

## Navigation

After successful baseline creation, the page navigates to the appropriate screen based on current state:

- If `baselineStatus === 'EXISTS'` and `timelineStatus === 'NONE'` → `/timelines` (timeline generation)
- Otherwise → Route determined by state-to-screen mapping

## Error Handling

- Errors are caught and displayed
- State is **not** updated on error
- User can retry the operation

## Form Validation

Required fields:
- File (PDF or DOCX)
- Program Name
- Institution
- Field of Study
- Start Date

Optional fields:
- Description
- Document Type
- Expected End Date
- Research Area

## API Calls

1. **Document Upload**
   - Endpoint: `POST /api/v1/documents/upload`
   - Service: `documentService.upload()`
   - Returns: `{ documentId: string }`

2. **Baseline Creation**
   - Endpoint: `POST /api/v1/baselines`
   - Service: `baselineService.create()`
   - Request: `CreateBaselineRequest`
   - Returns: `{ baselineId: string }`

## Example Usage

```typescript
// User fills form and submits
handleSubmit() {
  // 1. Upload document (no optimistic UI)
  const { documentId } = await documentService.upload(file, ...);
  
  // 2. Create baseline (no optimistic UI)
  await baselineService.create({ documentId, ... });
  
  // 3. Update state (only after success)
  setBaselineStatus('EXISTS');
  
  // 4. Navigate based on state
  navigate(getRouteFromState(state));
}
```

## Notes

- No optimistic UI - all updates wait for API responses
- State updates only on success
- Navigation uses state-to-screen mapping
- Errors don't update state
