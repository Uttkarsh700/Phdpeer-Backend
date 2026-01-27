# PhD Doctor Questionnaire UI Guide

Comprehensive journey health assessment system with save/resume functionality, single submission, and clear results display.

## Overview

The PhD Doctor feature helps PhD students assess their wellbeing and progress across 8 key dimensions through a structured questionnaire.

**Key Features:**
- ✅ Save and resume progress
- ✅ Submit once (prevents duplicate submissions)
- ✅ Clear results with actionable recommendations
- ✅ No charts (simple, clean presentation)

---

## Pages

### 1. Health Dashboard (`/health`)

**File:** `HealthDashboardPage.tsx`

Main entry point for health assessments.

**Features:**
- Latest assessment summary (if exists)
- Quick stats (total assessments, good ratings, days since last)
- Assessment history (last 5)
- "Take New Assessment" button
- Welcome screen for first-time users

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ PhD Journey Health                              │
├─────────────────────────────────────────────────┤
│ Latest Assessment                               │
│  [4.2]      [3.8]      [4.5]    Feb 15, 2024   │
│  Overall    Research   Timeline   10:30 AM      │
│                                                  │
│  ✓ Strengths   ⚠ Challenges   → Action Items   │
│  [View Full Report]                             │
├─────────────────────────────────────────────────┤
│ Quick Stats:  5 Assessments | 4 Good+ | 12 Days│
├─────────────────────────────────────────────────┤
│ Assessment History                     [View All]│
│  • Good      Feb 15, 2024  Overall: 4.2   →   │
│  • Fair      Jan 20, 2024  Overall: 3.1   →   │
│  • Excellent Dec 18, 2023  Overall: 4.6   →   │
└─────────────────────────────────────────────────┘
```

**First-Time User:**
```
┌─────────────────────────────────────────────────┐
│             Welcome to PhD Journey Health       │
│                                                  │
│                    📋                           │
│                                                  │
│     Take your first assessment to get          │
│     personalized insights about your journey.  │
│                                                  │
│        [Take Your First Assessment]            │
└─────────────────────────────────────────────────┘
```

---

### 2. Assessment Questionnaire (`/health/assessment`)

**File:** `AssessmentPage.tsx`

Interactive questionnaire with 27 questions across 8 dimensions.

**Features:**
- **Auto-save**: Progress saved to localStorage
- **Resume**: Loads draft on return visit
- **Dimension navigation**: 8 sections with progress dots
- **5-point rating scale**: Simple 1-5 buttons
- **Validation**: All questions required before submission
- **Notes**: Optional comments field at end

**Dimensions:**
1. Research Progress (4 questions)
2. Mental Wellbeing (4 questions)
3. Supervisor Relationship (4 questions)
4. Time Management (3 questions)
5. Work-Life Balance (3 questions)
6. Academic Skills (3 questions)
7. Funding Status (2 questions)
8. Peer Support (3 questions)

**Question Format:**
```
┌─────────────────────────────────────────────────┐
│ How satisfied are you with your research       │
│ progress?                                        │
│ 1 = Very dissatisfied, 5 = Very satisfied      │
│                                                  │
│  [1]  [2]  [3]  [4]  [5]                       │
│  Low              High                          │
└─────────────────────────────────────────────────┘
```

**Progress Bar:**
```
Overall Progress                              74%
[████████████████████████████░░░░░░░░░░░░░]
20 of 27 questions answered
```

**Navigation:**
```
Section 2 of 8: Mental Wellbeing

Progress Dots: ● ● ○ ○ ○ ○ ○ ○
               (completed=green, current=blue, pending=gray)

[← Previous]  [💾 Save Progress]       [Next →]
```

**Last Section:**
```
Additional Comments (Optional)
[Text area for notes...]

[← Previous]  [💾 Save Progress]  [Submit Assessment]
```

---

### 3. Assessment Results (`/health/:assessmentId`)

**File:** `AssessmentDetailPage.tsx`

Detailed results with scores, insights, and recommendations.

**Layout Structure:**
```
┌─────────────────────────────────────────────────┐
│ Assessment Results                              │
│ Completed on Feb 15, 2024 at 10:30 AM         │
├─────────────────────────────────────────────────┤
│ GOOD STATUS                              4.2    │
│ Overall Score: 4.2/5                            │
│ You're making solid progress with some areas   │
│ that could benefit from attention.              │
├─────────────────────────────────────────────────┤
│ Dimensions Overview                             │
│ ┌──────────────┐ ┌──────────────┐             │
│ │Research Prog │ │Mental Wellbg │             │
│ │   4.5/5      │ │   3.8/5      │             │
│ │[████████░]   │ │[██████░░░]   │             │
│ │✓ 2 strengths │ │⚠ 1 concern   │             │
│ └──────────────┘ └──────────────┘             │
├─────────────────────────────────────────────────┤
│ ⚠️ Areas Needing Attention                     │
│ • Mental Wellbeing (3.8/5)                     │
│   - Stress management needs improvement        │
│   - Consider work-life balance adjustments     │
├─────────────────────────────────────────────────┤
│ ✓ Your Strengths                               │
│ • Research Progress (4.5/5)                    │
│   - Clear research objectives                  │
│   - Strong methodology                         │
├─────────────────────────────────────────────────┤
│ 💡 Recommendations                             │
│ 1. Improve Time Management [HIGH PRIORITY]     │
│    Set realistic daily goals and use time      │
│    blocking techniques.                        │
│    → Schedule dedicated research blocks        │
│    → Use Pomodoro technique                    │
│    → Track time spent on tasks                 │
└─────────────────────────────────────────────────┘
```

**Status Colors:**
- 🟢 **Excellent** (4.5-5.0) - Green
- 🔵 **Good** (3.5-4.4) - Blue
- 🟡 **Fair** (2.5-3.4) - Yellow
- 🟠 **Concerning** (1.5-2.4) - Orange
- 🔴 **Critical** (1.0-1.4) - Red

---

## Key Features

### 1. Save and Resume

**Implementation:**
- Progress stored in `localStorage` with key `phd_doctor_draft`
- Auto-loaded on page mount
- Manual save button available
- Saves: responses, notes, current dimension, timestamp

**Draft Structure:**
```json
{
  "responses": {
    "rp1": 4,
    "rp2": 5,
    "mw1": 3
  },
  "notes": "Additional comments...",
  "currentDimension": 2,
  "savedAt": "2024-02-15T10:30:00Z"
}
```

**User Experience:**
```
User starts questionnaire
  ↓
Answers 10 questions
  ↓
Clicks "Save Progress"
  ↓
"Progress saved!" message
  ↓
Closes browser
  ↓
Returns later
  ↓
"Draft loaded. Continue where you left off!"
  ↓
Continues from question 11
```

---

### 2. Submit Once

**Prevention Mechanisms:**

1. **Front-end Validation:**
   - All questions must be answered
   - Submit button disabled until complete
   - Clear error message if incomplete

2. **Post-Submission:**
   - Draft cleared from localStorage
   - Immediate navigation to results page
   - No "back" to questionnaire after submission

3. **Backend Enforcement:**
   - Duplicate submissions prevented by backend
   - One assessment per submission
   - Timestamps tracked

**Submission Flow:**
```
User completes all questions
  ↓
Clicks "Submit Assessment"
  ↓
Validation check (27/27 answered?)
  ↓
API call to submit
  ↓
Backend processes responses
  ↓
Returns assessment summary
  ↓
Clear localStorage draft
  ↓
Navigate to results page
  ↓
Show results with recommendations
```

---

### 3. Clear Results Display

**Result Components:**

**Overall Status Card:**
- Large status badge (Excellent/Good/Fair/Concerning/Critical)
- Overall score (X/5)
- Summary text
- Color-coded background

**Dimension Cards:**
- Score out of 5
- Progress bar (color-coded)
- Status label
- Strength/concern counts

**Critical Areas (Red Section):**
- Low-scoring dimensions
- Specific concerns listed
- Bullet points for clarity

**Strengths (Green Section):**
- High-scoring dimensions
- Specific strengths listed
- Positive reinforcement

**Recommendations:**
- Priority badges (High/Medium/Low)
- Title and description
- Action items (bullet list)
- Related dimension

**No Charts:**
- Simple progress bars only
- Text-based summaries
- Clear numeric scores
- Color-coded status indicators

---

## Questions

### Complete Question Set (27 Total)

#### Research Progress (4)
1. How satisfied are you with your research progress?
2. How clear are your research objectives and methodology?
3. How confident are you about achieving your research goals?
4. How often do you encounter significant research roadblocks?

#### Mental Wellbeing (4)
1. How would you rate your overall mental health?
2. How often do you feel overwhelmed by your PhD work?
3. How well are you managing stress and anxiety?
4. How motivated do you feel about your PhD?

#### Supervisor Relationship (4)
1. How satisfied are you with your supervisor relationship?
2. How often do you receive helpful feedback from your supervisor?
3. How accessible is your supervisor when you need guidance?
4. How clear are expectations from your supervisor?

#### Time Management (3)
1. How well do you manage your time and priorities?
2. How often do you meet your own deadlines?
3. How organized is your research workflow?

#### Work-Life Balance (3)
1. How satisfied are you with your work-life balance?
2. How often do you take time for non-PhD activities?
3. How supported do you feel by family and friends?

#### Academic Skills (3)
1. How confident are you in your research methods and skills?
2. How comfortable are you with academic writing?
3. How prepared do you feel for presenting your research?

#### Funding Status (2)
1. How secure is your current funding situation?
2. How concerned are you about financial matters?

#### Peer Support (3)
1. How connected do you feel with fellow PhD students?
2. How often do you receive support from peers?
3. How integrated do you feel in your academic community?

---

## User Flows

### Flow 1: First-Time Assessment
```
1. Visit /health
   - See welcome message
   - Click "Take Your First Assessment"

2. Start Questionnaire (/health/assessment)
   - See overall progress bar (0%)
   - Start with Research Progress section
   - Answer 4 questions with 1-5 scale

3. Navigate Through Sections
   - Click "Next" to move forward
   - Progress dots show completion
   - Click dots to jump to specific section

4. Save Progress (Optional)
   - Click "Save Progress" button
   - See "Progress saved!" message
   - Can close and resume later

5. Complete All Questions
   - Reach final section (Peer Support)
   - Add optional comments
   - Progress bar shows 100%

6. Submit
   - Click "Submit Assessment"
   - See "Submitting..." loader
   - Auto-navigate to results page

7. View Results (/health/:assessmentId)
   - See overall status and score
   - Review dimensions breakdown
   - Read recommendations
   - Click "Take New Assessment" or "View History"
```

### Flow 2: Resume Draft
```
1. Start questionnaire previously

2. Answer 15/27 questions

3. Click "Save Progress"

4. Close browser

5. Return later to /health/assessment

6. See "Draft loaded" message

7. Resume at Section 6 (where left off)

8. Complete remaining questions

9. Submit

10. View results
```

### Flow 3: View History
```
1. Visit /health

2. See latest assessment summary

3. View assessment history list

4. Click any past assessment

5. View full results for that assessment

6. Compare with current progress
```

---

## API Integration

### Submit Assessment
```typescript
await assessmentService.submitQuestionnaire({
  responses: [
    {
      dimension: 'RESEARCH_PROGRESS',
      questionId: 'rp1',
      responseValue: 4,
      questionText: 'How satisfied are you with...'
    },
    // ... 26 more responses
  ],
  assessmentType: 'self_assessment',
  notes: 'Optional comments'
});

// Returns AssessmentSummary
{
  assessmentId: 'uuid',
  overallScore: 4.2,
  overallStatus: 'good',
  dimensions: { ... },
  recommendations: [ ... ]
}
```

### Get Latest Assessment
```typescript
const latest = await assessmentService.getLatest();
// Returns most recent JourneyAssessment or null
```

### Get Assessment History
```typescript
const history = await assessmentService.getHistory('self_assessment', 10);
// Returns array of up to 10 assessments
```

### Get Assessment Details
```typescript
const assessment = await assessmentService.getById(assessmentId);
// Returns full JourneyAssessment with summary data
```

---

## Design Patterns

### Rating Scale Buttons
```tsx
<div className="flex items-center space-x-2">
  {[1, 2, 3, 4, 5].map((rating) => (
    <button
      onClick={() => handleResponseChange(questionId, rating)}
      className={`flex-1 py-3 px-4 rounded-lg border-2 ${
        value === rating
          ? 'border-blue-600 bg-blue-600 text-white'
          : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
      }`}
    >
      {rating}
    </button>
  ))}
</div>
```

### Progress Dots
```tsx
{DIMENSIONS.map((_, index) => (
  <button
    onClick={() => setCurrentDimension(index)}
    className={`w-3 h-3 rounded-full ${
      index === currentDimension ? 'bg-blue-600 ring-2 ring-blue-200' :
      isDimensionComplete(index) ? 'bg-green-600' :
      'bg-gray-300'
    }`}
  />
))}
```

### Status Badge
```tsx
<span className={`px-3 py-1 rounded-full text-sm font-medium ${
  score >= 4.5 ? 'bg-green-100 text-green-800' :
  score >= 3.5 ? 'bg-blue-100 text-blue-800' :
  score >= 2.5 ? 'bg-yellow-100 text-yellow-800' :
  score >= 1.5 ? 'bg-orange-100 text-orange-800' :
  'bg-red-100 text-red-800'
}`}>
  {getStatusLabel(score)}
</span>
```

---

## Testing

### Test Scenarios

1. **New User Flow:**
   - Visit /health → See welcome
   - Take assessment → Complete all questions
   - Submit → View results
   - Return to /health → See latest assessment

2. **Save and Resume:**
   - Start questionnaire
   - Answer 10 questions
   - Save progress
   - Close browser
   - Reopen → Draft loads
   - Complete remaining
   - Submit

3. **Incomplete Submission:**
   - Answer 20/27 questions
   - Try to submit
   - See error: "Please answer all questions"
   - Complete remaining
   - Submit successfully

4. **Multiple Assessments:**
   - Complete first assessment
   - Wait 1 month
   - Take second assessment
   - View history → See both
   - Compare results

---

## Accessibility

- All form inputs labeled
- Keyboard navigation supported
- Focus states visible
- Error messages clear
- Color not sole indicator (text labels + colors)
- Screen reader friendly structure

---

## Future Enhancements

1. **Trend Analysis:**
   - Line charts showing score over time
   - Dimension comparison across assessments
   - Progress indicators

2. **Reminders:**
   - Email reminders for monthly assessments
   - In-app notifications

3. **Shareable Reports:**
   - PDF export
   - Share with supervisor option

4. **Customization:**
   - Add custom questions
   - Adjust dimension weights
   - Personalized recommendations

---

## Access

**Routes:**
- `/health` - Health dashboard
- `/health/assessment` - Take questionnaire
- `/health/:assessmentId` - View results
- `/health/history` - Assessment history

**Test:**
```
http://localhost:3000/health
http://localhost:3000/health/assessment
```
