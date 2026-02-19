"""Timeline response serialization builder."""
from datetime import datetime
from typing import Any, Dict

from app.orchestrators.timeline_pipeline import TimelinePipelineResult


class TimelineResponseBuilder:
    """Converts timeline pipeline results into API response payloads."""

    STATUS_DRAFT = "DRAFT"

    def build_generation_response(self, pipeline_result: TimelinePipelineResult) -> Dict[str, Any]:
        draft = pipeline_result.draft_timeline
        stages = pipeline_result.stage_records
        milestones = pipeline_result.milestone_records

        milestones_by_stage: dict[str, list] = {}
        for milestone in milestones:
            key = str(milestone.timeline_stage_id)
            milestones_by_stage.setdefault(key, []).append(milestone)

        stage_payload = []
        for stage in stages:
            stage_milestones = milestones_by_stage.get(str(stage.id), [])
            stage_payload.append(
                {
                    "id": str(stage.id),
                    "title": stage.title,
                    "description": stage.description,
                    "stage_order": stage.stage_order,
                    "duration_months": stage.duration_months,
                    "status": stage.status,
                    "milestones": [
                        {
                            "id": str(m.id),
                            "title": m.title,
                            "description": m.description,
                            "milestone_order": m.milestone_order,
                            "is_critical": m.is_critical,
                            "is_completed": m.is_completed,
                            "deliverable_type": m.deliverable_type,
                        }
                        for m in stage_milestones
                    ],
                }
            )

        duration_payload = [
            {
                "item_description": item.item_description,
                "item_type": item.item_type,
                "duration_weeks_min": item.duration_weeks_min,
                "duration_weeks_max": item.duration_weeks_max,
                "duration_months_min": item.duration_months_min,
                "duration_months_max": item.duration_months_max,
                "confidence": item.confidence,
                "basis": item.basis,
            }
            for item in pipeline_result.duration_estimates
        ]

        dependencies_payload = [
            {
                "dependent_item": dep.dependent_item,
                "depends_on_item": dep.depends_on_item,
                "dependency_type": dep.dependency_type,
                "confidence": dep.confidence,
                "reason": dep.reason,
            }
            for dep in pipeline_result.dependencies
        ]

        stage_durations = [d for d in pipeline_result.duration_estimates if d.item_type == "stage"]

        return {
            "timeline": {
                "id": str(draft.id),
                "baseline_id": str(draft.baseline_id),
                "user_id": str(draft.user_id),
                "title": draft.title,
                "description": draft.description,
                "version_number": draft.version_number,
                "is_active": draft.is_active,
                "status": self.STATUS_DRAFT,
                "created_at": draft.created_at.isoformat() if draft.created_at else None,
            },
            "stages": stage_payload,
            "dependencies": dependencies_payload,
            "durations": duration_payload,
            "metadata": {
                "total_stages": len(stages),
                "total_milestones": len(milestones),
                "total_duration_months_min": sum(d.duration_months_min for d in stage_durations),
                "total_duration_months_max": sum(d.duration_months_max for d in stage_durations),
                "is_dag_valid": len(dependencies_payload) > 0,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }
