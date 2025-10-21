"""
EpiWatch Disease Dictionary and Extraction

Handles disease name detection and matching using fuzzy string matching
and pre-trained models for disease entity recognition.

Author: EpiWatch Team
License: MIT
"""

import json
import logging
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import re
from rapidfuzz import fuzz, process
from pathlib import Path


@dataclass
class DiseaseMatch:
    """Represents a disease match with confidence score"""
    disease: str
    matched_text: str
    confidence: float
    start_pos: int
    end_pos: int
    category: Optional[str] = None


class DiseaseDict:
    """Disease dictionary for entity matching and normalization"""
    
    def __init__(self, dict_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Load disease dictionary
        if dict_path and Path(dict_path).exists():
            self.diseases = self._load_custom_dict(dict_path)
        else:
            self.diseases = self._load_default_dict()
        
        # Create normalized lookup
        self.normalized_diseases = self._create_normalized_lookup()
        
        # Disease categories for better classification
        self.disease_categories = {
            'viral': ['influenza', 'covid-19', 'ebola', 'zika', 'dengue', 'yellow fever', 'hepatitis'],
            'bacterial': ['tuberculosis', 'cholera', 'plague', 'anthrax', 'meningitis'],
            'parasitic': ['malaria', 'leishmaniasis', 'schistosomiasis', 'trypanosomiasis'],
            'respiratory': ['influenza', 'covid-19', 'sars', 'mers', 'tuberculosis'],
            'vector_borne': ['malaria', 'dengue', 'zika', 'chikungunya', 'yellow fever'],
            'hemorrhagic': ['ebola', 'marburg', 'lassa fever', 'crimean-congo hemorrhagic fever']
        }
        
        self.logger.info(f"Loaded {len(self.diseases)} disease terms")
    
    def _load_custom_dict(self, dict_path: str) -> List[str]:
        """Load custom disease dictionary from JSON file"""
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load custom dictionary: {e}")
            return self._load_default_dict()
    
    def _load_default_dict(self) -> List[str]:
        """Load default disease dictionary"""
        # This matches the diseases.json we created earlier
        return [
            "influenza", "flu", "h1n1", "h5n1", "avian flu", "swine flu",
            "covid-19", "coronavirus", "sars-cov-2", "covid", "pandemic",
            "ebola", "hemorrhagic fever", "filovirus", "marburg",
            "malaria", "plasmodium", "falciparum", "vivax",
            "tuberculosis", "tb", "mycobacterium", "pulmonary tb",
            "dengue", "dengue fever", "aedes", "breakbone fever",
            "zika", "zika virus", "microcephaly", "guillain-barre",
            "chikungunya", "chik", "alphavirus",
            "yellow fever", "jungle fever", "urban yellow fever",
            "hepatitis", "hepatitis a", "hepatitis b", "hepatitis c", "hep a", "hep b", "hep c",
            "measles", "rubeola", "mmr", "koplik spots",
            "mumps", "parotitis", "epidemic parotitis",
            "rubella", "german measles", "congenital rubella",
            "polio", "poliomyelitis", "paralysis", "poliovirus",
            "meningitis", "meningococcal", "bacterial meningitis", "viral meningitis",
            "cholera", "vibrio cholerae", "blue death", "asiatic cholera",
            "typhoid", "typhoid fever", "salmonella typhi", "enteric fever",
            "plague", "bubonic plague", "yersinia pestis", "black death",
            "anthrax", "bacillus anthracis", "cutaneous anthrax", "pulmonary anthrax",
            "smallpox", "variola", "pox", "vaccination",
            "monkeypox", "mpox", "orthopoxvirus", "monkey pox",
            "outbreak", "epidemic", "pandemic", "endemic", "cluster"
        ]
    
    def _create_normalized_lookup(self) -> Dict[str, str]:
        """Create normalized disease name lookup"""
        normalized = {}
        
        # Primary disease mappings
        primary_diseases = {
            'influenza': ['flu', 'h1n1', 'h5n1', 'avian flu', 'swine flu', 'influenza'],
            'covid-19': ['covid-19', 'coronavirus', 'sars-cov-2', 'covid', 'corona virus'],
            'ebola': ['ebola', 'hemorrhagic fever', 'filovirus'],
            'malaria': ['malaria', 'plasmodium', 'falciparum', 'vivax'],
            'tuberculosis': ['tuberculosis', 'tb', 'mycobacterium', 'pulmonary tb'],
            'dengue': ['dengue', 'dengue fever', 'breakbone fever'],
            'zika': ['zika', 'zika virus'],
            'chikungunya': ['chikungunya', 'chik', 'alphavirus'],
            'yellow_fever': ['yellow fever', 'jungle fever', 'urban yellow fever'],
            'hepatitis': ['hepatitis', 'hepatitis a', 'hepatitis b', 'hepatitis c', 'hep a', 'hep b', 'hep c'],
            'measles': ['measles', 'rubeola', 'mmr'],
            'mumps': ['mumps', 'parotitis', 'epidemic parotitis'],
            'rubella': ['rubella', 'german measles', 'congenital rubella'],
            'polio': ['polio', 'poliomyelitis', 'paralysis', 'poliovirus'],
            'meningitis': ['meningitis', 'meningococcal', 'bacterial meningitis', 'viral meningitis'],
            'cholera': ['cholera', 'vibrio cholerae', 'blue death', 'asiatic cholera'],
            'typhoid': ['typhoid', 'typhoid fever', 'salmonella typhi', 'enteric fever'],
            'plague': ['plague', 'bubonic plague', 'yersinia pestis', 'black death'],
            'anthrax': ['anthrax', 'bacillus anthracis', 'cutaneous anthrax', 'pulmonary anthrax'],
            'smallpox': ['smallpox', 'variola', 'pox'],
            'monkeypox': ['monkeypox', 'mpox', 'orthopoxvirus', 'monkey pox'],
            'marburg': ['marburg', 'marburg virus', 'green monkey disease']
        }
        
        # Create reverse lookup
        for primary, variants in primary_diseases.items():
            for variant in variants:
                normalized[variant.lower()] = primary
        
        return normalized
    
    def get_disease_category(self, disease: str) -> Optional[str]:
        """Get disease category"""
        disease_lower = disease.lower()
        for category, diseases in self.disease_categories.items():
            if any(d in disease_lower for d in diseases):
                return category
        return None


class DiseaseExtractor:
    """Disease name extraction using fuzzy matching and pattern recognition"""
    
    def __init__(self, disease_dict: Optional[DiseaseDict] = None, confidence_threshold: float = 0.8):
        self.logger = logging.getLogger(__name__)
        self.disease_dict = disease_dict or DiseaseDict()
        self.confidence_threshold = confidence_threshold
        
        # Compile regex patterns for common disease patterns
        self.disease_patterns = [
            re.compile(r'\b(?:outbreak|epidemic|pandemic)\s+of\s+(\w+(?:\s+\w+)?)', re.IGNORECASE),
            re.compile(r'\b(\w+(?:\s+\w+)?)\s+(?:outbreak|epidemic|pandemic)', re.IGNORECASE),
            re.compile(r'\b(?:cases|infections)\s+of\s+(\w+(?:\s+\w+)?)', re.IGNORECASE),
            re.compile(r'\b(\w+(?:\s+\w+)?)\s+(?:cases|infections|disease)', re.IGNORECASE),
            re.compile(r'\b(?:diagnosed|confirmed|suspected)\s+(?:with\s+)?(\w+(?:\s+\w+)?)', re.IGNORECASE),
        ]
    
    def extract_diseases(self, text: str) -> List[DiseaseMatch]:
        """Extract disease mentions from text"""
        if not text:
            return []
        
        matches = []
        text_lower = text.lower()
        
        # 1. Direct fuzzy matching against dictionary
        fuzzy_matches = self._fuzzy_match_diseases(text_lower)
        matches.extend(fuzzy_matches)
        
        # 2. Pattern-based extraction
        pattern_matches = self._pattern_extract_diseases(text)
        matches.extend(pattern_matches)
        
        # 3. Remove duplicates and overlaps
        matches = self._deduplicate_matches(matches)
        
        # 4. Filter by confidence threshold
        matches = [m for m in matches if m.confidence >= self.confidence_threshold]
        
        # 5. Add categories
        for match in matches:
            match.category = self.disease_dict.get_disease_category(match.disease)
        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)
    
    def _fuzzy_match_diseases(self, text: str) -> List[DiseaseMatch]:
        """Use fuzzy matching to find disease names"""
        matches = []
        
        # Split text into chunks for better matching
        words = text.split()
        
        # Check single words and phrases (up to 3 words)
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words) + 1)):
                phrase = ' '.join(words[i:j])
                
                if len(phrase) < 3:  # Skip very short phrases
                    continue
                
                # Find best match in disease dictionary
                best_match = process.extractOne(
                    phrase, 
                    self.disease_dict.diseases,
                    scorer=fuzz.partial_ratio,
                    score_cutoff=70
                )
                
                if best_match:
                    disease_term, confidence = best_match
                    
                    # Normalize confidence to 0-1 scale
                    confidence = confidence / 100.0
                    
                    # Find position in original text
                    start_pos = text.find(phrase)
                    end_pos = start_pos + len(phrase)
                    
                    # Normalize disease name
                    normalized_disease = self.disease_dict.normalized_diseases.get(
                        disease_term.lower(), disease_term
                    )
                    
                    match = DiseaseMatch(
                        disease=normalized_disease,
                        matched_text=phrase,
                        confidence=confidence,
                        start_pos=start_pos,
                        end_pos=end_pos
                    )
                    
                    matches.append(match)
        
        return matches
    
    def _pattern_extract_diseases(self, text: str) -> List[DiseaseMatch]:
        """Extract diseases using regex patterns"""
        matches = []
        
        for pattern in self.disease_patterns:
            for match in pattern.finditer(text):
                disease_candidate = match.group(1).strip()
                
                # Validate against disease dictionary
                best_match = process.extractOne(
                    disease_candidate.lower(),
                    self.disease_dict.diseases,
                    scorer=fuzz.ratio,
                    score_cutoff=60
                )
                
                if best_match:
                    disease_term, confidence = best_match
                    confidence = confidence / 100.0
                    
                    # Boost confidence for pattern matches
                    confidence = min(confidence + 0.1, 1.0)
                    
                    normalized_disease = self.disease_dict.normalized_diseases.get(
                        disease_term.lower(), disease_term
                    )
                    
                    disease_match = DiseaseMatch(
                        disease=normalized_disease,
                        matched_text=disease_candidate,
                        confidence=confidence,
                        start_pos=match.start(1),
                        end_pos=match.end(1)
                    )
                    
                    matches.append(disease_match)
        
        return matches
    
    def _deduplicate_matches(self, matches: List[DiseaseMatch]) -> List[DiseaseMatch]:
        """Remove duplicate and overlapping matches"""
        if not matches:
            return []
        
        # Sort by confidence (highest first)
        matches = sorted(matches, key=lambda x: x.confidence, reverse=True)
        
        deduplicated = []
        used_positions = set()
        
        for match in matches:
            # Check for overlap with existing matches
            overlap = False
            match_positions = set(range(match.start_pos, match.end_pos))
            
            if match_positions & used_positions:
                overlap = True
            
            # Check for duplicate diseases (keep highest confidence)
            duplicate = any(
                existing.disease == match.disease and 
                abs(existing.start_pos - match.start_pos) < 10
                for existing in deduplicated
            )
            
            if not overlap and not duplicate:
                deduplicated.append(match)
                used_positions.update(match_positions)
        
        return deduplicated
    
    def extract_disease_context(self, text: str, disease_matches: List[DiseaseMatch], 
                              context_window: int = 50) -> Dict[str, str]:
        """Extract context around disease mentions"""
        context = {}
        
        for match in disease_matches:
            start = max(0, match.start_pos - context_window)
            end = min(len(text), match.end_pos + context_window)
            
            context_text = text[start:end].strip()
            context[match.disease] = context_text
        
        return context
    
    def get_extraction_stats(self, disease_matches: List[DiseaseMatch]) -> Dict[str, any]:
        """Get statistics about extracted diseases"""
        if not disease_matches:
            return {
                'total_diseases': 0,
                'unique_diseases': 0,
                'avg_confidence': 0.0,
                'categories': {},
                'top_diseases': []
            }
        
        unique_diseases = set(match.disease for match in disease_matches)
        avg_confidence = sum(match.confidence for match in disease_matches) / len(disease_matches)
        
        # Count by category
        categories = {}
        for match in disease_matches:
            if match.category:
                categories[match.category] = categories.get(match.category, 0) + 1
        
        # Top diseases by frequency
        disease_counts = {}
        for match in disease_matches:
            disease_counts[match.disease] = disease_counts.get(match.disease, 0) + 1
        
        top_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_diseases': len(disease_matches),
            'unique_diseases': len(unique_diseases),
            'avg_confidence': round(avg_confidence, 3),
            'categories': categories,
            'top_diseases': top_diseases
        }