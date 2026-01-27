# BaseOrchestrator Guide

Complete guide for using the BaseOrchestrator class with idempotency, decision tracing, and evidence bundling.

---

## Overview

**BaseOrchestrator** is an abstract base class that provides:
1. **Idempotency** - Prevents duplicate operations
2. **Decision Tracing** - Audit trail of decisions
3. **Evidence Bundling** - Explainability of decisions
4. **Deterministic Pipeline** - Consistent execution pattern

All feature orchestrators (Baseline, Timeline, Assessment, etc.) should extend this class.

---

## Architecture

### Three Core Tables

**1. idempotency_keys**
- Tracks unique requests
- Caches responses
- Prevents duplicate operations
- TTL-based cleanup

**2. decision_traces**
- Records decisions made
- Audit trail
- Sequence tracking
- Input/output logging

**3. evidence_bundles**
- Stores evidence data
- Confidence scores
- Source tracking
- Metadata support

---

## Creating an Orchestrator

### Basic Structure

```python
from typing import Dict, Any
from app.orchestrators.base import BaseOrchestrator

class MyOrchestrator(BaseOrchestrator[MyResultType]):
    """
    My custom orchestrator.
    
    Extends BaseOrchestrator to add feature-specific logic.
    """
    
    @property
    def orchestrator_name(self) -> str:
        """Unique name for this orchestrator"""
        return "my_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> MyResultType:
        """
        Execute the orchestration pipeline.
        
        This is where your business logic goes.
        """
        # Step 1: Extract input
        input_data = context['input']
        user_id = context['user_id']
        
        # Step 2: Trace decision
        self.trace_decision(
            decision_point="validate_input",
            decision="input_valid",
            rationale="All required fields present",
            input_data=input_data
        )
        
        # Step 3: Bundle evidence
        self.bundle_evidence(
            evidence_type="input_data",
            evidence_data=input_data,
            source=f"User:{user_id}"
        )
        
        # Step 4: Execute business logic
        result = self._do_work(input_data)
        
        # Step 5: Return result
        return result
```

---

## Usage Example

### Simple Orchestrator

```python
from uuid import UUID
from dataclasses import dataclass
from app.orchestrators.base import BaseOrchestrator

@dataclass
class CalculationResult:
    """Result of calculation"""
    id: UUID
    sum_value: int
    product_value: int

class CalculationOrchestrator(BaseOrchestrator[CalculationResult]):
    """Performs calculations with full traceability"""
    
    @property
    def orchestrator_name(self) -> str:
        return "calculation_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> CalculationResult:
        input_data = context['input']
        numbers = input_data['numbers']
        
        # Trace: Input validation
        self.trace_decision(
            decision_point="validate_input",
            decision="accept",
            rationale=f"Received {len(numbers)} valid numbers",
            input_data={'count': len(numbers)}
        )
        
        # Bundle: Original data
        self.bundle_evidence(
            evidence_type="input_numbers",
            evidence_data={'numbers': numbers},
            confidence_score=1.0
        )
        
        # Calculate sum
        sum_value = sum(numbers)
        self.trace_decision(
            decision_point="calculate_sum",
            decision=f"sum={sum_value}",
            output_data={'sum': sum_value}
        )
        
        # Calculate product
        product_value = 1
        for n in numbers:
            product_value *= n
        
        self.trace_decision(
            decision_point="calculate_product",
            decision=f"product={product_value}",
            output_data={'product': product_value}
        )
        
        # Create result
        result = CalculationResult(
            id=UUID('12345678-1234-5678-1234-567812345678'),
            sum_value=sum_value,
            product_value=product_value
        )
        
        return result
```

### Using the Orchestrator

```python
from sqlalchemy.orm import Session
from app.database import SessionLocal

# Create session
db: Session = SessionLocal()

# Create orchestrator
orchestrator = CalculationOrchestrator(db, user_id=user.id)

# Execute with idempotency key
request_id = "calc-2024-01-15-001"
input_data = {'numbers': [1, 2, 3, 4, 5]}

result = orchestrator.execute(
    request_id=request_id,
    input_data=input_data,
    ttl_hours=24
)

print(f"Sum: {result.sum_value}")        # 15
print(f"Product: {result.product_value}") # 120

# Second call with same request_id returns cached result
result2 = orchestrator.execute(request_id, input_data)
assert result == result2  # Identical (cached)
```

---

## Idempotency

### How It Works

```
Client Request → BaseOrchestrator
                      ↓
            Check idempotency_keys table
                      ↓
         ┌───────────┴───────────┐
         │                       │
   Found COMPLETED          Not Found
         │                       │
   Return cached           Execute pipeline
     response                    │
                           Store result
                                 │
                           Cache response
```

### Request States

| Status | Meaning | Action |
|--------|---------|--------|
| **PENDING** | Just created | Transition to PROCESSING |
| **PROCESSING** | Currently running | Reject duplicate requests |
| **COMPLETED** | Finished successfully | Return cached response |
| **FAILED** | Execution failed | Allow retry |

### Duplicate Request Handling

```python
# First request
result1 = orchestrator.execute("req-123", data)
# Creates idempotency key, executes pipeline, caches result

# Second request (same ID)
result2 = orchestrator.execute("req-123", data)
# Returns cached result without re-execution

# Third request (in-flight)
# While first request is processing:
try:
    result3 = orchestrator.execute("req-123", data)
except DuplicateRequestError:
    # Request already being processed
    pass
```

---

## Decision Tracing

### Recording Decisions

```python
def _execute_pipeline(self, context):
    # Simple decision
    self.trace_decision(
        decision_point="step_1",
        decision="continue"
    )
    
    # Decision with rationale
    self.trace_decision(
        decision_point="validate_data",
        decision="data_valid",
        rationale="All required fields present and correctly formatted"
    )
    
    # Decision with input/output
    self.trace_decision(
        decision_point="transform_data",
        decision="transformed",
        input_data={'raw': raw_data},
        output_data={'processed': processed_data}
    )
    
    # Decision with timing
    start = time.time()
    result = expensive_operation()
    duration_ms = int((time.time() - start) * 1000)
    
    self.trace_decision(
        decision_point="expensive_op",
        decision="completed",
        duration_ms=duration_ms
    )
```

### Querying Decision Traces

```python
# Get all decisions for a request
traces = db.query(DecisionTrace).filter(
    DecisionTrace.request_id == request_id
).order_by(DecisionTrace.sequence_number).all()

for trace in traces:
    print(f"{trace.sequence_number}. {trace.decision_point}: {trace.decision}")
    if trace.rationale:
        print(f"   Reason: {trace.rationale}")
```

---

## Evidence Bundling

### Storing Evidence

```python
def _execute_pipeline(self, context):
    # Document text evidence
    self.bundle_evidence(
        evidence_type="document_text",
        evidence_data={'text': extracted_text, 'length': len(extracted_text)},
        source=f"DocumentArtifact:{doc_id}",
        confidence_score=0.95
    )
    
    # Analysis results
    self.bundle_evidence(
        evidence_type="analysis_results",
        evidence_data={'stages': detected_stages, 'milestones': detected_milestones},
        metadata={'algorithm': 'rule_based_v1', 'version': '1.0'}
    )
    
    # External data
    self.bundle_evidence(
        evidence_type="user_preferences",
        evidence_data={'preferences': user_prefs},
        source=f"User:{user_id}",
        confidence_score=1.0
    )
```

### Querying Evidence

```python
# Get all evidence for a request
bundles = db.query(EvidenceBundle).filter(
    EvidenceBundle.request_id == request_id
).all()

for bundle in bundles:
    print(f"Type: {bundle.evidence_type}")
    print(f"Confidence: {bundle.confidence_score}")
    print(f"Data: {bundle.evidence_data}")
```

---

## Advanced Features

### Custom Serialization

```python
class MyOrchestrator(BaseOrchestrator[MyComplexType]):
    def _serialize_result(self, result: MyComplexType) -> Dict[str, Any]:
        """Custom serialization for caching"""
        return {
            'id': str(result.id),
            'name': result.name,
            'items': [item.to_dict() for item in result.items]
        }
    
    def _deserialize_result(self, response_data: Dict[str, Any]) -> MyComplexType:
        """Custom deserialization from cache"""
        return MyComplexType(
            id=UUID(response_data['id']),
            name=response_data['name'],
            items=[Item.from_dict(item) for item in response_data['items']]
        )
```

### Custom Context Preparation

```python
class MyOrchestrator(BaseOrchestrator[MyResult]):
    def _prepare_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add custom context data"""
        context = super()._prepare_context(input_data)
        
        # Add custom data
        context['config'] = self._load_config()
        context['timestamp'] = datetime.utcnow()
        
        return context
```

### Timing Individual Steps

```python
def _execute_pipeline(self, context):
    # Time a step
    start = time.time()
    result = self._process_data(data)
    duration_ms = int((time.time() - start) * 1000)
    
    self.trace_decision(
        decision_point="process_data",
        decision="completed",
        duration_ms=duration_ms
    )
    
    # Or use elapsed time from start
    total_elapsed = self.get_elapsed_time_ms()
    print(f"Total time so far: {total_elapsed}ms")
```

---

## Error Handling

### Orchestration Errors

```python
from app.orchestrators.base import OrchestrationError, DuplicateRequestError

try:
    result = orchestrator.execute(request_id, input_data)
except DuplicateRequestError as e:
    # Request already being processed
    print(f"Duplicate request: {e}")
except OrchestrationError as e:
    # Orchestration failed
    print(f"Orchestration error: {e}")
```

### Failed Requests

```python
# Execution fails and is recorded
try:
    result = orchestrator.execute("req-fail", bad_data)
except OrchestrationError:
    pass

# Check failure status
idem_key = db.query(IdempotencyKey).filter(
    IdempotencyKey.request_id == "req-fail"
).first()

print(idem_key.status)         # FAILED
print(idem_key.error_message)  # Error details
```

---

## Integration with Existing Orchestrators

### Baseline Orchestrator

```python
class BaselineOrchestrator(BaseOrchestrator[Baseline]):
    @property
    def orchestrator_name(self) -> str:
        return "baseline_orchestrator"
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> Baseline:
        document_id = context['input']['document_id']
        user_context = context['input']['user_context']
        
        # Trace: Load document
        self.trace_decision(
            decision_point="load_document",
            decision=f"loaded_document_{document_id}"
        )
        
        document = self._load_document(document_id)
        
        # Bundle: Document evidence
        self.bundle_evidence(
            evidence_type="document_text",
            evidence_data={'text': document.extracted_text},
            source=f"DocumentArtifact:{document_id}"
        )
        
        # Create baseline
        baseline = self._create_baseline(document, user_context)
        
        return baseline
```

---

## Best Practices

### 1. Unique Request IDs

```python
# Good: UUID or timestamp-based
request_id = f"baseline-{uuid.uuid4()}"
request_id = f"timeline-{user_id}-{int(time.time())}"

# Bad: Not unique enough
request_id = "create_baseline"  # Will conflict
```

### 2. Meaningful Decision Points

```python
# Good: Clear, specific
self.trace_decision(
    decision_point="validate_document_format",
    decision="pdf_format_accepted"
)

# Bad: Vague
self.trace_decision(
    decision_point="step1",
    decision="ok"
)
```

### 3. Structured Evidence

```python
# Good: Structured, typed
self.bundle_evidence(
    evidence_type="extracted_stages",
    evidence_data={
        'stages': [...],
        'extraction_method': 'rule_based',
        'confidence': 0.85
    }
)

# Bad: Unstructured
self.bundle_evidence(
    evidence_type="data",
    evidence_data="some stages"
)
```

### 4. Appropriate TTL

```python
# Short-lived operation
result = orchestrator.execute(request_id, data, ttl_hours=1)

# Long-lived resource creation
result = orchestrator.execute(request_id, data, ttl_hours=168)  # 1 week
```

---

## Testing

### Unit Tests

```python
def test_my_orchestrator(db_session):
    orchestrator = MyOrchestrator(db_session)
    
    request_id = f"test-{uuid.uuid4()}"
    input_data = {'test': 'data'}
    
    result = orchestrator.execute(request_id, input_data)
    
    # Verify result
    assert result is not None
    
    # Verify idempotency
    idem_key = db_session.query(IdempotencyKey).filter(
        IdempotencyKey.request_id == request_id
    ).first()
    
    assert idem_key.status == RequestStatus.COMPLETED
    
    # Verify traces
    traces = db_session.query(DecisionTrace).filter(
        DecisionTrace.request_id == request_id
    ).all()
    
    assert len(traces) > 0
```

---

## Database Migration

Add to Alembic migration:

```python
def upgrade():
    # Create idempotency_keys table
    op.create_table(
        'idempotency_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', sa.String(255), nullable=False, unique=True),
        sa.Column('orchestrator_name', sa.String(100), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='request_status'), nullable=False),
        # ... other columns
    )
    
    # Create decision_traces table
    op.create_table('decision_traces', ...)
    
    # Create evidence_bundles table
    op.create_table('evidence_bundles', ...)
```

---

## Summary

✅ **BaseOrchestrator provides:**
- Automatic idempotency checking
- Response caching
- Decision audit trail
- Evidence bundling
- Consistent error handling
- Timing metrics

✅ **Orchestrators should:**
- Extend BaseOrchestrator
- Implement `orchestrator_name` property
- Implement `_execute_pipeline` method
- Trace important decisions
- Bundle relevant evidence

✅ **Benefits:**
- No duplicate operations
- Full traceability
- Explainable decisions
- Consistent patterns
- Easy debugging

**Start using BaseOrchestrator today for robust, traceable orchestrations!**
