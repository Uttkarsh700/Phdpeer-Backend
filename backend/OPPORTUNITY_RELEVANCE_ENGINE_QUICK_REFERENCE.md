# Opportunity Relevance Engine - Quick Reference

## Basic Usage

```python
from app.services.opportunity_relevance_engine import (
    OpportunityRelevanceEngine,
    Opportunity,
    UserProfile,
    ResearchStage,
    OpportunityType
)
from datetime import date, timedelta

engine = OpportunityRelevanceEngine()

# Define user
user = UserProfile(
    discipline="Computer Science",
    subdisciplines=["ML", "AI"],
    research_stage=ResearchStage.EARLY,
    keywords=["deep learning", "NLP"]
)

# Define opportunity
opp = Opportunity(
    opportunity_id="grant_1",
    title="Research Grant",
    opportunity_type=OpportunityType.GRANT,
    disciplines=["Computer Science"],
    eligible_stages=[ResearchStage.EARLY],
    deadline=date.today() + timedelta(days=60)
)

# Score
score = engine.score_opportunity(opp, user)
print(f"Score: {score.overall_score}/100")
print(f"Action: {score.recommended_action}")
```

## Score Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Discipline | 40% | Discipline alignment |
| Stage | 30% | Research stage match |
| Timeline | 15% | Timeline compatibility |
| Deadline | 15% | Deadline suitability |

## Discipline Scoring

| Match Type | Score |
|------------|-------|
| Exact match | 100.0 |
| Subdiscipline | 85.0 |
| Broad category | 70.0 |
| Keyword overlap | 50-80 |
| Mismatch | 20.0 |

## Stage Scoring

| Match Type | Score |
|------------|-------|
| Perfect match | 100.0 |
| Adjacent stage | 75.0 |
| All stages (3+) | 60.0 |
| Mismatch | 30.0 |

## Deadline Scoring

### Grants/Fellowships

| Days Until | Score | Tag |
|------------|-------|-----|
| < 0 | 0.0 | DEADLINE_MISSED |
| < 7 | 40.0 | DEADLINE_VERY_TIGHT |
| 7-13 | 65.0 | DEADLINE_TIGHT |
| 30-90 | 100.0 | DEADLINE_OPTIMAL |
| > 180 | 70.0 | DEADLINE_TOO_FAR |

### Conferences/Workshops

| Days Until | Score | Tag |
|------------|-------|-----|
| 14-60 | 100.0 | DEADLINE_OPTIMAL |
| 61-120 | 85.0 | - |
| > 120 | 75.0 | DEADLINE_TOO_FAR |

## Recommended Actions

| Action | Criteria |
|--------|----------|
| **apply_now** | High score + good deadline |
| **prepare** | Good score + optimal (far) deadline |
| **monitor** | Moderate score |
| **skip** | Low score |

## Urgency Levels

| Level | Criteria |
|-------|----------|
| **high** | Deadline ≥ 80 AND Overall ≥ 70 |
| **medium** | Deadline ≥ 65 AND Overall ≥ 50 |
| **low** | Otherwise |

## Research Stages

```python
ResearchStage.EARLY          # Year 1-2
ResearchStage.MID            # Year 2-4
ResearchStage.LATE           # Year 4+
ResearchStage.POST_SUBMISSION # Post-submission
```

## Opportunity Types

```python
OpportunityType.GRANT
OpportunityType.FELLOWSHIP
OpportunityType.CONFERENCE
OpportunityType.WORKSHOP
OpportunityType.COMPETITION
OpportunityType.INTERNSHIP
OpportunityType.AWARD
```

## Key Reason Tags

### Discipline

- `EXACT_DISCIPLINE_MATCH`
- `BROAD_DISCIPLINE_MATCH`
- `INTERDISCIPLINARY_MATCH`
- `DISCIPLINE_MISMATCH`

### Stage

- `STAGE_PERFECT_MATCH`
- `STAGE_GOOD_MATCH`
- `STAGE_MISMATCH`

### Timeline

- `ALIGNS_WITH_CURRENT_STAGE`
- `ALIGNS_WITH_UPCOMING_STAGE`
- `SUPPORTS_MILESTONE`

### Deadline

- `DEADLINE_OPTIMAL`
- `DEADLINE_TIGHT`
- `DEADLINE_VERY_TIGHT`
- `DEADLINE_MISSED`
- `DEADLINE_TOO_FAR`

### Characteristics

- `HIGH_PRESTIGE`
- `FUNDING_OPPORTUNITY`
- `PUBLICATION_VENUE`
- `NETWORKING_OPPORTUNITY`
- `CAREER_BUILDING`

## Ranking Multiple Opportunities

```python
opportunities = [opp1, opp2, opp3]

ranked = engine.rank_opportunities(
    opportunities=opportunities,
    user_profile=user,
    min_score=60.0  # Filter threshold
)

for score in ranked:
    print(f"{score.opportunity_id}: {score.overall_score}")
```

## With Timeline Context

```python
from app.services.opportunity_relevance_engine import TimelineContext

timeline = TimelineContext(
    current_stage_name="Data Collection",
    current_stage_progress=0.6,
    upcoming_stages=["Analysis", "Writing"],
    critical_milestones=["Complete dataset"],
    expected_completion_date=date(2028, 5, 1)
)

score = engine.score_opportunity(
    opportunity=opp,
    user_profile=user,
    timeline_context=timeline  # Improves timeline scoring
)
```

## RelevanceScore Output

```python
score.overall_score          # 0-100
score.discipline_score       # 0-100
score.stage_score           # 0-100
score.timeline_score        # 0-100
score.deadline_score        # 0-100
score.reason_tags           # List[ReasonTag]
score.explanation           # Human-readable string
score.urgency_level         # "high", "medium", "low"
score.recommended_action    # "apply_now", "prepare", "monitor", "skip"
```

## Example Score Calculation

```
User: CS, EARLY stage, keywords: ["ML", "AI"]
Opportunity: CS Conference, EARLY, 30 days, keywords: ["ML"]

Discipline:  100.0 (exact match) * 0.40 = 40.0
Stage:       100.0 (perfect)     * 0.30 = 30.0
Timeline:     50.0 (no context)  * 0.15 =  7.5
Deadline:    100.0 (optimal)     * 0.15 = 15.0
───────────────────────────────────────────────
Overall:                                 92.5

Action: apply_now
Urgency: high
Tags: [EXACT_DISCIPLINE_MATCH, STAGE_PERFECT_MATCH, DEADLINE_OPTIMAL]
```

## Testing

```bash
# Run all tests
pytest tests/test_opportunity_relevance_engine.py -v

# Test specific component
pytest tests/test_opportunity_relevance_engine.py::TestDisciplineScoring -v
```

## Performance

- **Single Score**: < 5ms
- **Rank 100 Opps**: < 50ms
- **Deterministic**: ✅ Yes

## Common Patterns

### Filter by Action

```python
ranked = engine.rank_opportunities(opportunities, user)
apply_now = [s for s in ranked if s.recommended_action == "apply_now"]
```

### Filter by Urgency

```python
ranked = engine.rank_opportunities(opportunities, user)
urgent = [s for s in ranked if s.urgency_level == "high"]
```

### Filter by Tag

```python
from app.services.opportunity_relevance_engine import ReasonTag

ranked = engine.rank_opportunities(opportunities, user)
funding = [
    s for s in ranked 
    if ReasonTag.FUNDING_OPPORTUNITY in s.reason_tags
]
```

### Top N Recommendations

```python
ranked = engine.rank_opportunities(opportunities, user, min_score=70.0)
top_5 = ranked[:5]
```

## Discipline Taxonomy (Built-in)

- **Computer Science**: CS, Computing, AI, ML
- **Biology**: Life Sciences, Molecular Biology, Genetics
- **Chemistry**: Organic, Inorganic, Biochemistry
- **Physics**: Theoretical, Experimental, Astrophysics
- **Mathematics**: Pure, Applied, Statistics
- **Engineering**: Electrical, Mechanical, Civil
- **Social Sciences**: Psychology, Sociology, Economics
- **Humanities**: History, Literature, Philosophy

## Key Principles

✅ **Deterministic** - Same inputs = same outputs  
✅ **Explainable** - Reason tags + explanations  
✅ **Fast** - < 5ms per opportunity  
✅ **No ML** - Pure rule-based logic  
✅ **Extensible** - Easy to modify weights/rules  

## Status

**Implementation**: ✅ Complete  
**Tests**: ✅ 31 tests passing  
**Documentation**: ✅ Comprehensive  
**Production Ready**: ✅ Yes  

---

For full documentation, see `OPPORTUNITY_RELEVANCE_ENGINE_COMPLETE.md`
