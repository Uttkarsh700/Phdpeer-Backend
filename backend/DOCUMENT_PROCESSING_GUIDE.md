# Document Processing Guide

## Overview

The DocumentService has been enhanced with deterministic text processing capabilities. All processing is rule-based with no ML or embeddings.

## Features

### 1. Text Normalization

Converts raw extracted text into clean, normalized format:

- Removes excessive whitespace
- Normalizes line breaks across OS formats
- Removes excessive blank lines
- Strips control characters
- Preserves paragraph structure

**Example:**

```python
from app.utils.text_processor import TextProcessor

raw_text = "Text  with   spaces\r\nand\n\n\n\nmultiple\nlines"
normalized = TextProcessor.normalize_text(raw_text)
# Result: "Text with spaces\nand\n\nmultiple\nlines"
```

### 2. Word Count

Accurate word counting with proper punctuation handling:

- Splits on whitespace
- Handles hyphens in compound words
- Ignores punctuation
- Counts hyphenated words as single units

**Example:**

```python
text = "This is a well-known fact."
word_count = TextProcessor.count_words(text)
# Result: 5 (well-known counts as one word)
```

### 3. Language Detection

Deterministic language detection using word frequency analysis:

- Supports: English (en), Spanish (es), French (fr), German (de)
- Uses common word lists for each language
- Requires minimum text length (100 chars) and word count (20 words)
- Returns 'unknown' if confidence is too low

**Example:**

```python
text = "This is a sample English text with many common words..."
language = TextProcessor.detect_language(text)
# Result: 'en'
```

**Confidence Thresholds:**
- Requires at least 5% of words to match common word list
- Higher percentages = more confident detection

### 4. Section Map Generation

Automatically identifies document structure using heading heuristics:

**Supported Heading Formats:**
1. **Numbered sections**: `1. Introduction`, `1.1. Background`, `2.3.4. Details`
2. **All-caps headings**: `ABSTRACT`, `INTRODUCTION`, `REFERENCES`
3. **Known academic sections**: `abstract`, `introduction`, `methodology`, etc.
4. **Title Case**: `Literature Review`, `Research Questions`

**Section Map Structure:**

```json
{
    "sections": [
        {
            "title": "Introduction",
            "level": 1,
            "start_char": 0,
            "end_char": 500,
            "start_line": 1,
            "end_line": 15,
            "word_count": 150
        },
        {
            "title": "Background",
            "level": 2,
            "start_char": 500,
            "end_char": 1200,
            "start_line": 16,
            "end_line": 35,
            "word_count": 200
        }
    ],
    "total_sections": 2,
    "has_abstract": true,
    "has_references": true,
    "max_depth": 2
}
```

**Example:**

```python
text = """1. Introduction
This is the introduction section.

2. Methodology
This describes the methods used."""

section_map = TextProcessor.generate_section_map(text)
print(section_map["total_sections"])  # 2
print(section_map["sections"][0]["title"])  # "Introduction"
```

## Database Schema

### DocumentArtifact Model

```python
class DocumentArtifact(Base, BaseModel):
    # ... existing fields ...
    
    # Enhanced text processing fields
    document_text = Column(Text, nullable=True)           # Normalized text
    word_count = Column(Integer, nullable=True)           # Total word count
    detected_language = Column(String(10), nullable=True) # ISO 639-1 code
    section_map_json = Column(JSONB, nullable=True)       # Section structure
    metadata = Column(JSONB, nullable=True)               # Additional metadata
```

## Service Usage

### Upload Document with Processing

```python
from app.services.document_service import DocumentService

service = DocumentService(db)

# Upload PDF or DOCX
document_id = service.upload_document(
    user_id=user.id,
    file_content=file_bytes,
    filename="research_proposal.pdf",
    title="My Research Proposal",
    description="PhD research proposal",
    document_type="proposal"
)

# Document is automatically processed:
# 1. Text extracted
# 2. Text normalized
# 3. Word count computed
# 4. Language detected
# 5. Section map generated
# 6. All stored in database
```

### Retrieve Processed Data

```python
# Get normalized text
text = service.get_extracted_text(document_id)

# Get section map
section_map = service.get_section_map(document_id)

# Get all metadata
metadata = service.get_document_metadata(document_id)
print(f"Word count: {metadata['word_count']}")
print(f"Language: {metadata['detected_language']}")
print(f"Sections: {metadata['section_count']}")
```

### Work with Sections

```python
from app.utils.text_processor import TextProcessor

# Get document and section map
doc = service.get_document(document_id)
section_map = doc.section_map_json

# Find specific section
intro_section = TextProcessor.find_section_by_title(section_map, "introduction")
if intro_section:
    # Extract section text
    intro_text = TextProcessor.extract_section_text(doc.document_text, intro_section)
    print(f"Introduction: {intro_text[:100]}...")

# Iterate through all sections
for section in section_map["sections"]:
    print(f"{section['title']} (Level {section['level']}): {section['word_count']} words")
```

## Advanced Usage

### Custom Section Detection

If default heuristics don't work for your document format, you can:

1. **Pre-process text** before passing to `generate_section_map()`
2. **Post-process section map** to merge/split sections
3. **Add custom patterns** to `TextProcessor.HEADING_PATTERNS`

### Language Detection for Other Languages

To add support for additional languages:

1. Create a new word set in `TextProcessor` (e.g., `ITALIAN_WORDS`)
2. Add to the detection logic in `detect_language()`
3. Update tests

Example:

```python
# In text_processor.py
ITALIAN_WORDS = {
    'il', 'di', 'e', 'che', 'la', 'non', 'per', 'in', 'un', 'a',
    # ... more common Italian words
}

# In detect_language() method
italian_matches = sum(1 for word in words if word in TextProcessor.ITALIAN_WORDS)
scores['it'] = (italian_matches / total_words) * 100
```

### Section Map Queries

Extract insights from section maps:

```python
def has_methodology(section_map):
    """Check if document has methodology section."""
    method_terms = ['method', 'methodology', 'approach']
    for section in section_map['sections']:
        if any(term in section['title'].lower() for term in method_terms):
            return True
    return False

def get_longest_section(section_map):
    """Find the longest section by word count."""
    if not section_map['sections']:
        return None
    return max(section_map['sections'], key=lambda s: s['word_count'])

def calculate_structure_score(section_map):
    """Rate document structure quality."""
    score = 0
    
    # Has abstract
    if section_map['has_abstract']:
        score += 20
    
    # Has references
    if section_map['has_references']:
        score += 20
    
    # Good number of sections (3-10)
    section_count = section_map['total_sections']
    if 3 <= section_count <= 10:
        score += 30
    
    # Has nested structure
    if section_map['max_depth'] >= 2:
        score += 30
    
    return score
```

## Performance Considerations

### Text Size Limits

- **Word count**: Fast for any document size
- **Normalization**: Linear time, handles documents up to 10MB efficiently
- **Language detection**: Samples first 10,000 words for large documents
- **Section map**: Scans entire document, efficient up to 1000 pages

### Memory Usage

All processing is streaming where possible:
- Text normalization processes line-by-line
- Section detection uses single-pass algorithm
- Word counting doesn't store words in memory

### Optimization Tips

```python
# For very large documents, process in chunks
def process_large_document(text, chunk_size=100000):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    # Process each chunk
    total_words = 0
    for chunk in chunks:
        total_words += TextProcessor.count_words(chunk)
    
    return total_words
```

## Testing

### Unit Tests

```bash
# Run text processor tests
pytest backend/tests/test_text_processor.py

# Run document service tests
pytest backend/tests/test_document_service.py
```

### Test Coverage

- ✅ Text normalization (whitespace, line breaks, control chars)
- ✅ Word counting (punctuation, hyphens, edge cases)
- ✅ Language detection (English, Spanish, French, German, unknown)
- ✅ Section mapping (all heading formats, nested sections, edge cases)
- ✅ Utility methods (section extraction, search)
- ✅ Service integration (upload, retrieve, metadata)

## Limitations

### What This System Does NOT Do

- ❌ **No ML models** - All logic is rule-based
- ❌ **No embeddings** - No vector representations
- ❌ **No semantic analysis** - Just structural analysis
- ❌ **No OCR** - Assumes text is extractable from PDF/DOCX
- ❌ **No content quality scoring** - Only structure analysis
- ❌ **No plagiarism detection** - Out of scope

### Known Edge Cases

1. **Unusual heading formats** may not be detected
   - Workaround: Normalize headings before upload

2. **Mixed languages** will detect the dominant language
   - No multi-language support in single document

3. **Very short documents** (<100 chars) return 'unknown' language
   - Intentional to avoid false positives

4. **Tables and figures** may confuse section detection
   - Section map focuses on textual headings only

## Migration from Old Schema

If you have existing `DocumentArtifact` records without the new fields:

```python
def migrate_existing_documents(db: Session):
    """Migrate existing documents to new schema."""
    from app.models.document_artifact import DocumentArtifact
    from app.utils.text_processor import TextProcessor
    
    documents = db.query(DocumentArtifact).filter(
        DocumentArtifact.document_text.is_(None)
    ).all()
    
    for doc in documents:
        # Assume old text was in metadata field
        if doc.metadata and isinstance(doc.metadata, str):
            raw_text = doc.metadata
            
            # Process text
            doc.document_text = TextProcessor.normalize_text(raw_text)
            doc.word_count = TextProcessor.count_words(doc.document_text)
            doc.detected_language = TextProcessor.detect_language(doc.document_text)
            doc.section_map_json = TextProcessor.generate_section_map(doc.document_text)
            
            # Move metadata to JSON field
            doc.metadata = {
                "migrated": True,
                "original_filename": doc.title
            }
    
    db.commit()
```

## Examples

### Example 1: Research Proposal Analysis

```python
# Upload research proposal
doc_id = service.upload_document(
    user_id=user.id,
    file_content=pdf_bytes,
    filename="proposal.pdf"
)

# Analyze structure
metadata = service.get_document_metadata(doc_id)
section_map = service.get_section_map(doc_id)

# Check for required sections
required = ['abstract', 'introduction', 'methodology', 'references']
found_sections = [s['title'].lower() for s in section_map['sections']]

for req in required:
    if any(req in title for title in found_sections):
        print(f"✓ {req.title()} section found")
    else:
        print(f"✗ {req.title()} section missing")
```

### Example 2: Multi-Document Language Analysis

```python
# Analyze language distribution across user's documents
documents = service.get_user_documents(user_id)

language_counts = {}
for doc in documents:
    lang = doc.detected_language or 'unknown'
    language_counts[lang] = language_counts.get(lang, 0) + 1

print("Language distribution:")
for lang, count in language_counts.items():
    print(f"  {lang}: {count} documents")
```

### Example 3: Extract Introduction for Timeline Generation

```python
# Get document
doc = service.get_document(document_id)

# Find introduction section
section_map = doc.section_map_json
intro_section = TextProcessor.find_section_by_title(section_map, "introduction")

if intro_section:
    intro_text = TextProcessor.extract_section_text(doc.document_text, intro_section)
    
    # Use intro text for timeline generation
    from app.services.timeline_intelligence_engine import TimelineIntelligenceEngine
    
    engine = TimelineIntelligenceEngine()
    stages = engine.detect_stages(intro_text)
    print(f"Detected {len(stages)} PhD stages from introduction")
```

## Summary

The enhanced DocumentService provides:

✅ **Normalized text** - Clean, consistent text format
✅ **Word counts** - Accurate word counting
✅ **Language detection** - 4 languages supported (en, es, fr, de)
✅ **Section mapping** - Automatic document structure detection
✅ **Deterministic** - No ML, no embeddings, pure rules
✅ **Fast** - Efficient processing for documents up to 10MB
✅ **Tested** - Comprehensive test coverage

All data is stored in `DocumentArtifact` model for downstream use by orchestrators and intelligence engines.
