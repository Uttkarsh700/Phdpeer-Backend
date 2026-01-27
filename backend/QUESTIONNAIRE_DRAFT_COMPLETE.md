# Questionnaire Draft System - Complete Implementation

## Overview

The Questionnaire Draft System enables **section-by-section saving**, **resumable drafts**, and **version management** for PhD Doctor questionnaires. **No scoring before submission** - drafts only store responses.

## Core Capabilities

✅ **Section-by-section saving** - Save progress incrementally  
✅ **Resumable drafts** - Users can return and continue  
✅ **Version management** - Track questionnaire schema versions  
✅ **Progress tracking** - Calculate completion percentage  
✅ **Multi-draft support** - Users can have multiple drafts  
✅ **Submission tracking** - Mark drafts as submitted  
✅ **No premature scoring** - Scoring only happens on submission  

## Key Features

### Draft Management
- Create new drafts
- Save responses section-by-section
- Resume drafts anytime
- Delete unsubmitted drafts
- Mark as submitted (immutable after)

### Version Management
- Multiple questionnaire versions
- Active version detection
- Deprecation support
- Schema storage in JSONB

### Progress Tracking
- Automatic progress calculation
- Section completion tracking
- Last edited section tracking

## Database Models

### QuestionnaireDraft

```python
class QuestionnaireDraft(Base, BaseModel):
    """
    Store incomplete questionnaire responses.
    """
    user_id: UUID                      # Owner
    questionnaire_version_id: UUID     # Which version
    draft_name: str                    # User-friendly name
    responses_json: JSONB              # {section_id: {question_id: value}}
    completed_sections: JSONB          # [section_id, ...]
    progress_percentage: int           # 0-100
    is_submitted: bool                 # Immutable after True
    submission_id: UUID                # JourneyAssessment reference
    last_section_edited: str           # For quick resume
    metadata_json: JSONB               # Device, browser, etc.
```

### QuestionnaireVersion

```python
class QuestionnaireVersion(Base, BaseModel):
    """
    Track questionnaire schema versions.
    """
    version_number: str                # e.g., "1.0", "1.1", "2.0"
    title: str                         # Version title
    description: str                   # Description of changes
    schema_json: JSONB                 # Complete questionnaire schema
    is_active: bool                    # Currently active version
    is_deprecated: bool                # No longer recommended
    total_questions: int               # Total question count
    total_sections: int                # Total section count
    release_notes: str                 # Version notes
```

## Service API

### QuestionnaireDraftService

#### 1. create_draft()

Create a new draft for a user.

```python
def create_draft(
    self,
    user_id: UUID,
    questionnaire_version_id: Optional[UUID] = None,  # Defaults to active
    draft_name: Optional[str] = None,                 # Auto-generated if None
    metadata: Optional[Dict[str, Any]] = None         # Device info, etc.
) -> UUID  # Returns draft ID
```

**Example:**
```python
from app.services.questionnaire_draft_service import QuestionnaireDraftService

service = QuestionnaireDraftService(db)

draft_id = service.create_draft(
    user_id=user.id,
    draft_name="My PhD Assessment",
    metadata={"device": "mobile", "browser": "Chrome"}
)

print(f"Draft created: {draft_id}")
```

#### 2. save_section()

Save responses for a specific section.

```python
def save_section(
    self,
    draft_id: UUID,
    user_id: UUID,
    section_id: str,
    responses: Dict[str, Any],           # {question_id: response_value}
    is_section_complete: bool = False    # Mark section as complete
) -> Dict[str, Any]  # Returns updated draft summary
```

**Example:**
```python
# Save research progress section
result = service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="research_progress",
    responses={
        "rp_1": 4,  # Question 1: 4 out of 5
        "rp_2": 3   # Question 2: 3 out of 5
    },
    is_section_complete=True
)

print(f"Progress: {result['progress_percentage']}%")
print(f"Completed sections: {result['completed_sections']}")
```

**Incremental Saving:**
```python
# Save first question
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="research_progress",
    responses={"rp_1": 4}
)

# Later, save second question
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="research_progress",
    responses={"rp_2": 3},
    is_section_complete=True
)
```

#### 3. get_draft()

Retrieve a draft by ID.

```python
def get_draft(
    self,
    draft_id: UUID,
    user_id: UUID  # For ownership verification
) -> Optional[Dict[str, Any]]
```

**Returns:**
```python
{
    "id": "uuid",
    "user_id": "uuid",
    "questionnaire_version_id": "uuid",
    "questionnaire_version_number": "1.0",
    "draft_name": "My PhD Assessment",
    "responses": {
        "research_progress": {
            "rp_1": 4,
            "rp_2": 3
        },
        "wellbeing": {
            "wb_1": 5
        }
    },
    "completed_sections": ["research_progress"],
    "progress_percentage": 60,
    "is_submitted": false,
    "submission_id": null,
    "last_section_edited": "wellbeing",
    "metadata": {},
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T11:45:00"
}
```

**Example:**
```python
draft = service.get_draft(draft_id, user.id)

if draft:
    print(f"Draft: {draft['draft_name']}")
    print(f"Progress: {draft['progress_percentage']}%")
    print(f"Last edited: {draft['last_section_edited']}")
    
    # Resume from last section
    last_section = draft['last_section_edited']
    previous_responses = draft['responses'].get(last_section, {})
```

#### 4. get_user_drafts()

Get all drafts for a user.

```python
def get_user_drafts(
    self,
    user_id: UUID,
    include_submitted: bool = False,  # Include submitted drafts
    limit: int = 10                   # Max number to return
) -> List[Dict[str, Any]]
```

**Example:**
```python
# Get active drafts only
drafts = service.get_user_drafts(user.id)

for draft in drafts:
    print(f"{draft['draft_name']}: {draft['progress_percentage']}% complete")
    print(f"  Last updated: {draft['updated_at']}")
    print(f"  Version: {draft['questionnaire_version_number']}")

# Get all drafts including submitted
all_drafts = service.get_user_drafts(user.id, include_submitted=True)
```

#### 5. delete_draft()

Delete an unsubmitted draft.

```python
def delete_draft(
    self,
    draft_id: UUID,
    user_id: UUID
) -> bool  # True if deleted, False if not found
```

**Example:**
```python
success = service.delete_draft(draft_id, user.id)

if success:
    print("Draft deleted")
else:
    print("Draft not found")
```

**Error Handling:**
```python
from app.services.questionnaire_draft_service import QuestionnaireDraftError

try:
    service.delete_draft(draft_id, user.id)
except QuestionnaireDraftError as e:
    if "Cannot delete submitted draft" in str(e):
        print("Cannot delete submitted draft")
```

#### 6. mark_as_submitted()

Mark a draft as submitted (immutable after this).

```python
def mark_as_submitted(
    self,
    draft_id: UUID,
    user_id: UUID,
    submission_id: UUID  # JourneyAssessment ID
) -> Dict[str, Any]  # Returns updated draft
```

**Example:**
```python
# After creating JourneyAssessment
submission_id = orchestrator.submit_questionnaire(...)

# Mark draft as submitted
result = service.mark_as_submitted(
    draft_id=draft_id,
    user_id=user.id,
    submission_id=submission_id
)

assert result['is_submitted'] is True
assert result['submission_id'] == str(submission_id)
```

## Version Management API

#### 1. create_version()

Create a new questionnaire version.

```python
def create_version(
    self,
    version_number: str,               # e.g., "1.0", "1.1", "2.0"
    title: str,
    schema: Dict[str, Any],            # Complete questionnaire schema
    description: Optional[str] = None,
    release_notes: Optional[str] = None,
    is_active: bool = True
) -> UUID  # Returns version ID
```

**Schema Format:**
```python
schema = {
    "sections": [
        {
            "id": "research_progress",
            "title": "Research Progress",
            "description": "How is your research progressing?",
            "questions": [
                {
                    "id": "rp_1",
                    "text": "How satisfied are you with your research progress?",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5,
                    "dimension": "research_progress"
                },
                {
                    "id": "rp_2",
                    "text": "Are you meeting your research milestones?",
                    "type": "scale",
                    "scale_min": 1,
                    "scale_max": 5,
                    "dimension": "research_progress"
                }
            ]
        },
        {
            "id": "wellbeing",
            "title": "Mental Well-being",
            "questions": [...]
        }
    ]
}
```

**Example:**
```python
version_id = service.create_version(
    version_number="1.0",
    title="PhD Journey Assessment v1.0",
    schema=schema,
    description="Initial version of the assessment",
    release_notes="First release with 8 dimensions and 27 questions",
    is_active=True
)
```

#### 2. get_active_version()

Get the currently active questionnaire version.

```python
def get_active_version(self) -> Optional[QuestionnaireVersion]
```

**Example:**
```python
active_version = service.get_active_version()

if active_version:
    print(f"Active version: {active_version.version_number}")
    print(f"Total questions: {active_version.total_questions}")
    schema = active_version.schema_json
```

#### 3. get_version()

Get a specific version by ID.

```python
def get_version(self, version_id: UUID) -> Optional[QuestionnaireVersion]
```

#### 4. get_all_versions()

Get all versions.

```python
def get_all_versions(
    self,
    include_deprecated: bool = False
) -> List[QuestionnaireVersion]
```

**Example:**
```python
versions = service.get_all_versions()

for version in versions:
    status = "ACTIVE" if version.is_active else "INACTIVE"
    print(f"{version.version_number} - {version.title} [{status}]")
```

#### 5. deprecate_version()

Mark a version as deprecated.

```python
def deprecate_version(self, version_id: UUID) -> bool
```

**Example:**
```python
# Deprecate old version
service.deprecate_version(old_version_id)

# Create new version
new_version_id = service.create_version(
    version_number="2.0",
    title="PhD Journey Assessment v2.0",
    schema=new_schema,
    is_active=True
)
```

## Complete Workflow Examples

### Example 1: Create and Save Draft

```python
from app.services.questionnaire_draft_service import QuestionnaireDraftService

service = QuestionnaireDraftService(db)

# Step 1: Create draft
draft_id = service.create_draft(
    user_id=user.id,
    draft_name="January 2024 Assessment"
)

# Step 2: User fills out first section
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="research_progress",
    responses={
        "rp_1": 4,
        "rp_2": 3,
        "rp_3": 5
    },
    is_section_complete=True
)

# Step 3: User takes a break, closes browser

# Step 4: User returns later, resumes draft
draft = service.get_draft(draft_id, user.id)
print(f"Welcome back! You're {draft['progress_percentage']}% complete")
print(f"Last section: {draft['last_section_edited']}")

# Step 5: User continues with next section
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id="wellbeing",
    responses={
        "wb_1": 4,
        "wb_2": 3
    },
    is_section_complete=True
)

# Step 6: User completes all sections
draft = service.get_draft(draft_id, user.id)
if draft['progress_percentage'] == 100:
    print("Questionnaire complete! Ready to submit.")
```

### Example 2: Incremental Section Saving

```python
# User answers one question at a time
section_id = "research_progress"

# Save first question
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id=section_id,
    responses={"rp_1": 4}
)

# User takes a break

# User returns, answers second question
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id=section_id,
    responses={"rp_2": 3}
)

# User finishes section
service.save_section(
    draft_id=draft_id,
    user_id=user.id,
    section_id=section_id,
    responses={"rp_3": 5},
    is_section_complete=True
)

# All responses for this section are now saved
draft = service.get_draft(draft_id, user.id)
assert "research_progress" in draft['completed_sections']
```

### Example 3: Multiple Drafts

```python
# User creates multiple drafts (e.g., comparing different time periods)

# Draft 1: Current assessment
draft1_id = service.create_draft(
    user_id=user.id,
    draft_name="January 2024 - Current State"
)

# Draft 2: Retrospective assessment
draft2_id = service.create_draft(
    user_id=user.id,
    draft_name="Year 2 Retrospective"
)

# Fill out both drafts independently
service.save_section(draft1_id, user.id, "research_progress", {...})
service.save_section(draft2_id, user.id, "research_progress", {...})

# List all drafts
drafts = service.get_user_drafts(user.id)
for draft in drafts:
    print(f"{draft['draft_name']}: {draft['progress_percentage']}%")
```

### Example 4: Resume from Last Section

```python
# Get draft
draft = service.get_draft(draft_id, user.id)

# Resume from last edited section
last_section = draft['last_section_edited']

if last_section:
    # Get previous responses for this section
    section_responses = draft['responses'].get(last_section, {})
    
    # Pre-fill form with saved responses
    print(f"Resuming section: {last_section}")
    print(f"Previous responses: {section_responses}")
    
    # User continues editing
    updated_responses = {**section_responses, "new_question": 4}
    service.save_section(
        draft_id=draft_id,
        user_id=user.id,
        section_id=last_section,
        responses=updated_responses
    )
```

### Example 5: Submit Draft

```python
# User completes questionnaire
draft = service.get_draft(draft_id, user.id)

if draft['progress_percentage'] < 100:
    print(f"Please complete remaining {100 - draft['progress_percentage']}%")
else:
    # Convert draft responses to submission format
    responses = []
    for section_id, section_responses in draft['responses'].items():
        for question_id, value in section_responses.items():
            responses.append({
                "dimension": get_dimension_for_question(question_id),
                "question_id": question_id,
                "response_value": value
            })
    
    # Submit to orchestrator
    from app.orchestrators.phd_doctor_orchestrator import PhDDoctorOrchestrator
    orchestrator = PhDDoctorOrchestrator(db)
    
    submission_result = orchestrator.submit_questionnaire(
        user_id=user.id,
        responses=responses
    )
    
    # Mark draft as submitted
    service.mark_as_submitted(
        draft_id=draft_id,
        user_id=user.id,
        submission_id=submission_result['assessment_id']
    )
    
    print("Questionnaire submitted!")
    print(f"Assessment ID: {submission_result['assessment_id']}")
```

### Example 6: Version Migration

```python
# Create new version with updated questions
new_schema = {
    "sections": [
        # Updated sections with new questions
    ]
}

new_version_id = service.create_version(
    version_number="2.0",
    title="PhD Journey Assessment v2.0",
    schema=new_schema,
    description="Added work-life balance dimension",
    release_notes="New questions about work-life balance and time management",
    is_active=True
)

# Existing drafts continue using their original version
old_draft = service.get_draft(old_draft_id, user.id)
print(f"Old draft uses version: {old_draft['questionnaire_version_number']}")

# New drafts use the new version
new_draft_id = service.create_draft(user_id=user.id)
new_draft = service.get_draft(new_draft_id, user.id)
print(f"New draft uses version: {new_draft['questionnaire_version_number']}")
```

## Progress Calculation

Progress is calculated automatically based on answered questions:

```python
progress_percentage = (answered_questions / total_questions) * 100
```

**Rules:**
- Empty responses (`None` or `""`) are not counted
- Progress updates on every `save_section()` call
- Progress is stored in database (no recalculation needed)

**Example:**
```
Total questions: 20
Section 1 (5 questions): 3 answered → 15% progress
Section 2 (5 questions): 5 answered → 40% progress
Section 3 (10 questions): 7 answered → 75% progress
```

## Immutability Rules

✅ **Before submission:**
- Drafts can be edited freely
- Sections can be saved multiple times
- Drafts can be deleted

❌ **After submission:**
- `is_submitted = True`
- Cannot edit responses
- Cannot delete draft
- Cannot mark as submitted again

**Enforcement:**
```python
if draft.is_submitted:
    raise QuestionnaireDraftError("Cannot edit submitted draft")
```

## Error Handling

```python
from app.services.questionnaire_draft_service import (
    QuestionnaireDraftError,
    QuestionnaireVersionError
)

try:
    service.save_section(draft_id, user_id, section_id, responses)
except QuestionnaireDraftError as e:
    if "not found or not owned" in str(e):
        print("Draft not found or access denied")
    elif "Cannot edit submitted draft" in str(e):
        print("This draft has already been submitted")
    else:
        print(f"Error: {e}")
```

## Testing

Run comprehensive tests:
```bash
cd backend
pytest tests/test_questionnaire_draft_service.py -v
```

**Test Coverage:**
- ✅ Draft creation
- ✅ Section-by-section saving
- ✅ Incremental saving
- ✅ Multiple sections
- ✅ Progress calculation
- ✅ Draft retrieval
- ✅ User drafts listing
- ✅ Draft deletion
- ✅ Submission marking
- ✅ Version management
- ✅ Version deprecation
- ✅ Ownership verification
- ✅ Immutability enforcement

## Integration with Frontend

### TypeScript Interfaces

```typescript
interface QuestionnaireDraft {
  id: string;
  draft_name: string;
  responses: Record<string, Record<string, any>>;
  completed_sections: string[];
  progress_percentage: number;
  is_submitted: boolean;
  last_section_edited: string;
  created_at: string;
  updated_at: string;
}

interface SaveSectionRequest {
  section_id: string;
  responses: Record<string, any>;
  is_section_complete: boolean;
}
```

### API Service

```typescript
// services/questionnaireDraftService.ts

export async function createDraft(
  draftName?: string
): Promise<string> {
  const response = await api.post('/drafts', { draft_name: draftName });
  return response.data.draft_id;
}

export async function saveSection(
  draftId: string,
  sectionId: string,
  responses: Record<string, any>,
  isComplete: boolean
): Promise<QuestionnaireDraft> {
  const response = await api.post(`/drafts/${draftId}/sections/${sectionId}`, {
    responses,
    is_section_complete: isComplete
  });
  return response.data;
}

export async function getDraft(
  draftId: string
): Promise<QuestionnaireDraft> {
  const response = await api.get(`/drafts/${draftId}`);
  return response.data;
}

export async function getUserDrafts(): Promise<QuestionnaireDraft[]> {
  const response = await api.get('/drafts');
  return response.data;
}
```

## Key Principles

✅ **No premature scoring** - Drafts only store responses  
✅ **Section-by-section** - Save progress incrementally  
✅ **Resumable** - Users can return anytime  
✅ **Versioned** - Support questionnaire evolution  
✅ **Immutable after submission** - Data integrity  
✅ **Progress tracking** - Visual feedback  

## Summary

The Questionnaire Draft System provides a **complete, production-ready solution** for managing PhD Doctor assessments with:

- ✅ Section-by-section saving
- ✅ Resumable drafts
- ✅ Version management
- ✅ Progress tracking
- ✅ Multi-draft support
- ✅ Submission tracking
- ✅ Comprehensive test coverage
- ✅ Full documentation

**No scoring before submission. Pure draft management.** 📝
