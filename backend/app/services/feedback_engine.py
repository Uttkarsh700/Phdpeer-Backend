"""Feedback Engine for learning from timeline corrections.

This module provides feedback capture, pattern analysis, and learned adjustments
to improve timeline predictions over time.
"""
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.feedback_record import FeedbackRecord
from app.models.progress_event import ProgressEvent
from app.models.user import User


logger = logging.getLogger(__name__)


@dataclass
class CorrectionPattern:
    """Represents a detected correction pattern."""
    stage_type: str
    average_adjustment: float  # positive = increase, negative = decrease
    sample_count: int
    confidence: float  # 0.0 to 1.0 based on sample size
    direction: str  # "increase", "decrease", "stable"


@dataclass
class FeedbackSummary:
    """Summary of feedback analysis."""
    total_feedbacks: int
    accuracy_score: float
    duration_adjustments: Dict[str, float]
    common_corrections: List[str]
    discipline_patterns: Dict[str, Dict[str, float]]
    generated_at: str


class FeedbackEngineError(Exception):
    """Base exception for feedback engine errors."""
    pass


class FeedbackEngine:
    """
    Engine for capturing and learning from timeline feedback.

    Capabilities:
    - Record feedback on timeline predictions
    - Retrieve feedback history for a user
    - Analyze patterns in corrections
    - Apply learned adjustments to new predictions
    - Generate feedback reports

    Rules:
    - Feedback is append-only (immutable once recorded)
    - Patterns require minimum sample size for confidence
    - Adjustments are capped to prevent extreme corrections
    """

    # Minimum samples needed for pattern confidence
    MIN_SAMPLES_FOR_PATTERN = 3
    MIN_SAMPLES_FOR_HIGH_CONFIDENCE = 10

    # Maximum adjustment percentage (caps extreme corrections)
    MAX_ADJUSTMENT_PERCENT = 0.5  # 50% max increase/decrease

    # Event type for feedback in ProgressEvent
    EVENT_TYPE_FEEDBACK = "feedback"

    def __init__(self, db: Session, use_llm: bool = True):
        """
        Initialize feedback engine.

        Args:
            db: Database session
            use_llm: Whether to use LLM for report generation
        """
        self.db = db
        self.use_llm = use_llm
        self._llm_client = None

        if use_llm:
            try:
                from app.services.llm.client import LLMClient
                self._llm_client = LLMClient()
            except Exception as e:
                logger.warning(f"LLM client initialization failed: {e}")
                self._llm_client = None

    def record_feedback(
        self,
        user_id: UUID,
        feedback_type: str,
        feedback_data: Dict[str, Any],
        source: str,
        entity_type: str = "timeline",
        entity_id: Optional[UUID] = None,
        discipline: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record feedback on a timeline prediction.

        Stores feedback in both FeedbackRecord (for analysis) and ProgressEvent
        (for the append-only event log).

        Args:
            user_id: ID of the user
            feedback_type: Type of feedback (duration_correction, stage_correction, etc.)
            feedback_data: Dictionary with 'original' and 'corrected' values
            source: Who provided feedback (supervisor, student, system)
            entity_type: Type of entity corrected (stage, milestone, timeline)
            entity_id: Optional ID of the specific entity
            discipline: Optional field of study
            notes: Optional additional context

        Returns:
            Dictionary with recorded feedback details

        Raises:
            FeedbackEngineError: If validation fails
        """
        # Validate user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise FeedbackEngineError(f"User with ID {user_id} not found")

        # Validate feedback type
        if feedback_type not in FeedbackRecord.VALID_FEEDBACK_TYPES:
            raise FeedbackEngineError(
                f"Invalid feedback_type: {feedback_type}. "
                f"Valid types: {FeedbackRecord.VALID_FEEDBACK_TYPES}"
            )

        # Validate source
        if source not in FeedbackRecord.VALID_SOURCES:
            raise FeedbackEngineError(
                f"Invalid source: {source}. "
                f"Valid sources: {FeedbackRecord.VALID_SOURCES}"
            )

        # Validate entity type
        if entity_type not in FeedbackRecord.VALID_ENTITY_TYPES:
            raise FeedbackEngineError(
                f"Invalid entity_type: {entity_type}. "
                f"Valid types: {FeedbackRecord.VALID_ENTITY_TYPES}"
            )

        # Validate feedback_data has required fields
        if "original" not in feedback_data or "corrected" not in feedback_data:
            raise FeedbackEngineError(
                "feedback_data must contain 'original' and 'corrected' keys"
            )

        # Calculate correction delta
        correction_delta = self._calculate_delta(
            feedback_data["original"],
            feedback_data["corrected"],
            feedback_type
        )

        # Create FeedbackRecord
        feedback_record = FeedbackRecord(
            user_id=user_id,
            feedback_type=feedback_type,
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            original_value=feedback_data["original"],
            corrected_value=feedback_data["corrected"],
            correction_delta=correction_delta,
            discipline=discipline,
            notes=notes,
        )

        self.db.add(feedback_record)
        self.db.flush()

        # Also log as ProgressEvent for event stream
        progress_event = ProgressEvent(
            user_id=user_id,
            event_type=self.EVENT_TYPE_FEEDBACK,
            title=f"Feedback: {feedback_type}",
            description=self._generate_feedback_description(
                feedback_type, feedback_data, source
            ),
            event_date=date.today(),
            impact_level="medium",
            tags=f"{feedback_type},{source},{entity_type}",
            notes=json.dumps({
                "feedback_record_id": str(feedback_record.id),
                "original": feedback_data["original"],
                "corrected": feedback_data["corrected"],
                "delta": correction_delta,
            }),
        )

        self.db.add(progress_event)
        self.db.commit()
        self.db.refresh(feedback_record)

        logger.info(
            f"Recorded feedback: type={feedback_type}, source={source}, "
            f"user={user_id}, record_id={feedback_record.id}"
        )

        return {
            "feedback_id": str(feedback_record.id),
            "feedback_type": feedback_type,
            "source": source,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "original": feedback_data["original"],
            "corrected": feedback_data["corrected"],
            "delta": correction_delta,
            "recorded_at": feedback_record.created_at.isoformat(),
        }

    def get_feedback_history(
        self,
        user_id: UUID,
        feedback_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve feedback history for a user.

        Args:
            user_id: User ID
            feedback_type: Optional filter by feedback type
            source: Optional filter by source
            limit: Maximum number of records to return

        Returns:
            List of feedback records as dictionaries, sorted by date (newest first)
        """
        query = self.db.query(FeedbackRecord).filter(
            FeedbackRecord.user_id == user_id
        )

        if feedback_type:
            query = query.filter(FeedbackRecord.feedback_type == feedback_type)

        if source:
            query = query.filter(FeedbackRecord.source == source)

        records = query.order_by(
            FeedbackRecord.created_at.desc()
        ).limit(limit).all()

        return [
            {
                "feedback_id": str(r.id),
                "feedback_type": r.feedback_type,
                "source": r.source,
                "entity_type": r.entity_type,
                "entity_id": str(r.entity_id) if r.entity_id else None,
                "original": r.original_value,
                "corrected": r.corrected_value,
                "delta": r.correction_delta,
                "discipline": r.discipline,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ]

    def compute_correction_patterns(
        self,
        feedbacks: Optional[List[Dict[str, Any]]] = None,
        discipline: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze feedback to find correction patterns.

        Identifies systematic biases in predictions:
        - Duration adjustments by stage type
        - Common correction types
        - Accuracy score
        - Discipline-specific patterns

        Args:
            feedbacks: Optional pre-fetched feedback list. If None, queries all.
            discipline: Optional filter by discipline

        Returns:
            Dictionary with pattern analysis:
            - duration_adjustments: stage_type -> average correction
            - common_corrections: list of frequent correction types
            - accuracy_score: 0-1 measuring prediction accuracy
            - discipline_patterns: corrections grouped by discipline
        """
        # Query all feedback if not provided
        if feedbacks is None:
            query = self.db.query(FeedbackRecord)
            if discipline:
                query = query.filter(FeedbackRecord.discipline == discipline)
            records = query.all()
            feedbacks = [
                {
                    "feedback_type": r.feedback_type,
                    "original": r.original_value,
                    "corrected": r.corrected_value,
                    "delta": r.correction_delta,
                    "discipline": r.discipline,
                    "entity_type": r.entity_type,
                }
                for r in records
            ]

        if not feedbacks:
            return {
                "duration_adjustments": {},
                "common_corrections": [],
                "accuracy_score": 1.0,  # No feedback = assume accurate
                "discipline_patterns": {},
                "total_feedbacks": 0,
            }

        # Analyze duration corrections
        duration_adjustments = self._compute_duration_adjustments(feedbacks)

        # Find common corrections
        common_corrections = self._find_common_corrections(feedbacks)

        # Calculate accuracy score
        accuracy_score = self._calculate_accuracy_score(feedbacks)

        # Group by discipline
        discipline_patterns = self._group_by_discipline(feedbacks)

        return {
            "duration_adjustments": duration_adjustments,
            "common_corrections": common_corrections,
            "accuracy_score": accuracy_score,
            "discipline_patterns": discipline_patterns,
            "total_feedbacks": len(feedbacks),
        }

    def apply_learned_adjustments(
        self,
        stages: List[Any],
        milestones: List[Any],
        durations: List[Any],
        discipline: Optional[str] = None,
    ) -> Tuple[List[Any], List[Any], List[Any]]:
        """
        Apply learned correction patterns to LLM output.

        Adjusts duration estimates based on historical feedback patterns.
        For example, if data_collection durations are consistently corrected
        upward by 30%, increases the LLM's data_collection duration by 30%.

        Args:
            stages: List of DetectedStage objects
            milestones: List of ExtractedMilestone objects
            durations: List of DurationEstimate objects
            discipline: Optional field of study for discipline-specific patterns

        Returns:
            Tuple of (adjusted_stages, adjusted_milestones, adjusted_durations)
        """
        # Get correction patterns
        patterns = self.compute_correction_patterns(discipline=discipline)

        if patterns["total_feedbacks"] < self.MIN_SAMPLES_FOR_PATTERN:
            logger.debug(
                f"Insufficient feedback samples ({patterns['total_feedbacks']}), "
                f"skipping adjustments"
            )
            return stages, milestones, durations

        duration_adjustments = patterns["duration_adjustments"]

        if not duration_adjustments:
            return stages, milestones, durations

        # Apply adjustments to durations
        adjusted_durations = []
        for duration in durations:
            adjusted = self._adjust_duration(duration, duration_adjustments)
            adjusted_durations.append(adjusted)

        logger.info(
            f"Applied learned adjustments to {len(adjusted_durations)} durations "
            f"based on {patterns['total_feedbacks']} feedback samples"
        )

        # Stages and milestones are not adjusted directly
        # (their structure is typically correct, only durations need adjustment)
        return stages, milestones, adjusted_durations

    def generate_feedback_report(
        self,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive feedback report for a user.

        Uses LLM to create a narrative summary of what the system has learned
        from feedback. Falls back to template if LLM fails.

        Args:
            user_id: User ID

        Returns:
            Dictionary with report including narrative summary
        """
        # Get user's feedback history
        feedbacks = self.get_feedback_history(user_id, limit=500)

        if not feedbacks:
            return {
                "user_id": str(user_id),
                "has_feedback": False,
                "total_feedbacks": 0,
                "summary": "No feedback has been recorded yet. As you work with "
                          "your timeline and receive supervisor input, the system "
                          "will learn from corrections to improve future predictions.",
                "generated_at": datetime.utcnow().isoformat(),
            }

        # Compute patterns
        patterns = self.compute_correction_patterns(feedbacks)

        # Generate narrative summary
        if self.use_llm and self._llm_client:
            try:
                narrative = self._generate_llm_report(feedbacks, patterns)
            except Exception as e:
                logger.warning(f"LLM report generation failed: {e}")
                narrative = self._generate_template_report(feedbacks, patterns)
        else:
            narrative = self._generate_template_report(feedbacks, patterns)

        return {
            "user_id": str(user_id),
            "has_feedback": True,
            "total_feedbacks": len(feedbacks),
            "accuracy_score": patterns["accuracy_score"],
            "duration_adjustments": patterns["duration_adjustments"],
            "common_corrections": patterns["common_corrections"],
            "discipline_patterns": patterns["discipline_patterns"],
            "summary": narrative,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # Private helper methods

    def _calculate_delta(
        self,
        original: Any,
        corrected: Any,
        feedback_type: str,
    ) -> Dict[str, Any]:
        """Calculate the difference between original and corrected values."""
        delta = {}

        if feedback_type == FeedbackRecord.FEEDBACK_TYPE_DURATION:
            # Duration correction - calculate numeric difference
            if isinstance(original, dict) and isinstance(corrected, dict):
                # Handle duration dict: {duration_months_min, duration_months_max}
                if "duration_months" in original and "duration_months" in corrected:
                    delta["months_change"] = (
                        corrected["duration_months"] - original["duration_months"]
                    )
                    delta["percent_change"] = (
                        delta["months_change"] / original["duration_months"]
                        if original["duration_months"] > 0 else 0
                    )
                elif "duration_months_min" in original:
                    orig_avg = (
                        original.get("duration_months_min", 0) +
                        original.get("duration_months_max", 0)
                    ) / 2
                    corr_avg = (
                        corrected.get("duration_months_min", 0) +
                        corrected.get("duration_months_max", 0)
                    ) / 2
                    delta["months_change"] = corr_avg - orig_avg
                    delta["percent_change"] = (
                        delta["months_change"] / orig_avg if orig_avg > 0 else 0
                    )
                # Preserve stage type for pattern analysis
                if "stage_type" in original:
                    delta["stage_type"] = original["stage_type"]

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_STAGE:
            # Stage correction
            if isinstance(original, dict) and isinstance(corrected, dict):
                delta["original_type"] = original.get("stage_type")
                delta["corrected_type"] = corrected.get("stage_type")
                delta["was_added"] = original.get("stage_type") is None
                delta["was_removed"] = corrected.get("stage_type") is None

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_MILESTONE:
            # Milestone correction
            if isinstance(original, dict) and isinstance(corrected, dict):
                delta["was_added"] = original.get("name") is None
                delta["was_removed"] = corrected.get("name") is None
                delta["title_changed"] = (
                    original.get("name") != corrected.get("name")
                )

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_RESTRUCTURE:
            # Major timeline change
            delta["restructure_type"] = "major"

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_COMMENT:
            # General comment - no numeric delta
            delta["has_comment"] = True

        return delta

    def _generate_feedback_description(
        self,
        feedback_type: str,
        feedback_data: Dict[str, Any],
        source: str,
    ) -> str:
        """Generate a human-readable description of the feedback."""
        source_label = {
            "supervisor": "Supervisor",
            "student": "Student",
            "system": "System",
        }.get(source, source.title())

        if feedback_type == FeedbackRecord.FEEDBACK_TYPE_DURATION:
            original = feedback_data.get("original", {})
            corrected = feedback_data.get("corrected", {})
            stage = original.get("stage_type", original.get("title", "stage"))
            return (
                f"{source_label} corrected duration estimate for {stage}: "
                f"changed from {original} to {corrected}"
            )

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_STAGE:
            return f"{source_label} made a stage correction"

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_MILESTONE:
            return f"{source_label} made a milestone correction"

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_RESTRUCTURE:
            return f"{source_label} restructured the timeline"

        elif feedback_type == FeedbackRecord.FEEDBACK_TYPE_COMMENT:
            return f"{source_label} provided feedback comment"

        return f"{source_label} provided {feedback_type} feedback"

    def _compute_duration_adjustments(
        self,
        feedbacks: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        Compute average duration adjustments by stage type.

        Returns:
            Dictionary mapping stage_type to average percent adjustment
            e.g., {"data_collection": 0.3, "writing": 0.15}
        """
        adjustments_by_stage = defaultdict(list)

        for fb in feedbacks:
            if fb.get("feedback_type") != FeedbackRecord.FEEDBACK_TYPE_DURATION:
                continue

            delta = fb.get("delta", {})
            percent_change = delta.get("percent_change")
            stage_type = delta.get("stage_type")

            if percent_change is not None and stage_type:
                adjustments_by_stage[stage_type].append(percent_change)

        # Calculate averages
        result = {}
        for stage_type, changes in adjustments_by_stage.items():
            if len(changes) >= self.MIN_SAMPLES_FOR_PATTERN:
                avg_change = sum(changes) / len(changes)
                # Cap adjustment
                avg_change = max(
                    -self.MAX_ADJUSTMENT_PERCENT,
                    min(self.MAX_ADJUSTMENT_PERCENT, avg_change)
                )
                result[stage_type] = round(avg_change, 3)

        return result

    def _find_common_corrections(
        self,
        feedbacks: List[Dict[str, Any]],
    ) -> List[str]:
        """Find the most common correction types."""
        type_counts = defaultdict(int)

        for fb in feedbacks:
            fb_type = fb.get("feedback_type", "unknown")
            type_counts[fb_type] += 1

        # Sort by count descending
        sorted_types = sorted(
            type_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top 5 with counts
        return [
            f"{fb_type} ({count})"
            for fb_type, count in sorted_types[:5]
        ]

    def _calculate_accuracy_score(
        self,
        feedbacks: List[Dict[str, Any]],
    ) -> float:
        """
        Calculate prediction accuracy score.

        Score is based on how often predictions required correction:
        - 1.0 = no corrections needed
        - Lower = more corrections needed

        Uses a weighted approach where smaller corrections count less.
        """
        if not feedbacks:
            return 1.0

        total_weight = 0
        correction_weight = 0

        for fb in feedbacks:
            fb_type = fb.get("feedback_type")

            # Weight by correction type severity
            if fb_type == FeedbackRecord.FEEDBACK_TYPE_COMMENT:
                # Comments don't affect accuracy
                continue
            elif fb_type == FeedbackRecord.FEEDBACK_TYPE_RESTRUCTURE:
                # Major restructure = significant miss
                total_weight += 3.0
                correction_weight += 3.0
            elif fb_type == FeedbackRecord.FEEDBACK_TYPE_STAGE:
                # Stage correction = moderate miss
                total_weight += 2.0
                correction_weight += 2.0
            elif fb_type == FeedbackRecord.FEEDBACK_TYPE_DURATION:
                # Duration correction - weight by size
                delta = fb.get("delta", {})
                percent_change = abs(delta.get("percent_change", 0))
                total_weight += 1.0
                # Small corrections (<10%) count less
                if percent_change < 0.1:
                    correction_weight += 0.3
                elif percent_change < 0.25:
                    correction_weight += 0.6
                else:
                    correction_weight += 1.0
            else:
                total_weight += 1.0
                correction_weight += 0.5

        if total_weight == 0:
            return 1.0

        # Accuracy = 1 - (correction_weight / (total_weight * 2))
        # Scaled so that perfect would be 1.0 and all major corrections would be ~0
        accuracy = 1.0 - (correction_weight / (total_weight * 2))
        return max(0.0, min(1.0, round(accuracy, 3)))

    def _group_by_discipline(
        self,
        feedbacks: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, float]]:
        """Group correction patterns by discipline."""
        by_discipline = defaultdict(lambda: defaultdict(list))

        for fb in feedbacks:
            discipline = fb.get("discipline")
            if not discipline:
                continue

            if fb.get("feedback_type") != FeedbackRecord.FEEDBACK_TYPE_DURATION:
                continue

            delta = fb.get("delta", {})
            stage_type = delta.get("stage_type")
            percent_change = delta.get("percent_change")

            if stage_type and percent_change is not None:
                by_discipline[discipline][stage_type].append(percent_change)

        # Calculate averages
        result = {}
        for discipline, stages in by_discipline.items():
            result[discipline] = {}
            for stage_type, changes in stages.items():
                if changes:
                    avg = sum(changes) / len(changes)
                    result[discipline][stage_type] = round(avg, 3)

        return result

    def _adjust_duration(
        self,
        duration: Any,
        adjustments: Dict[str, float],
    ) -> Any:
        """Apply learned adjustment to a duration estimate."""
        # Get the stage type from the duration
        item_desc = getattr(duration, "item_description", "").lower()
        item_type = getattr(duration, "item_type", "")

        # Only adjust stage durations
        if item_type != "stage":
            return duration

        # Find matching adjustment
        adjustment = None
        for stage_type, adj in adjustments.items():
            if stage_type.lower() in item_desc:
                adjustment = adj
                break

        if adjustment is None or abs(adjustment) < 0.01:
            return duration

        # Create adjusted copy
        # Import here to avoid circular import
        from app.services.timeline_intelligence_engine import DurationEstimate

        # Calculate adjusted values
        multiplier = 1.0 + adjustment

        new_duration = DurationEstimate(
            item_description=duration.item_description,
            item_type=duration.item_type,
            duration_weeks_min=max(1, int(duration.duration_weeks_min * multiplier)),
            duration_weeks_max=max(1, int(duration.duration_weeks_max * multiplier)),
            duration_months_min=max(1, int(duration.duration_months_min * multiplier)),
            duration_months_max=max(1, int(duration.duration_months_max * multiplier)),
            confidence=duration.confidence,
            basis=f"{duration.basis}+feedback_adjusted",
            source_text=duration.source_text,
        )

        logger.debug(
            f"Adjusted {duration.item_description}: "
            f"{duration.duration_months_min}-{duration.duration_months_max} -> "
            f"{new_duration.duration_months_min}-{new_duration.duration_months_max} months "
            f"({adjustment:+.1%})"
        )

        return new_duration

    def _generate_llm_report(
        self,
        feedbacks: List[Dict[str, Any]],
        patterns: Dict[str, Any],
    ) -> str:
        """Generate narrative report using LLM."""
        system_prompt = """You are an AI assistant analyzing feedback patterns for a PhD timeline system.
Generate a concise, helpful summary of what the system has learned from feedback.
Focus on:
1. What corrections were most common
2. Which predictions were systematically off
3. How this will improve future predictions
4. Any discipline-specific insights

Keep the summary to 3-4 sentences. Be encouraging and constructive."""

        user_prompt = f"""Analyze this feedback summary and generate a narrative report:

Total feedbacks: {patterns['total_feedbacks']}
Accuracy score: {patterns['accuracy_score']:.1%}

Duration adjustments learned (stage_type -> adjustment):
{json.dumps(patterns['duration_adjustments'], indent=2)}

Most common corrections:
{json.dumps(patterns['common_corrections'], indent=2)}

Discipline-specific patterns:
{json.dumps(patterns['discipline_patterns'], indent=2)}

Recent feedback examples (last 5):
{json.dumps(feedbacks[:5], indent=2)}

Generate a brief, helpful narrative summary."""

        try:
            response = self._llm_client.call(system_prompt, user_prompt)
            return response.get("summary", response.get("narrative", str(response)))
        except Exception as e:
            logger.error(f"LLM report generation error: {e}")
            raise

    def _generate_template_report(
        self,
        feedbacks: List[Dict[str, Any]],
        patterns: Dict[str, Any],
    ) -> str:
        """Generate template-based fallback report."""
        parts = []

        # Overall stats
        total = patterns["total_feedbacks"]
        accuracy = patterns["accuracy_score"]
        parts.append(
            f"Based on {total} feedback items, the system has an accuracy score of "
            f"{accuracy:.0%}."
        )

        # Duration adjustments
        if patterns["duration_adjustments"]:
            adjustments = patterns["duration_adjustments"]
            adj_parts = []
            for stage, adj in adjustments.items():
                direction = "increased" if adj > 0 else "decreased"
                adj_parts.append(f"{stage.replace('_', ' ')} ({direction} by {abs(adj):.0%})")

            if adj_parts:
                parts.append(
                    f"Duration estimates have been calibrated for: {', '.join(adj_parts)}."
                )

        # Common corrections
        if patterns["common_corrections"]:
            top = patterns["common_corrections"][0]
            parts.append(f"The most common correction type is {top}.")

        # Discipline patterns
        if patterns["discipline_patterns"]:
            disciplines = list(patterns["discipline_patterns"].keys())
            parts.append(
                f"Discipline-specific patterns have been identified for: "
                f"{', '.join(disciplines)}."
            )

        # Closing
        parts.append(
            "These learned patterns will be applied to future timeline predictions "
            "to improve accuracy."
        )

        return " ".join(parts)


# Convenience function
def record_feedback(
    db: Session,
    user_id: UUID,
    feedback_type: str,
    feedback_data: Dict[str, Any],
    source: str,
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to record feedback.

    Args:
        db: Database session
        user_id: User ID
        feedback_type: Type of feedback
        feedback_data: Dictionary with 'original' and 'corrected' values
        source: Who provided feedback
        **kwargs: Additional arguments passed to FeedbackEngine.record_feedback

    Returns:
        Dictionary with recorded feedback details
    """
    engine = FeedbackEngine(db, use_llm=False)
    return engine.record_feedback(
        user_id=user_id,
        feedback_type=feedback_type,
        feedback_data=feedback_data,
        source=source,
        **kwargs,
    )
