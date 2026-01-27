## Validation, Error Handling & Guardrails Guide

Comprehensive validation and error handling across all application flows to prevent invalid state transitions.

---

## Overview

This guide documents all validation rules, error handling patterns, and guardrails implemented to ensure data integrity and prevent invalid states.

**Key Principles:**
1. **Validate Early**: Client-side validation before API calls
2. **Clear Feedback**: User-friendly error messages
3. **Prevent Invalid States**: Guardrails at every transition
4. **Fail Safely**: Graceful degradation when errors occur
5. **Log for Debugging**: Comprehensive error logging

---

## Validation Utilities

**File:** `src/utils/validation.ts`

### Date Validation

```typescript
import { isValidDate, isDateAfter, isFutureDate, isPastDate } from '@/utils/validation';

// Check if date string is valid
isValidDate('2024-01-15'); // true
isValidDate('invalid'); // false

// Check date relationships
isDateAfter('2024-12-31', '2024-01-01'); // true

// Check relative to now
isFutureDate('2025-01-01'); // true
isPastDate('2023-01-01'); // true
```

### String Validation

```typescript
import { isNonEmptyString, hasMinLength, hasMaxLength } from '@/utils/validation';

isNonEmptyString('  '); // false
hasMinLength('hello', 3); // true
hasMaxLength('hello', 10); // true
```

### File Validation

```typescript
import { 
  isValidFileType, 
  isValidFileSize, 
  ALLOWED_DOCUMENT_TYPES, 
  MAX_FILE_SIZE 
} from '@/utils/validation';

const file = /* File object */;

isValidFileType(file, ALLOWED_DOCUMENT_TYPES); // PDF/DOCX only
isValidFileSize(file, MAX_FILE_SIZE); // Max 50MB
```

---

## Error Handling Utilities

**File:** `src/utils/errorHandling.ts`

### Get User-Friendly Messages

```typescript
import { getErrorMessage, extractErrorDetails } from '@/utils/errorHandling';

try {
  await api.call();
} catch (err) {
  const message = getErrorMessage(err);
  // Returns: "Unable to connect to the server. Please check your connection."
  
  const { title, message, details } = extractErrorDetails(err);
  // Returns structured error info
}
```

### Error Type Detection

```typescript
import {
  isNetworkError,
  isAuthError,
  isValidationError,
  isConflictError,
  isRateLimitError,
} from '@/utils/errorHandling';

if (isNetworkError(err)) {
  // Show retry option
}

if (isConflictError(err)) {
  // Handle duplicate/conflict
}
```

### Retry Logic

```typescript
import { shouldRetry, getRetryDelay } from '@/utils/errorHandling';

let attempts = 0;
while (attempts < 3) {
  try {
    await apiCall();
    break;
  } catch (err) {
    if (shouldRetry(err, attempts)) {
      await new Promise(resolve => setTimeout(resolve, getRetryDelay(attempts)));
      attempts++;
    } else {
      throw err;
    }
  }
}
```

---

## Component Integration

### ValidationMessage Component

```tsx
import { ValidationMessage } from '@/components/ValidationMessage';

<ValidationMessage
  errors={['Field is required', 'Must be at least 3 characters']}
  warnings={['This action cannot be undone']}
/>
```

### ConfirmDialog Component

```tsx
import { ConfirmDialog } from '@/components/ConfirmDialog';

<ConfirmDialog
  isOpen={showDialog}
  title="Commit Timeline"
  message="This will create an immutable version. Continue?"
  confirmText="Commit"
  confirmVariant="primary"
  onConfirm={handleCommit}
  onCancel={() => setShowDialog(false)}
  loading={committing}
/>
```

### ErrorBoundary Component

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

<ErrorBoundary>
  <App />
</ErrorBoundary>
```

---

## Flow-Specific Validation

### 1. Baseline Creation

**Validation Rules:**

```typescript
import { validateBaselineCreation } from '@/utils/validation';

const result = validateBaselineCreation({
  programName: 'PhD in Computer Science',
  institution: 'Stanford University',
  fieldOfStudy: 'Machine Learning',
  startDate: '2024-01-15',
  expectedEndDate: '2027-12-31',
});

// result.isValid: boolean
// result.errors: string[]
```

**Rules:**
- ✅ **Program name**: Required, 3-200 characters
- ✅ **Institution**: Required, min 2 characters
- ✅ **Field of study**: Required, min 2 characters
- ✅ **Start date**: Required, valid date, not in future
- ✅ **End date**: Optional, must be after start date if provided
- ✅ **Document ID**: Optional, must be valid UUID

**Guardrails:**
1. Cannot create baseline with future start date
2. End date must be after start date
3. All required fields must be non-empty
4. Field lengths validated
5. Date format validation

**Error States:**
- Invalid date format → "Start date is invalid"
- Future start date → "Start date cannot be in the future"
- End before start → "Expected end date must be after start date"
- Missing fields → "Program name is required"

---

### 2. Document Upload

**Validation Rules:**

```typescript
import { validateDocumentUpload } from '@/utils/validation';

const result = validateDocumentUpload(file, title);
```

**Rules:**
- ✅ **File**: Required, not null
- ✅ **File type**: PDF or DOCX only
- ✅ **File size**: Max 50MB
- ✅ **Title**: Required, min 3 characters

**Guardrails:**
1. File type restricted to PDF/DOCX
2. File size limit enforced
3. Title validated before upload
4. Upload progress tracked
5. Cancellation supported

**Error States:**
- No file selected → "Please select a file to upload"
- Wrong type → "File must be PDF or DOCX format"
- Too large → "File size must be less than 50MB"
- No title → "Document title is required"

**Implementation Example:**

```tsx
const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
  const selectedFile = e.target.files?.[0];
  
  if (selectedFile) {
    const validTypes = ALLOWED_DOCUMENT_TYPES;
    if (!validTypes.includes(selectedFile.type)) {
      setError('Please select a PDF or DOCX file');
      setFile(null);
      return;
    }
    
    if (!isValidFileSize(selectedFile, MAX_FILE_SIZE)) {
      setError('File size must be less than 50MB');
      setFile(null);
      return;
    }
    
    setFile(selectedFile);
    setError(null);
  }
};
```

---

### 3. Timeline Generation

**Validation Rules:**

**Rules:**
- ✅ **Baseline**: Must exist and be valid
- ✅ **Title**: Required, min 3 characters
- ✅ **User ownership**: Verified
- ✅ **No duplicate active drafts**: Enforced by backend

**Guardrails:**
1. Cannot generate timeline without baseline
2. Cannot generate timeline from non-existent baseline
3. Baseline must have complete data
4. User must own the baseline
5. Only one active draft per baseline (backend enforced)

**Error States:**
- Missing baseline → "Baseline not found"
- Invalid baseline ID → "Invalid baseline ID format"
- Ownership mismatch → "You don't have permission"
- Duplicate draft → "An active draft timeline already exists"

---

### 4. Timeline Commit

**Validation Rules:**

```typescript
import { validateTimelineCommit } from '@/utils/validation';

const result = validateTimelineCommit({
  title: 'PhD Timeline v1.0',
  hasMilestones: true,
  hasStages: true,
});
```

**Rules:**
- ✅ **Title**: Required, min 3 characters
- ✅ **Stages**: Must have at least one
- ✅ **Milestones**: Must have at least one
- ✅ **User ownership**: Verified
- ✅ **No double commit**: Enforced

**Guardrails:**
1. Cannot commit empty timeline
2. Cannot commit without stages
3. Cannot commit without milestones
4. Cannot commit twice (immutability)
5. User must own draft timeline
6. Version number auto-incremented

**State Transitions:**
```
DRAFT (editable)
  ↓ commit()
COMMITTED (immutable)
  ✗ Cannot edit
  ✗ Cannot delete
  ✗ Cannot uncommit
```

**Prevention Logic:**

```typescript
// Check if already committed
const isCommitted = await timelineService.isCommitted(draftTimelineId);
if (isCommitted.isCommitted) {
  throw new Error('Timeline already committed');
}

// Validate completeness
if (stages.length === 0) {
  throw new Error('Cannot commit an empty timeline');
}
```

**Error States:**
- Already committed → "This timeline has already been committed"
- No stages → "Timeline must have at least one stage"
- No milestones → "Timeline must have at least one milestone"
- Invalid title → "Timeline title must be at least 3 characters"

---

### 5. Progress Tracking

**Validation Rules:**

```typescript
import { validateMilestoneCompletion } from '@/utils/validation';

const result = validateMilestoneCompletion({
  completionDate: '2024-01-15',
  targetDate: '2024-01-20',
});
```

**Rules:**
- ✅ **Completion date**: Required, valid date
- ✅ **Not future**: Cannot complete in future
- ✅ **Milestone exists**: Must be valid milestone
- ✅ **Belongs to committed timeline**: Verified
- ✅ **User ownership**: Checked

**Guardrails:**
1. Cannot mark milestone complete in future
2. Cannot mark non-existent milestone
3. Can only mark milestones from user's timelines
4. Completion date must be valid
5. Can complete early (before target)
6. Can complete late (after target)

**State Transitions:**
```
PENDING
  ↓ mark_complete()
COMPLETED (with date)
  ✓ Can view completion date
  ✓ Delay calculated if late
```

**Error States:**
- Future completion → "Completion date cannot be in the future"
- Invalid date → "Completion date is invalid"
- Not found → "Milestone not found"
- Wrong owner → "You don't have permission"

---

### 6. PhD Doctor Assessment

**Validation Rules:**

```typescript
import { 
  validateAssessmentResponse, 
  validateAssessmentCompletion 
} from '@/utils/validation';

// Validate single response
validateAssessmentResponse(4); // true (1-5 range)
validateAssessmentResponse(6); // false

// Validate complete assessment
const result = validateAssessmentCompletion(
  responsesMap,
  requiredQuestions
);
```

**Rules:**
- ✅ **All questions**: Must answer all 27 questions
- ✅ **Valid range**: Each response 1-5
- ✅ **No duplicates**: Can't submit twice in short time
- ✅ **Valid dimensions**: All 8 dimensions covered

**Guardrails:**
1. Cannot submit incomplete assessment
2. Response values must be 1-5
3. All dimensions must have responses
4. Rate limiting prevents rapid submissions
5. Draft auto-saved to localStorage
6. Draft cleared after successful submission

**State Transitions:**
```
DRAFT (in progress)
  ↓ save_progress()
DRAFT (saved)
  ↓ resume
DRAFT (continue)
  ↓ submit() (all answered)
SUBMITTED (complete)
  ✗ Cannot edit
  ✓ Can view results
```

**Validation Flow:**

```typescript
// Before submit
const unanswered = requiredQuestions.filter(q => !responses.has(q));
if (unanswered.length > 0) {
  setError(`${unanswered.length} question(s) not answered`);
  return;
}

// Validate each response
for (const [questionId, value] of responses.entries()) {
  if (!validateAssessmentResponse(value)) {
    setError(`Invalid response value: ${value}`);
    return;
  }
}

// Submit
await assessmentService.submitQuestionnaire({...});

// Clear draft
localStorage.removeItem('phd_doctor_draft');
```

**Error States:**
- Incomplete → "Please answer all questions before submitting"
- Invalid value → "Invalid response value for question"
- Too soon → "You recently completed an assessment"
- Network error → "Unable to submit. Your progress is saved."

---

## Invalid State Prevention

### State Transition Matrix

| From State | To State | Allowed? | Validation |
|------------|----------|----------|------------|
| No Baseline | Create Baseline | ✅ | All fields valid |
| Baseline | Delete Baseline | ✅ | No dependent timelines |
| Baseline | Create Draft Timeline | ✅ | Baseline complete |
| Draft Timeline | Edit Draft | ✅ | User owns it |
| Draft Timeline | Commit | ✅ | Has stages + milestones |
| Draft Timeline | Delete | ✅ | Not yet committed |
| Committed Timeline | Edit | ❌ | **Immutable** |
| Committed Timeline | Delete | ❌ | **Immutable** |
| Committed Timeline | Uncommit | ❌ | **Immutable** |
| Committed Timeline | Create New Version | ✅ | From draft |
| Milestone (Pending) | Mark Complete | ✅ | Date not future |
| Milestone (Completed) | Unmark | ❌ | **Final state** |
| Assessment (Draft) | Save Progress | ✅ | Anytime |
| Assessment (Draft) | Submit | ✅ | All answered |
| Assessment (Submitted) | Edit | ❌ | **Immutable** |
| Assessment (Submitted) | Delete | ❌ | **Audit trail** |

### Immutability Enforcement

**Committed Timeline:**
```typescript
// Frontend guard
if (timeline.status === 'COMMITTED') {
  // Hide edit buttons
  // Show read-only message
  // Prevent navigation to edit view
}

// Backend enforcement (example)
def update_committed_timeline(timeline_id):
    timeline = get_timeline(timeline_id)
    if timeline.is_committed:
        raise ImmutableError("Cannot modify committed timeline")
```

**Assessment:**
```typescript
// Clear draft after submit
localStorage.removeItem('phd_doctor_draft');

// Backend ensures one submission per session
```

---

## Error Message Standards

### Format

```
[SEVERITY] [CONTEXT]: [USER_MESSAGE]
```

**Examples:**
- ✅ Good: "Start date cannot be in the future"
- ✅ Good: "Timeline must have at least one stage"
- ❌ Bad: "Invalid input"
- ❌ Bad: "Error 400"

### Severity Levels

1. **Error** (Red) - Action blocked
2. **Warning** (Yellow) - Caution advised
3. **Info** (Blue) - Informational
4. **Success** (Green) - Action completed

### User-Friendly Messages

| Technical Error | User-Friendly Message |
|----------------|----------------------|
| `400 Bad Request` | "Invalid request. Please check your input." |
| `401 Unauthorized` | "You are not authenticated. Please log in." |
| `403 Forbidden` | "You do not have permission for this action." |
| `404 Not Found` | "The requested resource was not found." |
| `409 Conflict` | "This action conflicts with existing data." |
| `422 Validation Error` | "Validation failed. Please check your input." |
| `429 Rate Limit` | "Too many requests. Please wait and try again." |
| `500 Server Error` | "A server error occurred. Please try again later." |
| `Network Error` | "Unable to connect. Please check your connection." |

---

## Testing Validation

### Unit Tests

```typescript
describe('validateBaselineCreation', () => {
  it('should reject empty program name', () => {
    const result = validateBaselineCreation({
      programName: '',
      institution: 'MIT',
      fieldOfStudy: 'CS',
      startDate: '2024-01-01',
    });
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Program name is required');
  });
  
  it('should reject future start date', () => {
    const futureDate = new Date();
    futureDate.setFullYear(futureDate.getFullYear() + 1);
    
    const result = validateBaselineCreation({
      programName: 'PhD in CS',
      institution: 'MIT',
      fieldOfStudy: 'ML',
      startDate: futureDate.toISOString().split('T')[0],
    });
    
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Start date cannot be in the future');
  });
});
```

### Integration Tests

```typescript
describe('Timeline Commit Flow', () => {
  it('should prevent double commit', async () => {
    const { draftTimelineId } = await createDraftTimeline();
    
    // First commit succeeds
    await timelineService.commit({ draftTimelineId });
    
    // Second commit fails
    await expect(
      timelineService.commit({ draftTimelineId })
    ).rejects.toThrow('Timeline already committed');
  });
});
```

---

## Checklist

### Before Deployment

- [ ] All validation functions tested
- [ ] Error messages user-friendly
- [ ] Invalid states prevented
- [ ] Immutability enforced
- [ ] Ownership checks in place
- [ ] Date validations working
- [ ] File upload restrictions enforced
- [ ] Rate limiting configured
- [ ] Error logging enabled
- [ ] User feedback clear

### Code Review

- [ ] Validation at form level
- [ ] API error handling
- [ ] User-friendly messages
- [ ] Loading states shown
- [ ] Success feedback provided
- [ ] Errors logged properly
- [ ] Edge cases handled
- [ ] Accessibility maintained

---

## Best Practices

1. **Validate Early**: Check on client before API call
2. **Validate Thoroughly**: Check on server regardless
3. **Clear Feedback**: Tell user exactly what's wrong
4. **Fail Gracefully**: Don't crash, show error
5. **Log Everything**: Debug production issues
6. **Test Edge Cases**: Empty, null, invalid, extreme
7. **Consistent Patterns**: Same validation style everywhere
8. **Document Rules**: Clear validation requirements
9. **User First**: Error messages for humans, not developers
10. **Prevent, Don't Punish**: Disable invalid actions

---

## Summary

✅ **Validation utilities created**
✅ **Error handling centralized**
✅ **Guardrails at every transition**
✅ **Invalid states prevented**
✅ **User-friendly feedback**
✅ **Comprehensive logging**
✅ **Reusable components**
✅ **Clear documentation**

**Result:** Robust, user-friendly application with comprehensive validation and error handling!
