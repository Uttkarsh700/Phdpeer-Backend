"""Tests for TextProcessor utilities."""

import pytest
from app.utils.text_processor import TextProcessor


class TestTextNormalization:
    """Tests for text normalization."""
    
    def test_normalize_removes_excessive_whitespace(self):
        text = "This  has   multiple    spaces"
        normalized = TextProcessor.normalize_text(text)
        assert normalized == "This has multiple spaces"
    
    def test_normalize_handles_line_breaks(self):
        text = "Line 1\r\nLine 2\rLine 3\nLine 4"
        normalized = TextProcessor.normalize_text(text)
        lines = normalized.split('\n')
        assert len(lines) == 4
        assert lines[0] == "Line 1"
    
    def test_normalize_removes_excessive_blank_lines(self):
        text = "Paragraph 1\n\n\n\n\nParagraph 2"
        normalized = TextProcessor.normalize_text(text)
        assert normalized == "Paragraph 1\n\nParagraph 2"
    
    def test_normalize_strips_lines(self):
        text = "  Line with spaces  \n\t  Another line  \t"
        normalized = TextProcessor.normalize_text(text)
        assert normalized == "Line with spaces\nAnother line"
    
    def test_normalize_empty_text(self):
        assert TextProcessor.normalize_text("") == ""
        assert TextProcessor.normalize_text(None) == ""
    
    def test_normalize_preserves_paragraph_structure(self):
        text = """First paragraph has some text.

Second paragraph starts here.

Third paragraph is last."""
        normalized = TextProcessor.normalize_text(text)
        paragraphs = [p for p in normalized.split('\n\n') if p.strip()]
        assert len(paragraphs) == 3


class TestWordCount:
    """Tests for word counting."""
    
    def test_count_simple_sentence(self):
        text = "This is a simple sentence."
        assert TextProcessor.count_words(text) == 5
    
    def test_count_with_punctuation(self):
        text = "Hello, world! How are you?"
        assert TextProcessor.count_words(text) == 5
    
    def test_count_with_hyphens(self):
        text = "This is a well-known fact."
        count = TextProcessor.count_words(text)
        assert count == 5  # "well-known" counts as one word
    
    def test_count_empty_text(self):
        assert TextProcessor.count_words("") == 0
        assert TextProcessor.count_words(None) == 0
    
    def test_count_multiple_spaces(self):
        text = "Word1    Word2     Word3"
        assert TextProcessor.count_words(text) == 3
    
    def test_count_with_newlines(self):
        text = "Line 1\nLine 2\nLine 3"
        assert TextProcessor.count_words(text) == 6


class TestLanguageDetection:
    """Tests for language detection."""
    
    def test_detect_english(self):
        text = """
        This is a sample English text. It contains many common English words
        such as the, and, of, to, in, that, have, it, for, not, on, with, he,
        as, you, do, at, this, but, his, by, from. The language detector should
        identify this as English with high confidence.
        """
        lang = TextProcessor.detect_language(text)
        assert lang == 'en'
    
    def test_detect_spanish(self):
        text = """
        Este es un texto de muestra en español. Contiene muchas palabras comunes
        en español como el, la, de, que, y, a, en, un, ser, se, no, haber, por,
        con, su, para, como, estar, tener. El detector de idioma debería identificar
        esto como español con alta confianza.
        """
        lang = TextProcessor.detect_language(text)
        assert lang == 'es'
    
    def test_detect_french(self):
        text = """
        Ceci est un exemple de texte en français. Il contient de nombreux mots
        français courants comme le, de, un, être, et, à, il, avoir, ne, je, son,
        que, se, qui, ce, dans, en, du, elle, au, pour, pas. Le détecteur de langue
        devrait identifier cela comme français avec une grande confiance.
        """
        lang = TextProcessor.detect_language(text)
        assert lang == 'fr'
    
    def test_detect_german(self):
        text = """
        Dies ist ein Beispieltext auf Deutsch. Es enthält viele deutsche Wörter
        wie der, die, und, in, den, von, zu, das, mit, sich, des, auf, für, ist,
        im, dem, nicht, ein, eine, als, auch, es, an, werden, aus. Der Sprachdetektor
        sollte dies mit hoher Zuversicht als Deutsch identifizieren.
        """
        lang = TextProcessor.detect_language(text)
        assert lang == 'de'
    
    def test_detect_too_short(self):
        text = "Short text"
        lang = TextProcessor.detect_language(text)
        assert lang == 'unknown'
    
    def test_detect_empty(self):
        lang = TextProcessor.detect_language("")
        assert lang == 'unknown'
    
    def test_detect_unknown_language(self):
        # Random characters
        text = "xyz abc def ghi jkl mno pqr stu vwx yz abc def ghi jkl mno pqr"
        lang = TextProcessor.detect_language(text)
        assert lang == 'unknown'


class TestSectionMap:
    """Tests for section map generation."""
    
    def test_generate_numbered_sections(self):
        text = """1. Introduction
This is the introduction.

2. Background
This is the background.

3. Methodology
This is the methodology."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 3
        assert len(section_map["sections"]) == 3
        assert section_map["sections"][0]["title"] == "Introduction"
        assert section_map["sections"][0]["level"] == 1
        assert section_map["sections"][1]["title"] == "Background"
        assert section_map["sections"][2]["title"] == "Methodology"
    
    def test_generate_nested_numbered_sections(self):
        text = """1. Introduction
Content here.

1.1. Background
More content.

1.2. Objectives
Even more.

2. Methods
Methods content."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 4
        assert section_map["max_depth"] == 2
        
        # Check levels
        assert section_map["sections"][0]["level"] == 1  # 1.
        assert section_map["sections"][1]["level"] == 2  # 1.1.
        assert section_map["sections"][2]["level"] == 2  # 1.2.
        assert section_map["sections"][3]["level"] == 1  # 2.
    
    def test_generate_all_caps_headings(self):
        text = """ABSTRACT
This is the abstract.

INTRODUCTION
This is the introduction.

REFERENCES
This is the references."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 3
        assert section_map["sections"][0]["title"] == "ABSTRACT"
        assert section_map["sections"][1]["title"] == "INTRODUCTION"
        assert section_map["sections"][2]["title"] == "REFERENCES"
    
    def test_generate_academic_sections(self):
        text = """abstract
This is the abstract section.

introduction
This is the introduction.

methodology
Methods described here.

results
Results presented here.

conclusion
Final thoughts.

references
Citation list."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 6
        assert section_map["has_abstract"] is True
        assert section_map["has_references"] is True
    
    def test_generate_title_case_headings(self):
        text = """Literature Review
Content about literature.

Research Questions
Questions listed here.

Data Analysis
Analysis details."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 3
        assert section_map["sections"][0]["title"] == "Literature Review"
        assert section_map["sections"][1]["title"] == "Research Questions"
        assert section_map["sections"][2]["title"] == "Data Analysis"
    
    def test_generate_with_word_counts(self):
        text = """1. Introduction
This section has exactly five words.

2. Conclusion
Short."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["sections"][0]["word_count"] > 0
        assert section_map["sections"][1]["word_count"] > 0
    
    def test_generate_empty_text(self):
        section_map = TextProcessor.generate_section_map("")
        
        assert section_map["total_sections"] == 0
        assert section_map["sections"] == []
        assert section_map["has_abstract"] is False
        assert section_map["has_references"] is False
        assert section_map["max_depth"] == 0
    
    def test_generate_no_sections(self):
        text = """This is just plain text with no headings or sections.
It goes on and on without any structure.
Just paragraphs of content."""
        
        section_map = TextProcessor.generate_section_map(text)
        
        assert section_map["total_sections"] == 0
        assert section_map["sections"] == []
    
    def test_section_char_positions(self):
        text = """1. First
Content

2. Second
More content"""
        
        section_map = TextProcessor.generate_section_map(text)
        
        # Check that char positions are sequential
        section1 = section_map["sections"][0]
        section2 = section_map["sections"][1]
        
        assert section1["start_char"] < section1["end_char"]
        assert section2["start_char"] < section2["end_char"]
        assert section1["end_char"] <= section2["start_char"]
    
    def test_section_line_positions(self):
        text = """1. First
Content

2. Second
More content"""
        
        section_map = TextProcessor.generate_section_map(text)
        
        section1 = section_map["sections"][0]
        section2 = section_map["sections"][1]
        
        assert section1["start_line"] == 1
        assert section2["start_line"] > section1["start_line"]


class TestUtilityMethods:
    """Tests for utility methods."""
    
    def test_extract_section_text(self):
        text = """1. Introduction
This is intro.

2. Conclusion
This is conclusion."""
        
        section_map = TextProcessor.generate_section_map(text)
        section = section_map["sections"][0]
        
        section_text = TextProcessor.extract_section_text(text, section)
        
        assert "Introduction" in section_text
        assert "This is intro" in section_text
        assert "Conclusion" not in section_text
    
    def test_find_section_by_title(self):
        text = """1. Introduction
Content

2. Methodology
More content

3. Results
Results here"""
        
        section_map = TextProcessor.generate_section_map(text)
        
        # Exact match
        section = TextProcessor.find_section_by_title(section_map, "Methodology")
        assert section is not None
        assert section["title"] == "Methodology"
        
        # Case-insensitive
        section = TextProcessor.find_section_by_title(section_map, "results")
        assert section is not None
        assert "Results" in section["title"]
        
        # Partial match
        section = TextProcessor.find_section_by_title(section_map, "Method")
        assert section is not None
        
        # Not found
        section = TextProcessor.find_section_by_title(section_map, "Discussion")
        assert section is None
    
    def test_find_section_empty_map(self):
        section_map = {"sections": []}
        section = TextProcessor.find_section_by_title(section_map, "Introduction")
        assert section is None
