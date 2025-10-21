"""
EpiWatch NLP Processing Pipeline

Main NLP processor for analyzing cleaned datasets and extracting
disease and location information with confidence scores.

Author: EpiWatch Team
License: MIT
"""

import logging
import asyncio
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

from .extractors import DiseaseExtractor, DiseaseDict
from .location_extractor import LocationExtractor, LocationDict
from .processors import TextProcessor, ConfidenceCalculator


@dataclass
class NLPResult:
    """NLP processing result for a single article/document"""
    article_id: str
    diseases: List[Dict[str, Any]]
    locations: List[Dict[str, Any]]
    overall_confidence: float
    processing_time_ms: float
    timestamp: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class TextProcessor:
    """Text preprocessing and normalization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for NLP analysis"""
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning (assuming your dataset is already cleaned)
        # Just normalize whitespace and basic cleanup
        text = text.strip()
        text = ' '.join(text.split())  # Normalize whitespace
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        return sentences


class ConfidenceCalculator:
    """Calculate confidence scores for NLP results"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_overall_confidence(self, disease_matches: List, 
                                   location_matches: List,
                                   text_quality: float = 1.0) -> float:
        """Calculate overall confidence score"""
        if not disease_matches and not location_matches:
            return 0.0
        
        disease_conf = 0.0
        if disease_matches:
            disease_conf = sum(match.confidence for match in disease_matches) / len(disease_matches)
        
        location_conf = 0.0
        if location_matches:
            location_conf = sum(match.confidence for match in location_matches) / len(location_matches)
        
        # Weighted combination
        overall = (disease_conf * 0.6 + location_conf * 0.3 + text_quality * 0.1)
        return min(overall, 1.0)


class EpiWatchNLPProcessor:
    """Main NLP processor for EpiWatch system"""
    
    def __init__(self, 
                 disease_dict_path: Optional[str] = None,
                 disease_confidence_threshold: float = 0.8,
                 location_confidence_threshold: float = 0.7):
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.disease_dict = DiseaseDict(disease_dict_path)
        self.location_dict = LocationDict()
        
        self.disease_extractor = DiseaseExtractor(
            disease_dict=self.disease_dict,
            confidence_threshold=disease_confidence_threshold
        )
        
        self.location_extractor = LocationExtractor(
            location_dict=self.location_dict,
            confidence_threshold=location_confidence_threshold
        )
        
        self.text_processor = TextProcessor()
        self.confidence_calculator = ConfidenceCalculator()
        
        self.logger.info("EpiWatch NLP Processor initialized successfully")
    
    def process_text(self, text: str, article_id: str = None, 
                    metadata: Dict[str, Any] = None) -> NLPResult:
        """Process a single text document"""
        start_time = datetime.now()
        
        if not article_id:
            article_id = f"doc_{int(start_time.timestamp())}"
        
        if metadata is None:
            metadata = {}
        
        try:
            # Preprocess text
            cleaned_text = self.text_processor.preprocess_text(text)
            
            if not cleaned_text:
                return self._create_empty_result(article_id, start_time, metadata)
            
            # Extract diseases
            disease_matches = self.disease_extractor.extract_diseases(cleaned_text)
            
            # Extract locations
            location_matches = self.location_extractor.extract_locations(cleaned_text)
            
            # Calculate overall confidence
            overall_confidence = self.confidence_calculator.calculate_overall_confidence(
                disease_matches, location_matches
            )
            
            # Convert matches to dictionaries
            diseases_data = [asdict(match) for match in disease_matches]
            locations_data = [asdict(match) for match in location_matches]
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Create result
            result = NLPResult(
                article_id=article_id,
                diseases=diseases_data,
                locations=locations_data,
                overall_confidence=overall_confidence,
                processing_time_ms=processing_time,
                timestamp=datetime.now().isoformat(),
                metadata={
                    **metadata,
                    'text_length': len(cleaned_text),
                    'disease_count': len(disease_matches),
                    'location_count': len(location_matches),
                    'sentences_count': len(self.text_processor.extract_sentences(cleaned_text))
                }
            )
            
            self.logger.debug(f"Processed article {article_id}: "
                            f"{len(disease_matches)} diseases, {len(location_matches)} locations")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process article {article_id}: {e}")
            return self._create_empty_result(article_id, start_time, metadata, error=str(e))
    
    def process_dataset(self, dataset: Union[pd.DataFrame, List[Dict], str], 
                       text_column: str = 'text',
                       id_column: str = 'id',
                       batch_size: int = 100) -> List[NLPResult]:
        """Process a dataset of documents"""
        
        self.logger.info("Starting dataset processing...")
        
        # Load dataset if it's a file path
        if isinstance(dataset, str):
            dataset = self._load_dataset(dataset)
        
        # Convert to DataFrame if it's a list
        if isinstance(dataset, list):
            dataset = pd.DataFrame(dataset)
        
        if not isinstance(dataset, pd.DataFrame):
            raise ValueError("Dataset must be a pandas DataFrame, list of dicts, or file path")
        
        # Validate required columns
        if text_column not in dataset.columns:
            raise ValueError(f"Text column '{text_column}' not found in dataset")
        
        if id_column not in dataset.columns:
            # Create IDs if not present
            dataset[id_column] = [f"doc_{i}" for i in range(len(dataset))]
        
        results = []
        total_docs = len(dataset)
        
        self.logger.info(f"Processing {total_docs} documents in batches of {batch_size}")
        
        for i in range(0, total_docs, batch_size):
            batch = dataset.iloc[i:i+batch_size]
            batch_results = []
            
            for _, row in batch.iterrows():
                text = row[text_column]
                doc_id = str(row[id_column])
                
                # Prepare metadata from other columns
                metadata = {}
                for col in dataset.columns:
                    if col not in [text_column, id_column]:
                        metadata[col] = row[col]
                
                result = self.process_text(text, doc_id, metadata)
                batch_results.append(result)
            
            results.extend(batch_results)
            
            processed_count = min(i + batch_size, total_docs)
            self.logger.info(f"Processed {processed_count}/{total_docs} documents "
                           f"({processed_count/total_docs*100:.1f}%)")
        
        self.logger.info(f"Dataset processing completed. Processed {len(results)} documents.")
        
        return results
    
    def process_dataset_async(self, dataset: Union[pd.DataFrame, List[Dict], str],
                            text_column: str = 'text',
                            id_column: str = 'id',
                            max_concurrent: int = 50) -> List[NLPResult]:
        """Process dataset asynchronously for better performance"""
        
        async def process_batch_async(texts_and_ids: List[Tuple]):
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_single(text_id_metadata):
                async with semaphore:
                    text, doc_id, metadata = text_id_metadata
                    # Run in thread pool since process_text is CPU-bound
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, self.process_text, text, doc_id, metadata
                    )
            
            tasks = [process_single(item) for item in texts_and_ids]
            return await asyncio.gather(*tasks)
        
        # Prepare data
        if isinstance(dataset, str):
            dataset = self._load_dataset(dataset)
        
        if isinstance(dataset, list):
            dataset = pd.DataFrame(dataset)
        
        if id_column not in dataset.columns:
            dataset[id_column] = [f"doc_{i}" for i in range(len(dataset))]
        
        # Prepare texts and metadata
        texts_and_ids = []
        for _, row in dataset.iterrows():
            text = row[text_column]
            doc_id = str(row[id_column])
            metadata = {col: row[col] for col in dataset.columns 
                       if col not in [text_column, id_column]}
            texts_and_ids.append((text, doc_id, metadata))
        
        # Run async processing
        results = asyncio.run(process_batch_async(texts_and_ids))
        
        return results
    
    def analyze_dataset_statistics(self, results: List[NLPResult]) -> Dict[str, Any]:
        """Analyze statistics from processing results"""
        if not results:
            return {}
        
        # Basic statistics
        total_docs = len(results)
        docs_with_diseases = sum(1 for r in results if r.diseases)
        docs_with_locations = sum(1 for r in results if r.locations)
        docs_with_both = sum(1 for r in results if r.diseases and r.locations)
        
        # Confidence statistics
        confidences = [r.overall_confidence for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Disease statistics
        all_diseases = []
        for result in results:
            for disease in result.diseases:
                all_diseases.append(disease['disease'])
        
        disease_counts = {}
        for disease in all_diseases:
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        top_diseases = sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Location statistics
        all_locations = []
        country_counts = {}
        
        for result in results:
            for location in result.locations:
                all_locations.append(location['location'])
                if location.get('country'):
                    country = location['country']
                    country_counts[country] = country_counts.get(country, 0) + 1
        
        location_counts = {}
        for location in all_locations:
            location_counts[location] = location_counts.get(location, 0) + 1
        
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Processing time statistics
        processing_times = [r.processing_time_ms for r in results]
        avg_processing_time = sum(processing_times) / len(processing_times)
        
        return {
            'total_documents': total_docs,
            'documents_with_diseases': docs_with_diseases,
            'documents_with_locations': docs_with_locations,
            'documents_with_both': docs_with_both,
            'coverage_percentage': {
                'diseases': round(docs_with_diseases / total_docs * 100, 2),
                'locations': round(docs_with_locations / total_docs * 100, 2),
                'both': round(docs_with_both / total_docs * 100, 2)
            },
            'confidence_stats': {
                'average': round(avg_confidence, 3),
                'min': round(min(confidences), 3),
                'max': round(max(confidences), 3)
            },
            'top_diseases': top_diseases,
            'top_locations': top_locations,
            'top_countries': top_countries,
            'unique_diseases': len(disease_counts),
            'unique_locations': len(location_counts),
            'unique_countries': len(country_counts),
            'processing_stats': {
                'avg_time_ms': round(avg_processing_time, 2),
                'total_time_s': round(sum(processing_times) / 1000, 2)
            }
        }
    
    def save_results(self, results: List[NLPResult], output_path: str, 
                    format: str = 'json') -> bool:
        """Save processing results to file"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump([result.to_dict() for result in results], f, 
                             indent=2, ensure_ascii=False)
            
            elif format.lower() == 'csv':
                # Flatten results for CSV
                flattened_data = []
                for result in results:
                    base_data = {
                        'article_id': result.article_id,
                        'overall_confidence': result.overall_confidence,
                        'processing_time_ms': result.processing_time_ms,
                        'timestamp': result.timestamp,
                        'disease_count': len(result.diseases),
                        'location_count': len(result.locations)
                    }
                    
                    # Add metadata
                    base_data.update(result.metadata)
                    
                    # Add top disease and location
                    if result.diseases:
                        top_disease = max(result.diseases, key=lambda x: x['confidence'])
                        base_data.update({
                            'top_disease': top_disease['disease'],
                            'top_disease_confidence': top_disease['confidence']
                        })
                    
                    if result.locations:
                        top_location = max(result.locations, key=lambda x: x['confidence'])
                        base_data.update({
                            'top_location': top_location['location'],
                            'top_country': top_location.get('country', ''),
                            'top_location_confidence': top_location['confidence']
                        })
                    
                    flattened_data.append(base_data)
                
                df = pd.DataFrame(flattened_data)
                df.to_csv(output_path, index=False)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Results saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return False
    
    def _load_dataset(self, file_path: str) -> pd.DataFrame:
        """Load dataset from file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        
        if file_path.suffix.lower() == '.csv':
            return pd.read_csv(file_path)
        elif file_path.suffix.lower() in ['.json', '.jsonl']:
            return pd.read_json(file_path, lines=file_path.suffix.lower() == '.jsonl')
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _create_empty_result(self, article_id: str, start_time: datetime, 
                           metadata: Dict[str, Any], error: str = None) -> NLPResult:
        """Create empty result for failed processing"""
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        if error:
            metadata['error'] = error
        
        return NLPResult(
            article_id=article_id,
            diseases=[],
            locations=[],
            overall_confidence=0.0,
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )