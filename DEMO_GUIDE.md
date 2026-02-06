## PhD Timeline Intelligence Platform - Demo Guide

Complete guide for exploring the platform with three realistic PhD student personas.

---

## Quick Start

### 1. Seed Demo Data

```bash
cd backend
python seed_demo_data.py
```

This creates three PhD student personas with complete timelines, progress data, and assessments.

### 2. Start Services

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

```

### 3. Access Demo

Access the API at: http://localhost:8000

**Demo login IDs** (use any email below, no password needed in demo mode):
- `sarah.chen@university.edu` (Early-stage)
- `marcus.johnson@university.edu` (Mid-stage)
- `elena.rodriguez@university.edu` (Late-stage)

---

## Demo Personas

### 👩‍🎓 Persona 1: Sarah Chen (Early-Stage PhD)

**Profile:**
- **Program:** PhD in Computer Science (Machine Learning)
- **Institution:** Stanford University
- **Progress:** 6 months into program
- **Status:** Coursework completed, developing research methodology

**Journey Story:**
Sarah recently completed her coursework with excellent grades and finished a comprehensive literature review. She's now in the exciting but challenging phase of defining her research scope in multi-agent reinforcement learning. Her advisor is supportive, and she's well-funded, but she's feeling some anxiety about narrowing down her research questions to a manageable scope.

**Current State:**
- ✅ Completed coursework (all A's)
- ✅ Completed literature review (10 days late but thorough)
- ✅ Research questions defined
- 🔄 Developing baseline algorithm (in progress)
- 📅 Preparing for qualifying exam (upcoming)

**Health Assessment:**
- Overall: 4.2/5 (Good)
- Research Progress: 4.0/5
- Mental Wellbeing: 4.5/5
- Timeline Adherence: 4.5/5
- Key Strength: Strong foundation and clear direction
- Key Challenge: Defining appropriate scope

---

### 👨‍🎓 Persona 2: Marcus Johnson (Mid-Stage PhD)

**Profile:**
- **Program:** PhD in EECS (Natural Language Processing)
- **Institution:** MIT
- **Progress:** 2.5 years into program
- **Status:** Conducting experiments, some delays, mixed emotions

**Journey Story:**
Marcus passed his qualifying exam (about a month late) and has been deep in research ever since. He recently had his first paper accepted to a top-tier NLP conference (ACL), which was a huge win. However, he's currently facing delays in running large-scale experiments due to GPU cluster issues, and a critical milestone is now 45 days overdue. He's feeling the pressure and his work-life balance has suffered.

**Current State:**
- ✅ Coursework completed
- ✅ Qualifying exam passed (30 days late)
- ✅ Baseline dialogue system built (30 days late)
- ✅ First paper accepted to ACL 2024
- ⚠️ Large-scale experiments **45 DAYS OVERDUE**
- 📅 Second paper submission planned
- 😰 Feeling stressed and burned out

**Health Assessment:**
- Overall: 3.2/5 (Fair)
- Research Progress: 4.0/5 (research quality is strong)
- Mental Wellbeing: 2.5/5 (struggling with stress)
- Timeline Adherence: 2.5/5 (behind schedule)
- Key Strength: Strong technical work, paper acceptance
- Key Challenge: Timeline delays, work-life balance, burnout

**Recent Events:**
- 🎉 Paper accepted (30 days ago)
- ⚠️ GPU cluster downtime causing delays (20 days ago)
- 😓 Assessment shows need for stress management

---

### 👩‍🔬 Persona 3: Elena Rodriguez (Late-Stage PhD)

**Profile:**
- **Program:** PhD in Computer Science (Computer Vision)
- **Institution:** UC Berkeley
- **Progress:** 4.5 years into program (90% complete)
- **Status:** Dissertation writing, job hunting, final push

**Journey Story:**
Elena is in the final stretch! With 4.5 years completed and a strong publication record, she's 90% done with her dissertation on 3D scene understanding. She's submitted 18 job applications and already has interview invitations from top institutions, including a faculty interview at University of Washington. She's feeling a mix of excitement and anxiety about finishing—the end is in sight, but there's still work to do.

**Current State:**
- ✅ All coursework completed
- ✅ Qualifying exam passed
- ✅ Multiple papers published
- ✅ Dissertation Chapters 1-5 complete
- ✅ Job applications submitted (18 applications)
- ✅ Faculty interview secured!
- 🔄 Final chapter in progress (due in 30 days)
- 📅 Defense scheduled in 90 days
- 📅 Final submission in 120 days

**Health Assessment:**
- Overall: 4.5/5 (Excellent)
- Research Progress: 4.8/5 (strong publication record)
- Mental Wellbeing: 4.3/5 (managing finishing anxiety)
- Timeline Adherence: 4.3/5 (on track)
- Key Strength: Clear path to completion, job prospects
- Key Challenge: Balancing dissertation and interviews

**Recent Events:**
- 📝 All job applications submitted (25 days ago)
- 🎉 Faculty interview invitation (10 days ago)
- 📊 Dissertation 90% complete (2 days ago)

---

## Demo Workflows

### Workflow 1: Early-Stage - Creating First Timeline

**As Sarah Chen:**

1. **Upload Document**
   - Go to `/documents/upload`
   - "Upload" PhD program requirements (simulated)
   - Create baseline with program details

2. **View Baseline**
   - Navigate to baseline detail
   - Click "Create Timeline"
   - System generates draft timeline

3. **Review Draft Timeline**
   - See 4 stages: Coursework, Research Dev, Experimentation, Writing
   - Review milestones for each stage
   - Edit if needed

4. **Commit Timeline**
   - Click "Commit Timeline"
   - Confirm commitment
   - Now have immutable roadmap

**Demo Endpoints:**
```bash
# View baseline
GET /api/v1/baselines/11111111-3333-1111-1111-111111111111

# View committed timeline
GET /api/v1/timelines/committed/11111111-4444-1111-1111-111111111111

# View progress
GET /api/v1/progress/timelines/11111111-4444-1111-1111-111111111111
```

---

### Workflow 2: Mid-Stage - Managing Delays

**As Marcus Johnson:**

1. **View Timeline Progress**
   - Go to `/progress/timeline/22222222-2222-2222-2222-222222222224`
   - See overall progress: ~60% complete
   - Notice red alert: "3 Critical Milestones Overdue"

2. **Examine Overdue Milestone**
   - Expand "Research and Experimentation" stage
   - See "Run Large-Scale Experiments" - 45 days overdue
   - Red background highlights urgency

3. **Mark Progress**
   - (When experiments complete) Mark milestone as done
   - System logs completion event
   - Updates progress calculations

4. **Take Health Assessment**
   - Go to `/health/assessment`
   - Answer 27 questions across 8 dimensions
   - Submit assessment

5. **View Recommendations**
   - See overall status: "Fair" (3.2/5)
   - Critical area: Mental Wellbeing (2.5/5)
   - Recommendations:
     - High Priority: Improve work-life balance
     - Medium Priority: Discuss timeline with advisor
     - Action items provided

**Demo Endpoints:**
```bash
# View timeline progress (shows delays)
GET /api/v1/progress/timelines/22222222-2222-2222-2222-222222222224

# Check specific milestone delay
GET /api/v1/progress/milestones/22222222-2222-2222-2222-222222222227/delay

# Submit assessment
POST /api/v1/assessments/submit
```

---

### Workflow 3: Late-Stage - Final Sprint

**As Elena Rodriguez:**

1. **View Overall Progress**
   - Dashboard shows 90% completion
   - 3 of 6 final milestones complete
   - Timeline adherence: 4.3/5

2. **Track Remaining Milestones**
   - ✅ Chapters 1-5 complete
   - ✅ Job applications submitted
   - 🔄 Final chapter in progress (due in 30 days)
   - 📅 Defense in 90 days
   - 📅 Final submission in 120 days

3. **Review Progress Events**
   - See job interview invitation
   - See dissertation progress update
   - All events timestamped and categorized

4. **Take Final Assessment**
   - Complete health check
   - See excellent status (4.5/5)
   - Strengths: Strong publication record, clear finish line
   - Challenge: Managing finishing anxiety

5. **Plan Final Weeks**
   - Use timeline as completion checklist
   - Track remaining milestones
   - Prepare for defense

**Demo Endpoints:**
```bash
# View late-stage timeline
GET /api/v1/timelines/committed/33333333-3333-3333-3333-333333333333

# View progress (should show high completion)
GET /api/v1/progress/timelines/33333333-3333-3333-3333-333333333333

# View stage progress
GET /api/v1/progress/stages/33333333-3333-3333-3333-333333333334

# View assessment
GET /api/v1/assessments/latest
```

---

## Demo Scenarios to Test

### Scenario 1: Document Upload → Baseline → Timeline
```
1. Login as Sarah
2. Upload document (/documents/upload)
3. Create baseline (toggle enabled)
4. Navigate to baseline detail
5. Click "Create Timeline"
6. Review generated timeline
7. Commit timeline
```

### Scenario 2: Progress Tracking
```
1. Login as Marcus
2. View timeline progress dashboard
3. See overdue indicators
4. Expand delayed stage
5. Review milestone details
6. Check delay calculations
```

### Scenario 3: Health Assessment
```
1. Login as any user
2. Go to /health
3. Click "Take Assessment"
4. Answer 27 questions
5. Save progress (test resume)
6. Complete and submit
7. View results with recommendations
```

### Scenario 4: Browse History
```
1. Login as Elena
2. View timelines list
3. Click committed timeline
4. View read-only timeline
5. Click "View Progress"
6. See high completion %
7. Review progress events
```

---

## API Testing Examples

### Get Timeline Progress
```bash
curl http://localhost:8000/api/v1/progress/timelines/22222222-2222-2222-2222-222222222224
```

**Expected Response:**
```json
{
  "timelineId": "22222222-2222-2222-2222-222222222224",
  "completionPercentage": 60,
  "overdueMilestones": 1,
  "overdueCriticalMilestones": 1,
  "averageDelayDays": 15,
  ...
}
```

### Get Milestone Delay
```bash
curl http://localhost:8000/api/v1/progress/milestones/22222222-2222-2222-2222-222222222227/delay
```

**Expected Response:**
```json
{
  "milestoneId": "...",
  "delayDays": 45,
  "status": "OVERDUE",
  "isCritical": true,
  ...
}
```

### Submit Assessment
```bash
curl -X POST http://localhost:8000/api/v1/assessments/submit \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {"dimension": "RESEARCH_PROGRESS", "questionId": "rp1", "responseValue": 4},
      ...
    ],
    "assessmentType": "self_assessment"
  }'
```

---

## Data Validation Points

### Sarah (Early-Stage)
- ✅ 2 milestones completed
- ✅ 3 milestones pending
- ✅ 0 milestones overdue
- ✅ Assessment: Good (4.2/5)
- ✅ High motivation, some anxiety

### Marcus (Mid-Stage)
- ✅ 3 milestones completed (some late)
- ✅ 1 milestone OVERDUE (45 days)
- ✅ 2 milestones pending
- ✅ Assessment: Fair (3.2/5)
- ✅ Shows stress indicators

### Elena (Late-Stage)
- ✅ 3 milestones completed (on time)
- ✅ 0 milestones overdue
- ✅ 3 milestones pending
- ✅ Assessment: Excellent (4.5/5)
- ✅ Nearly complete, job prospects

---

## Troubleshooting

### Data Not Showing
```bash
# Verify database has data
python backend/seed_demo_data.py

# Check user IDs match
# UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Progress Not Calculating
```bash
# Ensure committed timelines have milestones
# Check timeline_stage_id foreign keys
```

### Assessment Not Loading
```bash
# Verify journey_assessment records exist
# Check assessment_date is recent
```

---

## Demo Tips

1. **Start with Sarah** - Simplest case, clear success story
2. **Move to Marcus** - Shows realistic challenges
3. **Finish with Elena** - Demonstrates end goal

4. **Highlight Features:**
   - Color-coded status (green, yellow, red)
   - Delay calculations
   - Progress bars
   - Health recommendations

5. **Tell the Story:**
   - Each persona has a narrative arc
   - Shows different PhD stages
   - Demonstrates platform value

---

## Next Steps After Demo

1. **Add Real Data:**
   - Upload your own documents
   - Create your baseline
   - Generate your timeline

2. **Track Progress:**
   - Mark milestones as complete
   - Log progress events
   - Monitor delays

3. **Regular Check-ins:**
   - Take monthly assessments
   - Review recommendations
   - Adjust timeline as needed

---

## Demo Checklist

Before presenting:
- [ ] Database seeded successfully
- [ ] Backend server running
- [ ] API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Progress dashboards load
- [ ] Assessment questionnaire works
- [ ] Results display properly
- [ ] All three workflows tested

---

## Summary

**Three Complete Demo Journeys:**
1. 👩‍🎓 Sarah (Early) - Building foundation
2. 👨‍🎓 Marcus (Mid) - Managing challenges
3. 👩‍🔬 Elena (Late) - Approaching finish line

**End-to-End Coverage:**
- ✅ Document upload and baseline creation
- ✅ Timeline generation and commitment
- ✅ Progress tracking with delays
- ✅ Health assessments and recommendations
- ✅ Complete data for all personas
- ✅ Realistic scenarios and challenges

**Ready for Demo!** 🎉
