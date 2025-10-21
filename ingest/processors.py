"""
EpiWatch Text Processing and Validation

Handles text cleaning, content validation, and preprocessing
for the data ingestion pipeline.

Author: EpiWatch Team
License: MIT
"""

import re
import html
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import urlparse
import unicodedata


class TextCleaner:
    """Text cleaning and normalization utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Compile regex patterns for efficiency
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Special characters to remove
        self.special_chars_pattern = re.compile(r'[^\w\s\.,;:!?\-\(\)\'\"\/]')
        
        # Common noise patterns in RSS feeds
        self.rss_noise_patterns = [
            re.compile(r'Read more:.*$', re.IGNORECASE),
            re.compile(r'Continue reading.*$', re.IGNORECASE),
            re.compile(r'Source:.*$', re.IGNORECASE),
            re.compile(r'\[.*?\]'),  # Remove bracketed content
            re.compile(r'Advertisement', re.IGNORECASE),
            re.compile(r'Click here.*$', re.IGNORECASE),
        ]
    
    def clean_text(self, text: str) -> str:
        """Main text cleaning method"""
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        text = self.html_tag_pattern.sub(' ', text)
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove URLs and email addresses
        text = self.url_pattern.sub('', text)
        text = self.email_pattern.sub('', text)
        
        # Remove RSS-specific noise
        for pattern in self.rss_noise_patterns:
            text = pattern.sub('', text)
        
        # Remove excessive special characters (keep basic punctuation)
        text = self.special_chars_pattern.sub('', text)
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        # Strip and clean up
        text = text.strip()
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting (can be enhanced with NLTK/spaCy)
        sentence_endings = re.compile(r'[.!?]+')
        sentences = sentence_endings.split(text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text (simple implementation)"""
        # This is a simple implementation - can be enhanced with NLP libraries
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Create bigrams and trigrams
        phrases = []
        for i in range(len(filtered_words) - 1):
            bigram = f"{filtered_words[i]} {filtered_words[i+1]}"
            phrases.append(bigram)
            
            if i < len(filtered_words) - 2:
                trigram = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
                phrases.append(trigram)
        
        # Count phrase frequency and return top phrases
        phrase_counts = {}
        for phrase in phrases:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return [phrase for phrase, count in sorted_phrases[:max_phrases]]


class ContentValidator:
    """Content validation and quality checks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Health-related keywords for relevance checking
        self.health_keywords = {
            'outbreak', 'epidemic', 'pandemic', 'disease', 'virus', 'bacteria', 
            'infection', 'contagious', 'symptoms', 'fever', 'health', 'medical',
            'hospital', 'patient', 'death', 'mortality', 'morbidity', 'surveillance',
            'vaccination', 'vaccine', 'immunization', 'quarantine', 'isolation',
            'who', 'cdc', 'ministry of health', 'public health', 'health department'
        }
        
        # Quality indicators
        self.spam_indicators = {
            'advertisement', 'click here', 'buy now', 'limited time', 'free trial',
            'subscribe now', 'unsubscribe', 'spam', 'scam'
        }
        
        # Minimum quality thresholds
        self.min_title_length = 10
        self.max_title_length = 200
        self.min_content_length = 50
        self.max_content_length = 50000
        self.min_word_count = 10
    
    def is_valid_article(self, article) -> bool:
        """Check if article meets quality standards"""
        try:
            # Check basic structure
            if not article.title or not article.content or not article.url:
                return False
            
            # Check title length
            if not (self.min_title_length <= len(article.title) <= self.max_title_length):
                return False
            
            # Check content length
            if not (self.min_content_length <= len(article.content) <= self.max_content_length):
                return False
            
            # Check word count
            word_count = len(article.content.split())
            if word_count < self.min_word_count:
                return False
            
            # Check for spam indicators
            content_lower = article.content.lower()
            title_lower = article.title.lower()
            
            spam_score = sum(1 for indicator in self.spam_indicators 
                           if indicator in content_lower or indicator in title_lower)
            
            if spam_score > 2:  # Too many spam indicators
                return False
            
            # Check health relevance (at least one health keyword)
            has_health_content = any(keyword in content_lower or keyword in title_lower 
                                   for keyword in self.health_keywords)
            
            if not has_health_content:
                return False
            
            # Check URL validity
            if not self._is_valid_url(article.url):
                return False
            
            # Check publication date (not too old, not in future)
            if not self._is_valid_date(article.published_at):
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error validating article: {e}")
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc) and bool(parsed.scheme)
        except:
            return False
    
    def _is_valid_date(self, published_at: datetime) -> bool:
        """Check if publication date is reasonable"""
        now = datetime.now()
        
        # Not more than 30 days old
        too_old = now - timedelta(days=30)
        
        # Not in the future (with small tolerance for timezone differences)
        future_limit = now + timedelta(hours=12)
        
        return too_old <= published_at <= future_limit
    
    def calculate_quality_score(self, article) -> float:
        """Calculate quality score for article (0.0 to 1.0)"""
        score = 0.0
        
        try:
            # Title quality (0.2 max)
            title_len = len(article.title)
            if 20 <= title_len <= 100:
                score += 0.2
            elif 10 <= title_len <= 150:
                score += 0.1
            
            # Content length quality (0.2 max)
            content_len = len(article.content)
            if 200 <= content_len <= 2000:
                score += 0.2
            elif 100 <= content_len <= 5000:
                score += 0.1
            
            # Health relevance (0.3 max)
            content_lower = article.content.lower()
            title_lower = article.title.lower()
            
            health_matches = sum(1 for keyword in self.health_keywords 
                               if keyword in content_lower or keyword in title_lower)
            
            health_score = min(health_matches / 3.0, 1.0) * 0.3
            score += health_score
            
            # Source credibility (0.2 max) - based on source name
            credible_sources = {
                'who', 'cdc', 'reuters', 'bbc', 'associated press', 'ap news',
                'bloomberg', 'wall street journal', 'financial times', 'guardian',
                'nature', 'science', 'nejm', 'lancet', 'promed'
            }
            
            source_lower = article.source.lower()
            if any(credible in source_lower for credible in credible_sources):
                score += 0.2
            elif 'news' in source_lower or 'times' in source_lower:
                score += 0.1
            
            # Recency bonus (0.1 max)
            age_hours = (datetime.now() - article.published_at).total_seconds() / 3600
            if age_hours <= 24:
                score += 0.1
            elif age_hours <= 72:
                score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            self.logger.warning(f"Error calculating quality score: {e}")
            return 0.0
    
    def get_validation_issues(self, article) -> List[str]:
        """Get list of validation issues for debugging"""
        issues = []
        
        try:
            if not article.title:
                issues.append("Missing title")
            elif len(article.title) < self.min_title_length:
                issues.append("Title too short")
            elif len(article.title) > self.max_title_length:
                issues.append("Title too long")
            
            if not article.content:
                issues.append("Missing content")
            elif len(article.content) < self.min_content_length:
                issues.append("Content too short")
            elif len(article.content) > self.max_content_length:
                issues.append("Content too long")
            
            if not article.url:
                issues.append("Missing URL")
            elif not self._is_valid_url(article.url):
                issues.append("Invalid URL")
            
            if not self._is_valid_date(article.published_at):
                issues.append("Invalid publication date")
            
            # Check health relevance
            content_lower = article.content.lower()
            title_lower = article.title.lower()
            
            has_health_content = any(keyword in content_lower or keyword in title_lower 
                                   for keyword in self.health_keywords)
            
            if not has_health_content:
                issues.append("No health-related content detected")
            
            # Check spam indicators
            spam_score = sum(1 for indicator in self.spam_indicators 
                           if indicator in content_lower or indicator in title_lower)
            
            if spam_score > 2:
                issues.append(f"High spam score: {spam_score}")
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
        
        return issues