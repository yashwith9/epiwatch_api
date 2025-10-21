"""
EpiWatch NLP Dataset Processing Example

This script demonstrates how to use the EpiWatch NLP processor 
with your cleaned and preprocessed dataset.

Author: EpiWatch Team
License: MIT
"""

import sys
import json
from pathlib import Path
from nlp.processor import EpiWatchNLPProcessor


def process_your_dataset():
    """
    Example function showing how to process your dataset
    
    Modify the file paths and column names according to your dataset structure.
    """
    
    print("🔬 EpiWatch NLP Processing Example")
    print("=" * 50)
    
    # ===== CONFIGURATION =====
    # Modify these paths to match your dataset
    INPUT_FILE = "data/your_cleaned_dataset.csv"  # Change this to your dataset path
    OUTPUT_FILE = "results/nlp_results.json"     # Where to save results
    
    # Dataset column configuration
    TEXT_COLUMN = "text"        # Column containing the text to analyze
    ID_COLUMN = "id"           # Column containing document IDs (optional)
    
    # Processing configuration
    DISEASE_THRESHOLD = 0.8    # Confidence threshold for disease extraction
    LOCATION_THRESHOLD = 0.7   # Confidence threshold for location extraction
    BATCH_SIZE = 100          # Number of documents to process at once
    USE_ASYNC = True          # Use async processing for better performance
    
    # ===== PROCESSING =====
    try:
        # Initialize the NLP processor
        print("🚀 Initializing NLP processor...")
        processor = EpiWatchNLPProcessor(
            disease_confidence_threshold=DISEASE_THRESHOLD,
            location_confidence_threshold=LOCATION_THRESHOLD
        )
        
        # Check if input file exists
        input_path = Path(INPUT_FILE)
        if not input_path.exists():
            print(f"❌ Dataset file not found: {INPUT_FILE}")
            print("\n💡 Please update the INPUT_FILE path in this script to point to your dataset.")
            print("   Supported formats: CSV, JSON, JSONL, Excel (.xlsx, .xls)")
            return
        
        print(f"📁 Processing dataset: {INPUT_FILE}")
        
        # Process the dataset
        if USE_ASYNC:
            print("⚡ Using async processing for better performance...")
            results = processor.process_dataset_async(
                dataset=INPUT_FILE,
                text_column=TEXT_COLUMN,
                id_column=ID_COLUMN
            )
        else:
            print("🔄 Processing dataset synchronously...")
            results = processor.process_dataset(
                dataset=INPUT_FILE,
                text_column=TEXT_COLUMN,
                id_column=ID_COLUMN,
                batch_size=BATCH_SIZE
            )
        
        print(f"✅ Processed {len(results)} documents")
        
        # ===== ANALYZE RESULTS =====
        print("\n📊 Analyzing results...")
        stats = processor.analyze_dataset_statistics(results)
        
        print("\n" + "=" * 50)
        print("📈 PROCESSING STATISTICS")
        print("=" * 50)
        
        print(f"📄 Total documents: {stats['total_documents']}")
        print(f"🦠 Documents with diseases: {stats['documents_with_diseases']} ({stats['coverage_percentage']['diseases']}%)")
        print(f"🌍 Documents with locations: {stats['documents_with_locations']} ({stats['coverage_percentage']['locations']}%)")
        print(f"🎯 Documents with both: {stats['documents_with_both']} ({stats['coverage_percentage']['both']}%)")
        
        print(f"\n🎯 CONFIDENCE STATISTICS")
        print(f"Average confidence: {stats['confidence_stats']['average']}")
        print(f"Confidence range: {stats['confidence_stats']['min']} - {stats['confidence_stats']['max']}")
        
        print(f"\n🦠 TOP DISEASES FOUND:")
        for disease, count in stats['top_diseases'][:10]:
            print(f"  • {disease}: {count} mentions")
        
        print(f"\n🌍 TOP COUNTRIES FOUND:")
        for country, count in stats['top_countries'][:10]:
            print(f"  • {country}: {count} mentions")
        
        print(f"\n⏱️ PERFORMANCE METRICS:")
        print(f"Average processing time: {stats['processing_stats']['avg_time_ms']:.2f}ms per document")
        print(f"Total processing time: {stats['processing_stats']['total_time_s']:.2f} seconds")
        
        # ===== SAVE RESULTS =====
        print(f"\n💾 Saving results to: {OUTPUT_FILE}")
        
        # Create output directory if it doesn't exist
        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        success = processor.save_results(results, OUTPUT_FILE, format='json')
        if success:
            print("✅ Results saved successfully!")
        else:
            print("❌ Failed to save results")
            return
        
        # Also save as CSV for easier analysis
        csv_output = OUTPUT_FILE.replace('.json', '.csv')
        processor.save_results(results, csv_output, format='csv')
        print(f"📊 Summary also saved as CSV: {csv_output}")
        
        # ===== SHOW SAMPLE RESULTS =====
        print(f"\n🔍 SAMPLE RESULTS (Top 3 by confidence):")
        print("=" * 50)
        
        # Sort by confidence and show top 3
        top_results = sorted(results, key=lambda x: x.overall_confidence, reverse=True)[:3]
        
        for i, result in enumerate(top_results, 1):
            print(f"\n📄 Sample {i} (ID: {result.article_id}):")
            print(f"   Confidence: {result.overall_confidence:.3f}")
            
            if result.diseases:
                diseases = [f"{d['disease']} ({d['confidence']:.3f})" for d in result.diseases[:3]]
                print(f"   Diseases: {', '.join(diseases)}")
            
            if result.locations:
                locations = [f"{l['location']} ({l['confidence']:.3f})" for l in result.locations[:3]]
                print(f"   Locations: {', '.join(locations)}")
        
        print("\n🎉 Processing completed successfully!")
        print(f"\n📋 Next steps:")
        print(f"   1. Review the results in: {OUTPUT_FILE}")
        print(f"   2. Check the CSV summary: {csv_output}")
        print(f"   3. Use the extracted data for outbreak detection modeling")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()


def analyze_single_text_example():
    """Example of analyzing a single text"""
    
    print("\n" + "=" * 50)
    print("🔍 SINGLE TEXT ANALYSIS EXAMPLE")
    print("=" * 50)
    
    # Sample text (replace with your own)
    sample_text = """
    The World Health Organization reported a new outbreak of Ebola virus disease 
    in the Democratic Republic of Congo on Monday. Health officials in Kinshasa 
    confirmed 23 cases with 15 deaths in the North Kivu province. The outbreak 
    appears to be contained to rural areas near Beni, but authorities are 
    monitoring the situation closely.
    """
    
    try:
        # Initialize processor
        processor = EpiWatchNLPProcessor()
        
        # Process the text
        result = processor.process_text(sample_text, "example_001")
        
        print(f"📝 Sample Text:")
        print(f"   {sample_text.strip()}")
        
        print(f"\n🎯 Overall Confidence: {result.overall_confidence:.3f}")
        
        print(f"\n🦠 Diseases Extracted:")
        for disease in result.diseases:
            print(f"   • {disease['disease']}: {disease['confidence']:.3f}")
            print(f"     Matched text: '{disease['matched_text']}'")
            if disease.get('category'):
                print(f"     Category: {disease['category']}")
        
        print(f"\n🌍 Locations Extracted:")
        for location in result.locations:
            print(f"   • {location['location']}: {location['confidence']:.3f}")
            print(f"     Matched text: '{location['matched_text']}'")
            if location.get('country'):
                print(f"     Country: {location['country']} ({location.get('country_code', 'N/A')})")
            print(f"     Type: {location.get('location_type', 'unknown')}")
        
        print(f"\n📊 Processing Info:")
        print(f"   Processing time: {result.processing_time_ms:.2f}ms")
        print(f"   Text length: {result.metadata.get('text_length', 'N/A')} characters")
        
    except Exception as e:
        print(f"❌ Single text analysis failed: {e}")


def main():
    """Main function"""
    
    print("🔬 EpiWatch NLP Processing Demo")
    print("This script shows how to use the NLP processor with your dataset.")
    
    # Process dataset example
    process_your_dataset()
    
    # Single text analysis example
    analyze_single_text_example()


if __name__ == "__main__":
    main()