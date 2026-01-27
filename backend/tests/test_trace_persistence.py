"""
Tests for DecisionTrace and EvidenceBundle Persistence

Tests automatic trace and evidence persistence.
"""

import pytest
import uuid
from typing import Dict, Any

from app.orchestrators.base import BaseOrchestrator
from app.models.idempotency import DecisionTrace, EvidenceBundle


class TracingTestOrchestrator(BaseOrchestrator[Dict[str, Any]]):
    """Test orchestrator that uses tracing features"""
    
    @property
    def orchestrator_name(self) -> str:
        return "tracing_test_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline with multiple steps and evidence"""
        
        # Step 1: Validate input
        with self._trace_step("validate_input") as step:
            input_data = context['input']
            if 'required_field' not in input_data:
                raise ValueError("Missing required field")
            step.details = {"field_count": len(input_data)}
        
        # Step 2: Add evidence
        self.add_evidence(
            evidence_type="input_data",
            data={"fields": list(input_data.keys())},
            source="client_request",
            confidence=1.0
        )
        
        # Step 3: Process data
        with self._trace_step("process_data"):
            processed = {k: v.upper() if isinstance(v, str) else v 
                        for k, v in input_data.items()}
        
        # Step 4: Add more evidence
        self.add_evidence(
            evidence_type="processed_data",
            data={"processed_count": len(processed)},
            source="data_processor",
            confidence=0.95,
            metadata={"method": "uppercase_transform"}
        )
        
        # Step 5: Manual log
        self.log_step(
            action="finalize_result",
            status="success",
            details={"output_size": len(processed)}
        )
        
        return {
            "result": "success",
            "data": processed
        }


class FailingTracingOrchestrator(BaseOrchestrator[Dict[str, Any]]):
    """Test orchestrator that fails but still traces"""
    
    @property
    def orchestrator_name(self) -> str:
        return "failing_tracing_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Add some evidence before failing
        self.add_evidence(
            evidence_type="initial_state",
            data={"starting": True},
            source="test"
        )
        
        with self._trace_step("doomed_operation"):
            raise ValueError("Intentional failure")


def test_decision_trace_persistence(db_session):
    """Test that decision trace is persisted with structured JSON"""
    orchestrator = TracingTestOrchestrator(db_session)
    
    request_id = f"test-trace-{uuid.uuid4()}"
    input_data = {
        'required_field': 'value',
        'another_field': 'data'
    }
    
    # Execute
    result = orchestrator.execute(request_id, input_data)
    
    # Verify trace was created
    trace = db_session.query(DecisionTrace).filter(
        DecisionTrace.event_id == request_id
    ).first()
    
    assert trace is not None
    assert trace.event_id == request_id
    assert trace.trace_json is not None
    
    # Verify trace structure
    trace_data = trace.trace_json
    assert trace_data["orchestrator"] == "tracing_test_orchestrator"
    assert trace_data["request_id"] == request_id
    assert trace_data["result"] == "success"
    assert "started_at" in trace_data
    assert "completed_at" in trace_data
    assert "duration_ms" in trace_data
    assert trace_data["duration_ms"] > 0
    
    # Verify steps
    assert "steps" in trace_data
    steps = trace_data["steps"]
    assert len(steps) >= 3  # At least 3 steps
    
    # Check first step (validate_input)
    validate_step = next((s for s in steps if s["action"] == "validate_input"), None)
    assert validate_step is not None
    assert validate_step["status"] == "success"
    assert validate_step["duration_ms"] is not None
    assert "field_count" in validate_step["details"]
    
    # Check process step
    process_step = next((s for s in steps if s["action"] == "process_data"), None)
    assert process_step is not None
    assert process_step["status"] == "success"
    
    # Check manual log step
    finalize_step = next((s for s in steps if s["action"] == "finalize_result"), None)
    assert finalize_step is not None
    assert finalize_step["status"] == "success"
    assert "output_size" in finalize_step["details"]
    
    # Verify metadata
    assert "metadata" in trace_data
    assert trace_data["metadata"]["total_steps"] == len(steps)


def test_evidence_bundle_persistence(db_session):
    """Test that evidence bundle is persisted with structured JSON"""
    orchestrator = TracingTestOrchestrator(db_session)
    
    request_id = f"test-evidence-{uuid.uuid4()}"
    input_data = {
        'required_field': 'test_value',
        'data': 'sample'
    }
    
    # Execute
    result = orchestrator.execute(request_id, input_data)
    
    # Verify evidence bundle was created
    bundle = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.event_id == request_id
    ).first()
    
    assert bundle is not None
    assert bundle.event_id == request_id
    assert bundle.evidence_json is not None
    
    # Verify bundle structure
    evidence_data = bundle.evidence_json
    assert evidence_data["event_id"] == request_id
    assert evidence_data["orchestrator"] == "tracing_test_orchestrator"
    assert "evidence" in evidence_data
    
    # Verify evidence items
    evidence_items = evidence_data["evidence"]
    assert len(evidence_items) == 2  # Two evidence items added
    
    # Check first evidence (input_data)
    input_evidence = next((e for e in evidence_items if e["type"] == "input_data"), None)
    assert input_evidence is not None
    assert input_evidence["source"] == "client_request"
    assert input_evidence["confidence"] == 1.0
    assert "fields" in input_evidence["data"]
    assert "timestamp" in input_evidence
    
    # Check second evidence (processed_data)
    processed_evidence = next((e for e in evidence_items if e["type"] == "processed_data"), None)
    assert processed_evidence is not None
    assert processed_evidence["source"] == "data_processor"
    assert processed_evidence["confidence"] == 0.95
    assert "processed_count" in processed_evidence["data"]
    assert "metadata" in processed_evidence
    assert processed_evidence["metadata"]["method"] == "uppercase_transform"


def test_trace_on_failure(db_session):
    """Test that trace is still persisted when orchestration fails"""
    orchestrator = FailingTracingOrchestrator(db_session)
    
    request_id = f"test-fail-trace-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute (will fail)
    with pytest.raises(Exception):
        orchestrator.execute(request_id, input_data)
    
    # Verify trace was still created
    trace = db_session.query(DecisionTrace).filter(
        DecisionTrace.event_id == request_id
    ).first()
    
    assert trace is not None
    trace_data = trace.trace_json
    
    # Verify failure is recorded
    assert trace_data["result"] == "failed"
    assert "error" in trace_data
    assert "Intentional failure" in trace_data["error"]
    
    # Verify steps were recorded
    assert "steps" in trace_data
    assert len(trace_data["steps"]) > 0
    
    # Check that the failed step is marked
    failed_step = next((s for s in trace_data["steps"] if s["status"] == "failed"), None)
    assert failed_step is not None
    assert failed_step["action"] == "doomed_operation"
    assert "error" in failed_step
    
    # Verify evidence was still captured
    bundle = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.event_id == request_id
    ).first()
    
    assert bundle is not None
    evidence_data = bundle.evidence_json
    assert len(evidence_data["evidence"]) > 0


def test_no_evidence_no_bundle(db_session):
    """Test that no evidence bundle is created if no evidence is added"""
    
    class NoEvidenceOrchestrator(BaseOrchestrator[Dict[str, Any]]):
        @property
        def orchestrator_name(self) -> str:
            return "no_evidence_orchestrator"
        
        def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Just steps, no evidence
            with self._trace_step("simple_step"):
                pass
            return {"result": "success"}
    
    orchestrator = NoEvidenceOrchestrator(db_session)
    request_id = f"test-no-evidence-{uuid.uuid4()}"
    
    result = orchestrator.execute(request_id, {})
    
    # Trace should exist
    trace = db_session.query(DecisionTrace).filter(
        DecisionTrace.event_id == request_id
    ).first()
    assert trace is not None
    
    # But no evidence bundle
    bundle = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.event_id == request_id
    ).first()
    assert bundle is None


def test_trace_step_context_manager(db_session):
    """Test that trace_step context manager works correctly"""
    
    class ContextManagerTestOrchestrator(BaseOrchestrator[Dict[str, Any]]):
        @property
        def orchestrator_name(self) -> str:
            return "context_test_orchestrator"
        
        def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Use context manager with details
            with self._trace_step("step_with_details") as step:
                step.details = {"custom": "data", "count": 42}
            
            # Nested context managers
            with self._trace_step("outer_step"):
                with self._trace_step("inner_step"):
                    pass
            
            return {"done": True}
    
    orchestrator = ContextManagerTestOrchestrator(db_session)
    request_id = f"test-context-{uuid.uuid4()}"
    
    result = orchestrator.execute(request_id, {})
    
    trace = db_session.query(DecisionTrace).filter(
        DecisionTrace.event_id == request_id
    ).first()
    
    steps = trace.trace_json["steps"]
    
    # Find step with details
    detail_step = next((s for s in steps if s["action"] == "step_with_details"), None)
    assert detail_step is not None
    assert detail_step["details"]["custom"] == "data"
    assert detail_step["details"]["count"] == 42
    
    # Verify nested steps
    outer = next((s for s in steps if s["action"] == "outer_step"), None)
    inner = next((s for s in steps if s["action"] == "inner_step"), None)
    assert outer is not None
    assert inner is not None
    # Inner should have higher step number
    assert inner["step"] > outer["step"]


def test_json_serialization_safe(db_session):
    """Test that non-JSON-serializable data is handled gracefully"""
    
    class SerializationTestOrchestrator(BaseOrchestrator[Dict[str, Any]]):
        @property
        def orchestrator_name(self) -> str:
            return "serialization_test_orchestrator"
        
        def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Add evidence with basic JSON-safe types
            self.add_evidence(
                evidence_type="safe_data",
                data={
                    "string": "text",
                    "number": 42,
                    "float": 3.14,
                    "bool": True,
                    "null": None,
                    "list": [1, 2, 3],
                    "dict": {"nested": "value"}
                }
            )
            return {"result": "success"}
    
    orchestrator = SerializationTestOrchestrator(db_session)
    request_id = f"test-serialization-{uuid.uuid4()}"
    
    # Should not raise any serialization errors
    result = orchestrator.execute(request_id, {})
    
    bundle = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.event_id == request_id
    ).first()
    
    assert bundle is not None
    evidence_item = bundle.evidence_json["evidence"][0]
    
    # Verify all types are preserved
    data = evidence_item["data"]
    assert data["string"] == "text"
    assert data["number"] == 42
    assert data["float"] == 3.14
    assert data["bool"] is True
    assert data["null"] is None
    assert data["list"] == [1, 2, 3]
    assert data["dict"]["nested"] == "value"
