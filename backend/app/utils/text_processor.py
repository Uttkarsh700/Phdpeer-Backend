"""
Text processing utilities for document analysis.

Pure deterministic logic - no ML, no embeddings.
"""

import re
from typing import Dict, List, Tuple, Optional


class TextProcessor:
    """Deterministic text processing utilities."""
    
    # Common English words for language detection
    ENGLISH_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over'
    }
    
    # Spanish common words
    SPANISH_WORDS = {
        'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se',
        'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar', 'tener',
        'le', 'lo', 'todo', 'pero', 'más', 'hacer', 'o', 'poder', 'decir',
        'este', 'ir', 'otro', 'ese', 'la', 'si', 'me', 'ya', 'ver', 'porque',
        'dar', 'cuando', 'él', 'muy', 'sin', 'vez', 'mucho', 'saber', 'qué',
        'sobre', 'mi', 'alguno', 'mismo', 'yo', 'también', 'hasta', 'año',
        'dos', 'querer', 'entre', 'así', 'primero', 'desde', 'grande', 'eso'
    }
    
    # French common words
    FRENCH_WORDS = {
        'le', 'de', 'un', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je',
        'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au',
        'pour', 'pas', 'que', 'vous', 'par', 'sur', 'faire', 'plus', 'dire',
        'me', 'on', 'mon', 'lui', 'nous', 'comme', 'mais', 'pouvoir', 'avec',
        'tout', 'y', 'aller', 'voir', 'en', 'bien', 'où', 'sans', 'tu', 'ou'
    }
    
    # German common words
    GERMAN_WORDS = {
        'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich',
        'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als',
        'auch', 'es', 'an', 'werden', 'aus', 'er', 'hat', 'dass', 'sie', 'nach',
        'wird', 'bei', 'einer', 'um', 'am', 'sind', 'noch', 'wie', 'einem', 'über',
        'einen', 'so', 'zum', 'war', 'haben', 'nur', 'oder', 'aber', 'vor', 'zur'
    }
    
    # Academic heading patterns (case-insensitive)
    HEADING_PATTERNS = [
        # Numbered sections
        r'^(\d+\.)+\s+([A-Z][^\n]{2,80})$',
        # Roman numerals
        r'^([IVX]+)\.\s+([A-Z][^\n]{2,80})$',
        # All caps headings
        r'^([A-Z\s]{3,80})$',
        # Title case with minimal words
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,8})$',
    ]
    
    # Common academic section names
    ACADEMIC_SECTIONS = {
        'abstract', 'introduction', 'background', 'literature review',
        'methodology', 'methods', 'approach', 'materials and methods',
        'results', 'findings', 'discussion', 'analysis',
        'conclusion', 'conclusions', 'future work', 'references',
        'bibliography', 'acknowledgments', 'acknowledgements', 'appendix',
        'supplementary material', 'objectives', 'research questions',
        'hypothesis', 'limitations', 'recommendations'
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize extracted text.
        
        - Remove excessive whitespace
        - Normalize line breaks
        - Remove special characters but keep punctuation
        - Preserve paragraph structure
        
        Args:
            text: Raw extracted text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Normalize line breaks (handle different OS formats)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove control characters except newline and tab
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalize Unicode spaces to regular space
        text = re.sub(r'[\u00A0\u1680\u2000-\u200B\u202F\u205F\u3000]', ' ', text)
        
        # Final cleanup
        text = text.strip()
        
        return text
    
    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.
        
        Uses simple whitespace splitting with basic punctuation handling.
        
        Args:
            text: Input text
            
        Returns:
            Word count
        """
        if not text:
            return 0
        
        # Remove common punctuation that shouldn't split words
        # but keep hyphens in compound words
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Split on whitespace and filter empty strings
        words = [word.strip() for word in text.split() if word.strip()]
        
        return len(words)
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect document language using word frequency heuristics.
        
        Compares text against common word lists for English, Spanish,
        French, and German. Returns ISO 639-1 language code.
        
        Args:
            text: Input text
            
        Returns:
            Language code ('en', 'es', 'fr', 'de', or 'unknown')
        """
        if not text or len(text) < 100:
            return 'unknown'
        
        # Extract words and convert to lowercase
        words = re.findall(r'\b[a-z]+\b', text.lower())
        
        if len(words) < 20:
            return 'unknown'
        
        # Count matches for each language
        english_matches = sum(1 for word in words if word in TextProcessor.ENGLISH_WORDS)
        spanish_matches = sum(1 for word in words if word in TextProcessor.SPANISH_WORDS)
        french_matches = sum(1 for word in words if word in TextProcessor.FRENCH_WORDS)
        german_matches = sum(1 for word in words if word in TextProcessor.GERMAN_WORDS)
        
        # Calculate match percentages
        total_words = len(words)
        scores = {
            'en': (english_matches / total_words) * 100,
            'es': (spanish_matches / total_words) * 100,
            'fr': (french_matches / total_words) * 100,
            'de': (german_matches / total_words) * 100,
        }
        
        # Find language with highest score
        max_lang = max(scores, key=scores.get)
        max_score = scores[max_lang]
        
        # Require at least 5% match to be confident
        if max_score < 5.0:
            return 'unknown'
        
        return max_lang
    
    @staticmethod
    def generate_section_map(text: str) -> Dict:
        """
        Generate a section map of the document.
        
        Uses heading patterns and heuristics to identify document sections:
        - Numbered headings (1. Introduction, 1.1 Background, etc.)
        - All-caps headings (ABSTRACT, INTRODUCTION)
        - Title-case headings
        - Known academic section names
        
        Returns:
        {
            "sections": [
                {
                    "title": "Introduction",
                    "level": 1,
                    "start_char": 0,
                    "end_char": 500,
                    "start_line": 1,
                    "end_line": 15,
                    "word_count": 150,
                    "subsections": []
                },
                ...
            ],
            "total_sections": 5,
            "has_abstract": true,
            "has_references": true,
            "max_depth": 2
        }
        
        Args:
            text: Normalized document text
            
        Returns:
            Section map as dictionary
        """
        if not text:
            return {
                "sections": [],
                "total_sections": 0,
                "has_abstract": False,
                "has_references": False,
                "max_depth": 0
            }
        
        lines = text.split('\n')
        sections = []
        current_char = 0
        
        # Compile heading patterns
        compiled_patterns = [re.compile(pattern, re.MULTILINE) for pattern in TextProcessor.HEADING_PATTERNS]
        
        for line_num, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped or len(line_stripped) < 3:
                current_char += len(line) + 1
                continue
            
            # Check if line matches heading patterns
            is_heading = False
            heading_text = None
            heading_level = 1
            
            # Check numbered sections (1.2.3 Title)
            numbered_match = re.match(r'^(\d+(?:\.\d+)*)\.\s+(.+)$', line_stripped)
            if numbered_match:
                is_heading = True
                numbering = numbered_match.group(1)
                heading_text = numbered_match.group(2).strip()
                heading_level = numbering.count('.') + 1
            
            # Check all-caps headings (minimum 3 chars, max 80 chars)
            elif re.match(r'^[A-Z\s]{3,80}$', line_stripped) and len(line_stripped.split()) <= 10:
                is_heading = True
                heading_text = line_stripped
                heading_level = 1
            
            # Check known academic sections (case-insensitive)
            elif line_stripped.lower() in TextProcessor.ACADEMIC_SECTIONS:
                is_heading = True
                heading_text = line_stripped
                heading_level = 1
            
            # Check Title Case (multiple capitalized words, reasonable length)
            elif (re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line_stripped) and 
                  len(line_stripped) <= 80 and len(line_stripped.split()) <= 10):
                is_heading = True
                heading_text = line_stripped
                heading_level = 2
            
            if is_heading and heading_text:
                section = {
                    "title": heading_text,
                    "level": heading_level,
                    "start_char": current_char,
                    "start_line": line_num + 1,
                    "end_char": None,  # Will be set later
                    "end_line": None,  # Will be set later
                    "word_count": 0,  # Will be calculated
                }
                sections.append(section)
            
            current_char += len(line) + 1  # +1 for newline
        
        # Calculate end positions and word counts
        for i, section in enumerate(sections):
            if i < len(sections) - 1:
                # Section ends where next section starts
                section["end_char"] = sections[i + 1]["start_char"] - 1
                section["end_line"] = sections[i + 1]["start_line"] - 1
            else:
                # Last section ends at document end
                section["end_char"] = len(text)
                section["end_line"] = len(lines)
            
            # Extract section text and count words
            section_text = text[section["start_char"]:section["end_char"]]
            section["word_count"] = TextProcessor.count_words(section_text)
        
        # Build metadata
        section_titles_lower = [s["title"].lower() for s in sections]
        has_abstract = any('abstract' in title for title in section_titles_lower)
        has_references = any(
            title in ['references', 'bibliography', 'works cited']
            for title in section_titles_lower
        )
        max_depth = max([s["level"] for s in sections]) if sections else 0
        
        return {
            "sections": sections,
            "total_sections": len(sections),
            "has_abstract": has_abstract,
            "has_references": has_references,
            "max_depth": max_depth
        }
    
    @staticmethod
    def extract_section_text(text: str, section: Dict) -> str:
        """
        Extract text for a specific section.
        
        Args:
            text: Full document text
            section: Section dictionary from section_map
            
        Returns:
            Section text
        """
        start = section.get("start_char", 0)
        end = section.get("end_char", len(text))
        return text[start:end].strip()
    
    @staticmethod
    def find_section_by_title(section_map: Dict, title: str) -> Optional[Dict]:
        """
        Find a section by title (case-insensitive).
        
        Args:
            section_map: Section map dictionary
            title: Section title to find
            
        Returns:
            Section dictionary or None
        """
        title_lower = title.lower()
        for section in section_map.get("sections", []):
            if title_lower in section["title"].lower():
                return section
        return None
