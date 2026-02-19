"""LLM service package for Anthropic Claude integration."""
from app.services.llm.client import (
    LLMClient,
    LLMError,
    LLMParseError,
    LLMTimeoutError,
    LLMRateLimitError,
    get_llm_client,
)
from app.services.llm.prompts import (
    build_stages_and_milestones_prompt,
    build_durations_and_dependencies_prompt,
    get_stage_types,
    get_milestone_types,
    get_dependency_types,
    VALID_STAGE_TYPES,
    VALID_MILESTONE_TYPES,
    VALID_DEPENDENCY_TYPES,
)
from app.services.llm.parsers import (
    parse_stages,
    parse_milestones,
    parse_durations,
    parse_dependencies,
)
from app.services.llm.validators import (
    validate_output,
    validate_stage_milestone_consistency,
)
from app.services.llm.metadata_extractor import (
    DocumentMetadataExtractor,
    extract_document_metadata,
)
from app.services.llm.cold_start import (
    ColdStartGenerator,
    generate_cold_start_timeline,
)
from app.services.llm.cold_start_templates import (
    get_template,
    get_all_disciplines,
)
from app.services.intervention_engine import (
    InterventionEngine,
    RiskScores,
    Intervention,
    InterventionReport,
    InterventionType,
    InterventionUrgency,
    evaluate_and_intervene,
)
from app.services.intervention_templates import (
    get_dropout_risk_template,
    get_engagement_template,
    get_continuity_template,
    get_health_dimension_template,
    get_milestone_template,
    get_check_in_template,
    get_resources_by_category,
)
from app.services.explainability_engine import (
    ExplainabilityEngine,
    explain_assessment,
)
from app.services.temporal_engine import (
    TemporalEngine,
    analyze_temporal_trends,
)
from app.services.feedback_engine import (
    FeedbackEngine,
    FeedbackEngineError,
    CorrectionPattern,
    FeedbackSummary,
    record_feedback,
)
from app.services.privacy_engine import (
    PrivacyEngine,
    PrivacyEngineError,
    TenantIsolationError,
    enforce_tenant_isolation,
    anonymize_for_aggregation,
)
from app.services.audit_logger import (
    AuditLogger,
    AuditLoggerError,
    log_access,
    log_data_modification,
    get_audit_trail,
)

__all__ = [
    # Client
    "LLMClient",
    "LLMError",
    "LLMParseError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "get_llm_client",
    # Prompts
    "build_stages_and_milestones_prompt",
    "build_durations_and_dependencies_prompt",
    "get_stage_types",
    "get_milestone_types",
    "get_dependency_types",
    "VALID_STAGE_TYPES",
    "VALID_MILESTONE_TYPES",
    "VALID_DEPENDENCY_TYPES",
    # Parsers
    "parse_stages",
    "parse_milestones",
    "parse_durations",
    "parse_dependencies",
    # Validators
    "validate_output",
    "validate_stage_milestone_consistency",
    # Metadata Extractor
    "DocumentMetadataExtractor",
    "extract_document_metadata",
    # Cold Start
    "ColdStartGenerator",
    "generate_cold_start_timeline",
    "get_template",
    "get_all_disciplines",
    # Intervention Engine
    "InterventionEngine",
    "RiskScores",
    "Intervention",
    "InterventionReport",
    "InterventionType",
    "InterventionUrgency",
    "evaluate_and_intervene",
    # Intervention Templates
    "get_dropout_risk_template",
    "get_engagement_template",
    "get_continuity_template",
    "get_health_dimension_template",
    "get_milestone_template",
    "get_check_in_template",
    "get_resources_by_category",
    # Explainability Engine
    "ExplainabilityEngine",
    "explain_assessment",
    # Temporal Engine
    "TemporalEngine",
    "analyze_temporal_trends",
    # Feedback Engine
    "FeedbackEngine",
    "FeedbackEngineError",
    "CorrectionPattern",
    "FeedbackSummary",
    "record_feedback",
    # Privacy Engine
    "PrivacyEngine",
    "PrivacyEngineError",
    "TenantIsolationError",
    "enforce_tenant_isolation",
    "anonymize_for_aggregation",
    # Audit Logger
    "AuditLogger",
    "AuditLoggerError",
    "log_access",
    "log_data_modification",
    "get_audit_trail",
]
