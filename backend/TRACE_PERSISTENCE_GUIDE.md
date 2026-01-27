# DecisionTrace and EvidenceBundle Persistence Guide

## Overview

The BaseOrchestrator automatically captures execution traces and evidence during orchestration. All data is stored as structured JSON for flexibility and auditability.

## Database Models

### DecisionTrace

Stores complete execution trace:

```python
{
    "orchestrator": "baseline_orchestrator",
    "request_id": "req-123",
    "started_at": "2024-01-15T10:30:00",
    "completed_at": "2024-01-15T10:30:05",
    "duration_ms": 5000,
    "steps": [
        {
            "step": 1,
            "action": "validate_input",
            "status": "success",
            "started_at": "2024-01-15T10:30:00",
            "completed_at": "2024-01-15T10:30:00.010",
            "duration_ms": 10,
            "details": {"field_count": 3}
        },
        {
            "step": 2,
            "action": "load_document",
            "status": "success",
            "started_at": "2024-01-15T10:30:00.010",
            "completed_at": "2024-01-15T10:30:01",
            "duration_ms": 990,
            "details": {"document_size": 1024}
        }
    ],
    "result": "success",
    "metadata": {
        "user_id": "user-uuid",
        "total_steps": 2
    }
}
```

### EvidenceBundle

Stores evidence snippets used during computation:

```python
{
    "event_id": "req-123",
    "orchestrator": "baseline_orchestrator",
    "evidence": [
        {
            "type": "document_text",
            "source": "DocumentArtifact:abc-123",
            "data": {
                "excerpt": "Introduction: This research...",
                "length": 5000
            },
            "confidence": 0.95,
            "timestamp": "2024-01-15T10:30:01"
        },
        {
            "type": "analysis_result",
            "source": "TimelineIntelligenceEngine",
            "data": {
                "stages_detected": 4,
                "milestones_extracted": 12
            },
            "confidence": 0.85,
            "timestamp": "2024-01-15T10:30:03",
            "metadata": {
                "method": "pattern_matching",
                "patterns_used": ["phd_stage_keywords"]
            }
        }
    ],
    "metadata": {}
}
```

## Usage in Orchestrators

### Automatic Step Tracing

Use the `_trace_step` context manager for automatic tracing:

```python
class MyOrchestrator(BaseOrchestrator[MyResult]):
    
    def _execute_pipeline(self, context: Dict[str, Any]) -> MyResult:
        # Automatic tracing with context manager
        with self._trace_step("validate_input") as step:
            # Your validation logic
            if not context.get('required_field'):
                raise ValueError("Missing field")
            
            # Add details to the step
            step.details = {
                "field_count": len(context),
                "validated_fields": list(context.keys())
            }
        
        # Another traced step
        with self._trace_step("process_data"):
            result = self._process(context['data'])
        
        return result
```

### Manual Step Logging

For steps that don't need error handling:

```python
def _execute_pipeline(self, context: Dict[str, Any]) -> MyResult:
    # Manual logging
    self.log_step(
        action="cache_check",
        status="hit",
        details={"cached_items": 5}
    )
    
    # Continue with logic
    return result
```

### Adding Evidence

Capture evidence during computation:

```python
def _execute_pipeline(self, context: Dict[str, Any]) -> MyResult:
    # Load document
    with self._trace_step("load_document"):
        doc = self.db.query(DocumentArtifact).get(context['document_id'])
        
        # Capture evidence
        self.add_evidence(
            evidence_type="document_text",
            data={
                "excerpt": doc.text[:500],
                "full_length": len(doc.text),
                "format": doc.format
            },
            source=f"DocumentArtifact:{doc.id}",
            confidence=1.0
        )
    
    # Analyze document
    with self._trace_step("analyze_document"):
        analysis = self.analyzer.analyze(doc.text)
        
        # Capture analysis evidence
        self.add_evidence(
            evidence_type="analysis_result",
            data={
                "metrics": analysis.metrics,
                "classifications": analysis.classes
            },
            source="AnalysisEngine",
            confidence=analysis.confidence,
            metadata={
                "method": "rule_based",
                "version": "1.0"
            }
        )
    
    return result
```

## Step Status Values

- `success` - Step completed successfully
- `failed` - Step failed with error
- `skipped` - Step was skipped (conditional logic)
- `warning` - Step succeeded but with warnings
- `partial` - Step partially completed

## Evidence Types

Recommended evidence type naming:

- `document_text` - Raw document content
- `user_context` - User-provided context
- `analysis_result` - Results from analysis engines
- `validation_result` - Validation outcomes
- `service_response` - External service responses
- `database_query` - Database query results
- `computation_result` - Internal computation results

## Confidence Scores

When adding evidence, provide confidence scores:

- `1.0` - Absolute certainty (e.g., direct user input, database records)
- `0.9-0.99` - Very high confidence (e.g., validated data)
- `0.7-0.89` - High confidence (e.g., deterministic analysis)
- `0.5-0.69` - Moderate confidence (e.g., heuristic-based)
- `< 0.5` - Low confidence (e.g., guesses, fallbacks)

## Querying Traces and Evidence

### Retrieve Execution Trace

```python
from app.models.idempotency import DecisionTrace

trace = db.query(DecisionTrace).filter(
    DecisionTrace.event_id == request_id
).first()

trace_data = trace.trace_json
print(f"Duration: {trace_data['duration_ms']}ms")
print(f"Total steps: {len(trace_data['steps'])}")

for step in trace_data['steps']:
    print(f"Step {step['step']}: {step['action']} - {step['status']}")
```

### Retrieve Evidence

```python
from app.models.idempotency import EvidenceBundle

bundle = db.query(EvidenceBundle).filter(
    EvidenceBundle.event_id == request_id
).first()

evidence_data = bundle.evidence_json

for item in evidence_data['evidence']:
    print(f"Type: {item['type']}")
    print(f"Source: {item['source']}")
    print(f"Confidence: {item.get('confidence', 'N/A')}")
```

### Find All Traces for an Orchestrator

```python
traces = db.query(DecisionTrace).filter(
    DecisionTrace.trace_json['orchestrator'].astext == 'baseline_orchestrator'
).order_by(DecisionTrace.created_at.desc()).all()

for trace in traces:
    event_id = trace.event_id
    duration = trace.trace_json['duration_ms']
    result = trace.trace_json['result']
    print(f"{event_id}: {result} in {duration}ms")
```

### Analyze Failure Patterns

```python
failed_traces = db.query(DecisionTrace).filter(
    DecisionTrace.trace_json['result'].astext == 'failed'
).all()

for trace in failed_traces:
    error = trace.trace_json.get('error', 'Unknown')
    orchestrator = trace.trace_json['orchestrator']
    print(f"{orchestrator} failed: {error}")
    
    # Find which step failed
    for step in trace.trace_json['steps']:
        if step['status'] == 'failed':
            print(f"  Failed at step {step['step']}: {step['action']}")
            print(f"  Error: {step.get('error', 'N/A')}")
```

## Best Practices

### 1. Trace Key Decision Points

```python
with self._trace_step("evaluate_eligibility") as step:
    eligible = self._check_eligibility(baseline)
    step.details = {
        "eligible": eligible,
        "reason": self._get_eligibility_reason(baseline)
    }
    
    if not eligible:
        step.status = "blocked"
```

### 2. Capture Input and Output Evidence

```python
# Capture input
self.add_evidence(
    evidence_type="user_context",
    data=context,
    source="client_request",
    confidence=1.0
)

# Process
result = self._process(context)

# Capture output
self.add_evidence(
    evidence_type="computation_result",
    data=result,
    source="internal_processing",
    confidence=0.9
)
```

### 3. Include Metadata for Complex Evidence

```python
self.add_evidence(
    evidence_type="analysis_result",
    data={"detected_stages": stages},
    source="TimelineIntelligenceEngine",
    confidence=0.85,
    metadata={
        "engine_version": "1.0",
        "patterns_used": ["phd_keywords", "timeline_markers"],
        "processing_mode": "deterministic",
        "text_length": len(text)
    }
)
```

### 4. Handle Failures Gracefully

```python
with self._trace_step("risky_operation") as step:
    try:
        result = self._perform_risky_operation()
        step.details = {"records_processed": len(result)}
    except Exception as e:
        # Exception is automatically captured
        # But you can add extra context
        step.details = {"attempted_records": count}
        raise
```

### 5. Skip Unnecessary Steps

```python
with self._trace_step("conditional_processing") as step:
    if not should_process:
        step.complete(status="skipped", details={"reason": "conditions_not_met"})
        return early_result
    
    # Continue if not skipped
    result = self._process()
```

## Performance Considerations

1. **Evidence Size**: Keep evidence data focused. Don't store entire documents—store excerpts or summaries.

   ```python
   # BAD: Store entire document
   self.add_evidence("document", {"text": doc.full_text})  # Could be MB
   
   # GOOD: Store excerpt
   self.add_evidence("document", {
       "excerpt": doc.text[:500],
       "length": len(doc.text)
   })
   ```

2. **Step Granularity**: Balance detail with performance. Don't trace every line.

   ```python
   # BAD: Too granular
   for item in items:
       with self._trace_step(f"process_item_{item.id}"):
           process(item)
   
   # GOOD: Appropriate granularity
   with self._trace_step("process_items") as step:
       results = [process(item) for item in items]
       step.details = {"items_processed": len(results)}
   ```

3. **JSON Serialization**: Ensure data is JSON-serializable. Use simple types.

   ```python
   # GOOD: JSON-safe types
   self.add_evidence("data", {
       "count": 42,
       "name": "test",
       "values": [1, 2, 3],
       "metadata": {"key": "value"}
   })
   ```

## Testing

Use the provided test utilities:

```python
def test_my_orchestrator_tracing(db_session):
    orchestrator = MyOrchestrator(db_session)
    request_id = f"test-{uuid.uuid4()}"
    
    result = orchestrator.execute(request_id, input_data)
    
    # Verify trace
    trace = db_session.query(DecisionTrace).filter(
        DecisionTrace.event_id == request_id
    ).first()
    
    assert trace is not None
    assert trace.trace_json['result'] == 'success'
    assert len(trace.trace_json['steps']) > 0
    
    # Verify evidence
    bundle = db_session.query(EvidenceBundle).filter(
        EvidenceBundle.event_id == request_id
    ).first()
    
    assert bundle is not None
    assert len(bundle.evidence_json['evidence']) > 0
```

## Migration from Old Tracing

If you have existing orchestrators using the old `trace_decision` and `bundle_evidence` methods, migrate them:

### Before (Old API)

```python
def _execute_pipeline(self, context):
    self.trace_decision(
        decision_point="validate",
        decision="accept",
        input_data=context,
        rationale="All fields present"
    )
    
    self.bundle_evidence(
        evidence_type="document",
        evidence_data={"text": doc.text}
    )
```

### After (New API)

```python
def _execute_pipeline(self, context):
    with self._trace_step("validate") as step:
        # validation logic
        step.details = {"decision": "accept", "reason": "All fields present"}
    
    self.add_evidence(
        evidence_type="document",
        data={"excerpt": doc.text[:500]},
        source=f"DocumentArtifact:{doc.id}"
    )
```

## Summary

- Use `with self._trace_step(action):` for automatic step tracing
- Use `self.log_step(action, status, details)` for manual logging
- Use `self.add_evidence(type, data, ...)` to capture evidence
- All data is stored as structured JSON
- Traces are automatically persisted even on failure
- Query using SQLAlchemy with JSON operators
