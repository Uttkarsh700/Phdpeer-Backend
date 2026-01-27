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
    1. Discipline alignment (40% weight)
    2. Research stage appropriateness (30% weight)
    3. Timeline compatibility (15% weight)
    4. Deadline suitability (15% weight)
    """
    
    # Weights for overall score
    DISCIPLINE_WEIGHT = 0.40
    STAGE_WEIGHT = 0.30
    TIMELINE_WEIGHT = 0.15
    DEADLINE_WEIGHT = 0.15
    
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
        
        # 2. Score research stage appropriateness
        stage_score, stage_tags = self._score_stage(
            opportunity.eligible_stages,
            user_profile.research_stage
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
        deadline_score, deadline_tags = self._score_deadline(
            opportunity.deadline,
            current_date,
            opportunity.opportunity_type
        )
        reason_tags.extend(deadline_tags)
        
        # Add characteristic tags
        characteristic_tags = self._add_characteristic_tags(opportunity)
        reason_tags.extend(characteristic_tags)
        
        # Calculate overall score
        overall_score = (
            discipline_score * self.DISCIPLINE_WEIGHT +
            stage_score * self.STAGE_WEIGHT +
            timeline_score * self.TIMELINE_WEIGHT +
            deadline_score * self.DEADLINE_WEIGHT
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
        """Score timeline compatibility."""
        tags = []
        
        if timeline_context is None:
            # No timeline context, use neutral score
            return 50.0, tags
        
        score = 50.0  # Base score
        
        # Check if opportunity aligns with current stage
        current_stage_lower = timeline_context.current_stage_name.lower()
        opp_keywords_lower = [k.lower() for k in opportunity_keywords]
        
        # Direct stage name match
        if any(keyword in current_stage_lower for keyword in opp_keywords_lower):
            tags.append(ReasonTag.ALIGNS_WITH_CURRENT_STAGE)
            score += 30.0
        
        # Check upcoming stages
        upcoming_stages_lower = [s.lower() for s in timeline_context.upcoming_stages]
        if any(keyword in stage for keyword in opp_keywords_lower for stage in upcoming_stages_lower):
            tags.append(ReasonTag.ALIGNS_WITH_UPCOMING_STAGE)
            score += 20.0
        
        # Check critical milestones
        milestones_lower = [m.lower() for m in timeline_context.critical_milestones]
        if any(keyword in milestone for keyword in opp_keywords_lower for milestone in milestones_lower):
            tags.append(ReasonTag.SUPPORTS_MILESTONE)
            score += 20.0
        
        # Opportunity type alignment
        if opportunity_type == OpportunityType.CONFERENCE:
            # Conferences useful in mid-late stages
            if "writing" in current_stage_lower or "analysis" in current_stage_lower:
                score += 10.0
        elif opportunity_type == OpportunityType.GRANT:
            # Grants useful in early-mid stages
            if "data collection" in current_stage_lower or "methodology" in current_stage_lower:
                score += 10.0
        
        return min(score, 100.0), tags
    
    def _score_deadline(
        self,
        deadline: date,
        current_date: date,
        opportunity_type: OpportunityType
    ) -> tuple[float, List[ReasonTag]]:
        """Score deadline suitability."""
        tags = []
        
        days_until_deadline = (deadline - current_date).days
        
        # Missed deadline
        if days_until_deadline < 0:
            tags.append(ReasonTag.DEADLINE_MISSED)
            return 0.0, tags
        
        # Very tight deadline (< 1 week)
        if days_until_deadline < 7:
            tags.append(ReasonTag.DEADLINE_VERY_TIGHT)
            return 40.0, tags
        
        # Tight deadline (1-2 weeks)
        if days_until_deadline < 14:
            tags.append(ReasonTag.DEADLINE_TIGHT)
            return 65.0, tags
        
        # Optimal window depends on opportunity type
        if opportunity_type in [OpportunityType.GRANT, OpportunityType.FELLOWSHIP]:
            # Grants need more prep time
            if 30 <= days_until_deadline <= 90:
                tags.append(ReasonTag.DEADLINE_OPTIMAL)
                return 100.0, tags
            elif 14 <= days_until_deadline < 30:
                return 80.0, tags
            elif 90 < days_until_deadline <= 180:
                return 90.0, tags
            else:  # > 180 days
                tags.append(ReasonTag.DEADLINE_TOO_FAR)
                return 70.0, tags
        
        else:  # Conference, workshop, competition
            # Less prep time needed
            if 14 <= days_until_deadline <= 60:
                tags.append(ReasonTag.DEADLINE_OPTIMAL)
                return 100.0, tags
            elif 60 < days_until_deadline <= 120:
                return 85.0, tags
            else:  # > 120 days
                tags.append(ReasonTag.DEADLINE_TOO_FAR)
                return 75.0, tags
    
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
