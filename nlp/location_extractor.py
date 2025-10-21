"""
EpiWatch Location Extraction and Geocoding

Handles location extraction from text using spaCy NER and geographic
normalization using pycountry and fuzzy matching.

Author: EpiWatch Team
License: MIT
"""

import logging
import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
import pycountry
from rapidfuzz import fuzz, process


@dataclass
class LocationMatch:
    """Represents a location match with geographic information"""
    location: str
    matched_text: str
    confidence: float
    start_pos: int
    end_pos: int
    country: Optional[str] = None
    country_code: Optional[str] = None  # ISO3 country code
    location_type: Optional[str] = None  # country, city, region, etc.
    coordinates: Optional[Tuple[float, float]] = None  # (lat, lon)


class LocationDict:
    """Geographic location dictionary and normalization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load country data
        self.countries = self._load_countries()
        self.country_lookup = self._create_country_lookup()
        
        # Load major cities and regions
        self.major_cities = self._load_major_cities()
        self.regions = self._load_regions()
        
        # Create combined location lookup
        self.all_locations = {**self.country_lookup, **self.major_cities, **self.regions}
        
        self.logger.info(f"Loaded geographic data: {len(self.countries)} countries, "
                        f"{len(self.major_cities)} cities, {len(self.regions)} regions")
    
    def _load_countries(self) -> Dict[str, Dict]:
        """Load country data from pycountry"""
        countries = {}
        
        for country in pycountry.countries:
            country_data = {
                'name': country.name,
                'alpha_2': country.alpha_2,
                'alpha_3': country.alpha_3,
                'official_name': getattr(country, 'official_name', country.name),
                'common_name': getattr(country, 'common_name', country.name)
            }
            countries[country.alpha_3] = country_data
        
        return countries
    
    def _create_country_lookup(self) -> Dict[str, str]:
        """Create normalized country name lookup"""
        lookup = {}
        
        for alpha_3, country_data in self.countries.items():
            # Add various name forms
            names_to_add = [
                country_data['name'],
                country_data['official_name'],
                country_data['common_name'],
                country_data['alpha_2'],
                country_data['alpha_3']
            ]
            
            # Add common variations
            country_variations = self._get_country_variations(country_data['name'])
            names_to_add.extend(country_variations)
            
            for name in names_to_add:
                if name and len(name) > 1:
                    lookup[name.lower()] = alpha_3
        
        return lookup
    
    def _get_country_variations(self, country_name: str) -> List[str]:
        """Get common variations and abbreviations for countries"""
        variations = []
        
        # Common country name mappings
        common_variations = {
            'United States': ['USA', 'US', 'America', 'United States of America'],
            'United Kingdom': ['UK', 'Britain', 'Great Britain', 'England'],
            'Russia': ['Russian Federation'],
            'China': ['Peoples Republic of China', 'PRC'],
            'South Korea': ['Korea South', 'Republic of Korea'],
            'North Korea': ['Korea North', 'Democratic Peoples Republic of Korea'],
            'Iran': ['Islamic Republic of Iran'],
            'Syria': ['Syrian Arab Republic'],
            'Venezuela': ['Bolivarian Republic of Venezuela'],
            'Bolivia': ['Plurinational State of Bolivia'],
            'Tanzania': ['United Republic of Tanzania'],
            'Democratic Republic of the Congo': ['DRC', 'Congo DRC', 'Zaire'],
            'Republic of the Congo': ['Congo', 'Congo Republic'],
            'Ivory Coast': ['Cote dIvoire'],
            'Cape Verde': ['Cabo Verde']
        }
        
        for standard_name, vars in common_variations.items():
            if country_name == standard_name:
                variations.extend(vars)
        
        # Remove "the" prefix
        if country_name.startswith('The '):
            variations.append(country_name[4:])
        
        return variations
    
    def _load_major_cities(self) -> Dict[str, str]:
        """Load major world cities with country mappings"""
        # This is a sample - in production, you'd load from a comprehensive database
        cities = {
            # Major global cities with known disease outbreak history
            'beijing': 'CHN', 'shanghai': 'CHN', 'wuhan': 'CHN', 'guangzhou': 'CHN',
            'tokyo': 'JPN', 'osaka': 'JPN',
            'delhi': 'IND', 'mumbai': 'IND', 'kolkata': 'IND', 'chennai': 'IND',
            'bangkok': 'THA', 'ho chi minh city': 'VNM', 'hanoi': 'VNM',
            'jakarta': 'IDN', 'manila': 'PHL',
            'singapore': 'SGP', 'kuala lumpur': 'MYS',
            'seoul': 'KOR', 'busan': 'KOR',
            'london': 'GBR', 'manchester': 'GBR', 'birmingham': 'GBR',
            'paris': 'FRA', 'marseille': 'FRA', 'lyon': 'FRA',
            'berlin': 'DEU', 'hamburg': 'DEU', 'munich': 'DEU',
            'rome': 'ITA', 'milan': 'ITA', 'naples': 'ITA',
            'madrid': 'ESP', 'barcelona': 'ESP', 'seville': 'ESP',
            'moscow': 'RUS', 'st petersburg': 'RUS',
            'istanbul': 'TUR', 'ankara': 'TUR',
            'cairo': 'EGY', 'alexandria': 'EGY',
            'lagos': 'NGA', 'abuja': 'NGA', 'kano': 'NGA',
            'kinshasa': 'COD', 'lubumbashi': 'COD',
            'johannesburg': 'ZAF', 'cape town': 'ZAF', 'durban': 'ZAF',
            'nairobi': 'KEN', 'mombasa': 'KEN',
            'addis ababa': 'ETH',
            'dakar': 'SEN', 'bamako': 'MLI', 'ouagadougou': 'BFA',
            'accra': 'GHA', 'abidjan': 'CIV',
            'new york': 'USA', 'los angeles': 'USA', 'chicago': 'USA', 
            'houston': 'USA', 'philadelphia': 'USA', 'phoenix': 'USA',
            'san antonio': 'USA', 'san diego': 'USA', 'dallas': 'USA',
            'san jose': 'USA', 'austin': 'USA', 'jacksonville': 'USA',
            'toronto': 'CAN', 'montreal': 'CAN', 'vancouver': 'CAN',
            'mexico city': 'MEX', 'guadalajara': 'MEX', 'monterrey': 'MEX',
            'sao paulo': 'BRA', 'rio de janeiro': 'BRA', 'brasilia': 'BRA',
            'salvador': 'BRA', 'fortaleza': 'BRA',
            'buenos aires': 'ARG', 'cordoba': 'ARG', 'rosario': 'ARG',
            'lima': 'PER', 'arequipa': 'PER',
            'bogota': 'COL', 'medellin': 'COL', 'cali': 'COL',
            'caracas': 'VEN', 'maracaibo': 'VEN',
            'santiago': 'CHL', 'valparaiso': 'CHL',
            'sydney': 'AUS', 'melbourne': 'AUS', 'brisbane': 'AUS',
            'perth': 'AUS', 'adelaide': 'AUS'
        }
        
        return cities
    
    def _load_regions(self) -> Dict[str, str]:
        """Load regions, provinces, and states"""
        regions = {
            # US States
            'california': 'USA', 'texas': 'USA', 'florida': 'USA', 'new york': 'USA',
            'pennsylvania': 'USA', 'illinois': 'USA', 'ohio': 'USA', 'georgia': 'USA',
            
            # Chinese Provinces
            'hubei': 'CHN', 'guangdong': 'CHN', 'shandong': 'CHN', 'henan': 'CHN',
            'sichuan': 'CHN', 'jiangsu': 'CHN', 'hebei': 'CHN', 'hunan': 'CHN',
            
            # Indian States
            'maharashtra': 'IND', 'uttar pradesh': 'IND', 'bihar': 'IND', 
            'west bengal': 'IND', 'madhya pradesh': 'IND', 'tamil nadu': 'IND',
            
            # African Regions
            'west africa': None, 'east africa': None, 'central africa': None,
            'southern africa': None, 'north africa': None,
            'sahel': None, 'horn of africa': None,
            
            # Other notable regions
            'middle east': None, 'southeast asia': None, 'central asia': None,
            'eastern europe': None, 'western europe': None, 'balkans': None
        }
        
        return regions


class LocationExtractor:
    """Location extraction using NER and geographic matching"""
    
    def __init__(self, location_dict: Optional[LocationDict] = None, 
                 confidence_threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.location_dict = location_dict or LocationDict()
        self.confidence_threshold = confidence_threshold
        
        # Initialize spaCy if available
        self.nlp = None
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.info("spaCy model loaded successfully")
            except IOError:
                self.logger.warning("spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
        except ImportError:
            self.logger.warning("spaCy not available. Using pattern-based extraction only.")
        
        # Regex patterns for location extraction
        self.location_patterns = [
            re.compile(r'\bin\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\.|$)', re.MULTILINE),
            re.compile(r'\bfrom\s+([A-Z][a-zA-Z\s]+?)(?:\s*,|\s*\.|$)', re.MULTILINE),
            re.compile(r'\b([A-Z][a-zA-Z\s]+?)\s+(?:reports|reported|confirms|confirmed)', re.IGNORECASE),
            re.compile(r'\b(?:outbreak|epidemic|cases)\s+in\s+([A-Z][a-zA-Z\s]+)', re.IGNORECASE),
            re.compile(r'\b([A-Z][a-zA-Z\s]+?)\s+(?:health|ministry|government|officials)', re.IGNORECASE),
        ]
    
    def extract_locations(self, text: str) -> List[LocationMatch]:
        """Extract location mentions from text"""
        if not text:
            return []
        
        matches = []
        
        # 1. spaCy NER extraction (if available)
        if self.nlp:
            spacy_matches = self._extract_with_spacy(text)
            matches.extend(spacy_matches)
        
        # 2. Pattern-based extraction
        pattern_matches = self._extract_with_patterns(text)
        matches.extend(pattern_matches)
        
        # 3. Dictionary-based fuzzy matching
        fuzzy_matches = self._extract_with_fuzzy_matching(text)
        matches.extend(fuzzy_matches)
        
        # 4. Remove duplicates and overlaps
        matches = self._deduplicate_location_matches(matches)
        
        # 5. Filter by confidence threshold
        matches = [m for m in matches if m.confidence >= self.confidence_threshold]
        
        # 6. Enrich with geographic data
        matches = self._enrich_with_geo_data(matches)
        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)
    
    def _extract_with_spacy(self, text: str) -> List[LocationMatch]:
        """Extract locations using spaCy NER"""
        matches = []
        
        try:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                if ent.label_ in ['GPE', 'LOC']:  # Geopolitical entities and locations
                    location_text = ent.text.strip()
                    
                    # Skip very short or obviously non-geographic entities
                    if len(location_text) < 2 or location_text.lower() in ['who', 'cdc', 'the']:
                        continue
                    
                    # Check against location dictionary
                    match_info = self._match_location_in_dict(location_text)
                    
                    if match_info:
                        location_name, country_code, confidence = match_info
                        
                        # Boost confidence for NER matches
                        confidence = min(confidence + 0.1, 1.0)
                        
                        match = LocationMatch(
                            location=location_name,
                            matched_text=location_text,
                            confidence=confidence,
                            start_pos=ent.start_char,
                            end_pos=ent.end_char,
                            country_code=country_code,
                            location_type=self._determine_location_type(location_name, country_code)
                        )
                        
                        matches.append(match)
        
        except Exception as e:
            self.logger.warning(f"spaCy extraction failed: {e}")
        
        return matches
    
    def _extract_with_patterns(self, text: str) -> List[LocationMatch]:
        """Extract locations using regex patterns"""
        matches = []
        
        for pattern in self.location_patterns:
            for match in pattern.finditer(text):
                location_candidate = match.group(1).strip()
                
                # Clean up the candidate
                location_candidate = re.sub(r'\s+', ' ', location_candidate)
                location_candidate = location_candidate.strip('.,;:')
                
                if len(location_candidate) < 2:
                    continue
                
                # Check against location dictionary
                match_info = self._match_location_in_dict(location_candidate)
                
                if match_info:
                    location_name, country_code, confidence = match_info
                    
                    location_match = LocationMatch(
                        location=location_name,
                        matched_text=location_candidate,
                        confidence=confidence,
                        start_pos=match.start(1),
                        end_pos=match.end(1),
                        country_code=country_code,
                        location_type=self._determine_location_type(location_name, country_code)
                    )
                    
                    matches.append(location_match)
        
        return matches
    
    def _extract_with_fuzzy_matching(self, text: str) -> List[LocationMatch]:
        """Extract locations using fuzzy matching against dictionary"""
        matches = []
        
        # Split text into potential location phrases
        words = text.split()
        
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words) + 1)):  # Up to 3-word phrases
                phrase = ' '.join(words[i:j])
                
                # Skip very short phrases or common words
                if len(phrase) < 3 or phrase.lower() in ['the', 'and', 'for', 'with']:
                    continue
                
                # Check against location dictionary
                match_info = self._match_location_in_dict(phrase)
                
                if match_info and match_info[2] >= 0.8:  # High confidence fuzzy matches only
                    location_name, country_code, confidence = match_info
                    
                    start_pos = text.lower().find(phrase.lower())
                    end_pos = start_pos + len(phrase)
                    
                    if start_pos >= 0:  # Found in text
                        match = LocationMatch(
                            location=location_name,
                            matched_text=phrase,
                            confidence=confidence,
                            start_pos=start_pos,
                            end_pos=end_pos,
                            country_code=country_code,
                            location_type=self._determine_location_type(location_name, country_code)
                        )
                        
                        matches.append(match)
        
        return matches
    
    def _match_location_in_dict(self, location_text: str) -> Optional[Tuple[str, str, float]]:
        """Match location text against dictionary"""
        location_lower = location_text.lower().strip()
        
        # 1. Exact match
        if location_lower in self.location_dict.all_locations:
            country_code = self.location_dict.all_locations[location_lower]
            return location_text, country_code, 1.0
        
        # 2. Fuzzy match
        best_match = process.extractOne(
            location_lower,
            self.location_dict.all_locations.keys(),
            scorer=fuzz.ratio,
            score_cutoff=75
        )
        
        if best_match:
            matched_location, confidence = best_match
            country_code = self.location_dict.all_locations[matched_location]
            
            # Get proper case for location name
            if country_code and country_code in self.location_dict.countries:
                location_name = self.location_dict.countries[country_code]['name']
            else:
                location_name = matched_location.title()
            
            return location_name, country_code, confidence / 100.0
        
        return None
    
    def _determine_location_type(self, location: str, country_code: Optional[str]) -> str:
        """Determine the type of location (country, city, region)"""
        if not country_code:
            return 'region'
        
        # Check if it's a country
        if country_code in self.location_dict.countries:
            country_name = self.location_dict.countries[country_code]['name']
            if location.lower() == country_name.lower():
                return 'country'
        
        # Check if it's in major cities
        location_lower = location.lower()
        if location_lower in self.location_dict.major_cities:
            return 'city'
        
        # Check if it's a region
        if location_lower in self.location_dict.regions:
            return 'region'
        
        return 'city'  # Default assumption
    
    def _deduplicate_location_matches(self, matches: List[LocationMatch]) -> List[LocationMatch]:
        """Remove duplicate and overlapping location matches"""
        if not matches:
            return []
        
        # Sort by confidence
        matches = sorted(matches, key=lambda x: x.confidence, reverse=True)
        
        deduplicated = []
        used_positions = set()
        seen_locations = set()
        
        for match in matches:
            # Check for position overlap
            match_positions = set(range(match.start_pos, match.end_pos))
            
            if match_positions & used_positions:
                continue  # Skip overlapping matches
            
            # Check for duplicate locations (same country/location)
            location_key = f"{match.location}_{match.country_code}"
            if location_key in seen_locations:
                continue
            
            deduplicated.append(match)
            used_positions.update(match_positions)
            seen_locations.add(location_key)
        
        return deduplicated
    
    def _enrich_with_geo_data(self, matches: List[LocationMatch]) -> List[LocationMatch]:
        """Enrich location matches with additional geographic data"""
        for match in matches:
            if match.country_code and match.country_code in self.location_dict.countries:
                country_data = self.location_dict.countries[match.country_code]
                match.country = country_data['name']
                
                # Add coordinates for countries (simplified - in production use proper geocoding)
                country_coordinates = self._get_country_coordinates(match.country_code)
                if country_coordinates:
                    match.coordinates = country_coordinates
        
        return matches
    
    def _get_country_coordinates(self, country_code: str) -> Optional[Tuple[float, float]]:
        """Get approximate country coordinates (center point)"""
        # This is a simplified implementation - in production, use a proper geocoding service
        country_coords = {
            'USA': (39.8283, -98.5795), 'CHN': (35.8617, 104.1954),
            'IND': (20.5937, 78.9629), 'BRA': (-14.2350, -51.9253),
            'RUS': (61.5240, 105.3188), 'JPN': (36.2048, 138.2529),
            'DEU': (51.1657, 10.4515), 'GBR': (55.3781, -3.4360),
            'FRA': (46.6034, 1.8883), 'ITA': (41.8719, 12.5674),
            'ESP': (40.4637, -3.7492), 'CAN': (56.1304, -106.3468),
            'AUS': (-25.2744, 133.7751), 'ZAF': (-30.5595, 22.9375),
            'KEN': (-0.0236, 37.9062), 'NGA': (9.0820, 8.6753),
            'EGY': (26.0975, 30.0444), 'TUR': (38.9637, 35.2433),
            'IRN': (32.4279, 53.6880), 'THA': (15.8700, 100.9925),
            'VNM': (14.0583, 108.2772), 'IDN': (-0.7893, 113.9213),
            'PHL': (12.8797, 121.7740), 'MYS': (4.2105, 101.9758),
            'SGP': (1.3521, 103.8198), 'KOR': (35.9078, 127.7669),
        }
        
        return country_coords.get(country_code)
    
    def get_extraction_stats(self, location_matches: List[LocationMatch]) -> Dict[str, any]:
        """Get statistics about extracted locations"""
        if not location_matches:
            return {
                'total_locations': 0,
                'unique_locations': 0,
                'countries': 0,
                'cities': 0,
                'regions': 0,
                'avg_confidence': 0.0,
                'top_countries': []
            }
        
        unique_locations = set(match.location for match in location_matches)
        avg_confidence = sum(match.confidence for match in location_matches) / len(location_matches)
        
        # Count by type
        type_counts = {'country': 0, 'city': 0, 'region': 0}
        for match in location_matches:
            if match.location_type in type_counts:
                type_counts[match.location_type] += 1
        
        # Top countries
        country_counts = {}
        for match in location_matches:
            if match.country:
                country_counts[match.country] = country_counts.get(match.country, 0) + 1
        
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_locations': len(location_matches),
            'unique_locations': len(unique_locations),
            'countries': type_counts['country'],
            'cities': type_counts['city'],
            'regions': type_counts['region'],
            'avg_confidence': round(avg_confidence, 3),
            'top_countries': top_countries
        }