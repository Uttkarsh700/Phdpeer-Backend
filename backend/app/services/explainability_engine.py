"""
Explainability Engine for generating human-readable explanations of risk scores and interventions.

Provides plain English explanations of why certain risk scores were computed
and why specific interventions were triggered.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.llm.client import LLMClient, get_llm_client, LLMError

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Risk level thresholds
RISK_LEVELS = {
    "dropout_risk": [
        (0.7, "high"),
        (0.4, "moderate"),
        (0.0, "low"),
    ],
    "engagement_score": [
        (0.7, "high"),
        (0.4, "moderate"),
        (0.0, "low"),
    ],
    "continuity_index": [
        (0.7, "good"),
        (0.4, "moderate"),
        (0.0, "poor"),
    ],
}

# Component factor descriptions for plain English explanations
FACTOR_DESCRIPTIONS = {
    # Dropout risk factors
    "dropout_critical_factor": {
        "name": "Overdue Critical Milestones",
        "high_template": "{count} critical milestone(s) are overdue",
        "low_template": "no critical milestones are overdue",
        "threshold": 0.1,
    },
    "dropout_health_factor": {
        "name": "Health Score Impact",
        "high_template": "overall health score is low ({score}/100)",
        "low_template": "health score is stable",
        "threshold": 0.1,
    },
    "dropout_status_factor": {
        "name": "Timeline Status",
        "high_template": "timeline is delayed",
        "low_template": "timeline is on track",
        "threshold": 0.05,
    },
    "dropout_delay_factor": {
        "name": "Average Delay Severity",
        "high_template": "average delay is {days} days",
        "low_template": "delays are minimal",
        "threshold": 0.05,
    },
    # Engagement factors
    "engagement_completion_factor": {
        "name": "Milestone Completion",
        "high_template": "milestone completion is strong ({pct}%)",
        "low_template": "milestone completion is low ({pct}%)",
        "threshold": 0.15,
        "inverse": True,  # Higher is better
    },
    "engagement_status_factor": {
        "name": "Timeline Progress",
        "high_template": "timeline is progressing well",
        "low_template": "timeline progress has stalled",
        "threshold": 0.1,
        "inverse": True,
    },
    "engagement_health_factor": {
        "name": "Health Engagement",
        "high_template": "overall wellbeing supports engagement",
        "low_template": "low wellbeing is affecting engagement",
        "threshold": 0.1,
        "inverse": True,
    },
    # Continuity factors
    "continuity_overdue_factor": {
        "name": "Overdue Ratio",
        "high_template": "few milestones are overdue",
        "low_template": "{count} milestones are overdue",
        "threshold": 0.15,
        "inverse": True,
    },
    "continuity_consistency_factor": {
        "name": "Completion Consistency",
        "high_template": "milestone completion is consistent",
        "low_template": "milestone completion has gaps",
        "threshold": 0.1,
        "inverse": True,
    },
    "continuity_coherence_factor": {
        "name": "Timeline Coherence",
        "high_template": "timeline structure is coherent",
        "low_template": "timeline needs restructuring",
        "threshold": 0.1,
        "inverse": True,
    },
}

# Intervention trigger rule descriptions
TRIGGER_DESCRIPTIONS = {
    "dropout_risk_high": "high dropout risk score ({score:.2f})",
    "dropout_risk_high_email": "high dropout risk requiring supervisor outreach",
    "dropout_risk_moderate": "elevated dropout risk ({score:.2f})",
    "engagement_low": "low engagement score ({score:.2f})",
    "engagement_low_resources": "low engagement requiring productivity support",
    "continuity_poor": "poor timeline continuity ({score:.2f})",
    "continuity_moderate": "moderate timeline continuity issues",
    "milestone_overdue_critical": "{count} critical milestone(s) overdue",
    "milestone_critical_checkin": "critical milestone delays requiring check-in",
    "milestone_multiple_overdue": "{count} milestones overdue",
    "health_overall_checkin": "overall health score ({score:.1f}) below threshold",
}


# =============================================================================
# LLM Prompts
# =============================================================================

NARRATIVE_SYSTEM_PROMPT = """You are an academic advisor writing a brief status summary for a PhD student's progress dashboard.

Write a 3-5 sentence paragraph that:
1. Describes the student's current situation clearly
2. Highlights the most important concerns or achievements
3. Provides actionable context without being alarmist
4. Uses a supportive, professional tone

The summary should be readable by both the student and their supervisor.

Respond with ONLY a JSON object:
{
    "narrative": "Your 3-5 sentence summary here."
}

No markdown fences, no preamble."""


# =============================================================================
# Explainability Engine
# =============================================================================

class ExplainabilityEngine:
    """
    Engine for generating human-readable explanations of risk assessments.

    Capabilities:
    - Explains risk scores by analyzing component factor contributions
    - Provides reasoning for each triggered intervention
    - Generates LLM-powered narrative summaries with template fallback
    - Identifies trends from longitudinal data

    All explanations are deterministic except for the LLM narrative,
    which falls back to templates if LLM is unavailable.
    """

    def __init__(self, client: Optional[LLMClient] = None, use_llm: bool = True):
        """
        Initialize the explainability engine.

        Args:
            client: Optional LLMClient instance. If not provided, uses singleton.
            use_llm: Whether to use LLM for narrative generation.
        """
        self._client = client
        self.use_llm = use_llm

    @property
    def client(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def explain(
        self,
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        interventions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanations for risk assessment.

        Args:
            risk_scores: Risk scores dict from InterventionEngine
            analytics_summary: Analytics summary dict
            health_report: Health report dict
            interventions: List of intervention dicts

        Returns:
            Dictionary containing:
            - score_explanations: Explanation for each risk score
            - intervention_explanations: Interventions with reasoning
            - narrative_summary: LLM-generated paragraph
            - trends: Improving/declining signals
            - generated_at: Timestamp
        """
        logger.info("Generating explainability report")

        # Step 1: Explain each risk score
        score_explanations = self._explain_risk_scores(
            risk_scores=risk_scores,
            analytics_summary=analytics_summary,
            health_report=health_report,
        )

        # Step 2: Explain each intervention
        intervention_explanations = self._explain_interventions(
            interventions=interventions,
            risk_scores=risk_scores,
            analytics_summary=analytics_summary,
            health_report=health_report,
        )

        # Step 3: Generate narrative summary
        narrative_summary = self._generate_narrative(
            risk_scores=risk_scores,
            analytics_summary=analytics_summary,
            health_report=health_report,
            score_explanations=score_explanations,
        )

        # Step 4: Identify trends
        trends = self._identify_trends(
            analytics_summary=analytics_summary,
            health_report=health_report,
        )

        return {
            "score_explanations": score_explanations,
            "intervention_explanations": intervention_explanations,
            "narrative_summary": narrative_summary,
            "trends": trends,
            "generated_at": datetime.now().isoformat(),
        }

    # =========================================================================
    # Risk Score Explanations
    # =========================================================================

    def _explain_risk_scores(
        self,
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate explanations for each risk score.

        Args:
            risk_scores: Risk scores with components
            analytics_summary: Analytics data
            health_report: Health data

        Returns:
            Dictionary with explanations for each score
        """
        explanations = {}
        components = risk_scores.get("components", {})

        # Dropout Risk
        explanations["dropout_risk"] = self._explain_dropout_risk(
            score=risk_scores.get("dropout_risk", 0),
            components=components,
            analytics_summary=analytics_summary,
            health_report=health_report,
        )

        # Engagement Score
        explanations["engagement_score"] = self._explain_engagement_score(
            score=risk_scores.get("engagement_score", 0),
            components=components,
            analytics_summary=analytics_summary,
            health_report=health_report,
        )

        # Continuity Index
        explanations["continuity_index"] = self._explain_continuity_index(
            score=risk_scores.get("continuity_index", 0),
            components=components,
            analytics_summary=analytics_summary,
        )

        return explanations

    def _explain_dropout_risk(
        self,
        score: float,
        components: Dict[str, float],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Explain dropout risk score."""
        level = self._get_risk_level("dropout_risk", score)

        # Get contributing factors
        factors = [
            ("dropout_critical_factor", components.get("dropout_critical_factor", 0)),
            ("dropout_health_factor", components.get("dropout_health_factor", 0)),
            ("dropout_status_factor", components.get("dropout_status_factor", 0)),
            ("dropout_delay_factor", components.get("dropout_delay_factor", 0)),
        ]

        # Sort by contribution (highest first)
        factors.sort(key=lambda x: x[1], reverse=True)

        # Get primary factors (those above threshold)
        primary_factors = []
        factor_descriptions = []

        for factor_name, factor_value in factors:
            factor_info = FACTOR_DESCRIPTIONS.get(factor_name, {})
            threshold = factor_info.get("threshold", 0.05)

            if factor_value >= threshold:
                # Build description based on actual data
                description = self._build_factor_description(
                    factor_name=factor_name,
                    factor_value=factor_value,
                    analytics_summary=analytics_summary,
                    health_report=health_report,
                )
                primary_factors.append({
                    "name": factor_info.get("name", factor_name),
                    "value": round(factor_value, 3),
                    "contribution_pct": round((factor_value / max(score, 0.001)) * 100, 1),
                    "description": description,
                })
                factor_descriptions.append(description)

        # Build plain English explanation
        if level == "high":
            plain_english = f"Dropout risk is high ({score:.2f})"
        elif level == "moderate":
            plain_english = f"Dropout risk is moderate ({score:.2f})"
        else:
            plain_english = f"Dropout risk is low ({score:.2f})"

        if factor_descriptions:
            plain_english += f" primarily because {self._join_factors(factor_descriptions)}"

        return {
            "score": round(score, 3),
            "level": level,
            "primary_factors": primary_factors[:3],  # Top 3 factors
            "plain_english": plain_english,
        }

    def _explain_engagement_score(
        self,
        score: float,
        components: Dict[str, float],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Explain engagement score."""
        level = self._get_risk_level("engagement_score", score)

        factors = [
            ("engagement_completion_factor", components.get("engagement_completion_factor", 0)),
            ("engagement_status_factor", components.get("engagement_status_factor", 0)),
            ("engagement_health_factor", components.get("engagement_health_factor", 0)),
        ]

        # Sort by contribution
        factors.sort(key=lambda x: x[1], reverse=True)

        primary_factors = []
        positive_descriptions = []
        negative_descriptions = []

        for factor_name, factor_value in factors:
            factor_info = FACTOR_DESCRIPTIONS.get(factor_name, {})
            threshold = factor_info.get("threshold", 0.1)
            max_contribution = 0.4 if "completion" in factor_name else 0.3

            # Determine if this is a positive or negative signal
            is_strong = factor_value >= max_contribution * 0.7

            description = self._build_factor_description(
                factor_name=factor_name,
                factor_value=factor_value,
                analytics_summary=analytics_summary,
                health_report=health_report,
                is_positive=is_strong,
            )

            primary_factors.append({
                "name": factor_info.get("name", factor_name),
                "value": round(factor_value, 3),
                "contribution_pct": round((factor_value / max(score, 0.001)) * 100, 1),
                "description": description,
                "is_strength": is_strong,
            })

            if is_strong:
                positive_descriptions.append(description)
            elif factor_value < threshold:
                negative_descriptions.append(description)

        # Build plain English
        if level == "high":
            plain_english = f"Engagement is strong ({score:.2f})"
            if positive_descriptions:
                plain_english += f" because {self._join_factors(positive_descriptions)}"
        elif level == "moderate":
            plain_english = f"Engagement is moderate ({score:.2f})"
        else:
            plain_english = f"Engagement is low ({score:.2f})"
            if negative_descriptions:
                plain_english += f" because {self._join_factors(negative_descriptions)}"

        return {
            "score": round(score, 3),
            "level": level,
            "primary_factors": primary_factors,
            "plain_english": plain_english,
        }

    def _explain_continuity_index(
        self,
        score: float,
        components: Dict[str, float],
        analytics_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Explain continuity index."""
        level = self._get_risk_level("continuity_index", score)

        factors = [
            ("continuity_overdue_factor", components.get("continuity_overdue_factor", 0)),
            ("continuity_consistency_factor", components.get("continuity_consistency_factor", 0)),
            ("continuity_coherence_factor", components.get("continuity_coherence_factor", 0)),
        ]

        factors.sort(key=lambda x: x[1], reverse=True)

        primary_factors = []
        descriptions = []

        for factor_name, factor_value in factors:
            factor_info = FACTOR_DESCRIPTIONS.get(factor_name, {})
            max_contribution = 0.4 if "overdue" in factor_name else 0.3
            is_strong = factor_value >= max_contribution * 0.7

            description = self._build_factor_description(
                factor_name=factor_name,
                factor_value=factor_value,
                analytics_summary=analytics_summary,
                health_report={},
                is_positive=is_strong,
            )

            primary_factors.append({
                "name": factor_info.get("name", factor_name),
                "value": round(factor_value, 3),
                "contribution_pct": round((factor_value / max(score, 0.001)) * 100, 1),
                "description": description,
            })

            if not is_strong:
                descriptions.append(description)

        # Build plain English
        if level == "good":
            plain_english = f"Timeline continuity is good ({score:.2f})"
        elif level == "moderate":
            plain_english = f"Timeline continuity is moderate ({score:.2f})"
        else:
            plain_english = f"Timeline continuity is poor ({score:.2f})"
            if descriptions:
                plain_english += f" because {self._join_factors(descriptions)}"

        return {
            "score": round(score, 3),
            "level": level,
            "primary_factors": primary_factors,
            "plain_english": plain_english,
        }

    def _build_factor_description(
        self,
        factor_name: str,
        factor_value: float,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        is_positive: bool = False,
    ) -> str:
        """Build a description for a specific factor using actual data."""
        factor_info = FACTOR_DESCRIPTIONS.get(factor_name, {})

        # Use appropriate template
        if factor_info.get("inverse", False):
            # For inverse factors (higher = better), swap templates
            template = factor_info.get("high_template" if is_positive else "low_template", "")
        else:
            # For regular factors (higher = worse)
            template = factor_info.get("high_template" if factor_value > 0.05 else "low_template", "")

        # Fill in template with actual data
        if "critical" in factor_name:
            count = analytics_summary.get("overdue_critical_milestones", 0)
            return template.format(count=count)
        elif "health" in factor_name:
            score = health_report.get("overall_score", 50) or 50
            return template.format(score=round(score))
        elif "delay" in factor_name:
            days = analytics_summary.get("average_delay_days", 0) or 0
            return template.format(days=round(days))
        elif "completion" in factor_name:
            pct = analytics_summary.get("milestone_completion_percentage", 0) or 0
            return template.format(pct=round(pct))
        elif "overdue" in factor_name and "continuity" in factor_name:
            count = analytics_summary.get("overdue_milestones", 0)
            return template.format(count=count)

        return template

    def _get_risk_level(self, score_type: str, score: float) -> str:
        """Get risk level label for a score."""
        thresholds = RISK_LEVELS.get(score_type, [(0.7, "high"), (0.4, "moderate"), (0.0, "low")])
        for threshold, level in thresholds:
            if score >= threshold:
                return level
        return thresholds[-1][1]

    def _join_factors(self, descriptions: List[str]) -> str:
        """Join factor descriptions with proper grammar."""
        if not descriptions:
            return ""
        if len(descriptions) == 1:
            return descriptions[0]
        if len(descriptions) == 2:
            return f"{descriptions[0]} and {descriptions[1]}"
        return f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}"

    # =========================================================================
    # Intervention Explanations
    # =========================================================================

    def _explain_interventions(
        self,
        interventions: List[Dict[str, Any]],
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Add reasoning to each intervention.

        Args:
            interventions: List of intervention dicts
            risk_scores: Risk scores
            analytics_summary: Analytics data
            health_report: Health data

        Returns:
            Interventions with added reasoning field
        """
        explained = []

        for intervention in interventions:
            # Copy the intervention
            explained_intervention = dict(intervention)

            # Generate reasoning based on trigger rule
            reasoning = self._generate_intervention_reasoning(
                intervention=intervention,
                risk_scores=risk_scores,
                analytics_summary=analytics_summary,
                health_report=health_report,
            )

            explained_intervention["reasoning"] = reasoning
            explained.append(explained_intervention)

        return explained

    def _generate_intervention_reasoning(
        self,
        intervention: Dict[str, Any],
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> str:
        """Generate reasoning for why an intervention was triggered."""
        trigger_rule = intervention.get("trigger_rule", "")
        metadata = intervention.get("metadata", {})
        target = intervention.get("target_dimension", "")

        # Start with the base trigger description
        parts = []

        # Get trigger description template
        if trigger_rule in TRIGGER_DESCRIPTIONS:
            template = TRIGGER_DESCRIPTIONS[trigger_rule]

            # Fill in template values
            if "dropout_risk" in trigger_rule:
                parts.append(template.format(score=risk_scores.get("dropout_risk", 0)))
            elif "engagement" in trigger_rule:
                parts.append(template.format(score=risk_scores.get("engagement_score", 0)))
            elif "continuity" in trigger_rule:
                parts.append(template.format(score=risk_scores.get("continuity_index", 0)))
            elif "milestone" in trigger_rule:
                if "critical" in trigger_rule:
                    count = analytics_summary.get("overdue_critical_milestones", 0)
                else:
                    count = analytics_summary.get("overdue_milestones", 0)
                parts.append(template.format(count=count))
            elif "health" in trigger_rule:
                score = health_report.get("overall_score", 50) or 50
                parts.append(template.format(score=score))
            else:
                parts.append(template)
        else:
            # Generic trigger description
            parts.append(f"triggered by {trigger_rule.replace('_', ' ')}")

        # Add context about contributing factors
        if "dropout" in trigger_rule:
            # Add what's driving dropout risk
            drivers = []
            overdue_critical = analytics_summary.get("overdue_critical_milestones", 0)
            if overdue_critical > 0:
                drivers.append(f"{overdue_critical} overdue critical milestone(s)")
            health_score = health_report.get("overall_score")
            if health_score and health_score < 50:
                drivers.append(f"declining health score ({health_score:.0f}/100)")
            if drivers:
                parts.append(f"driven by {self._join_factors(drivers)}")

        elif "engagement" in trigger_rule:
            completion = analytics_summary.get("milestone_completion_percentage", 0)
            if completion < 30:
                parts.append(f"with only {completion:.0f}% milestone completion")

        elif "health" in target:
            # Add health dimension context
            dimension_score = metadata.get("dimension_score")
            if dimension_score is not None:
                parts.append(f"with {target.replace('_', ' ')} score at {dimension_score:.0f}/100")

        # Build final reasoning
        reasoning = "This intervention was triggered because " + ". ".join(parts) + "."

        return reasoning

    # =========================================================================
    # Narrative Generation
    # =========================================================================

    def _generate_narrative(
        self,
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        score_explanations: Dict[str, Any],
    ) -> str:
        """
        Generate narrative summary using LLM with template fallback.

        Args:
            risk_scores: Risk scores
            analytics_summary: Analytics data
            health_report: Health data
            score_explanations: Previously generated explanations

        Returns:
            Narrative paragraph
        """
        if self.use_llm:
            try:
                narrative = self._generate_narrative_via_llm(
                    risk_scores=risk_scores,
                    analytics_summary=analytics_summary,
                    health_report=health_report,
                    score_explanations=score_explanations,
                )
                if narrative:
                    return narrative
            except LLMError as e:
                logger.warning(f"LLM narrative generation failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in narrative generation: {e}")

        # Fallback to template
        return self._generate_template_narrative(
            risk_scores=risk_scores,
            analytics_summary=analytics_summary,
            health_report=health_report,
            score_explanations=score_explanations,
        )

    def _generate_narrative_via_llm(
        self,
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        score_explanations: Dict[str, Any],
    ) -> Optional[str]:
        """Generate narrative using LLM."""
        # Build context for LLM
        context_parts = ["Student Progress Summary:"]

        # Timeline status
        status = analytics_summary.get("timeline_status", "unknown")
        context_parts.append(f"- Timeline status: {status}")

        # Completion
        completion = analytics_summary.get("milestone_completion_percentage", 0)
        total = analytics_summary.get("total_milestones", 0)
        completed = analytics_summary.get("completed_milestones", 0)
        context_parts.append(f"- Milestones: {completed}/{total} completed ({completion:.1f}%)")

        # Overdue
        overdue = analytics_summary.get("overdue_milestones", 0)
        overdue_critical = analytics_summary.get("overdue_critical_milestones", 0)
        if overdue > 0:
            context_parts.append(f"- Overdue milestones: {overdue} ({overdue_critical} critical)")

        # Delays
        avg_delay = analytics_summary.get("average_delay_days", 0)
        if avg_delay > 0:
            context_parts.append(f"- Average delay: {avg_delay:.1f} days")

        # Health
        health_score = health_report.get("overall_score")
        if health_score is not None:
            context_parts.append(f"- Overall health score: {health_score:.1f}/100")

        # Health dimensions
        dimension_scores = health_report.get("dimension_scores", {})
        low_dimensions = []
        for dim, score_data in dimension_scores.items():
            score = score_data.get("score", 50) if isinstance(score_data, dict) else score_data
            if score < 50:
                low_dimensions.append(f"{dim.replace('_', ' ')} ({score:.0f})")
        if low_dimensions:
            context_parts.append(f"- Concerning health areas: {', '.join(low_dimensions)}")

        # Risk scores
        context_parts.append(f"\nRisk Assessment:")
        context_parts.append(f"- Dropout risk: {score_explanations['dropout_risk']['level']} ({risk_scores.get('dropout_risk', 0):.2f})")
        context_parts.append(f"- Engagement: {score_explanations['engagement_score']['level']} ({risk_scores.get('engagement_score', 0):.2f})")
        context_parts.append(f"- Timeline continuity: {score_explanations['continuity_index']['level']} ({risk_scores.get('continuity_index', 0):.2f})")

        # Key explanations
        context_parts.append(f"\nKey findings:")
        context_parts.append(f"- {score_explanations['dropout_risk']['plain_english']}")
        context_parts.append(f"- {score_explanations['engagement_score']['plain_english']}")

        user_prompt = "\n".join(context_parts)
        user_prompt += "\n\nWrite a 3-5 sentence summary for the student dashboard."

        result = self.client.call(
            system_prompt=NARRATIVE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=512,
        )

        return result.get("narrative")

    def _generate_template_narrative(
        self,
        risk_scores: Dict[str, Any],
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
        score_explanations: Dict[str, Any],
    ) -> str:
        """Generate narrative using templates (fallback)."""
        sentences = []

        # Opening: current status
        status = analytics_summary.get("timeline_status", "on_track")
        completion = analytics_summary.get("milestone_completion_percentage", 0)

        if status == "completed":
            sentences.append("Great progress - the timeline is complete!")
        elif status == "delayed":
            sentences.append(f"The timeline is currently delayed with {completion:.0f}% of milestones completed.")
        else:
            sentences.append(f"The timeline is on track with {completion:.0f}% of milestones completed.")

        # Concerns
        overdue_critical = analytics_summary.get("overdue_critical_milestones", 0)
        overdue = analytics_summary.get("overdue_milestones", 0)
        avg_delay = analytics_summary.get("average_delay_days", 0)

        if overdue_critical > 0:
            sentences.append(f"{overdue_critical} critical milestone(s) are overdue and require immediate attention.")
        elif overdue > 2:
            sentences.append(f"{overdue} milestones are overdue by an average of {avg_delay:.0f} days.")

        # Health
        health_score = health_report.get("overall_score")
        if health_score is not None and health_score < 50:
            sentences.append(f"Overall wellbeing score has dropped to {health_score:.0f}/100, which may be affecting progress.")

        # Risk level recommendation
        dropout_risk = risk_scores.get("dropout_risk", 0)
        if dropout_risk >= 0.7:
            sentences.append("We strongly recommend scheduling a supervisor check-in this week to discuss support options.")
        elif dropout_risk >= 0.4:
            sentences.append("Consider reviewing your timeline and discussing any challenges with your supervisor.")
        elif status == "on_track":
            sentences.append("Keep up the good work and maintain your current momentum.")

        return " ".join(sentences)

    # =========================================================================
    # Trend Identification
    # =========================================================================

    def _identify_trends(
        self,
        analytics_summary: Dict[str, Any],
        health_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Identify improving and declining signals from longitudinal data.

        Args:
            analytics_summary: Analytics data with longitudinal_summary
            health_report: Health data

        Returns:
            Dictionary with improving and declining lists
        """
        improving = []
        declining = []
        stable = []

        longitudinal = analytics_summary.get("longitudinal_summary", {})

        # Check duration progress vs completion
        duration_pct = longitudinal.get("duration_progress_percentage")
        completion_pct = analytics_summary.get("milestone_completion_percentage", 0)

        if duration_pct is not None:
            if completion_pct >= duration_pct:
                improving.append({
                    "signal": "milestone_completion",
                    "description": f"Completion ({completion_pct:.0f}%) is ahead of time elapsed ({duration_pct:.0f}%)",
                })
            elif completion_pct < duration_pct - 20:
                declining.append({
                    "signal": "milestone_completion",
                    "description": f"Completion ({completion_pct:.0f}%) is behind time elapsed ({duration_pct:.0f}%)",
                })

        # Check event activity
        total_events = longitudinal.get("total_progress_events", 0)
        if total_events > 10:
            improving.append({
                "signal": "activity",
                "description": f"Active engagement with {total_events} progress events recorded",
            })
        elif total_events == 0:
            declining.append({
                "signal": "activity",
                "description": "No progress events recorded yet",
            })

        # Check health dimensions for concerning trends
        dimension_scores = health_report.get("dimension_scores", {})
        for dim, score_data in dimension_scores.items():
            score = score_data.get("score", 50) if isinstance(score_data, dict) else score_data
            if score >= 70:
                improving.append({
                    "signal": f"health_{dim}",
                    "description": f"{dim.replace('_', ' ').title()} is strong ({score:.0f}/100)",
                })
            elif score < 35:
                declining.append({
                    "signal": f"health_{dim}",
                    "description": f"{dim.replace('_', ' ').title()} is critical ({score:.0f}/100)",
                })

        # Check overdue trajectory
        overdue = analytics_summary.get("overdue_milestones", 0)
        total = analytics_summary.get("total_milestones", 1)
        overdue_ratio = overdue / max(total, 1)

        if overdue_ratio > 0.3:
            declining.append({
                "signal": "overdue_ratio",
                "description": f"{overdue}/{total} milestones ({overdue_ratio*100:.0f}%) are overdue",
            })
        elif overdue == 0 and total > 0:
            improving.append({
                "signal": "overdue_ratio",
                "description": "No milestones are currently overdue",
            })

        return {
            "improving": improving,
            "declining": declining,
            "stable": stable,
            "overall_trajectory": "declining" if len(declining) > len(improving) else "improving" if len(improving) > len(declining) else "stable",
        }


# =============================================================================
# Convenience Function
# =============================================================================

def explain_assessment(
    risk_scores: Dict[str, Any],
    analytics_summary: Dict[str, Any],
    health_report: Dict[str, Any],
    interventions: List[Dict[str, Any]],
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    Generate explanations for a risk assessment.

    Convenience function that creates an engine and calls explain.

    Args:
        risk_scores: Risk scores from InterventionEngine
        analytics_summary: Analytics summary
        health_report: Health report
        interventions: List of interventions
        use_llm: Whether to use LLM for narrative

    Returns:
        Explanation dictionary
    """
    engine = ExplainabilityEngine(use_llm=use_llm)
    return engine.explain(
        risk_scores=risk_scores,
        analytics_summary=analytics_summary,
        health_report=health_report,
        interventions=interventions,
    )
