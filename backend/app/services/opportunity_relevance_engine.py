"""
OpportunityRelevanceEngine - Deterministic opportunity ranking system.

Scores opportunities (grants, conferences, fellowships) based on:
- User discipline alignment
- Research stage appropriateness
- Timeline stage compatibility
- Deadline suitability

All scoring is rule-based and deterministic.
"""

from dataclasses import dataclass
from typing import List, Optional, Set, Dict, Any
from datetime import date, timedelta
from enum import Enum

from sqlalchemy.orm import Session

from app.services.scoring_config_service import ScoringConfigService


class ResearchStage(Enum):
    """PhD research stage."""
    EARLY = "early"           # Year 1-2, coursework, proposal
    MID = "mid"               # Year 2-4, data collection, analysis
    LATE = "late"             # Year 4+, writing, submission
    POST_SUBMISSION = "post"  # Post-submission, pre-defense


class OpportunityType(Enum):
    """Type of opportunity."""
    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    COMPETITION = "competition"
    INTERNSHIP = "internship"
    AWARD = "award"


class ReasonTag(Enum):
    """Reason tags for relevance scoring."""
    # Discipline matching
    EXACT_DISCIPLINE_MATCH = "exact_discipline_match"
    BROAD_DISCIPLINE_MATCH = "broad_discipline_match"
    INTERDISCIPLINARY_MATCH = "interdisciplinary_match"
    DISCIPLINE_MISMATCH = "discipline_mismatch"
    
    # Stage appropriateness
    STAGE_PERFECT_MATCH = "stage_perfect_match"
    STAGE_GOOD_MATCH = "stage_good_match"
    STAGE_ACCEPTABLE = "stage_acceptable"
    STAGE_MISMATCH = "stage_mismatch"
    
    # Timeline compatibility
    ALIGNS_WITH_CURRENT_STAGE = "aligns_with_current_stage"
    ALIGNS_WITH_UPCOMING_STAGE = "aligns_with_upcoming_stage"
    SUPPORTS_MILESTONE = "supports_milestone"
    
    # Deadline suitability
    DEADLINE_OPTIMAL = "deadline_optimal"
    DEADLINE_TIGHT = "deadline_tight"
    DEADLINE_VERY_TIGHT = "deadline_very_tight"
    DEADLINE_MISSED = "deadline_missed"
    DEADLINE_TOO_FAR = "deadline_too_far"
    
    # Opportunity characteristics
    HIGH_PRESTIGE = "high_prestige"
    CAREER_BUILDING = "career_building"
    NETWORKING_OPPORTUNITY = "networking_opportunity"
    FUNDING_OPPORTUNITY = "funding_opportunity"
    PUBLICATION_VENUE = "publication_venue"


@dataclass
class UserProfile:
    """User research profile."""
    discipline: str                          # Primary discipline
    subdisciplines: List[str]                # Sub-disciplines or specializations
    research_stage: ResearchStage            # Current stage
    keywords: List[str]                      # Research keywords/topics
    institution_type: Optional[str] = None   # R1, R2, Liberal Arts, etc.
    geographic_region: Optional[str] = None  # US, EU, Global, etc.


@dataclass
class TimelineContext:
    """User's timeline context."""
    current_stage_name: str                  # e.g., "Literature Review", "Data Collection"
    current_stage_progress: float            # 0.0 to 1.0
    upcoming_stages: List[str]               # Next 2-3 stages
    critical_milestones: List[str]           # Upcoming critical milestones
    expected_completion_date: Optional[date] = None


@dataclass
class Opportunity:
    """Opportunity to be ranked."""
    opportunity_id: str
    title: str
    opportunity_type: OpportunityType
    disciplines: List[str]                   # Target disciplines
    eligible_stages: List[ResearchStage]     # Eligible research stages
    deadline: date
    description: Optional[str] = None
    keywords: List[str] = None               # Opportunity keywords
    funding_amount: Optional[float] = None   # For grants/fellowships
    prestige_level: Optional[str] = None     # "high", "medium", "low"
    geographic_scope: Optional[str] = None   # "us", "eu", "global"
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class RelevanceScore:
    """Relevance score and reasoning."""
    opportunity_id: str
    overall_score: float                     # 0.0 to 100.0
    discipline_score: float                  # 0.0 to 100.0
    stage_score: float                       # 0.0 to 100.0
    timeline_score: float                    # 0.0 to 100.0
    deadline_score: float                    # 0.0 to 100.0
    reason_tags: List[ReasonTag]
    explanation: str                         # Human-readable explanation
    urgency_level: str                       # "high", "medium", "low"
    recommended_action: str                  # "apply_now", "prepare", "monitor", "skip"


class OpportunityRelevanceEngine:
    """
    Deterministic opportunity relevance scoring engine.

    Scores opportunities based on:
    1. Discipline alignment (30% weight)
    2. Research stage appropriateness (30% weight)
    3. Timeline compatibility (25% weight)
    4. Deadline suitability (15% weight)
    """

    # Weights for overall score
    DISCIPLINE_WEIGHT = 0.30
    STAGE_WEIGHT = 0.30
    TIMELINE_WEIGHT = 0.25
    DEADLINE_WEIGHT = 0.15
    CONFIG_NAME = "opportunity_relevance"
    DEFAULT_VERSION = "opportunity_relevance_v1"

    def __init__(self, db: Optional[Session] = None):
        self._scoring_version = self.DEFAULT_VERSION
        self._weights = {
            "discipline": self.DISCIPLINE_WEIGHT,
            "stage": self.STAGE_WEIGHT,
            "timeline": self.TIMELINE_WEIGHT,
            "deadline": self.DEADLINE_WEIGHT,
        }
        if db is not None:
            resolved = ScoringConfigService(db).resolve(
                engine_name=self.CONFIG_NAME,
                default_version=self.DEFAULT_VERSION,
                default_weights=self._weights,
            )
            self._scoring_version = resolved.version
            self._weights = resolved.weights
    
    # Discipline taxonomy (broad categories)
    DISCIPLINE_TAXONOMY = {
        "Computer Science": ["CS", "Computing", "Informatics", "AI", "Machine Learning"],
        "Biology": ["Life Sciences", "Molecular Biology", "Genetics", "Ecology"],
        "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Biochemistry"],
        "Physics": ["Theoretical Physics", "Experimental Physics", "Astrophysics"],
        "Mathematics": ["Pure Mathematics", "Applied Mathematics", "Statistics"],
        "Engineering": ["Electrical", "Mechanical", "Civil", "Biomedical"],
        "Social Sciences": ["Psychology", "Sociology", "Anthropology", "Economics"],
        "Humanities": ["History", "Literature", "Philosophy", "Languages"],
    }

    # Keywords used to map a granular stage name string → coarse ResearchStage enum.
    # Each list entry is a substring that, if present in the lowercased stage name,
    # identifies the corresponding ResearchStage.
    _STAGE_NAME_KEYWORDS: Dict[ResearchStage, List[str]] = {
        ResearchStage.EARLY: [
            "coursework", "literature review", "literature_review",
            "proposal", "qualifying", "prelim", "preliminary",
            "orientation", "onboarding",
        ],
        ResearchStage.MID: [
            "methodology", "data collection", "data_collection",
            "fieldwork", "field work", "field_work",
            "experiment", "survey", "interviews", "lab",
        ],
        ResearchStage.LATE: [
            "analysis", "writing", "drafting",
            "dissertation", "thesis", "manuscript", "conclusions",
        ],
        ResearchStage.POST_SUBMISSION: [
            "submission", "defense", "viva", "publication",
            "revision", "post submission", "post_submission", "job market",
        ],
    }
    
    def score_opportunity(
        self,
        opportunity: Opportunity,
        user_profile: UserProfile,
        timeline_context: Optional[TimelineContext] = None,
        current_date: Optional[date] = None
    ) -> RelevanceScore:
        """
        Score an opportunity for relevance to user.
        
        Args:
            opportunity: Opportunity to score
            user_profile: User's research profile
            timeline_context: Optional timeline context
            current_date: Optional current date (defaults to today)
            
        Returns:
            RelevanceScore with overall score and reasoning
        """
        if current_date is None:
            current_date = date.today()
        
        reason_tags: List[ReasonTag] = []
        
        # 1. Score discipline alignment
        discipline_score, discipline_tags = self._score_discipline(
            opportunity.disciplines,
            opportunity.keywords,
            user_profile.discipline,
            user_profile.subdisciplines,
            user_profile.keywords
        )
        reason_tags.extend(discipline_tags)
        
        # 2. Score research stage appropriateness.
        # If a granular stage name is available via TimelineContext, derive the
        # coarse ResearchStage from it so the two representations stay in sync.
        effective_stage = user_profile.research_stage
        if timeline_context and timeline_context.current_stage_name:
            effective_stage = self._map_stage_name_to_research_stage(
                timeline_context.current_stage_name
            )

        stage_score, stage_tags = self._score_stage(
            opportunity.eligible_stages,
            effective_stage
        )
        reason_tags.extend(stage_tags)

        # 3. Score timeline compatibility
        timeline_score, timeline_tags = self._score_timeline(
            opportunity.opportunity_type,
            opportunity.keywords,
            timeline_context
        )
        reason_tags.extend(timeline_tags)

        # 4. Score deadline suitability
        expected_completion = (
            timeline_context.expected_completion_date if timeline_context else None
        )
        deadline_score, deadline_tags = self._score_deadline(
            opportunity.deadline,
            current_date,
            opportunity.opportunity_type,
            expected_completion
        )
        reason_tags.extend(deadline_tags)
        
        # Add characteristic tags
        characteristic_tags = self._add_characteristic_tags(opportunity)
        reason_tags.extend(characteristic_tags)
        
        # Calculate overall score
        overall_score = (
            discipline_score * self._weights["discipline"] +
            stage_score * self._weights["stage"] +
            timeline_score * self._weights["timeline"] +
            deadline_score * self._weights["deadline"]
        )
        
        # Determine urgency and recommendation
        urgency_level = self._determine_urgency(deadline_score, overall_score)
        recommended_action = self._determine_action(overall_score, deadline_score, stage_score)
        
        # Generate explanation
        explanation = self._generate_explanation(
            opportunity,
            discipline_score,
            stage_score,
            timeline_score,
            deadline_score,
            reason_tags
        )
        
        return RelevanceScore(
            opportunity_id=opportunity.opportunity_id,
            overall_score=round(overall_score, 2),
            discipline_score=round(discipline_score, 2),
            stage_score=round(stage_score, 2),
            timeline_score=round(timeline_score, 2),
            deadline_score=round(deadline_score, 2),
            reason_tags=reason_tags,
            explanation=explanation,
            urgency_level=urgency_level,
            recommended_action=recommended_action
        )
    
    def rank_opportunities(
        self,
        opportunities: List[Opportunity],
        user_profile: UserProfile,
        timeline_context: Optional[TimelineContext] = None,
        current_date: Optional[date] = None,
        min_score: float = 0.0
    ) -> List[RelevanceScore]:
        """
        Rank multiple opportunities by relevance.
        
        Args:
            opportunities: List of opportunities to rank
            user_profile: User's research profile
            timeline_context: Optional timeline context
            current_date: Optional current date
            min_score: Minimum score threshold (0-100)
            
        Returns:
            List of RelevanceScore objects, sorted by overall_score descending
        """
        scores = []
        
        for opp in opportunities:
            score = self.score_opportunity(
                opportunity=opp,
                user_profile=user_profile,
                timeline_context=timeline_context,
                current_date=current_date
            )
            
            if score.overall_score >= min_score:
                scores.append(score)
        
        # Sort by overall_score descending
        scores.sort(key=lambda s: s.overall_score, reverse=True)
        
        return scores
    
    # Stage-mapping helpers

    def _map_stage_name_to_research_stage(self, stage_name: str) -> ResearchStage:
        """Map a granular stage name string to the coarse ResearchStage enum.

        Checks `_STAGE_NAME_KEYWORDS` in order (EARLY → MID → LATE → POST).
        Falls back to MID for unrecognised names so scoring degrades gracefully.

        Examples:
            "Literature Review"  → EARLY
            "Data Collection"    → MID
            "Writing"            → LATE
            "Defense"            → POST_SUBMISSION
        """
        stage_lower = stage_name.lower()
        for stage, keywords in self._STAGE_NAME_KEYWORDS.items():
            if any(kw in stage_lower for kw in keywords):
                return stage
        return ResearchStage.MID  # safe default

    def _build_timeline_context_from_stages(
        self,
        stages: list,
        milestones: list
    ) -> TimelineContext:
        """Build a basic TimelineContext from an ordered list of stage names and milestones.

        The first entry in ``stages`` is treated as the current stage at 0% progress.
        The next two entries (if present) become ``upcoming_stages``.

        Useful when callers have stage order data but haven't constructed a full
        TimelineContext yet.
        """
        current_stage = stages[0] if stages else "Unknown"
        upcoming = stages[1:3] if len(stages) > 1 else []
        return TimelineContext(
            current_stage_name=current_stage,
            current_stage_progress=0.0,
            upcoming_stages=upcoming,
            critical_milestones=list(milestones),
        )

    # Private scoring methods

    def _score_discipline(
        self,
        opportunity_disciplines: List[str],
        opportunity_keywords: List[str],
        user_discipline: str,
        user_subdisciplines: List[str],
        user_keywords: List[str]
    ) -> tuple[float, List[ReasonTag]]:
        """Score discipline alignment."""
        tags = []
        
        # Normalize for case-insensitive comparison
        opp_disciplines_lower = [d.lower() for d in opportunity_disciplines]
        user_discipline_lower = user_discipline.lower()
        user_subdisciplines_lower = [s.lower() for s in user_subdisciplines]
        
        # Exact match
        if user_discipline_lower in opp_disciplines_lower:
            tags.append(ReasonTag.EXACT_DISCIPLINE_MATCH)
            score = 100.0
        # Subdiscipline match
        elif any(sub in opp_disciplines_lower for sub in user_subdisciplines_lower):
            tags.append(ReasonTag.BROAD_DISCIPLINE_MATCH)
            score = 85.0
        # Broad category match
        elif self._check_broad_category_match(user_discipline, opportunity_disciplines):
            tags.append(ReasonTag.BROAD_DISCIPLINE_MATCH)
            score = 70.0
        # Keyword overlap
        elif self._check_keyword_overlap(opportunity_keywords, user_keywords, threshold=0.3):
            tags.append(ReasonTag.INTERDISCIPLINARY_MATCH)
            overlap_ratio = self._calculate_keyword_overlap(opportunity_keywords, user_keywords)
            score = 50.0 + (overlap_ratio * 30.0)  # 50-80 based on overlap
        else:
            tags.append(ReasonTag.DISCIPLINE_MISMATCH)
            score = 20.0
        
        return score, tags
    
    def _score_stage(
        self,
        eligible_stages: List[ResearchStage],
        user_stage: ResearchStage
    ) -> tuple[float, List[ReasonTag]]:
        """Score research stage appropriateness."""
        tags = []
        
        # Perfect match
        if user_stage in eligible_stages:
            tags.append(ReasonTag.STAGE_PERFECT_MATCH)
            score = 100.0
        # Adjacent stage (off by one)
        elif self._is_adjacent_stage(user_stage, eligible_stages):
            tags.append(ReasonTag.STAGE_GOOD_MATCH)
            score = 75.0
        # Any stage acceptable (e.g., all stages listed)
        elif len(eligible_stages) >= 3:
            tags.append(ReasonTag.STAGE_ACCEPTABLE)
            score = 60.0
        else:
            tags.append(ReasonTag.STAGE_MISMATCH)
            score = 30.0
        
        return score, tags
    
    def _score_timeline(
        self,
        opportunity_type: OpportunityType,
        opportunity_keywords: List[str],
        timeline_context: Optional[TimelineContext]
    ) -> tuple[float, List[ReasonTag]]:
        """Score timeline compatibility, incorporating stage progress.

        Score is a normalized weighted combination of three keyword signals
        (current stage, upcoming stages, milestones) plus an opportunity-type
        alignment signal — no additive bonuses on a fixed base.

        Progress drives the current-vs-upcoming weighting:
          - progress ~0.0 → current stage has 80% weight, upcoming 20%
          - progress ~1.0 → current stage has 20% weight, upcoming 80%

        Without any keyword matches the score degrades to a low-neutral range
        (~20-44) derived from the type-alignment signal only.
        """
        tags: List[ReasonTag] = []

        if timeline_context is None:
            return 50.0, tags

        opp_keywords_lower = [k.lower() for k in opportunity_keywords]
        current_stage_lower = timeline_context.current_stage_name.lower()
        # Clamp progress to [0, 1] in case callers supply out-of-range values
        progress = max(0.0, min(1.0, timeline_context.current_stage_progress))
        upcoming_stages_lower = [s.lower() for s in timeline_context.upcoming_stages]
        milestones_lower = [m.lower() for m in timeline_context.critical_milestones]

        # --- Binary keyword match signals ---
        current_match = any(kw in current_stage_lower for kw in opp_keywords_lower)
        upcoming_match = any(
            kw in stage
            for kw in opp_keywords_lower
            for stage in upcoming_stages_lower
        )
        milestone_match = any(
            kw in milestone
            for kw in opp_keywords_lower
            for milestone in milestones_lower
        )

        if current_match:
            tags.append(ReasonTag.ALIGNS_WITH_CURRENT_STAGE)
        if upcoming_match:
            tags.append(ReasonTag.ALIGNS_WITH_UPCOMING_STAGE)
        if milestone_match:
            tags.append(ReasonTag.SUPPORTS_MILESTONE)

        # --- Progress-aware weighting (current_weight + upcoming_weight == 1.0) ---
        current_weight = 0.80 - (progress * 0.60)   # 0.80 → 0.20
        upcoming_weight = 0.20 + (progress * 0.60)  # 0.20 → 0.80

        # Keyword component: normalize over max possible raw value.
        # Max raw = current_weight + upcoming_weight + 0.5 = 1.0 + 0.5 = 1.5
        keyword_raw = (
            float(current_match) * current_weight
            + float(upcoming_match) * upcoming_weight
            + float(milestone_match) * 0.5
        )
        keyword_component = keyword_raw / 1.5  # 0.0 to 1.0

        # --- Opportunity-type alignment component (0.0 to 1.0) ---
        type_component = 0.5  # neutral default
        if opportunity_type == OpportunityType.CONFERENCE:
            if "writing" in current_stage_lower or "analysis" in current_stage_lower:
                type_component = 0.8
        elif opportunity_type == OpportunityType.GRANT:
            if "data collection" in current_stage_lower or "methodology" in current_stage_lower:
                type_component = 0.8

        # --- Final score: 70% keyword, 30% type alignment ---
        # Without any keyword match, deflate to near-neutral (20–44 range).
        has_any_match = current_match or upcoming_match or milestone_match
        if has_any_match:
            score = (keyword_component * 0.70 + type_component * 0.30) * 100.0
        else:
            score = type_component * 30.0 + 20.0

        return min(score, 100.0), tags
    
    def _score_deadline(
        self,
        deadline: date,
        current_date: date,
        opportunity_type: OpportunityType,
        expected_completion_date: Optional[date] = None
    ) -> tuple[float, List[ReasonTag]]:
        """Score deadline suitability, accounting for expected completion date.

        After the base timing score is computed two optional adjustments apply:
        - If the deadline falls *after* ``expected_completion_date`` the student
          is unlikely to benefit, so the score is halved.
        - If the deadline falls within 90 days *before* ``expected_completion_date``
          (final phase alignment) the score receives a 10% boost, capped at 100.
        """
        tags = []
        days_until_deadline = (deadline - current_date).days

        # Missed deadline
        if days_until_deadline < 0:
            tags.append(ReasonTag.DEADLINE_MISSED)
            return 0.0, tags

        # Very tight (< 1 week)
        if days_until_deadline < 7:
            tags.append(ReasonTag.DEADLINE_VERY_TIGHT)
            score = 40.0
        # Tight (1–2 weeks)
        elif days_until_deadline < 14:
            tags.append(ReasonTag.DEADLINE_TIGHT)
            score = 65.0
        # Type-dependent optimal window
        elif opportunity_type in [OpportunityType.GRANT, OpportunityType.FELLOWSHIP]:
            # Grants need more prep time
            if 30 <= days_until_deadline <= 90:
                tags.append(ReasonTag.DEADLINE_OPTIMAL)
                score = 100.0
            elif 14 <= days_until_deadline < 30:
                score = 80.0
            elif 90 < days_until_deadline <= 180:
                score = 90.0
            else:  # > 180 days
                tags.append(ReasonTag.DEADLINE_TOO_FAR)
                score = 70.0
        else:  # Conference, workshop, competition
            if 14 <= days_until_deadline <= 60:
                tags.append(ReasonTag.DEADLINE_OPTIMAL)
                score = 100.0
            elif 60 < days_until_deadline <= 120:
                score = 85.0
            else:  # > 120 days
                tags.append(ReasonTag.DEADLINE_TOO_FAR)
                score = 75.0

        # Adjust for expected completion date when available
        if expected_completion_date is not None:
            if deadline > expected_completion_date:
                # Opportunity falls after graduation — student unlikely to benefit
                score *= 0.5
            elif (expected_completion_date - deadline).days <= 90:
                # Deadline aligns with the final phase of studies
                score = min(score * 1.10, 100.0)

        return score, tags
    
    def _add_characteristic_tags(self, opportunity: Opportunity) -> List[ReasonTag]:
        """Add tags based on opportunity characteristics."""
        tags = []
        
        if opportunity.prestige_level == "high":
            tags.append(ReasonTag.HIGH_PRESTIGE)
        
        if opportunity.opportunity_type in [OpportunityType.GRANT, OpportunityType.FELLOWSHIP]:
            tags.append(ReasonTag.FUNDING_OPPORTUNITY)
        
        if opportunity.opportunity_type == OpportunityType.CONFERENCE:
            tags.append(ReasonTag.PUBLICATION_VENUE)
            tags.append(ReasonTag.NETWORKING_OPPORTUNITY)
        
        if opportunity.opportunity_type in [OpportunityType.WORKSHOP, OpportunityType.CONFERENCE]:
            tags.append(ReasonTag.CAREER_BUILDING)
        
        return tags
    
    # Helper methods
    
    def _check_broad_category_match(
        self,
        user_discipline: str,
        opportunity_disciplines: List[str]
    ) -> bool:
        """Check if disciplines match at broad category level."""
        for broad_category, subcategories in self.DISCIPLINE_TAXONOMY.items():
            user_in_category = (
                user_discipline.lower() == broad_category.lower() or
                any(user_discipline.lower() in sub.lower() for sub in subcategories)
            )
            
            opp_in_category = any(
                opp_disc.lower() == broad_category.lower() or
                any(opp_disc.lower() in sub.lower() for sub in subcategories)
                for opp_disc in opportunity_disciplines
            )
            
            if user_in_category and opp_in_category:
                return True
        
        return False
    
    def _check_keyword_overlap(
        self,
        keywords1: List[str],
        keywords2: List[str],
        threshold: float = 0.3
    ) -> bool:
        """Check if keyword overlap exceeds threshold."""
        return self._calculate_keyword_overlap(keywords1, keywords2) >= threshold
    
    def _calculate_keyword_overlap(
        self,
        keywords1: List[str],
        keywords2: List[str]
    ) -> float:
        """Calculate keyword overlap ratio (Jaccard similarity)."""
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(k.lower() for k in keywords1)
        set2 = set(k.lower() for k in keywords2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _is_adjacent_stage(
        self,
        user_stage: ResearchStage,
        eligible_stages: List[ResearchStage]
    ) -> bool:
        """Check if user stage is adjacent to any eligible stage."""
        stage_order = [
            ResearchStage.EARLY,
            ResearchStage.MID,
            ResearchStage.LATE,
            ResearchStage.POST_SUBMISSION
        ]
        
        try:
            user_idx = stage_order.index(user_stage)
            
            for eligible_stage in eligible_stages:
                eligible_idx = stage_order.index(eligible_stage)
                if abs(user_idx - eligible_idx) == 1:
                    return True
        except ValueError:
            pass
        
        return False
    
    def _determine_urgency(self, deadline_score: float, overall_score: float) -> str:
        """Determine urgency level."""
        if deadline_score >= 80 and overall_score >= 70:
            return "high"
        elif deadline_score >= 65 and overall_score >= 50:
            return "medium"
        else:
            return "low"
    
    def _determine_action(
        self,
        overall_score: float,
        deadline_score: float,
        stage_score: float
    ) -> str:
        """Determine recommended action."""
        # High relevance + good deadline
        if overall_score >= 75 and deadline_score >= 65:
            return "apply_now"
        
        # High relevance + tight deadline
        if overall_score >= 70 and deadline_score >= 40:
            return "apply_now"
        
        # Good relevance + optimal deadline
        if overall_score >= 60 and deadline_score >= 80:
            return "prepare"
        
        # Moderate relevance
        if overall_score >= 50:
            return "monitor"
        
        # Low relevance
        return "skip"
    
    def _generate_explanation(
        self,
        opportunity: Opportunity,
        discipline_score: float,
        stage_score: float,
        timeline_score: float,
        deadline_score: float,
        reason_tags: List[ReasonTag]
    ) -> str:
        """Generate human-readable explanation."""
        parts = []
        
        # Discipline explanation
        if ReasonTag.EXACT_DISCIPLINE_MATCH in reason_tags:
            parts.append("Exact discipline match")
        elif ReasonTag.BROAD_DISCIPLINE_MATCH in reason_tags:
            parts.append("Broad discipline alignment")
        elif ReasonTag.INTERDISCIPLINARY_MATCH in reason_tags:
            parts.append("Interdisciplinary relevance")
        else:
            parts.append("Limited discipline match")
        
        # Stage explanation
        if ReasonTag.STAGE_PERFECT_MATCH in reason_tags:
            parts.append("perfect for your research stage")
        elif ReasonTag.STAGE_GOOD_MATCH in reason_tags:
            parts.append("suitable for your research stage")
        
        # Deadline explanation
        if ReasonTag.DEADLINE_OPTIMAL in reason_tags:
            parts.append("optimal deadline timing")
        elif ReasonTag.DEADLINE_TIGHT in reason_tags:
            parts.append("tight but achievable deadline")
        elif ReasonTag.DEADLINE_VERY_TIGHT in reason_tags:
            parts.append("very tight deadline")
        elif ReasonTag.DEADLINE_MISSED in reason_tags:
            parts.append("deadline has passed")
        
        # Timeline explanation
        if ReasonTag.ALIGNS_WITH_CURRENT_STAGE in reason_tags:
            parts.append("aligns with your current timeline stage")
        
        return "; ".join(parts).capitalize() + "."
