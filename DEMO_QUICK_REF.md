# Demo Quick Reference Card

## 🚀 Setup (One-Time)

```bash
# Seed data
cd backend
python seed_demo_data.py

# Start backend
cd backend && uvicorn app.main:app --reload
```

**Access API:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

---

## 👥 Demo Users

| Persona | Email | Stage | Status | Highlights |
|---------|-------|-------|--------|-----------|
| **Sarah Chen** | sarah.chen@university.edu | Early (6mo) | 🟢 On Track | Coursework done, developing methodology |
| **Marcus Johnson** | marcus.johnson@university.edu | Mid (2.5yr) | 🟡 Delayed | Paper accepted, experiments overdue 45d |
| **Elena Rodriguez** | elena.rodriguez@university.edu | Late (4.5yr) | 🟢 Nearly Done | 90% complete, job interviews secured |

---

## 📊 Key Metrics

### Sarah (Early-Stage)
- ✅ Completion: 40%
- ✅ Assessment: 4.2/5 (Good)
- ✅ Overdue: 0
- 🎯 Next: Develop baseline algorithm

### Marcus (Mid-Stage)
- ⚠️ Completion: 60%
- ⚠️ Assessment: 3.2/5 (Fair)
- ⚠️ Overdue: 1 (45 days)
- 🎯 Next: Complete experiments ASAP

### Elena (Late-Stage)
- ✅ Completion: 90%
- ✅ Assessment: 4.5/5 (Excellent)
- ✅ Overdue: 0
- 🎯 Next: Finish final chapter, defend

---

## 🔗 Direct Links

### Sarah's Journey
- Timeline: `/timelines/committed/11111111-4444-1111-1111-111111111111`
- Progress: `/progress/timeline/11111111-4444-1111-1111-111111111111`
- Health: `/health`

### Marcus's Journey
- Timeline: `/timelines/committed/22222222-2222-2222-2222-222222222224`
- Progress: `/progress/timeline/22222222-2222-2222-2222-222222222224`
- Health: `/health`

### Elena's Journey
- Timeline: `/timelines/committed/33333333-3333-3333-3333-333333333333`
- Progress: `/progress/timeline/33333333-3333-3333-3333-333333333333`
- Health: `/health`

---

## 🎬 Demo Scenarios (5 min each)

### Scenario 1: Early Success (Sarah)
```
1. View timeline → 4 stages, clear progression
2. Check progress → 40% complete, all green
3. Take assessment → High scores, positive outlook
4. Show: Clean start, good foundation
```

### Scenario 2: Mid Challenges (Marcus)
```
1. View progress → Red alert: 1 overdue
2. Expand stage → 45 days late, critical
3. View assessment → Fair status, stress indicators
4. Show: Realistic struggles, needs support
```

### Scenario 3: Late Finish (Elena)
```
1. View timeline → 90% complete, 3 milestones left
2. Check progress → Strong metrics, on schedule
3. View events → Job interviews, nearly done
4. Show: Success story, approaching goal
```

---

## 💡 Demo Script

**Opening (1 min):**
> "PhD Timeline Intelligence Platform helps students track progress, 
> manage timelines, and assess journey health. Let me show you three 
> real student journeys..."

**Early-Stage Demo (4 min):**
> "Sarah is 6 months in. She's completed coursework and is developing 
> her methodology. Her timeline shows clear progression through 4 stages.
> Her health assessment shows strong motivation with some scope anxiety—
> perfectly normal for this stage."

**Mid-Stage Demo (4 min):**
> "Marcus is 2.5 years in and facing realistic challenges. His experiments 
> are 45 days overdue, shown in red. But his research quality is strong—
> he just had a paper accepted. His health assessment indicates stress 
> and suggests work-life balance improvements."

**Late-Stage Demo (4 min):**
> "Elena is 4.5 years in and approaching the finish line. She's 90% complete,
> has job interviews lined up, and just needs to finish her final chapter.
> Her assessment shows excellent status with manageable finishing anxiety.
> This is what success looks like."

**Closing (2 min):**
> "The platform provides: (1) Clear visual timelines, (2) Automatic delay 
> tracking, (3) Health assessments with recommendations. It helps students 
> stay on track and get support when needed."

---

## 🎯 Key Features to Highlight

### 1. Visual Timeline
- ✅ Stage-by-stage breakdown
- ✅ Color-coded status
- ✅ Progress bars
- ✅ Expandable details

### 2. Delay Tracking
- ✅ Automatic calculation
- ✅ Red alerts for overdue
- ✅ Days behind/ahead shown
- ✅ Critical milestone flagging

### 3. Health Assessment
- ✅ 8 dimensions measured
- ✅ 27 questions total
- ✅ Save and resume
- ✅ Personalized recommendations

### 4. Progress Dashboard
- ✅ Overall completion %
- ✅ Stage-by-stage metrics
- ✅ Overdue count
- ✅ Average delays

---

## 📞 API Examples

```bash
# Get Marcus's timeline progress
curl http://localhost:8000/api/v1/progress/timelines/22222222-2222-2222-2222-222222222224

# Check overdue milestone
curl http://localhost:8000/api/v1/progress/milestones/22222222-2222-2222-2222-222222222227/delay

# Get Elena's stage progress
curl http://localhost:8000/api/v1/progress/stages/33333333-3333-3333-3333-333333333334
```

---

## ✅ Pre-Demo Checklist

- [ ] Database seeded (`seed_demo_data.py` run)
- [ ] Backend running (port 8000)
- [ ] Can access http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] All three users exist in database
- [ ] API endpoints respond correctly

---

## 🐛 Quick Fixes

**Users not loading?**
```bash
cd backend && python seed_demo_data.py
```

**Backend not starting?**
```
Check backend/.env file exists and has correct DATABASE_URL
```

**Progress not calculating?**
```bash
# Restart backend
cd backend && uvicorn app.main:app --reload
```

---

## 📊 Expected Demo Results

### Sarah
- ✅ 2 completed milestones
- ✅ 3 pending milestones
- ✅ 0 overdue
- ✅ Good health status

### Marcus  
- ✅ 3 completed milestones (some late)
- ✅ 1 overdue milestone (45d late)
- ✅ 2 pending milestones
- ✅ Fair health status, stress indicators

### Elena
- ✅ 3 completed milestones (on time)
- ✅ 3 pending milestones
- ✅ 0 overdue
- ✅ Excellent health status

---

## 🎓 Demo Value Propositions

1. **For Students:** 
   - Clear roadmap to completion
   - Early warning for delays
   - Health check-ins with support

2. **For Advisors:**
   - Student progress visibility
   - Data-driven interventions
   - Timeline adherence tracking

3. **For Institutions:**
   - Completion rate improvement
   - Student wellbeing monitoring
   - Retention insights

---

## ⏱️ Time Allocations

**15-Minute Demo:**
- Intro: 2 min
- Sarah: 4 min
- Marcus: 4 min
- Elena: 4 min
- Q&A: 1 min

**30-Minute Demo:**
- Intro: 3 min
- Sarah: 7 min (with workflow)
- Marcus: 8 min (with assessment)
- Elena: 7 min (with progress details)
- Features summary: 3 min
- Q&A: 2 min

**60-Minute Workshop:**
- Full walkthrough: 20 min
- Hands-on exploration: 30 min
- Discussion: 10 min

---

## 🔥 Power User Tips

1. **Show progression:** Sarah → Marcus → Elena demonstrates journey
2. **Highlight contrast:** Early optimism vs mid struggle vs late success
3. **Focus on value:** Emphasize delay detection and health support
4. **Be relatable:** PhD struggles are universal, platform helps
5. **End positive:** Elena's success is the goal for everyone

---

## 📝 Demo Notes

**Talking Points:**
- Real data, realistic scenarios
- All automated, no manual tracking
- Proactive not reactive support
- Evidence-based recommendations
- Scalable to entire institution

**Avoid:**
- Getting lost in technical details
- Spending too long on one persona
- Ignoring the human stories
- Forgetting to show recommendations

**Remember:**
- This is about helping students succeed
- Data enables early intervention
- Platform reduces PhD attrition
- Students, advisors, institutions all benefit

---

**Ready to Demo!** 🚀
