"""
Intervention Engine for generating personalized interventions.

Computes risk scores and generates interventions based on analytics,
health data, and timeline progress. Uses LLM for personalized messages
with template fallbacks.
"""
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.services.llm.client import LLMClient, get_llm_client, LLMError
from app.services.explainability_engine import ExplainabilityEngine
from app.services.intervention_templates import (
    get_dropout_risk_template,
    get_engagement_template,
    get_continuity_template,
    get_health_dimension_template,
    get_milestone_template,
    get_check_in_template,
    get_resources_by_category,
    INTERVENTION_TYPES,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

class InterventionType(str, Enum):
    """Types of interventions."""
    NOTIFICATION = "notification"
    EMAIL_SUGGESTION = "email_suggestion"
    MILESTONE_RESTRUCTURE = "milestone_restructure"
    CHECK_IN_SCHEDULE = "check_in_schedule"
    RESOURCE_RECOMMENDATION = "resource_recommendation"


class InterventionUrgency(str, Enum):
    """Urgency levels for interventions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class RiskScores:
    """Risk assessment scores."""
    dropout_risk: float  # 0.0-1.0 (higher = more at risk)
    engagement_score: float  # 0.0-1.0 (higher = more engaged)
    continuity_index: float  # 0.0-1.0 (higher = better continuity)

    # Component scores for transparency
    components: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dropout_risk": round(self.dropout_risk, 3),
            "engagement_score": round(self.engagement_score, 3),
            "continuity_index": round(self.continuity_index, 3),
            "components": {k: round(v, 3) for k, v in self.components.items()},
        }


@dataclass
class Intervention:
    """A single intervention recommendation."""
    intervention_id: str
    intervention_type: InterventionType
    urgency: InterventionUrgency
    title: str
    message: str
    actions: List[str]
    trigger_rule: str
    target_dimension: Optional[str] = None
    resources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "intervention_id": self.intervention_id,
            "intervention_type": self.intervention_type.value,
            "urgency": self.urgency.value,
            "title": self.title,
            "message": self.message,
            "actions": self.actions,
            "trigger_rule": self.trigger_rule,
            "target_dimension": self.target_dimension,
            "resources": self.resources,
            "metadata": self.metadata,
        }


@dataclass
class InterventionReport:
    """Complete intervention assessment report."""
    user_id: UUID
    generated_at: datetime
    risk_scores: RiskScores
    interventions: List[Intervention]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": str(self.user_id),
            "generated_at": self.generated_at.isoformat(),
            "risk_scores": self.risk_scores.to_dict(),
            "interventions": [i.to_dict() for i in self.interventions],
            "summary": self.summary,
        }


# =============================================================================
# LLM Personalization Prompt
# =============================================================================

PERSONALIZATION_SYSTEM_PROMPT = """You are an empathetic academic advisor helping personalize intervention messages for PhD students.

Given the context about a student's situation, personalize the provided intervention message to be more relevant and supportive.

Guidelines:
1. Maintain a warm, supportive, and professional tone
2. Reference specific details from their situation when appropriate
3. Avoid being preachy or condescending
4. Keep the message concise (2-3 sentences maximum)
5. Acknowledge their challenges without being alarmist

Respond with ONLY a JSON object:
{
    "personalized_title": "A personalized version of the title",
    "personalized_message": "A personalized version of the message"
}

No markdown fences, no preamble."""


# =============================================================================
# Intervention Engine
# =============================================================================

class InterventionEngine:
    """
    Engine for computing risk scores and generating interventions.

    Rules:
    - Deterministic risk score computation from input signals
    - Rule-based intervention generation based on thresholds
    - LLM personalization with template fallback
    - No predictions beyond immediate interventions

    Inputs:
    - Analytics summary (timeline status, milestone metrics, delays)
    - Health report (dimension scores, overall health)
    - Timeline stages and milestones

    Outputs:
    - Risk scores (dropout_risk, engagement_score, continuity_index)
    - List of interventions with urgency levels
    """

    # Risk thresholds for triggering interventions
    DROPOUT_RISK_HIGH = 0.7
    DROPOUT_RISK_MODERATE = 0.4
    ENGAGEMENT_LOW = 0.4
    ENGAGEMENT_DECLINING = 0.6
    CONTINUITY_POOR = 0.4
    CONTINUITY_MODERATE = 0.6

    # Health dimension thresholds (0-100 scale)
    HEALTH_CRITICAL = 35
    HEALTH_CONCERNING = 50

    def __init__(
        self,
        client: Optional[LLMClient] = None,
        use_llm: bool = True,
        include_explanations: bool = True,
    ):
        """
        Initialize the intervention engine.

        Args:
            client: Optional LLMClient instance. If not provided, uses singleton.
            use_llm: Whether to use LLM for personalization (default True).
            include_explanations: Whether to include explainability output (default True).
        """
        self._client = client
        self.use_llm = use_llm
        self.include_explanations = include_explanations
        self._explainability_engine: Optional[ExplainabilityEngine] = None

    @property
    def client(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def evaluate_and_intervene(
        self,
        user_id: UUID,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        timeline_stages: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate user status and generate interventions.

        Args:
            user_id: User ID
            analytics_summary: Analytics summary dict (from AnalyticsSummary)
            health_report: Health report dict (from JourneyHealthReport)
            timeline_stages: List of timeline stage dictionaries
            milestones: List of milestone dictionaries

        Returns:
            Dictionary containing:
            - risk_scores: Computed risk metrics
            - interventions: List of recommended interventions
            - summary: Overall assessment summary
        """
        logger.info(f"Evaluating interventions for user: {user_id}")

        # Step 1: Compute risk scores
        risk_scores = self._compute_risk_scores(
            analytics_summary=analytics_summary,
            health_report=health_report,
            timeline_stages=timeline_stages,
            milestones=milestones,
        )
        logger.debug(f"Risk scores computed: {risk_scores.to_dict()}")

        # Step 2: Generate interventions based on rules
        interventions = self._generate_interventions(
            user_id=user_id,
            risk_scores=risk_scores,
            analytics_summary=analytics_summary,
            health_report=health_report,
            milestones=milestones,
        )
        logger.info(f"Generated {len(interventions)} interventions")

        # Step 3: Personalize messages if LLM available
        if self.use_llm and interventions:
            interventions = self._personalize_interventions(
                interventions=interventions,
                analytics_summary=analytics_summary,
                health_report=health_report,
            )

        # Step 4: Create summary
        summary = self._create_summary(
            risk_scores=risk_scores,
            interventions=interventions,
        )

        report = InterventionReport(
            user_id=user_id,
            generated_at=datetime.now(),
            risk_scores=risk_scores,
            interventions=interventions,
            summary=summary,
        )

        result = report.to_dict()

        # Step 5: Generate explanations if enabled
        if self.include_explanations:
            try:
                if self._explainability_engine is None:
                    self._explainability_engine = ExplainabilityEngine(
                        client=self._client,
                        use_llm=self.use_llm,
                    )

                explanations = self._explainability_engine.explain(
                    risk_scores=result["risk_scores"],
                    analytics_summary=analytics_summary,
                    health_report=health_report,
                    interventions=result["interventions"],
                )
                result["explanations"] = explanations
                logger.info("Explainability report generated")
            except Exception as e:
                logger.error(f"Failed to generate explanations: {e}")
                result["explanations"] = None

        return result

    # =========================================================================
    # Risk Score Computation
    # =========================================================================

    def _compute_risk_scores(
        self,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        timeline_stages: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
    ) -> RiskScores:
        """
        Compute dropout risk, engagement score, and continuity index.

        All computations are deterministic and rule-based.

        Args:
            analytics_summary: Analytics data
            health_report: Health assessment data
            timeline_stages: Timeline stages
            milestones: Milestones

        Returns:
            RiskScores with all computed metrics
        """
        components = {}

        # =====================================================================
        # Dropout Risk (0.0-1.0, higher = more at risk)
        # =====================================================================
        # Factors: overdue critical milestones, health score, delay trends

        # Factor 1: Overdue critical milestones (0-0.3)
        overdue_critical = analytics_summary.get("overdue_critical_milestones", 0)
        critical_factor = min(overdue_critical * 0.15, 0.3)
        components["dropout_critical_factor"] = critical_factor

        # Factor 2: Health score inverse (0-0.3)
        health_score = health_report.get("overall_score", 50) or 50
        health_factor = (100 - health_score) / 100 * 0.3
        components["dropout_health_factor"] = health_factor

        # Factor 3: Timeline status (0-0.2)
        timeline_status = analytics_summary.get("timeline_status", "on_track")
        status_factor = {
            "on_track": 0.0,
            "delayed": 0.15,
            "completed": 0.0,
        }.get(timeline_status, 0.1)
        components["dropout_status_factor"] = status_factor

        # Factor 4: Average delay severity (0-0.2)
        avg_delay = analytics_summary.get("average_delay_days", 0) or 0
        delay_factor = min(avg_delay / 60, 1.0) * 0.2  # Cap at 60 days
        components["dropout_delay_factor"] = delay_factor

        dropout_risk = critical_factor + health_factor + status_factor + delay_factor
        dropout_risk = min(max(dropout_risk, 0.0), 1.0)

        # =====================================================================
        # Engagement Score (0.0-1.0, higher = more engaged)
        # =====================================================================
        # Factors: completion rate, recent progress, health engagement

        # Factor 1: Milestone completion (0-0.4)
        completion_pct = analytics_summary.get("milestone_completion_percentage", 0) or 0
        completion_factor = (completion_pct / 100) * 0.4
        components["engagement_completion_factor"] = completion_factor

        # Factor 2: Timeline status (0-0.3)
        status_engagement = {
            "on_track": 0.3,
            "delayed": 0.15,
            "completed": 0.3,
        }.get(timeline_status, 0.2)
        components["engagement_status_factor"] = status_engagement

        # Factor 3: Health score contribution (0-0.3)
        health_engagement = (health_score / 100) * 0.3
        components["engagement_health_factor"] = health_engagement

        engagement_score = completion_factor + status_engagement + health_engagement
        engagement_score = min(max(engagement_score, 0.0), 1.0)

        # =====================================================================
        # Continuity Index (0.0-1.0, higher = better continuity)
        # =====================================================================
        # Factors: milestone distribution, overdue ratio, timeline coherence

        # Factor 1: Overdue ratio inverse (0-0.4)
        total_milestones = analytics_summary.get("total_milestones", 1) or 1
        overdue_milestones = analytics_summary.get("overdue_milestones", 0) or 0
        overdue_ratio = overdue_milestones / total_milestones
        overdue_inverse = (1 - overdue_ratio) * 0.4
        components["continuity_overdue_factor"] = overdue_inverse

        # Factor 2: Completion consistency (0-0.3)
        pending = analytics_summary.get("pending_milestones", 0) or 0
        completed = analytics_summary.get("completed_milestones", 0) or 0
        if total_milestones > 0:
            consistency = (completed / total_milestones) * 0.3
        else:
            consistency = 0.15  # Default for no milestones
        components["continuity_consistency_factor"] = consistency

        # Factor 3: Timeline status coherence (0-0.3)
        coherence = {
            "on_track": 0.3,
            "delayed": 0.1,
            "completed": 0.3,
        }.get(timeline_status, 0.2)
        components["continuity_coherence_factor"] = coherence

        continuity_index = overdue_inverse + consistency + coherence
        continuity_index = min(max(continuity_index, 0.0), 1.0)

        return RiskScores(
            dropout_risk=dropout_risk,
            engagement_score=engagement_score,
            continuity_index=continuity_index,
            components=components,
        )

    # =========================================================================
    # Intervention Generation Rules
    # =========================================================================

    def _generate_interventions(
        self,
        user_id: UUID,
        risk_scores: RiskScores,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        milestones: List[Dict[str, Any]],
    ) -> List[Intervention]:
        """
        Generate interventions based on rule triggers.

        Rules evaluated:
        1. High dropout risk → notification + email_suggestion
        2. Moderate dropout risk → notification
        3. Low engagement → notification + resource_recommendation
        4. Poor continuity → milestone_restructure
        5. Critical health dimensions → notification + resource
        6. Concerning health dimensions → notification
        7. Overdue critical milestones → notification + check_in
        8. Multiple overdue milestones → milestone_restructure
        9. Declining health trend → check_in_schedule

        Args:
            user_id: User ID
            risk_scores: Computed risk scores
            analytics_summary: Analytics data
            health_report: Health report
            milestones: Milestones

        Returns:
            List of Intervention objects
        """
        interventions = []
        intervention_counter = 0

        def make_id() -> str:
            nonlocal intervention_counter
            intervention_counter += 1
            return f"int_{user_id.hex[:8]}_{intervention_counter:03d}"

        # =====================================================================
        # Rule 1: High dropout risk
        # =====================================================================
        if risk_scores.dropout_risk >= self.DROPOUT_RISK_HIGH:
            template = get_dropout_risk_template("high")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.NOTIFICATION,
                urgency=InterventionUrgency.HIGH,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="dropout_risk_high",
                target_dimension="dropout_risk",
                metadata={"dropout_risk": risk_scores.dropout_risk},
            ))

            # Also suggest email to supervisor
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.EMAIL_SUGGESTION,
                urgency=InterventionUrgency.HIGH,
                title="Reach Out to Supervisor",
                message="Consider sending an email to your supervisor to discuss your current challenges and explore support options.",
                actions=[
                    "Draft an email outlining your concerns",
                    "Suggest potential meeting times",
                    "Be honest about challenges you're facing",
                ],
                trigger_rule="dropout_risk_high_email",
                target_dimension="supervisor_relationship",
            ))

        # =====================================================================
        # Rule 2: Moderate dropout risk
        # =====================================================================
        elif risk_scores.dropout_risk >= self.DROPOUT_RISK_MODERATE:
            template = get_dropout_risk_template("moderate")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.NOTIFICATION,
                urgency=InterventionUrgency.MEDIUM,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="dropout_risk_moderate",
                target_dimension="dropout_risk",
                metadata={"dropout_risk": risk_scores.dropout_risk},
            ))

        # =====================================================================
        # Rule 3: Low engagement
        # =====================================================================
        if risk_scores.engagement_score < self.ENGAGEMENT_LOW:
            template = get_engagement_template("low")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.NOTIFICATION,
                urgency=InterventionUrgency.MEDIUM,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="engagement_low",
                target_dimension="engagement",
                metadata={"engagement_score": risk_scores.engagement_score},
            ))

            # Add productivity resources
            resources = get_resources_by_category("productivity")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.RESOURCE_RECOMMENDATION,
                urgency=InterventionUrgency.LOW,
                title="Productivity Resources",
                message="Here are some resources that might help you re-engage with your work.",
                actions=["Review the recommended resources", "Try one new productivity technique"],
                trigger_rule="engagement_low_resources",
                target_dimension="productivity",
                resources=resources,
            ))

        # =====================================================================
        # Rule 4: Poor continuity
        # =====================================================================
        if risk_scores.continuity_index < self.CONTINUITY_POOR:
            template = get_continuity_template("poor")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.MILESTONE_RESTRUCTURE,
                urgency=InterventionUrgency.HIGH,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="continuity_poor",
                target_dimension="timeline",
                metadata={"continuity_index": risk_scores.continuity_index},
            ))
        elif risk_scores.continuity_index < self.CONTINUITY_MODERATE:
            template = get_continuity_template("moderate")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.NOTIFICATION,
                urgency=InterventionUrgency.MEDIUM,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="continuity_moderate",
                target_dimension="timeline",
            ))

        # =====================================================================
        # Rule 5 & 6: Health dimension checks
        # =====================================================================
        dimension_scores = health_report.get("dimension_scores", {})

        for dimension_name, score_data in dimension_scores.items():
            # Handle both dict format and direct score
            if isinstance(score_data, dict):
                score = score_data.get("score", 50)
            else:
                score = score_data

            dimension_key = dimension_name.lower().replace(" ", "_")

            # Rule 5: Critical health dimension
            if score < self.HEALTH_CRITICAL:
                template = get_health_dimension_template(dimension_key, "critical")
                interventions.append(Intervention(
                    intervention_id=make_id(),
                    intervention_type=InterventionType.NOTIFICATION,
                    urgency=InterventionUrgency.HIGH,
                    title=template["title"],
                    message=template["message"],
                    actions=template["actions"],
                    trigger_rule=f"health_{dimension_key}_critical",
                    target_dimension=dimension_key,
                    resources=template.get("resources", []),
                    metadata={"dimension_score": score},
                ))

                # Add mental health resources if relevant
                if dimension_key in ["mental_wellbeing", "motivation", "work_life_balance"]:
                    resources = get_resources_by_category("mental_health")
                    interventions.append(Intervention(
                        intervention_id=make_id(),
                        intervention_type=InterventionType.RESOURCE_RECOMMENDATION,
                        urgency=InterventionUrgency.HIGH,
                        title="Support Resources",
                        message="These resources may help you address current challenges.",
                        actions=["Review available support services"],
                        trigger_rule=f"health_{dimension_key}_resources",
                        target_dimension=dimension_key,
                        resources=resources,
                    ))

            # Rule 6: Concerning health dimension
            elif score < self.HEALTH_CONCERNING:
                template = get_health_dimension_template(dimension_key, "concerning")
                interventions.append(Intervention(
                    intervention_id=make_id(),
                    intervention_type=InterventionType.NOTIFICATION,
                    urgency=InterventionUrgency.MEDIUM,
                    title=template["title"],
                    message=template["message"],
                    actions=template["actions"],
                    trigger_rule=f"health_{dimension_key}_concerning",
                    target_dimension=dimension_key,
                    metadata={"dimension_score": score},
                ))

        # =====================================================================
        # Rule 7: Overdue critical milestones
        # =====================================================================
        overdue_critical = analytics_summary.get("overdue_critical_milestones", 0)
        if overdue_critical > 0:
            template = get_milestone_template("overdue_critical")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.NOTIFICATION,
                urgency=InterventionUrgency.HIGH,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="milestone_overdue_critical",
                target_dimension="milestones",
                metadata={"overdue_critical_count": overdue_critical},
            ))

            # Schedule check-in
            check_in = get_check_in_template("weekly")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.CHECK_IN_SCHEDULE,
                urgency=InterventionUrgency.HIGH,
                title=check_in["title"],
                message=check_in["message"],
                actions=check_in.get("suggested_agenda", []),
                trigger_rule="milestone_critical_checkin",
                target_dimension="milestones",
                metadata={"frequency": check_in["frequency"]},
            ))

        # =====================================================================
        # Rule 8: Multiple overdue milestones (non-critical)
        # =====================================================================
        overdue_total = analytics_summary.get("overdue_milestones", 0)
        if overdue_total >= 3 and overdue_critical == 0:
            template = get_milestone_template("multiple_overdue")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.MILESTONE_RESTRUCTURE,
                urgency=InterventionUrgency.MEDIUM,
                title=template["title"],
                message=template["message"],
                actions=template["actions"],
                trigger_rule="milestone_multiple_overdue",
                target_dimension="milestones",
                metadata={"overdue_count": overdue_total},
            ))

        # =====================================================================
        # Rule 9: Low overall health (suggests check-in)
        # =====================================================================
        overall_health = health_report.get("overall_score")
        if overall_health is not None and overall_health < self.HEALTH_CONCERNING:
            # Recommend biweekly check-ins
            check_in = get_check_in_template("biweekly")
            interventions.append(Intervention(
                intervention_id=make_id(),
                intervention_type=InterventionType.CHECK_IN_SCHEDULE,
                urgency=InterventionUrgency.MEDIUM,
                title=check_in["title"],
                message=check_in["message"],
                actions=check_in.get("suggested_agenda", []),
                trigger_rule="health_overall_checkin",
                target_dimension="overall_health",
                metadata={"frequency": check_in["frequency"], "health_score": overall_health},
            ))

        return interventions

    # =========================================================================
    # LLM Personalization
    # =========================================================================

    def _personalize_interventions(
        self,
        interventions: List[Intervention],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> List[Intervention]:
        """
        Personalize intervention messages using LLM.

        Falls back to templates if LLM fails.

        Args:
            interventions: List of interventions to personalize
            analytics_summary: Analytics context
            health_report: Health context

        Returns:
            Interventions with personalized messages
        """
        # Build context for personalization
        context = self._build_personalization_context(analytics_summary, health_report)

        for intervention in interventions:
            try:
                personalized = self._personalize_single_intervention(
                    intervention=intervention,
                    context=context,
                )
                if personalized:
                    intervention.title = personalized.get("title", intervention.title)
                    intervention.message = personalized.get("message", intervention.message)
            except LLMError as e:
                logger.warning(f"LLM personalization failed for {intervention.intervention_id}: {e}")
                # Keep template message
            except Exception as e:
                logger.error(f"Unexpected error personalizing {intervention.intervention_id}: {e}")
                # Keep template message

        return interventions

    def _build_personalization_context(
        self,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> str:
        """Build context string for LLM personalization."""
        parts = ["Student context:"]

        # Timeline status
        status = analytics_summary.get("timeline_status", "unknown")
        parts.append(f"- Timeline status: {status}")

        # Completion progress
        completion = analytics_summary.get("milestone_completion_percentage", 0)
        parts.append(f"- Milestone completion: {completion:.1f}%")

        # Delays
        overdue = analytics_summary.get("overdue_milestones", 0)
        if overdue > 0:
            parts.append(f"- Overdue milestones: {overdue}")

        avg_delay = analytics_summary.get("average_delay_days", 0)
        if avg_delay > 0:
            parts.append(f"- Average delay: {avg_delay:.1f} days")

        # Health score
        health_score = health_report.get("overall_score")
        if health_score is not None:
            parts.append(f"- Overall health score: {health_score:.1f}/100")

        # Dimension challenges
        dimension_scores = health_report.get("dimension_scores", {})
        low_dimensions = []
        for dim, score_data in dimension_scores.items():
            score = score_data.get("score", 50) if isinstance(score_data, dict) else score_data
            if score < 50:
                low_dimensions.append(dim.replace("_", " "))

        if low_dimensions:
            parts.append(f"- Challenging areas: {', '.join(low_dimensions)}")

        return "\n".join(parts)

    def _personalize_single_intervention(
        self,
        intervention: Intervention,
        context: str,
    ) -> Optional[Dict[str, str]]:
        """
        Personalize a single intervention using LLM.

        Args:
            intervention: Intervention to personalize
            context: Student context string

        Returns:
            Dict with personalized title and message, or None if failed
        """
        user_prompt = f"""{context}

Intervention to personalize:
- Type: {intervention.intervention_type.value}
- Urgency: {intervention.urgency.value}
- Target: {intervention.target_dimension or 'general'}
- Original title: {intervention.title}
- Original message: {intervention.message}

Provide a personalized version that references the student's specific situation."""

        try:
            result = self.client.call(
                system_prompt=PERSONALIZATION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                max_tokens=512,
            )

            return {
                "title": result.get("personalized_title", intervention.title),
                "message": result.get("personalized_message", intervention.message),
            }
        except Exception:
            return None

    # =========================================================================
    # Summary Generation
    # =========================================================================

    def _create_summary(
        self,
        risk_scores: RiskScores,
        interventions: List[Intervention],
    ) -> Dict[str, Any]:
        """
        Create intervention summary.

        Args:
            risk_scores: Computed risk scores
            interventions: Generated interventions

        Returns:
            Summary dictionary
        """
        # Count by urgency
        urgency_counts = {"high": 0, "medium": 0, "low": 0}
        for intervention in interventions:
            urgency_counts[intervention.urgency.value] += 1

        # Count by type
        type_counts = {}
        for intervention in interventions:
            type_name = intervention.intervention_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Risk level classification
        if risk_scores.dropout_risk >= self.DROPOUT_RISK_HIGH:
            risk_level = "high"
        elif risk_scores.dropout_risk >= self.DROPOUT_RISK_MODERATE:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return {
            "total_interventions": len(interventions),
            "by_urgency": urgency_counts,
            "by_type": type_counts,
            "risk_level": risk_level,
            "requires_immediate_attention": urgency_counts["high"] > 0,
            "primary_concerns": [
                i.target_dimension
                for i in interventions
                if i.urgency == InterventionUrgency.HIGH
            ],
        }


# =============================================================================
# Convenience Function
# =============================================================================

def evaluate_and_intervene(
    user_id: UUID,
    analytics_summary: Dict[str, Any],
    health_report: Dict[str, Any],
    timeline_stages: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]],
    use_llm: bool = True,
    include_explanations: bool = True,
) -> Dict[str, Any]:
    """
    Evaluate user status and generate interventions.

    Convenience function that creates an engine and calls evaluate_and_intervene.

    Args:
        user_id: User ID
        analytics_summary: Analytics summary from AnalyticsEngine
        health_report: Health report from JourneyHealthEngine
        timeline_stages: Timeline stages
        milestones: Milestones
        use_llm: Whether to use LLM for personalization
        include_explanations: Whether to include explainability output

    Returns:
        Intervention report dictionary with optional explanations
    """
    engine = InterventionEngine(
        use_llm=use_llm,
        include_explanations=include_explanations,
    )
    return engine.evaluate_and_intervene(
        user_id=user_id,
        analytics_summary=analytics_summary,
        health_report=health_report,
        timeline_stages=timeline_stages,
        milestones=milestones,
    )
