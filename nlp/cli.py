#!/usr/bin/env python3
"""
EpiWatch NLP Processing CLI

Command-line interface for processing datasets with the EpiWatch NLP pipeline.
Supports various input formats and provides detailed analysis capabilities.

Usage:
    python -m nlp.cli process-dataset --input data.csv --output results.json
    python -m nlp.cli analyze-text --text "Outbreak of flu in New York"
    python -m nlp.cli test-extraction --sample-size 10

Author: EpiWatch Team
License: MIT
"""

import click
import logging
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Optional

from .processor import EpiWatchNLPProcessor
from .extractors import DiseaseExtractor, DiseaseDict
from .location_extractor import LocationExtractor, LocationDict


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """EpiWatch NLP Processing CLI"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input dataset file (CSV, JSON, Excel)')
@click.option('--output', '-o', required=True, help='Output file for results')
@click.option('--text-column', default='text', help='Name of text column in dataset')
@click.option('--id-column', default='id', help='Name of ID column in dataset')
@click.option('--format', default='json', type=click.Choice(['json', 'csv']), 
              help='Output format')
@click.option('--disease-threshold', default=0.8, type=float, 
              help='Disease extraction confidence threshold')
@click.option('--location-threshold', default=0.7, type=float,
              help='Location extraction confidence threshold')
@click.option('--batch-size', default=100, type=int, help='Processing batch size')
@click.option('--async-processing', is_flag=True, help='Use async processing for speed')
def process_dataset(input, output, text_column, id_column, format, 
                   disease_threshold, location_threshold, batch_size, async_processing):
    """Process a dataset with EpiWatch NLP pipeline"""
    
    click.echo(f"🔬 Processing dataset: {input}")
    
    try:
        # Initialize processor
        processor = EpiWatchNLPProcessor(
            disease_confidence_threshold=disease_threshold,
            location_confidence_threshold=location_threshold
        )
        
        # Load and validate dataset
        click.echo("📥 Loading dataset...")
        
        input_path = Path(input)
        if not input_path.exists():
            click.echo(f"❌ Input file not found: {input}")
            sys.exit(1)
        
        # Process dataset
        if async_processing:
            click.echo("⚡ Using async processing...")
            results = processor.process_dataset_async(
                dataset=input,
                text_column=text_column,
                id_column=id_column
            )
        else:
            click.echo("🔄 Processing dataset...")
            results = processor.process_dataset(
                dataset=input,
                text_column=text_column,
                id_column=id_column,
                batch_size=batch_size
            )
        
        # Save results
        click.echo(f"💾 Saving results to: {output}")
        success = processor.save_results(results, output, format)
        
        if success:
            # Show statistics
            stats = processor.analyze_dataset_statistics(results)
            
            click.echo("\n📊 Processing Statistics:")
            click.echo(f"  Total documents: {stats['total_documents']}")
            click.echo(f"  Documents with diseases: {stats['documents_with_diseases']} "
                      f"({stats['coverage_percentage']['diseases']}%)")
            click.echo(f"  Documents with locations: {stats['documents_with_locations']} "
                      f"({stats['coverage_percentage']['locations']}%)")
            click.echo(f"  Documents with both: {stats['documents_with_both']} "
                      f"({stats['coverage_percentage']['both']}%)")
            
            click.echo(f"\n🎯 Confidence Stats:")
            click.echo(f"  Average confidence: {stats['confidence_stats']['average']}")
            click.echo(f"  Min confidence: {stats['confidence_stats']['min']}")
            click.echo(f"  Max confidence: {stats['confidence_stats']['max']}")
            
            click.echo(f"\n🦠 Top Diseases Found:")
            for disease, count in stats['top_diseases'][:5]:
                click.echo(f"  {disease}: {count}")
            
            click.echo(f"\n🌍 Top Countries Found:")
            for country, count in stats['top_countries'][:5]:
                click.echo(f"  {country}: {count}")
            
            click.echo(f"\n⏱️ Performance:")
            click.echo(f"  Average processing time: {stats['processing_stats']['avg_time_ms']:.2f}ms per document")
            click.echo(f"  Total processing time: {stats['processing_stats']['total_time_s']:.2f}s")
            
            click.echo("\n✅ Processing completed successfully!")
        else:
            click.echo("❌ Failed to save results")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Processing failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--text', required=True, help='Text to analyze')
@click.option('--verbose', is_flag=True, help='Show detailed extraction results')
def analyze_text(text, verbose):
    """Analyze a single text for diseases and locations"""
    
    click.echo("🔍 Analyzing text...")
    
    try:
        processor = EpiWatchNLPProcessor()
        result = processor.process_text(text, "sample_text")
        
        click.echo(f"\n📝 Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        click.echo(f"🎯 Overall confidence: {result.overall_confidence:.3f}")
        
        if result.diseases:
            click.echo(f"\n🦠 Diseases found ({len(result.diseases)}):")
            for disease in result.diseases:
                click.echo(f"  • {disease['disease']}: {disease['confidence']:.3f}")
                if verbose:
                    click.echo(f"    Matched text: '{disease['matched_text']}'")
                    if disease.get('category'):
                        click.echo(f"    Category: {disease['category']}")
        else:
            click.echo("\n🦠 No diseases found")
        
        if result.locations:
            click.echo(f"\n🌍 Locations found ({len(result.locations)}):")
            for location in result.locations:
                click.echo(f"  • {location['location']}: {location['confidence']:.3f}")
                if verbose:
                    click.echo(f"    Matched text: '{location['matched_text']}'")
                    if location.get('country'):
                        click.echo(f"    Country: {location['country']} ({location.get('country_code', 'N/A')})")
                    click.echo(f"    Type: {location.get('location_type', 'unknown')}")
        else:
            click.echo("\n🌍 No locations found")
        
        if verbose:
            click.echo(f"\n📊 Metadata:")
            click.echo(f"  Processing time: {result.processing_time_ms:.2f}ms")
            click.echo(f"  Text length: {result.metadata.get('text_length', 'N/A')} characters")
            click.echo(f"  Sentences: {result.metadata.get('sentences_count', 'N/A')}")
            
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--sample-size', default=10, type=int, help='Number of test samples to generate')
@click.option('--save-results', is_flag=True, help='Save test results to file')
def test_extraction(sample_size, save_results):
    """Test extraction capabilities with sample texts"""
    
    # Sample test texts for validation
    test_texts = [
        "WHO reports new outbreak of Ebola virus in Democratic Republic of Congo with 15 confirmed cases.",
        "Health officials in India confirm 200 new cases of dengue fever in Mumbai this week.",
        "COVID-19 pandemic continues to spread across Europe with Germany reporting 5000 new infections.",
        "Malaria outbreak affects rural communities in Kenya, with Nairobi hospitals treating patients.",
        "Tuberculosis cases rise in South Africa as health ministry issues alert for Western Cape province.",
        "Zika virus detected in Brazil causes concern for pregnant women in São Paulo region.",
        "Influenza season begins early in United States with CDC reporting H1N1 strain in California.",
        "Cholera outbreak in Yemen kills dozens as humanitarian crisis worsens in Sanaa.",
        "Measles vaccination campaign launched in Nigeria following outbreak in Lagos state.",
        "Hepatitis A cases surge in Australia with health authorities investigating contaminated food.",
        "Anthrax exposure incident reported at laboratory in Atlanta, Georgia under investigation.",
        "Yellow fever outbreak spreads in Angola with cases confirmed in Luanda province.",
        "Meningitis epidemic declared in Niger as cases rise in Niamey and surrounding regions.",
        "Plague outbreak confirmed in Madagascar with pneumonic cases in Antananarivo.",
        "Lassa fever kills 50 people in Nigeria with cases reported across multiple states."
    ]
    
    # Select sample texts
    import random
    selected_texts = random.sample(test_texts, min(sample_size, len(test_texts)))
    
    click.echo(f"🧪 Testing extraction with {len(selected_texts)} samples...")
    
    try:
        processor = EpiWatchNLPProcessor()
        results = []
        
        for i, text in enumerate(selected_texts, 1):
            click.echo(f"\n📝 Test {i}/{len(selected_texts)}:")
            click.echo(f"Text: {text}")
            
            result = processor.process_text(text, f"test_{i}")
            results.append(result)
            
            click.echo(f"🎯 Confidence: {result.overall_confidence:.3f}")
            
            if result.diseases:
                diseases_str = ", ".join([d['disease'] for d in result.diseases])
                click.echo(f"🦠 Diseases: {diseases_str}")
            
            if result.locations:
                locations_str = ", ".join([l['location'] for l in result.locations])
                click.echo(f"🌍 Locations: {locations_str}")
            
            if not result.diseases and not result.locations:
                click.echo("⚠️ No extractions found")
        
        # Overall statistics
        stats = processor.analyze_dataset_statistics(results)
        
        click.echo(f"\n📊 Test Results Summary:")
        click.echo(f"  Successful extractions: {stats['documents_with_both']}/{len(results)}")
        click.echo(f"  Average confidence: {stats['confidence_stats']['average']:.3f}")
        click.echo(f"  Unique diseases found: {stats['unique_diseases']}")
        click.echo(f"  Unique locations found: {stats['unique_locations']}")
        
        if save_results:
            output_file = "nlp_test_results.json"
            processor.save_results(results, output_file)
            click.echo(f"💾 Test results saved to: {output_file}")
            
    except Exception as e:
        click.echo(f"❌ Testing failed: {e}")
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input dataset file')
@click.option('--text-column', default='text', help='Name of text column')
@click.option('--sample-size', default=5, type=int, help='Number of samples to show')
def preview_dataset(input, text_column, sample_size):
    """Preview dataset and show what will be processed"""
    
    click.echo(f"👀 Previewing dataset: {input}")
    
    try:
        # Load dataset
        processor = EpiWatchNLPProcessor()
        
        input_path = Path(input)
        if not input_path.exists():
            click.echo(f"❌ Input file not found: {input}")
            sys.exit(1)
        
        if input_path.suffix.lower() == '.csv':
            df = pd.read_csv(input)
        elif input_path.suffix.lower() == '.json':
            df = pd.read_json(input)
        elif input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input)
        else:
            click.echo(f"❌ Unsupported file format: {input_path.suffix}")
            sys.exit(1)
        
        click.echo(f"\n📊 Dataset Info:")
        click.echo(f"  Rows: {len(df)}")
        click.echo(f"  Columns: {len(df.columns)}")
        click.echo(f"  Columns: {', '.join(df.columns.tolist())}")
        
        if text_column in df.columns:
            # Text statistics
            text_lengths = df[text_column].astype(str).str.len()
            click.echo(f"\n📝 Text Column Stats ({text_column}):")
            click.echo(f"  Average length: {text_lengths.mean():.0f} characters")
            click.echo(f"  Min length: {text_lengths.min()} characters")
            click.echo(f"  Max length: {text_lengths.max()} characters")
            
            # Show samples
            click.echo(f"\n📖 Sample Texts (first {sample_size}):")
            
            for i, (_, row) in enumerate(df.head(sample_size).iterrows()):
                text = str(row[text_column])
                preview_text = text[:200] + "..." if len(text) > 200 else text
                click.echo(f"\n  Sample {i+1}:")
                click.echo(f"    Text: {preview_text}")
                
                # Show other columns
                other_cols = [col for col in df.columns if col != text_column]
                if other_cols:
                    click.echo(f"    Metadata: {', '.join([f'{col}={row[col]}' for col in other_cols[:3]])}")
        else:
            click.echo(f"❌ Text column '{text_column}' not found in dataset")
            click.echo(f"Available columns: {', '.join(df.columns.tolist())}")
            
    except Exception as e:
        click.echo(f"❌ Preview failed: {e}")
        sys.exit(1)


@cli.command()
def validate_setup():
    """Validate NLP setup and dependencies"""
    
    click.echo("🔧 Validating EpiWatch NLP setup...")
    
    # Test processor initialization
    try:
        processor = EpiWatchNLP    Processor()
        click.echo("✅ NLP Processor initialized successfully")
    except Exception as e:
        click.echo(f"❌ Processor initialization failed: {e}")
        return
    
    # Test spaCy
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        click.echo("✅ spaCy model 'en_core_web_sm' loaded successfully")
    except ImportError:
        click.echo("⚠️ spaCy not installed")
    except IOError:
        click.echo("⚠️ spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    
    # Test disease dictionary
    try:
        disease_dict = DiseaseDict()
        click.echo(f"✅ Disease dictionary loaded: {len(disease_dict.diseases)} terms")
    except Exception as e:
        click.echo(f"❌ Disease dictionary failed: {e}")
    
    # Test location dictionary
    try:
        location_dict = LocationDict()
        click.echo(f"✅ Location dictionary loaded: {len(location_dict.countries)} countries")
    except Exception as e:
        click.echo(f"❌ Location dictionary failed: {e}")
    
    # Test extraction
    try:
        test_text = "Ebola outbreak reported in Congo affecting Kinshasa region"
        result = processor.process_text(test_text)
        
        if result.diseases and result.locations:
            click.echo("✅ Extraction test passed")
        else:
            click.echo("⚠️ Extraction test had limited results")
            
    except Exception as e:
        click.echo(f"❌ Extraction test failed: {e}")
    
    click.echo("\n🎉 Validation complete!")


if __name__ == "__main__":
    cli()