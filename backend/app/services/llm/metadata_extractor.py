"""Document metadata extraction using LLM."""
import logging
from typing import Any, Dict, List, Optional

from app.services.llm.client import LLMClient, get_llm_client, LLMError

logger = logging.getLogger(__name__)


# Default empty result for when extraction fails
DEFAULT_METADATA = {
    "supervisor_names": [],
    "research_domain": None,
    "research_goals": [],
    "methodologies": [],
    "funding_sources": [],
    "deadlines": [],
    "institution_name": None,
    "expected_duration_years": None,
    "key_tools_and_technologies": [],
    "ethical_requirements": [],
}

METADATA_EXTRACTION_SYSTEM_PROMPT = """You are an expert academic document analyst. Extract structured metadata from PhD research documents.

Analyze the provided document text and extract the following information. If a field cannot be determined from the text, use null for single values or empty array [] for lists.

Return a JSON object with exactly these keys:

{
    "supervisor_names": ["list of advisor/supervisor names found in the document"],
    "research_domain": "specific research field like 'Natural Language Processing' or 'Behavioral Economics', not generic fields like 'Computer Science'",
    "research_goals": ["list of 2-5 main research objectives or goals"],
    "methodologies": ["list of research methods mentioned, e.g., 'qualitative interviews', 'RCT', 'machine learning', 'ethnography'"],
    "funding_sources": ["list of grants, fellowships, scholarships, or funding sources mentioned"],
    "deadlines": ["list of specific dates or deadlines mentioned, formatted as strings"],
    "institution_name": "university or research institution name if mentioned",
    "expected_duration_years": number representing expected program length in years (e.g., 4 or 5), or null if not mentioned,
    "key_tools_and_technologies": ["software, frameworks, equipment, platforms mentioned, e.g., 'Python', 'SPSS', 'fMRI', 'AWS'"],
    "ethical_requirements": ["IRB approval, ethics board requirements, consent protocols, HIPAA, GDPR requirements if mentioned"]
}

Be precise and extract only information explicitly stated or strongly implied in the document.
Do not invent or assume information that is not present.
For research_domain, be as specific as possible based on the document content.

Respond with ONLY valid JSON, no markdown fences, no preamble."""


class DocumentMetadataExtractor:
    """
    Extracts structured metadata from PhD research documents using LLM.

    Extracts:
    - Supervisor/advisor names
    - Research domain (specific field)
    - Research goals and objectives
    - Methodologies
    - Funding sources
    - Deadlines
    - Institution name
    - Expected duration
    - Tools and technologies
    - Ethical requirements
    """

    def __init__(self, client: Optional[LLMClient] = None):
        """
        Initialize the metadata extractor.

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

    def extract_metadata(
        self,
        text: str,
        section_map: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from document text using LLM.

        Args:
            text: Normalized document text
            section_map: Optional section map with document structure

        Returns:
            Dictionary with extracted metadata fields.
            Returns default empty values if extraction fails.
        """
        if not text or len(text.strip()) < 50:
            logger.warning("Text too short for metadata extraction")
            return DEFAULT_METADATA.copy()

        try:
            # Build user prompt
            user_prompt = self._build_user_prompt(text, section_map)

            # Call LLM
            logger.info("Extracting document metadata via LLM")
            result = self.client.call(
                system_prompt=METADATA_EXTRACTION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                max_tokens=2048
            )

            # Validate and normalize result
            return self._normalize_result(result)

        except LLMError as e:
            logger.error(f"LLM metadata extraction failed: {e}")
            return DEFAULT_METADATA.copy()
        except Exception as e:
            logger.error(f"Unexpected error in metadata extraction: {e}")
            return DEFAULT_METADATA.copy()

    def _build_user_prompt(
        self,
        text: str,
        section_map: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build the user prompt for metadata extraction.

        Args:
            text: Document text
            section_map: Optional section map

        Returns:
            Formatted user prompt
        """
        # Truncate text if too long (keep first ~8000 chars for context window)
        max_text_length = 8000
        if len(text) > max_text_length:
            truncated_text = text[:max_text_length] + "\n\n[... document truncated ...]"
        else:
            truncated_text = text

        prompt_parts = ["Analyze this PhD research document and extract metadata:\n"]

        # Add section structure if available
        if section_map and section_map.get("sections"):
            sections = section_map["sections"]
            section_titles = [s.get("title", "Untitled") for s in sections[:15]]
            prompt_parts.append(f"Document sections: {', '.join(section_titles)}\n")

        prompt_parts.append(f"\n--- DOCUMENT TEXT ---\n{truncated_text}\n--- END DOCUMENT ---")
        prompt_parts.append("\n\nExtract the metadata as specified. Return JSON only.")

        return "\n".join(prompt_parts)

    def _normalize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate the LLM result.

        Ensures all expected fields are present with correct types.

        Args:
            result: Raw LLM response dict

        Returns:
            Normalized result dict
        """
        normalized = DEFAULT_METADATA.copy()

        # List fields
        list_fields = [
            "supervisor_names",
            "research_goals",
            "methodologies",
            "funding_sources",
            "deadlines",
            "key_tools_and_technologies",
            "ethical_requirements",
        ]

        for field in list_fields:
            value = result.get(field)
            if isinstance(value, list):
                # Filter out empty strings and non-strings
                normalized[field] = [
                    str(item).strip()
                    for item in value
                    if item and str(item).strip()
                ]
            elif isinstance(value, str) and value.strip():
                # Single string provided instead of list
                normalized[field] = [value.strip()]

        # String fields
        string_fields = ["research_domain", "institution_name"]
        for field in string_fields:
            value = result.get(field)
            if isinstance(value, str) and value.strip():
                normalized[field] = value.strip()
            else:
                normalized[field] = None

        # Numeric field: expected_duration_years
        duration = result.get("expected_duration_years")
        if duration is not None:
            try:
                duration_float = float(duration)
                if 1 <= duration_float <= 10:
                    normalized["expected_duration_years"] = duration_float
                else:
                    normalized["expected_duration_years"] = None
            except (TypeError, ValueError):
                normalized["expected_duration_years"] = None

        return normalized


# Convenience function
def extract_document_metadata(
    text: str,
    section_map: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract metadata from document text.

    Convenience function that creates extractor and calls extract_metadata.

    Args:
        text: Normalized document text
        section_map: Optional section map

    Returns:
        Extracted metadata dictionary
    """
    extractor = DocumentMetadataExtractor()
    return extractor.extract_metadata(text, section_map)
