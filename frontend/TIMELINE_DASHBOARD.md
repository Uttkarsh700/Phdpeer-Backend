# Timeline Progress Dashboard

Comprehensive dashboard for tracking PhD timeline progress with visual indicators for stages, milestones, completion status, and delays.

## Overview

The Timeline Progress Dashboard provides a read-only view of committed timelines with real-time progress tracking, delay indicators, and completion metrics.

**Route:** `/progress/timeline/:timelineId`

**File:** `src/pages/TimelineProgressPage.tsx`

---

## Features

### 1. **Overall Progress Summary (Top Cards)**

Four key metrics displayed in card format:

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Overall Progress│  │ Stages          │  │ Overdue         │  │ Avg Delay       │
│                 │  │                 │  │                 │  │                 │
│     75%        │  │   2 / 4         │  │      3          │  │   5 days        │
│ 15 of 20       │  │ Stages complete │  │ 1 critical      │  │ Max: 12 days    │
│ milestones     │  │                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

**Card 1: Overall Progress**
- Percentage complete (large number)
- Completed vs total milestones
- Blue icon

**Card 2: Stages**
- Completed stages / Total stages
- Stage completion ratio
- Purple icon

**Card 3: Overdue**
- Number of overdue milestones
- Critical overdue count (if any)
- Red icon (attention needed)

**Card 4: Average Delay**
- Average delay across all milestones
- Maximum delay encountered
- Yellow icon

---

### 2. **Timeline Completion Bar**

Large progress bar showing overall completion:

```
Timeline Completion                                           75%
[████████████████████████████████████░░░░░░░░░░] 

Started: Jan 1, 2024                        Target: Dec 31, 2027
```

- **Visual bar** with percentage
- **Start date** from committed timeline
- **Target date** (if set)
- Smooth animation on load

---

### 3. **Critical Milestones Alert**

Red alert banner appears when critical milestones are overdue:

```
⚠️ Critical Milestones Overdue
   You have 2 critical milestone(s) that are overdue. 
   Please review and take action immediately.
```

- Only shows when `overdueCriticalMilestones > 0`
- Prominent red background
- Warning icon
- Clear call to action

---

### 4. **Stage Cards (Expandable)**

Each stage is displayed as an expandable card:

```
┌──────────────────────────────────────────────────────────────────┐
│  [1]  Literature Review                        65% Complete  ▼   │
│       Complete comprehensive literature review  4 / 6 milestones  │
│                                                 [Progress Bar]     │
│       🔴 2 overdue     Avg delay: 3 days                         │
├──────────────────────────────────────────────────────────────────┤
│  [Milestones expanded below when clicked]                        │
└──────────────────────────────────────────────────────────────────┘
```

**Stage Header:**
- **Order number** (circular badge, blue)
- **Stage title** and description
- **Completion percentage** and milestone count
- **Progress bar** (color-coded: green=complete, red=overdue, blue=in-progress)
- **Overdue badge** (if any overdue milestones)
- **Average delay** indicator
- **Expand/collapse arrow**

**Interactions:**
- Click anywhere on header to expand/collapse
- All stages expanded by default
- Hover effect on header

---

### 5. **Milestone Cards (Inside Stages)**

Each milestone displays detailed status and delay information:

```
┌────────────────────────────────────────────────────────────────┐
│ ☑  Literature Search         Target: Mar 15, 2024  [Completed] │
│    Complete systematic lit    Completed: Mar 10, 2024          │
│    search...                                                    │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│ ☐  Paper Review [Critical]   Target: Apr 1, 2024  [5 days     │
│    Review and summarize 50                         overdue]    │
│    key papers...                                               │
└────────────────────────────────────────────────────────────────┘
```

**Milestone Components:**

**Checkbox (left side):**
- ✅ Green checkmark if completed
- ⚠️ Red border if critical and pending
- ⬜ Gray border if regular pending

**Content (center):**
- **Title** with critical badge if applicable
- **Description** (if available)
- **Target date** and **Completion date** (if completed)

**Status Badge (right side):**
- 🟢 **"Completed"** - Green badge
- 🔴 **"X days overdue"** - Red badge (missed target)
- 🟡 **"X days behind"** - Yellow badge (delayed)
- 🟢 **"On track"** - Green badge (on schedule)

**Color-Coded Backgrounds:**
- 🔴 **Red background** - Critical milestone overdue
- 🟡 **Yellow background** - Milestone delayed
- 🟢 **Green background** - Milestone completed
- ⚪ **White background** - Milestone pending, on track

---

### 6. **Footer Stats**

Bottom summary bar with key metrics:

```
┌────────────────────────────────────────────────────────────────┐
│     20              15              5               3          │
│ Total Milestones  Completed      Pending         Overdue      │
└────────────────────────────────────────────────────────────────┘
```

- Total milestone count
- Completed count (green)
- Pending count (yellow)
- Overdue count (red)

---

## Visual Indicators

### Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| **Completed** | 🟢 Green | Milestone/stage done |
| **On Track** | 🟢 Green | Meeting target dates |
| **Delayed** | 🟡 Yellow | Behind schedule |
| **Overdue** | 🔴 Red | Missed target date |
| **Critical** | 🔴 Red border | High priority |

### Progress Bars

```
Stage 100% complete:  [████████████████████] Green
Stage with overdue:   [███████░░░░░░░░░░░░░] Red
Stage in progress:    [████████░░░░░░░░░░░░] Blue
Overall timeline:     [███████████░░░░░░░░░] Blue
```

---

## Data Sources

The dashboard loads data from multiple API endpoints:

1. **Timeline Details**
   - `timelineService.getCommittedWithDetails()`
   - Returns: timeline, stages, milestones, baseline

2. **Overall Progress**
   - `progressService.getTimelineProgress()`
   - Returns: completion %, overdue count, avg delay, etc.

3. **Stage Progress** (for each stage)
   - `progressService.getStageProgress(stageId)`
   - Returns: stage completion %, overdue milestones, avg delay

4. **Milestone Delays** (for each milestone)
   - `progressService.getMilestoneDelay(milestoneId)`
   - Returns: delay days, status, target/completion dates

---

## Key Metrics Explained

### Completion Percentage
```
(Completed Milestones / Total Milestones) × 100
```

### Delay Days
- **Positive number** = Days overdue
- **Negative number** = Days ahead of schedule
- **Zero** = On target

### Status Determination
- **COMPLETED** - Milestone marked as complete
- **OVERDUE** - Not completed and past target date
- **DELAYED** - Completion date past target date
- **ON_TRACK** - On schedule or no target date

### Average Delay
```
Sum of all delay days / Number of milestones with target dates
```

---

## User Interactions

### Click Actions
1. **Stage Header** → Expand/collapse milestones
2. **"View Timeline" Button** → Navigate to committed timeline page
3. **Back to Timelines** → Navigate to timeline list

### Visual Feedback
- **Hover effects** on stage headers
- **Expand/collapse animation** for milestones
- **Progress bar animations** on load
- **Color transitions** for status changes

---

## Use Cases

### 1. Daily Check-in
PhD student reviews dashboard to see:
- Overall progress toward degree
- Upcoming milestones
- Overdue tasks requiring attention

### 2. Advisor Meeting Prep
Student prepares for meeting by:
- Reviewing completion percentage
- Identifying delayed milestones
- Noting critical overdue items

### 3. Progress Reporting
Student generates progress report using:
- Stage completion metrics
- Milestone achievements
- Delay analysis

### 4. Timeline Adjustment Planning
Student identifies need to revise timeline based on:
- Average delay trends
- Overdue critical milestones
- Stage-by-stage progress

---

## Example Flow

```
User Flow:
1. View committed timeline
   ↓
2. Click "View Progress" button
   ↓
3. Dashboard loads with all metrics
   ↓
4. Review overall progress (75% complete)
   ↓
5. Notice critical alert (2 overdue)
   ↓
6. Expand Stage 2 to see details
   ↓
7. Identify specific overdue milestones
   ↓
8. Take action on critical items
   ↓
9. Return to committed timeline view
```

---

## Responsive Design

The dashboard adapts to different screen sizes:

**Desktop (>1024px):**
- 4-column card grid for metrics
- Full progress bars
- Expanded view by default

**Tablet (768-1024px):**
- 2-column card grid
- Abbreviated labels
- Collapsible stages

**Mobile (<768px):**
- Single column layout
- Stacked cards
- Compact milestone cards

---

## Performance

**Optimizations:**
- All data loaded in parallel using `Promise.all()`
- Stage progress cached in Map for O(1) lookup
- Milestone delays cached in Map for O(1) lookup
- Stages expanded by default (no re-render on expand)

**Load Time:**
- Initial load: 1-2 seconds (multiple API calls)
- Expand/collapse: Instant (no API calls)
- Navigation: <100ms

---

## Future Enhancements

1. **Charts & Graphs**
   - Burndown chart
   - Velocity graph
   - Completion timeline

2. **Filtering**
   - Show only overdue
   - Show only critical
   - Filter by stage

3. **Sorting**
   - Sort by delay
   - Sort by priority
   - Sort by date

4. **Export**
   - PDF report generation
   - CSV export
   - Print-friendly view

5. **Real-time Updates**
   - WebSocket for live updates
   - Refresh button
   - Auto-refresh option

6. **Historical Trends**
   - Compare to previous months
   - Progress velocity
   - Completion predictions

---

## Testing

**Test Scenarios:**

1. **All Completed**
   - Green progress bar at 100%
   - All milestones with checkmarks
   - No overdue alerts

2. **Mix of States**
   - Some completed, some pending, some overdue
   - Progress bar partially filled
   - Critical alert if applicable

3. **All Overdue**
   - Red indicators throughout
   - Critical alert prominent
   - High delay numbers

4. **Empty Timeline**
   - Graceful handling of no milestones
   - Appropriate empty states
   - No errors

**Access:**
```
http://localhost:3000/progress/timeline/:timelineId
```

Replace `:timelineId` with actual committed timeline UUID.
