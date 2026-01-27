"""
Tests for BaseOrchestrator

Tests idempotency, decision tracing, and evidence bundling.
"""

import pytest
import uuid
from typing import Dict, Any
from datetime import datetime

from app.orchestrators.base import (
    BaseOrchestrator,
    OrchestrationError,
    DuplicateRequestError
)
from app.models.idempotency import (
    IdempotencyKey,
    DecisionTrace,
    EvidenceBundle,
    RequestStatus
)


# Test orchestrator implementation
class TestOrchestrator(BaseOrchestrator[Dict[str, Any]]):
    """Simple orchestrator for testing"""
    
    @property
    def orchestrator_name(self) -> str:
        return "test_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple pipeline that echoes input and adds timestamp"""
        # Trace a decision
        self.trace_decision(
            decision_point="process_input",
            decision="accept_input",
            rationale="Input validation passed",
            input_data=context['input']
        )
        
        # Bundle some evidence
        self.bundle_evidence(
            evidence_type="input_data",
            evidence_data=context['input'],
            source="test_client"
        )
        
        # Return result
        result = {
            'input_echo': context['input'],
            'processed_at': datetime.utcnow().isoformat(),
            'user_id': str(context['user_id']) if context['user_id'] else None
        }
        
        return result


class FailingOrchestrator(BaseOrchestrator[Dict[str, Any]]):
    """Orchestrator that always fails (for testing)"""
    
    @property
    def orchestrator_name(self) -> str:
        return "failing_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise ValueError("Intentional failure for testing")


def test_orchestrator_basic_execution(db_session):
    """Test basic orchestrator execution"""
    user_id = uuid.uuid4()
    orchestrator = TestOrchestrator(db_session, user_id)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'message': 'hello', 'value': 42}
    
    # Execute
    result = orchestrator.execute(request_id, input_data)
    
    # Verify result
    assert result['input_echo'] == input_data
    assert result['user_id'] == str(user_id)
    assert 'processed_at' in result
    
    # Verify idempotency key created
    idem_key = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).first()
    
    assert idem_key is not None
    assert idem_key.status == RequestStatus.COMPLETED
    assert idem_key.orchestrator_name == "test_orchestrator"
    assert idem_key.user_id == user_id
    assert idem_key.response_data is not None


def test_orchestrator_idempotency(db_session):
    """Test that duplicate requests return cached response"""
    user_id = uuid.uuid4()
    orchestrator = TestOrchestrator(db_session, user_id)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'message': 'hello'}
    
    # First execution
    result1 = orchestrator.execute(request_id, input_data)
    first_timestamp = result1['processed_at']
    
    # Second execution with same request_id (should return cached)
    result2 = orchestrator.execute(request_id, input_data)
    second_timestamp = result2['processed_at']
    
    # Timestamps should be identical (cached response)
    assert first_timestamp == second_timestamp
    assert result1 == result2
    
    # Verify only one idempotency key
    idem_keys = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).all()
    
    assert len(idem_keys) == 1


def test_orchestrator_decision_tracing(db_session):
    """Test that decisions are traced"""
    orchestrator = TestOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute
    orchestrator.execute(request_id, input_data)
    
    # Verify decision trace created
    traces = db_session.query(DecisionTrace).filter(
        DecisionTrace.request_id == request_id
    ).all()
    
    assert len(traces) == 1
    assert traces[0].decision_point == "process_input"
    assert traces[0].decision == "accept_input"
    assert traces[0].orchestrator_name == "test_orchestrator"
    assert traces[0].sequence_number == 1


def test_orchestrator_evidence_bundling(db_session):
    """Test that evidence is bundled"""
    orchestrator = TestOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute
    orchestrator.execute(request_id, input_data)
    
    # Verify evidence bundle created
    bundles = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.request_id == request_id
    ).all()
    
    assert len(bundles) == 1
    assert bundles[0].evidence_type == "input_data"
    assert bundles[0].orchestrator_name == "test_orchestrator"
    assert bundles[0].source == "test_client"


def test_orchestrator_failure_handling(db_session):
    """Test that failures are recorded"""
    orchestrator = FailingOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute (should fail)
    with pytest.raises(OrchestrationError):
        orchestrator.execute(request_id, input_data)
    
    # Verify idempotency key marked as failed
    idem_key = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).first()
    
    assert idem_key is not None
    assert idem_key.status == RequestStatus.FAILED
    assert idem_key.error_message is not None
    assert "Intentional failure" in idem_key.error_message


def test_orchestrator_different_orchestrators_same_request_id(db_session):
    """Test that different orchestrators can use same request_id"""
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute with TestOrchestrator
    orch1 = TestOrchestrator(db_session)
    result1 = orch1.execute(request_id, input_data)
    
    # Execute with FailingOrchestrator (different orchestrator, same request_id)
    orch2 = FailingOrchestrator(db_session)
    with pytest.raises(OrchestrationError):
        orch2.execute(request_id, input_data)
    
    # Verify two separate idempotency keys
    idem_keys = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).all()
    
    assert len(idem_keys) == 2
    assert {k.orchestrator_name for k in idem_keys} == {"test_orchestrator", "failing_orchestrator"}


def test_orchestrator_ttl_setting(db_session):
    """Test that TTL is set correctly"""
    orchestrator = TestOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Execute with custom TTL
    orchestrator.execute(request_id, input_data, ttl_hours=48)
    
    # Verify TTL
    idem_key = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).first()
    
    assert idem_key.expires_at is not None
    # TTL should be approximately 48 hours from now
    time_diff = (idem_key.expires_at - datetime.utcnow()).total_seconds()
    assert 47 * 3600 < time_diff < 49 * 3600  # Allow 1 hour variance


def test_orchestrator_elapsed_time(db_session):
    """Test elapsed time tracking"""
    orchestrator = TestOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # Start execution
    orchestrator._current_request_id = request_id
    orchestrator._start_time = orchestrator._start_time or __import__('time').time()
    
    # Wait a bit
    import time
    time.sleep(0.1)
    
    # Check elapsed time
    elapsed = orchestrator.get_elapsed_time_ms()
    assert elapsed >= 100  # At least 100ms
    assert elapsed < 200   # But not too much more


def test_orchestrator_retry_after_failure(db_session):
    """Test that failed requests can be retried"""
    orchestrator = FailingOrchestrator(db_session)
    
    request_id = f"test-request-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    # First attempt (fails)
    with pytest.raises(OrchestrationError):
        orchestrator.execute(request_id, input_data)
    
    # Verify marked as failed
    idem_key = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).first()
    assert idem_key.status == RequestStatus.FAILED
    
    # Second attempt should also fail (not return cached error)
    with pytest.raises(OrchestrationError) as exc_info:
        orchestrator.execute(request_id, input_data)
    
    # Should get the "previous request failed" message
    assert "Previous request failed" in str(exc_info.value)
