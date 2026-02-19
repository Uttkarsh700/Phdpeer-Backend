"""
Cold start timeline generation for users without uploaded documents.

Generates realistic PhD timelines based on discipline and program information
when no document is available for extraction.
"""
import logging
from typing import Any, Dict, List, Optional

from app.services.llm.client import LLMClient, get_llm_client, LLMError
from app.services.llm.cold_start_templates import get_template

logger = logging.getLogger(__name__)


# =============================================================================
# System Prompt for Cold Start Generation
# =============================================================================

COLD_START_SYSTEM_PROMPT = """You are an expert academic advisor who helps PhD students plan their doctoral journey.
Generate a realistic, discipline-specific PhD timeline based on the provided information.

Your response must be a JSON object with exactly these keys:

{
    "stages": [
        {
            "title": "Stage title (e.g., 'Literature Review and Theory Development')",
            "stage_type": "one of: coursework, literature_review, methodology, data_collection, analysis, writing, defense, other",
            "description": "Detailed description of what this stage involves",
            "order_hint": 1,
            "duration_months": 6,
            "confidence": 0.85
        }
    ],
    "milestones": [
        {
            "name": "Milestone name (e.g., 'Pass Qualifying Examination')",
            "stage": "Title of the stage this milestone belongs to (must match a stage title exactly)",
            "description": "What this milestone involves",
            "milestone_type": "one of: academic, examination, deliverable, publication, regulatory, training, other",
            "is_critical": true,
            "confidence": 0.8
        }
    ],
    "durations": [
        {
            "item_description": "Stage or milestone name",
            "item_type": "stage or milestone",
            "duration_weeks_min": 24,
            "duration_weeks_max": 32,
            "duration_months_min": 6,
            "duration_months_max": 8,
            "confidence": 0.8,
            "basis": "Based on typical [discipline] PhD programs"
        }
    ],
    "dependencies": [
        {
            "dependent_item": "Item that depends on another (milestone or stage name)",
            "depends_on_item": "Item that must be completed first",
            "dependency_type": "one of: finish_to_start, start_to_start, finish_to_finish",
            "confidence": 0.9,
            "reason": "Why this dependency exists"
        }
    ]
}

Guidelines:
1. Generate 5-7 stages appropriate for the discipline
2. Include discipline-specific requirements (e.g., IRB approval for human subjects research, lab work for sciences, archival research for humanities)
3. Each stage should have 2-4 milestones
4. Include critical milestones: qualifying exam, proposal defense, final defense
5. Total duration should be 4-6 years (48-72 months) depending on discipline
6. Dependencies should form a valid DAG (no circular dependencies)
7. Be realistic about durations based on the specific discipline

Respond with ONLY valid JSON, no markdown fences, no preamble."""


# =============================================================================
# Cold Start Generator
# =============================================================================

class ColdStartGenerator:
    """
    Generates PhD timelines without an uploaded document.

    Uses LLM to create discipline-specific timelines based on program information.
    Falls back to hardcoded templates if LLM fails.
    """

    def __init__(self, client: Optional[LLMClient] = None):
        """
        Initialize the cold start generator.

        Args:
            client: Optional LLMClient instance. If not provided, uses singleton.
        """
        self._client = client

    @property
    def client(self) -> LLMClient:
        """Lazy initialization of LLM client."""
        if self._client is None:
            self._client = get_llm_client()
        return self._client

    def generate_cold_start_timeline(
        self,
        field_of_study: str,
        institution: Optional[str] = None,
        program_name: Optional[str] = None,
        start_date: Optional[str] = None,
        total_duration_months: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a timeline without a document using LLM or fallback templates.

        Args:
            field_of_study: Research field/discipline (e.g., "Computer Science")
            institution: Academic institution name
            program_name: PhD program name
            start_date: Program start date (ISO format)
            total_duration_months: Expected program duration

        Returns:
            Dictionary with keys: stages, milestones, durations, dependencies
            in the same format used by the timeline intelligence engine.
        """
        if not field_of_study:
            logger.warning("No field of study provided, using generic template")
            return self._get_fallback_timeline("generic")

        # Try LLM generation first
        try:
            logger.info(f"Generating cold start timeline for: {field_of_study}")
            result = self._generate_via_llm(
                field_of_study=field_of_study,
                institution=institution,
                program_name=program_name,
                start_date=start_date,
                total_duration_months=total_duration_months
            )

            # Validate the result has required keys
            if self._validate_result(result):
                return result
            else:
                logger.warning("LLM result validation failed, using fallback")
                return self._get_fallback_timeline(field_of_study)

        except LLMError as e:
            logger.error(f"LLM cold start generation failed: {e}")
            return self._get_fallback_timeline(field_of_study)
        except Exception as e:
            logger.error(f"Unexpected error in cold start generation: {e}")
            return self._get_fallback_timeline(field_of_study)

    def _generate_via_llm(
        self,
        field_of_study: str,
        institution: Optional[str],
        program_name: Optional[str],
        start_date: Optional[str],
        total_duration_months: Optional[int],
    ) -> Dict[str, Any]:
        """
        Generate timeline using LLM.

        Args:
            field_of_study: Research field
            institution: Institution name
            program_name: Program name
            start_date: Start date
            total_duration_months: Duration

        Returns:
            Parsed LLM response
        """
        user_prompt = self._build_user_prompt(
            field_of_study=field_of_study,
            institution=institution,
            program_name=program_name,
            start_date=start_date,
            total_duration_months=total_duration_months
        )

        result = self.client.call(
            system_prompt=COLD_START_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=4096
        )

        return self._normalize_result(result)

    def _build_user_prompt(
        self,
        field_of_study: str,
        institution: Optional[str],
        program_name: Optional[str],
        start_date: Optional[str],
        total_duration_months: Optional[int],
    ) -> str:
        """Build the user prompt for LLM generation."""
        parts = [f"Generate a PhD timeline for a student in {field_of_study}"]

        if institution:
            parts.append(f"at {institution}")

        if program_name:
            parts.append(f"in the {program_name} program")

        parts.append(".")

        if start_date:
            parts.append(f"\nProgram start date: {start_date}")

        if total_duration_months:
            years = total_duration_months / 12
            parts.append(f"\nExpected program duration: {total_duration_months} months ({years:.1f} years)")
        else:
            parts.append("\nExpected program duration: 4-5 years (typical PhD)")

        # Add discipline-specific guidance
        parts.append(self._get_discipline_guidance(field_of_study))

        parts.append("\n\nGenerate the complete timeline as JSON.")

        return " ".join(parts)

    def _get_discipline_guidance(self, field_of_study: str) -> str:
        """Get discipline-specific guidance for the LLM."""
        field_lower = field_of_study.lower()

        if any(kw in field_lower for kw in ["computer", "software", "data", "machine learning", "ai"]):
            return """
Consider including:
- Implementation and coding phases
- Experiments and benchmarks
- Conference paper submissions
- System evaluation and ablation studies"""

        elif any(kw in field_lower for kw in ["biology", "biochem", "molecular", "genetics", "neuro"]):
            return """
Consider including:
- Laboratory safety training
- IRB/IACUC approval for human/animal subjects
- Wet lab experiments
- Sample collection and analysis
- Longer data collection phases (experiments may fail)"""

        elif any(kw in field_lower for kw in ["psychology", "cognitive", "behavioral"]):
            return """
Consider including:
- IRB approval for human subjects
- Participant recruitment
- Behavioral experiments or surveys
- Statistical analysis training"""

        elif any(kw in field_lower for kw in ["engineer", "mechanical", "electrical", "civil"]):
            return """
Consider including:
- System design and prototyping
- Laboratory experiments
- Simulation and modeling
- Hardware fabrication/testing
- Patent considerations"""

        elif any(kw in field_lower for kw in ["history", "philosophy", "literature", "classics", "humanities"]):
            return """
Consider including:
- Language proficiency requirements
- Archival research and fieldwork
- Longer literature review phases
- Chapter-by-chapter writing
- Prospectus/comprehensive exams"""

        elif any(kw in field_lower for kw in ["business", "management", "economics", "finance"]):
            return """
Consider including:
- Empirical research methods
- Data collection (surveys, interviews, archival)
- Journal paper submissions
- Job market preparation"""

        elif any(kw in field_lower for kw in ["medicine", "clinical", "health", "nursing", "epidem"]):
            return """
Consider including:
- IRB approval for clinical research
- Clinical trial registration
- Patient recruitment
- Regulatory compliance
- Clinical rotations if applicable"""

        return ""

    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate that the LLM result has required structure."""
        required_keys = ["stages", "milestones", "durations", "dependencies"]

        for key in required_keys:
            if key not in result:
                logger.warning(f"Missing required key: {key}")
                return False
            if not isinstance(result[key], list):
                logger.warning(f"Key {key} is not a list")
                return False

        # Check stages have required fields
        for stage in result.get("stages", []):
            if not stage.get("title") or not stage.get("stage_type"):
                logger.warning("Stage missing title or stage_type")
                return False

        # Check we have at least some content
        if len(result.get("stages", [])) < 3:
            logger.warning("Too few stages generated")
            return False

        return True

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and clean up the LLM result."""
        normalized = {
            "stages": [],
            "milestones": [],
            "durations": [],
            "dependencies": []
        }

        # Normalize stages
        for i, stage in enumerate(result.get("stages", [])):
            normalized["stages"].append({
                "title": str(stage.get("title", f"Stage {i+1}")).strip(),
                "stage_type": str(stage.get("stage_type", "other")).lower(),
                "description": str(stage.get("description", "")).strip(),
                "order_hint": int(stage.get("order_hint", i + 1)),
                "duration_months": int(stage.get("duration_months", 6)),
                "confidence": float(stage.get("confidence", 0.8))
            })

        # Normalize milestones
        for milestone in result.get("milestones", []):
            normalized["milestones"].append({
                "name": str(milestone.get("name", "")).strip(),
                "stage": str(milestone.get("stage", "")).strip(),
                "description": str(milestone.get("description", "")).strip(),
                "milestone_type": str(milestone.get("milestone_type", "deliverable")).lower(),
                "is_critical": bool(milestone.get("is_critical", False)),
                "confidence": float(milestone.get("confidence", 0.8))
            })

        # Normalize durations
        for duration in result.get("durations", []):
            normalized["durations"].append({
                "item_description": str(duration.get("item_description", "")).strip(),
                "item_type": str(duration.get("item_type", "stage")).lower(),
                "duration_weeks_min": int(duration.get("duration_weeks_min", 4)),
                "duration_weeks_max": int(duration.get("duration_weeks_max", 8)),
                "duration_months_min": int(duration.get("duration_months_min", 1)),
                "duration_months_max": int(duration.get("duration_months_max", 2)),
                "confidence": float(duration.get("confidence", 0.7)),
                "basis": str(duration.get("basis", "")).strip()
            })

        # Normalize dependencies
        for dep in result.get("dependencies", []):
            normalized["dependencies"].append({
                "dependent_item": str(dep.get("dependent_item", "")).strip(),
                "depends_on_item": str(dep.get("depends_on_item", "")).strip(),
                "dependency_type": str(dep.get("dependency_type", "finish_to_start")).lower(),
                "confidence": float(dep.get("confidence", 0.8)),
                "reason": str(dep.get("reason", "")).strip()
            })

        return normalized

    def _get_fallback_timeline(self, discipline: str) -> Dict[str, Any]:
        """
        Get a fallback timeline from hardcoded templates.

        Args:
            discipline: Field of study

        Returns:
            Template-based timeline
        """
        logger.info(f"Using fallback template for: {discipline}")
        template = get_template(discipline)

        # Convert template format to expected output format
        stages = []
        for stage in template.get("stages", []):
            stages.append({
                "title": stage["title"],
                "stage_type": stage.get("stage_type", "other"),
                "description": stage.get("description", ""),
                "order_hint": stage.get("order_hint", 1),
                "duration_months": stage.get("duration_months", 6),
                "confidence": stage.get("confidence", 0.8)
            })

        milestones = []
        for milestone in template.get("milestones", []):
            milestones.append({
                "name": milestone["name"],
                "stage": milestone["stage"],
                "description": milestone.get("description", ""),
                "milestone_type": milestone.get("milestone_type", "deliverable"),
                "is_critical": milestone.get("is_critical", False),
                "confidence": 0.85
            })

        # Generate durations from stages
        durations = []
        for stage in template.get("stages", []):
            duration_months = stage.get("duration_months", 6)
            durations.append({
                "item_description": stage["title"],
                "item_type": "stage",
                "duration_weeks_min": duration_months * 4 - 4,
                "duration_weeks_max": duration_months * 4 + 4,
                "duration_months_min": max(1, duration_months - 2),
                "duration_months_max": duration_months + 2,
                "confidence": 0.8,
                "basis": f"Based on typical {template.get('discipline', 'PhD')} programs"
            })

        # Convert dependencies
        dependencies = []
        for dep in template.get("dependencies", []):
            dependencies.append({
                "dependent_item": dep["dependent"],
                "depends_on_item": dep["depends_on"],
                "dependency_type": dep.get("type", "finish_to_start"),
                "confidence": 0.9,
                "reason": "Standard PhD progression"
            })

        return {
            "stages": stages,
            "milestones": milestones,
            "durations": durations,
            "dependencies": dependencies
        }


# =============================================================================
# Convenience Function
# =============================================================================

def generate_cold_start_timeline(
    field_of_study: str,
    institution: Optional[str] = None,
    program_name: Optional[str] = None,
    start_date: Optional[str] = None,
    total_duration_months: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate a timeline without a document.

    Convenience function that creates a generator and calls generate_cold_start_timeline.

    Args:
        field_of_study: Research field/discipline
        institution: Academic institution name
        program_name: PhD program name
        start_date: Program start date
        total_duration_months: Expected duration

    Returns:
        Timeline dictionary with stages, milestones, durations, dependencies
    """
    generator = ColdStartGenerator()
    return generator.generate_cold_start_timeline(
        field_of_study=field_of_study,
        institution=institution,
        program_name=program_name,
        start_date=start_date,
        total_duration_months=total_duration_months
    )
