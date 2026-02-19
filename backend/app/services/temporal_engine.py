"""
Temporal Modeling Engine for analyzing trends and patterns over time.

Provides velocity tracking, drift detection, stage transition analysis,
completion prediction, and activity pattern recognition.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.services.llm.client import LLMClient, get_llm_client, LLMError

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Velocity trend thresholds
VELOCITY_ACCELERATING_THRESHOLD = 0.2  # 20% increase
VELOCITY_DECELERATING_THRESHOLD = -0.2  # 20% decrease

# Drift thresholds
DRIFT_ON_TRACK_THRESHOLD = 0.1  # Within 10%
DRIFT_SIGNIFICANT_THRESHOLD = 0.25  # 25% drift

# Stage stuck threshold
STAGE_STUCK_FACTOR = 1.5  # 50% over estimated duration

# Pattern detection
INACTIVE_THRESHOLD_DAYS = 30
BURST_THRESHOLD = 3  # Events within a week
REGULAR_CADENCE_VARIANCE = 0.3  # 30% variance in gaps

# Prediction confidence
MIN_POINTS_HIGH_CONFIDENCE = 6
MIN_POINTS_MEDIUM_CONFIDENCE = 3


# =============================================================================
# LLM Prompts
# =============================================================================

TEMPORAL_SUMMARY_SYSTEM_PROMPT = """You are an academic advisor analyzing temporal patterns in a PhD student's progress.

Write a 3-5 sentence summary that:
1. Describes the student's pace and trajectory
2. Notes any concerning patterns or positive trends
3. Provides context about timeline health
4. Uses supportive, clear language

Respond with ONLY a JSON object:
{
    "summary": "Your 3-5 sentence temporal summary here."
}

No markdown fences, no preamble."""


# =============================================================================
# Temporal Engine
# =============================================================================

class TemporalEngine:
    """
    Engine for analyzing temporal patterns in PhD progress.

    Capabilities:
    - Velocity tracking: completion rate over time
    - Drift detection: comparing expected vs actual progress
    - Stage transition analysis: tracking movements between stages
    - Completion prediction: linear projection based on velocity
    - Activity pattern detection: gaps, bursts, regularity

    All methods are deterministic except generate_temporal_summary.
    Uses simple math: moving averages, linear regression, date arithmetic.
    """

    def __init__(self, client: Optional[LLMClient] = None, use_llm: bool = True):
        """
        Initialize the temporal engine.

        Args:
            client: Optional LLMClient instance.
            use_llm: Whether to use LLM for summary generation.
        """
        self._client = client
        self.use_llm = use_llm

    @property
    def client(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    # =========================================================================
    # Main Entry Point
    # =========================================================================

    def analyze_trends(
        self,
        user_id: UUID,
        snapshots: List[Dict[str, Any]],
        progress_events: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        total_duration_months: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze all temporal trends and patterns.

        Args:
            user_id: User ID
            snapshots: List of AnalyticsSnapshot dicts (chronological)
            progress_events: List of ProgressEvent dicts
            milestones: List of milestone dicts
            total_duration_months: Expected program duration

        Returns:
            Complete temporal analysis dictionary
        """
        logger.info(f"Analyzing temporal trends for user: {user_id}")

        # Run all sub-analyses
        velocity = self.detect_velocity_trend(progress_events)
        drift = self.detect_drift(snapshots)
        stage_transitions = self.detect_stage_transitions(progress_events, milestones)
        completion_prediction = self.predict_completion(
            snapshots=snapshots,
            milestones=milestones,
            total_duration_months=total_duration_months,
        )
        activity_patterns = self.detect_patterns(progress_events)

        # Combine analysis
        analysis = {
            "velocity": velocity,
            "drift": drift,
            "stage_transitions": stage_transitions,
            "completion_prediction": completion_prediction,
            "activity_patterns": activity_patterns,
        }

        # Generate narrative summary
        temporal_summary = self.generate_temporal_summary(analysis)

        return {
            "velocity": velocity,
            "drift": drift,
            "stage_transitions": stage_transitions,
            "completion_prediction": completion_prediction,
            "activity_patterns": activity_patterns,
            "temporal_summary": temporal_summary,
            "analyzed_at": datetime.now().isoformat(),
        }

    # =========================================================================
    # Velocity Trend Detection
    # =========================================================================

    def detect_velocity_trend(
        self,
        progress_events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Measure milestone completion velocity over time.

        Groups events by month, counts completions, calculates trend.

        Args:
            progress_events: List of progress event dicts

        Returns:
            Dictionary with velocity metrics:
            - current_velocity: completions/month (last 3 months average)
            - average_velocity: overall average
            - trend: 'accelerating'/'decelerating'/'stable'
            - velocity_history: list of monthly counts
        """
        if not progress_events:
            return {
                "current_velocity": 0.0,
                "average_velocity": 0.0,
                "trend": "stable",
                "velocity_history": [],
                "has_data": False,
            }

        # Filter to completion events
        completion_events = [
            e for e in progress_events
            if e.get("event_type") == "milestone_completed"
        ]

        if not completion_events:
            return {
                "current_velocity": 0.0,
                "average_velocity": 0.0,
                "trend": "stable",
                "velocity_history": [],
                "has_data": False,
            }

        # Group by month
        monthly_counts = defaultdict(int)
        for event in completion_events:
            event_date = self._parse_date(event.get("event_date"))
            if event_date:
                month_key = event_date.strftime("%Y-%m")
                monthly_counts[month_key] += 1

        if not monthly_counts:
            return {
                "current_velocity": 0.0,
                "average_velocity": 0.0,
                "trend": "stable",
                "velocity_history": [],
                "has_data": False,
            }

        # Sort months chronologically
        sorted_months = sorted(monthly_counts.keys())
        velocity_history = [
            {"month": m, "completions": monthly_counts[m]}
            for m in sorted_months
        ]

        # Calculate velocities
        total_completions = sum(monthly_counts.values())
        num_months = len(sorted_months)
        average_velocity = total_completions / num_months if num_months > 0 else 0.0

        # Current velocity: average of last 3 months
        recent_months = sorted_months[-3:] if len(sorted_months) >= 3 else sorted_months
        recent_total = sum(monthly_counts[m] for m in recent_months)
        current_velocity = recent_total / len(recent_months) if recent_months else 0.0

        # Determine trend by comparing first half to second half
        trend = "stable"
        if num_months >= 4:
            mid = num_months // 2
            first_half = sorted_months[:mid]
            second_half = sorted_months[mid:]

            first_avg = sum(monthly_counts[m] for m in first_half) / len(first_half)
            second_avg = sum(monthly_counts[m] for m in second_half) / len(second_half)

            if first_avg > 0:
                change_rate = (second_avg - first_avg) / first_avg
                if change_rate >= VELOCITY_ACCELERATING_THRESHOLD:
                    trend = "accelerating"
                elif change_rate <= VELOCITY_DECELERATING_THRESHOLD:
                    trend = "decelerating"

        return {
            "current_velocity": round(current_velocity, 2),
            "average_velocity": round(average_velocity, 2),
            "trend": trend,
            "velocity_history": velocity_history,
            "total_completions": total_completions,
            "months_tracked": num_months,
            "has_data": True,
        }

    # =========================================================================
    # Drift Detection
    # =========================================================================

    def detect_drift(
        self,
        snapshots: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Detect timeline drift by comparing snapshots over time.

        Drift = completion percentage not keeping pace with elapsed time.

        Args:
            snapshots: List of AnalyticsSnapshot dicts (chronological)

        Returns:
            Dictionary with drift metrics:
            - drift_score: 0.0-1.0 (higher = more drift)
            - drift_direction: 'behind_schedule'/'ahead_schedule'/'on_track'
            - expected_completion_pct: based on elapsed time
            - actual_completion_pct: current completion
            - drift_months: estimated months behind/ahead
        """
        if not snapshots:
            return {
                "drift_score": 0.0,
                "drift_direction": "on_track",
                "expected_completion_pct": 0.0,
                "actual_completion_pct": 0.0,
                "drift_months": 0.0,
                "has_data": False,
            }

        # Get the latest snapshot
        latest = snapshots[-1]
        summary = latest.get("summary_json", {})

        # Extract longitudinal data
        longitudinal = summary.get("longitudinal_summary", {})
        duration_progress_pct = longitudinal.get("duration_progress_percentage")

        # Get completion percentage
        actual_completion_pct = summary.get("milestone_completion_percentage", 0) or 0

        if duration_progress_pct is None:
            # Try to calculate from dates
            committed_date = self._parse_date(longitudinal.get("timeline_committed_date"))
            target_date = self._parse_date(longitudinal.get("target_completion_date"))

            if committed_date and target_date:
                total_days = (target_date - committed_date).days
                elapsed_days = (date.today() - committed_date).days
                if total_days > 0:
                    duration_progress_pct = (elapsed_days / total_days) * 100

        if duration_progress_pct is None:
            return {
                "drift_score": 0.0,
                "drift_direction": "on_track",
                "expected_completion_pct": 0.0,
                "actual_completion_pct": actual_completion_pct,
                "drift_months": 0.0,
                "has_data": False,
                "reason": "Cannot calculate drift without timeline dates",
            }

        expected_completion_pct = duration_progress_pct

        # Calculate drift
        drift_difference = expected_completion_pct - actual_completion_pct
        drift_score = min(abs(drift_difference) / 100, 1.0)

        # Determine direction
        if abs(drift_difference) <= DRIFT_ON_TRACK_THRESHOLD * 100:
            drift_direction = "on_track"
        elif drift_difference > 0:
            drift_direction = "behind_schedule"
        else:
            drift_direction = "ahead_schedule"

        # Estimate months behind/ahead
        timeline_duration_days = longitudinal.get("timeline_duration_days")
        drift_months = 0.0
        if timeline_duration_days and timeline_duration_days > 0:
            drift_days = (drift_difference / 100) * timeline_duration_days
            drift_months = drift_days / 30.0

        # Calculate drift trajectory from multiple snapshots
        drift_trajectory = None
        if len(snapshots) >= 3:
            drift_history = []
            for snap in snapshots[-5:]:  # Last 5 snapshots
                snap_summary = snap.get("summary_json", {})
                snap_longitudinal = snap_summary.get("longitudinal_summary", {})
                snap_duration_pct = snap_longitudinal.get("duration_progress_percentage", 0)
                snap_completion_pct = snap_summary.get("milestone_completion_percentage", 0)
                if snap_duration_pct:
                    drift_history.append(snap_duration_pct - snap_completion_pct)

            if len(drift_history) >= 2:
                if drift_history[-1] > drift_history[0]:
                    drift_trajectory = "worsening"
                elif drift_history[-1] < drift_history[0]:
                    drift_trajectory = "improving"
                else:
                    drift_trajectory = "stable"

        return {
            "drift_score": round(drift_score, 3),
            "drift_direction": drift_direction,
            "expected_completion_pct": round(expected_completion_pct, 1),
            "actual_completion_pct": round(actual_completion_pct, 1),
            "drift_months": round(drift_months, 1),
            "drift_trajectory": drift_trajectory,
            "is_significant": drift_score >= DRIFT_SIGNIFICANT_THRESHOLD,
            "has_data": True,
        }

    # =========================================================================
    # Stage Transition Detection
    # =========================================================================

    def detect_stage_transitions(
        self,
        progress_events: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Identify stage transitions from progress events.

        Args:
            progress_events: List of progress event dicts
            milestones: List of milestone dicts

        Returns:
            Dictionary with stage transition data:
            - current_stage: current stage name
            - stages_completed: list with completion dates
            - average_stage_duration_months: average time per stage
            - time_in_current_stage_months: time spent in current stage
            - is_stuck: true if exceeding estimated duration by >50%
        """
        if not progress_events:
            return {
                "current_stage": None,
                "stages_completed": [],
                "average_stage_duration_months": 0.0,
                "time_in_current_stage_months": 0.0,
                "is_stuck": False,
                "has_data": False,
            }

        # Find stage events
        stage_started_events = [
            e for e in progress_events
            if e.get("event_type") == "stage_started"
        ]
        stage_completed_events = [
            e for e in progress_events
            if e.get("event_type") == "stage_completed"
        ]

        # Build stage transition timeline
        stages_completed = []
        for event in stage_completed_events:
            event_date = self._parse_date(event.get("event_date"))
            stages_completed.append({
                "stage_title": event.get("title", "").replace("Stage Completed: ", ""),
                "completed_date": event_date.isoformat() if event_date else None,
            })

        # Sort by date
        stages_completed.sort(key=lambda x: x["completed_date"] or "")

        # Determine current stage
        current_stage = None
        current_stage_start_date = None

        # Look for most recent stage_started that hasn't been completed
        started_stages = {}
        for event in stage_started_events:
            event_date = self._parse_date(event.get("event_date"))
            stage_title = event.get("title", "").replace("Stage Started: ", "")
            started_stages[stage_title] = event_date

        completed_stage_titles = {s["stage_title"] for s in stages_completed}

        for stage_title, start_date in started_stages.items():
            if stage_title not in completed_stage_titles:
                if current_stage_start_date is None or start_date > current_stage_start_date:
                    current_stage = stage_title
                    current_stage_start_date = start_date

        # Calculate time in current stage
        time_in_current_stage_months = 0.0
        if current_stage_start_date:
            days_in_stage = (date.today() - current_stage_start_date).days
            time_in_current_stage_months = days_in_stage / 30.0

        # Calculate average stage duration
        stage_durations = []
        for i, completed in enumerate(stages_completed):
            # Find when this stage started
            stage_title = completed["stage_title"]
            start_date = started_stages.get(stage_title)
            end_date = self._parse_date(completed["completed_date"])

            if start_date and end_date:
                duration_days = (end_date - start_date).days
                stage_durations.append(duration_days / 30.0)

        average_stage_duration_months = (
            sum(stage_durations) / len(stage_durations)
            if stage_durations else 0.0
        )

        # Determine if stuck (>50% over average duration)
        is_stuck = False
        if average_stage_duration_months > 0 and time_in_current_stage_months > 0:
            threshold = average_stage_duration_months * STAGE_STUCK_FACTOR
            is_stuck = time_in_current_stage_months > threshold

        # Try to infer current stage from milestones if no stage events
        if not current_stage and milestones:
            # Group milestones by stage
            stage_milestones = defaultdict(list)
            for m in milestones:
                stage = m.get("stage_title") or m.get("stage")
                if stage:
                    stage_milestones[stage].append(m)

            # Find stage with incomplete milestones
            for stage, stage_ms in stage_milestones.items():
                completed_count = sum(1 for m in stage_ms if m.get("is_completed"))
                if completed_count < len(stage_ms):
                    current_stage = stage
                    break

        return {
            "current_stage": current_stage,
            "stages_completed": stages_completed,
            "stages_completed_count": len(stages_completed),
            "average_stage_duration_months": round(average_stage_duration_months, 1),
            "time_in_current_stage_months": round(time_in_current_stage_months, 1),
            "is_stuck": is_stuck,
            "stuck_threshold_months": round(average_stage_duration_months * STAGE_STUCK_FACTOR, 1) if average_stage_duration_months > 0 else None,
            "has_data": len(stage_started_events) > 0 or len(stage_completed_events) > 0 or current_stage is not None,
        }

    # =========================================================================
    # Completion Prediction
    # =========================================================================

    def predict_completion(
        self,
        snapshots: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        total_duration_months: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Predict completion date using linear projection.

        At current velocity, when will remaining milestones be done?

        Args:
            snapshots: List of AnalyticsSnapshot dicts
            milestones: List of milestone dicts
            total_duration_months: Expected program duration

        Returns:
            Dictionary with prediction:
            - predicted_completion_date: estimated date
            - predicted_total_months: total months from start
            - confidence: 'low'/'medium'/'high'
            - on_track: bool
            - months_ahead_or_behind: positive = behind
        """
        if not snapshots and not milestones:
            return {
                "predicted_completion_date": None,
                "predicted_total_months": None,
                "confidence": "low",
                "on_track": None,
                "months_ahead_or_behind": None,
                "has_data": False,
            }

        # Get current state from latest snapshot or milestones
        total_milestones = len(milestones) if milestones else 0
        completed_milestones = 0

        if milestones:
            completed_milestones = sum(1 for m in milestones if m.get("is_completed"))

        if snapshots:
            latest = snapshots[-1]
            summary = latest.get("summary_json", {})
            total_milestones = summary.get("total_milestones", total_milestones)
            completed_milestones = summary.get("completed_milestones", completed_milestones)

        remaining_milestones = total_milestones - completed_milestones

        # Calculate velocity from snapshots
        velocity = 0.0
        if len(snapshots) >= 2:
            # Use completion rate between first and last snapshot
            first = snapshots[0]
            last = snapshots[-1]

            first_completed = first.get("summary_json", {}).get("completed_milestones", 0)
            last_completed = last.get("summary_json", {}).get("completed_milestones", 0)

            first_date = self._parse_date(first.get("created_at"))
            last_date = self._parse_date(last.get("created_at"))

            if first_date and last_date and last_date > first_date:
                months_elapsed = (last_date - first_date).days / 30.0
                if months_elapsed > 0:
                    velocity = (last_completed - first_completed) / months_elapsed

        # Determine confidence based on data points
        confidence = "low"
        if len(snapshots) >= MIN_POINTS_HIGH_CONFIDENCE:
            confidence = "high"
        elif len(snapshots) >= MIN_POINTS_MEDIUM_CONFIDENCE:
            confidence = "medium"

        # Calculate prediction
        if velocity > 0 and remaining_milestones > 0:
            months_to_complete = remaining_milestones / velocity
            predicted_completion_date = date.today() + timedelta(days=months_to_complete * 30)
        elif remaining_milestones == 0:
            predicted_completion_date = date.today()
            months_to_complete = 0
        else:
            predicted_completion_date = None
            months_to_complete = None

        # Get original timeline info
        target_completion_date = None
        committed_date = None
        if snapshots:
            latest_summary = snapshots[-1].get("summary_json", {})
            longitudinal = latest_summary.get("longitudinal_summary", {})
            target_completion_date = self._parse_date(longitudinal.get("target_completion_date"))
            committed_date = self._parse_date(longitudinal.get("timeline_committed_date"))

        # Calculate total months and deviation
        predicted_total_months = None
        months_ahead_or_behind = None
        on_track = None

        if committed_date and predicted_completion_date:
            predicted_total_months = (predicted_completion_date - committed_date).days / 30.0

        if target_completion_date and predicted_completion_date:
            months_ahead_or_behind = (predicted_completion_date - target_completion_date).days / 30.0
            on_track = months_ahead_or_behind <= 1  # Within 1 month

        if total_duration_months and predicted_total_months:
            deviation = predicted_total_months - total_duration_months
            if months_ahead_or_behind is None:
                months_ahead_or_behind = deviation
                on_track = deviation <= 1

        return {
            "predicted_completion_date": predicted_completion_date.isoformat() if predicted_completion_date else None,
            "predicted_total_months": round(predicted_total_months, 1) if predicted_total_months else None,
            "confidence": confidence,
            "on_track": on_track,
            "months_ahead_or_behind": round(months_ahead_or_behind, 1) if months_ahead_or_behind is not None else None,
            "remaining_milestones": remaining_milestones,
            "current_velocity": round(velocity, 2) if velocity else 0.0,
            "target_completion_date": target_completion_date.isoformat() if target_completion_date else None,
            "has_data": len(snapshots) > 0 or len(milestones) > 0,
        }

    # =========================================================================
    # Activity Pattern Detection
    # =========================================================================

    def detect_patterns(
        self,
        progress_events: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Find patterns in event timing.

        Are there gaps? Bursts of activity? Regular cadence?

        Args:
            progress_events: List of progress event dicts

        Returns:
            Dictionary with pattern analysis:
            - pattern_type: 'regular'/'bursty'/'sporadic'/'inactive'
            - average_gap_days: between events
            - longest_gap_days: maximum gap
            - last_activity_days_ago: days since last event
            - activity_periods: list of active/inactive windows
        """
        if not progress_events:
            return {
                "pattern_type": "inactive",
                "average_gap_days": 0,
                "longest_gap_days": 0,
                "last_activity_days_ago": None,
                "activity_periods": [],
                "has_data": False,
            }

        # Parse and sort event dates
        event_dates = []
        for event in progress_events:
            event_date = self._parse_date(event.get("event_date"))
            if event_date:
                event_dates.append(event_date)

        if not event_dates:
            return {
                "pattern_type": "inactive",
                "average_gap_days": 0,
                "longest_gap_days": 0,
                "last_activity_days_ago": None,
                "activity_periods": [],
                "has_data": False,
            }

        event_dates.sort()

        # Calculate gaps between events
        gaps = []
        for i in range(1, len(event_dates)):
            gap_days = (event_dates[i] - event_dates[i - 1]).days
            gaps.append(gap_days)

        average_gap_days = sum(gaps) / len(gaps) if gaps else 0
        longest_gap_days = max(gaps) if gaps else 0

        # Days since last activity
        last_activity_days_ago = (date.today() - event_dates[-1]).days

        # Detect pattern type
        pattern_type = self._classify_pattern(
            gaps=gaps,
            average_gap=average_gap_days,
            last_activity_days_ago=last_activity_days_ago,
            event_dates=event_dates,
        )

        # Identify activity periods (windows of high/low activity)
        activity_periods = self._identify_activity_periods(event_dates)

        # Calculate burst metrics
        burst_count = 0
        for i in range(len(event_dates) - BURST_THRESHOLD + 1):
            window = event_dates[i:i + BURST_THRESHOLD]
            if (window[-1] - window[0]).days <= 7:
                burst_count += 1

        return {
            "pattern_type": pattern_type,
            "average_gap_days": round(average_gap_days, 1),
            "longest_gap_days": longest_gap_days,
            "last_activity_days_ago": last_activity_days_ago,
            "activity_periods": activity_periods,
            "total_events": len(event_dates),
            "burst_count": burst_count,
            "gap_variance": round(self._calculate_variance(gaps), 1) if gaps else 0,
            "has_data": True,
        }

    def _classify_pattern(
        self,
        gaps: List[int],
        average_gap: float,
        last_activity_days_ago: int,
        event_dates: List[date],
    ) -> str:
        """Classify the activity pattern type."""
        if not gaps or last_activity_days_ago > INACTIVE_THRESHOLD_DAYS:
            return "inactive"

        if not gaps:
            return "sporadic"

        # Calculate coefficient of variation (std / mean)
        variance = self._calculate_variance(gaps)
        std_dev = variance ** 0.5
        cv = std_dev / average_gap if average_gap > 0 else 0

        # Check for bursts (multiple events within a week)
        burst_count = 0
        for i in range(len(event_dates) - 2):
            if (event_dates[i + 2] - event_dates[i]).days <= 7:
                burst_count += 1

        # Classify
        if cv <= REGULAR_CADENCE_VARIANCE:
            return "regular"
        elif burst_count >= 2:
            return "bursty"
        else:
            return "sporadic"

    def _identify_activity_periods(
        self,
        event_dates: List[date],
    ) -> List[Dict[str, Any]]:
        """Identify periods of high and low activity."""
        if len(event_dates) < 2:
            return []

        periods = []

        # Group by month
        monthly_events = defaultdict(int)
        for d in event_dates:
            month_key = d.strftime("%Y-%m")
            monthly_events[month_key] += 1

        if not monthly_events:
            return []

        # Calculate average monthly activity
        avg_monthly = sum(monthly_events.values()) / len(monthly_events)

        # Identify high and low activity months
        for month, count in sorted(monthly_events.items()):
            if count >= avg_monthly * 1.5:
                period_type = "high_activity"
            elif count <= avg_monthly * 0.5:
                period_type = "low_activity"
            else:
                period_type = "normal"

            periods.append({
                "month": month,
                "event_count": count,
                "period_type": period_type,
            })

        return periods[-6:]  # Last 6 months

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    # =========================================================================
    # Temporal Summary Generation
    # =========================================================================

    def generate_temporal_summary(
        self,
        analysis: Dict[str, Any],
    ) -> str:
        """
        Generate narrative summary of temporal analysis.

        Uses LLM with template fallback.

        Args:
            analysis: Complete temporal analysis dict

        Returns:
            3-5 sentence narrative summary
        """
        if self.use_llm:
            try:
                summary = self._generate_summary_via_llm(analysis)
                if summary:
                    return summary
            except LLMError as e:
                logger.warning(f"LLM temporal summary failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in temporal summary: {e}")

        return self._generate_template_summary(analysis)

    def _generate_summary_via_llm(
        self,
        analysis: Dict[str, Any],
    ) -> Optional[str]:
        """Generate summary using LLM."""
        velocity = analysis.get("velocity", {})
        drift = analysis.get("drift", {})
        prediction = analysis.get("completion_prediction", {})
        patterns = analysis.get("activity_patterns", {})
        stages = analysis.get("stage_transitions", {})

        context_parts = ["Temporal Analysis Summary:"]

        # Velocity
        if velocity.get("has_data"):
            context_parts.append(f"- Completion velocity: {velocity.get('current_velocity', 0)} milestones/month ({velocity.get('trend', 'stable')})")
            context_parts.append(f"- Total completions tracked: {velocity.get('total_completions', 0)} over {velocity.get('months_tracked', 0)} months")

        # Drift
        if drift.get("has_data"):
            context_parts.append(f"- Timeline drift: {drift.get('drift_direction', 'on_track')}")
            context_parts.append(f"- Expected completion: {drift.get('expected_completion_pct', 0):.1f}%, Actual: {drift.get('actual_completion_pct', 0):.1f}%")
            if drift.get("drift_months"):
                context_parts.append(f"- Estimated {abs(drift.get('drift_months', 0)):.1f} months {'behind' if drift.get('drift_months', 0) > 0 else 'ahead'}")

        # Prediction
        if prediction.get("has_data"):
            if prediction.get("predicted_completion_date"):
                context_parts.append(f"- Predicted completion: {prediction.get('predicted_completion_date')}")
            if prediction.get("on_track") is not None:
                status = "on track" if prediction.get("on_track") else "may miss target"
                context_parts.append(f"- Completion status: {status}")

        # Patterns
        if patterns.get("has_data"):
            context_parts.append(f"- Activity pattern: {patterns.get('pattern_type', 'unknown')}")
            context_parts.append(f"- Last activity: {patterns.get('last_activity_days_ago', 'N/A')} days ago")

        # Stages
        if stages.get("has_data"):
            context_parts.append(f"- Current stage: {stages.get('current_stage', 'Unknown')}")
            if stages.get("is_stuck"):
                context_parts.append("- WARNING: May be stuck in current stage")

        user_prompt = "\n".join(context_parts)
        user_prompt += "\n\nWrite a 3-5 sentence summary of the student's temporal progress patterns."

        result = self.client.call(
            system_prompt=TEMPORAL_SUMMARY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=512,
        )

        return result.get("summary")

    def _generate_template_summary(
        self,
        analysis: Dict[str, Any],
    ) -> str:
        """Generate summary using templates (fallback)."""
        sentences = []

        velocity = analysis.get("velocity", {})
        drift = analysis.get("drift", {})
        prediction = analysis.get("completion_prediction", {})
        patterns = analysis.get("activity_patterns", {})
        stages = analysis.get("stage_transitions", {})

        # Opening: velocity trend
        if velocity.get("has_data"):
            trend = velocity.get("trend", "stable")
            current_vel = velocity.get("current_velocity", 0)
            if trend == "accelerating":
                sentences.append(f"Milestone completion is accelerating, currently at {current_vel:.1f} completions per month.")
            elif trend == "decelerating":
                sentences.append(f"Milestone completion has slowed to {current_vel:.1f} completions per month.")
            else:
                sentences.append(f"Milestone completion is steady at {current_vel:.1f} per month.")

        # Drift status
        if drift.get("has_data"):
            direction = drift.get("drift_direction", "on_track")
            drift_months = drift.get("drift_months", 0)
            if direction == "behind_schedule":
                sentences.append(f"The timeline is running approximately {abs(drift_months):.1f} months behind schedule.")
            elif direction == "ahead_schedule":
                sentences.append(f"Progress is ahead of schedule by about {abs(drift_months):.1f} months.")
            else:
                sentences.append("The timeline is currently on track.")

        # Stage status
        if stages.get("has_data"):
            current_stage = stages.get("current_stage")
            if stages.get("is_stuck"):
                time_in_stage = stages.get("time_in_current_stage_months", 0)
                sentences.append(f"The current stage ({current_stage}) has taken {time_in_stage:.1f} months, longer than typical.")
            elif current_stage:
                sentences.append(f"Currently in the {current_stage} stage.")

        # Activity pattern
        if patterns.get("has_data"):
            pattern = patterns.get("pattern_type", "sporadic")
            last_activity = patterns.get("last_activity_days_ago", 0)
            if pattern == "inactive" or last_activity > 30:
                sentences.append(f"Activity has been low, with no updates in {last_activity} days.")
            elif pattern == "bursty":
                sentences.append("Work tends to happen in bursts rather than steadily.")

        # Prediction
        if prediction.get("has_data") and prediction.get("on_track") is not None:
            if not prediction.get("on_track"):
                behind = prediction.get("months_ahead_or_behind", 0)
                if behind and behind > 0:
                    sentences.append(f"At current pace, completion may be delayed by {behind:.1f} months.")

        return " ".join(sentences) if sentences else "Insufficient data for temporal analysis."

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse a date from various formats."""
        if date_value is None:
            return None
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()
        if isinstance(date_value, str):
            try:
                # Try ISO format
                if "T" in date_value:
                    return datetime.fromisoformat(date_value.replace("Z", "+00:00")).date()
                else:
                    return date.fromisoformat(date_value)
            except ValueError:
                pass
        return None


# =============================================================================
# Convenience Function
# =============================================================================

def analyze_temporal_trends(
    user_id: UUID,
    snapshots: List[Dict[str, Any]],
    progress_events: List[Dict[str, Any]],
    milestones: List[Dict[str, Any]],
    total_duration_months: Optional[int] = None,
    use_llm: bool = True,
) -> Dict[str, Any]:
    """
    Analyze temporal trends for a user.

    Convenience function that creates an engine and calls analyze_trends.

    Args:
        user_id: User ID
        snapshots: AnalyticsSnapshot list
        progress_events: ProgressEvent list
        milestones: Milestone list
        total_duration_months: Expected duration
        use_llm: Whether to use LLM for summary

    Returns:
        Complete temporal analysis dictionary
    """
    engine = TemporalEngine(use_llm=use_llm)
    return engine.analyze_trends(
        user_id=user_id,
        snapshots=snapshots,
        progress_events=progress_events,
        milestones=milestones,
        total_duration_months=total_duration_months,
    )
