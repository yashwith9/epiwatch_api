"""
Process Your Disease Outbreaks Dataset

This script processes your disease_outbreaks_minimal.csv dataset
with the EpiWatch NLP pipeline.

Dataset: C:\\Users\\Bruger\\Downloads\\disease_outbreaks_minimal.csv
Format: CSV
"""

import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path to import nlp module
sys.path.insert(0, str(Path(__file__).parent))

from nlp.processor import EpiWatchNLPProcessor


def inspect_dataset():
    """First, let's inspect the dataset structure"""
    
    dataset_path = r"C:\Users\Bruger\Downloads\disease_outbreaks_minimal.csv"
    
    print("🔍 Inspecting Your Dataset")
    print("=" * 60)
    
    try:
        # Load the dataset
        df = pd.read_csv(dataset_path)
        
        print(f"📊 Dataset Overview:")
        print(f"   File: {dataset_path}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        print(f"\n📋 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📈 Data Types:")
        print(df.dtypes)
        
        print(f"\n🔍 First Few Rows:")
        print(df.head(3).to_string())
        
        print(f"\n📊 Basic Statistics:")
        if df.select_dtypes(include=['object']).columns.any():
            text_cols = df.select_dtypes(include=['object']).columns
            for col in text_cols:
                avg_length = df[col].astype(str).str.len().mean()
                print(f"   {col}: avg length = {avg_length:.0f} characters")
        
        return df.columns.tolist()
        
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {dataset_path}")
        print("   Please verify the file path is correct.")
        return None
    except Exception as e:
        print(f"❌ Error inspecting dataset: {e}")
        import traceback
        traceback.print_exc()
        return None


def process_dataset(text_column=None, id_column=None):
    """Process the dataset with EpiWatch NLP"""
    
    dataset_path = r"C:\Users\Bruger\Downloads\disease_outbreaks_minimal.csv"
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    output_json = output_dir / "disease_outbreaks_nlp_results.json"
    output_csv = output_dir / "disease_outbreaks_nlp_summary.csv"
    
    print("\n" + "=" * 60)
    print("🚀 Processing Dataset with EpiWatch NLP")
    print("=" * 60)
    
    try:
        # If columns not specified, try to detect them
        if not text_column:
            df = pd.read_csv(dataset_path, nrows=1)
            columns = df.columns.tolist()
            
            # Try to find text column
            text_candidates = ['text', 'content', 'description', 'article', 'body', 'message']
            for candidate in text_candidates:
                matching = [col for col in columns if candidate.lower() in col.lower()]
                if matching:
                    text_column = matching[0]
                    print(f"📝 Auto-detected text column: '{text_column}'")
                    break
            
            if not text_column:
                text_column = columns[0] if columns else 'text'
                print(f"⚠️  Using first column as text: '{text_column}'")
            
            # Try to find ID column
            id_candidates = ['id', 'index', 'doc_id', 'article_id', 'key']
            for candidate in id_candidates:
                matching = [col for col in columns if candidate.lower() in col.lower()]
                if matching:
                    id_column = matching[0]
                    print(f"🔑 Auto-detected ID column: '{id_column}'")
                    break
        
        # Initialize NLP processor
        print("\n🔬 Initializing NLP Processor...")
        processor = EpiWatchNLPProcessor(
            disease_confidence_threshold=0.8,
            location_confidence_threshold=0.7
        )
        
        # Process dataset
        print(f"📥 Loading dataset from: {dataset_path}")
        print(f"⚙️  Configuration:")
        print(f"   Text column: {text_column}")
        print(f"   ID column: {id_column if id_column else 'Auto-generated'}")
        print(f"   Disease threshold: 0.8")
        print(f"   Location threshold: 0.7")
        
        print(f"\n⚡ Processing dataset (this may take a few minutes)...")
        
        # Use async processing for better performance
        results = processor.process_dataset_async(
            dataset=dataset_path,
            text_column=text_column,
            id_column=id_column,
            max_concurrent=50
        )
        
        print(f"✅ Processed {len(results):,} documents")
        
        # Analyze results
        print(f"\n📊 Analyzing results...")
        stats = processor.analyze_dataset_statistics(results)
        
        # Display statistics
        print("\n" + "=" * 60)
        print("📈 PROCESSING RESULTS")
        print("=" * 60)
        
        print(f"\n📄 Document Statistics:")
        print(f"   Total documents: {stats['total_documents']:,}")
        print(f"   Documents with diseases: {stats['documents_with_diseases']:,} ({stats['coverage_percentage']['diseases']}%)")
        print(f"   Documents with locations: {stats['documents_with_locations']:,} ({stats['coverage_percentage']['locations']}%)")
        print(f"   Documents with both: {stats['documents_with_both']:,} ({stats['coverage_percentage']['both']}%)")
        
        print(f"\n🎯 Confidence Statistics:")
        print(f"   Average: {stats['confidence_stats']['average']}")
        print(f"   Range: {stats['confidence_stats']['min']} - {stats['confidence_stats']['max']}")
        
        print(f"\n🦠 Top 10 Diseases Found:")
        for i, (disease, count) in enumerate(stats['top_diseases'][:10], 1):
            print(f"   {i:2}. {disease:25} - {count:4} mentions")
        
        print(f"\n🌍 Top 10 Countries Found:")
        for i, (country, count) in enumerate(stats['top_countries'][:10], 1):
            print(f"   {i:2}. {country:25} - {count:4} mentions")
        
        print(f"\n📊 Extraction Statistics:")
        print(f"   Unique diseases: {stats['unique_diseases']}")
        print(f"   Unique locations: {stats['unique_locations']}")
        print(f"   Unique countries: {stats['unique_countries']}")
        
        print(f"\n⏱️  Performance:")
        print(f"   Avg processing time: {stats['processing_stats']['avg_time_ms']:.2f}ms per document")
        print(f"   Total time: {stats['processing_stats']['total_time_s']:.2f} seconds")
        print(f"   Throughput: {stats['total_documents'] / stats['processing_stats']['total_time_s']:.1f} docs/sec")
        
        # Save results
        print(f"\n💾 Saving Results...")
        print(f"   JSON (detailed): {output_json}")
        success_json = processor.save_results(results, str(output_json), format='json')
        
        print(f"   CSV (summary): {output_csv}")
        success_csv = processor.save_results(results, str(output_csv), format='csv')
        
        if success_json and success_csv:
            print("   ✅ Results saved successfully!")
        else:
            print("   ⚠️  Some results may not have been saved")
        
        # Show sample results
        print(f"\n🔍 Sample Results (Top 5 by Confidence):")
        print("=" * 60)
        
        top_results = sorted(results, key=lambda x: x.overall_confidence, reverse=True)[:5]
        
        for i, result in enumerate(top_results, 1):
            print(f"\n📄 Sample {i}:")
            print(f"   ID: {result.article_id}")
            print(f"   Confidence: {result.overall_confidence:.3f}")
            
            if result.diseases:
                diseases_str = ", ".join([f"{d['disease']} ({d['confidence']:.2f})" 
                                         for d in result.diseases[:3]])
                print(f"   Diseases: {diseases_str}")
                if len(result.diseases) > 3:
                    print(f"   ... and {len(result.diseases) - 3} more")
            else:
                print(f"   Diseases: None found")
            
            if result.locations:
                locations_str = ", ".join([f"{l['location']} ({l['confidence']:.2f})" 
                                          for l in result.locations[:3]])
                print(f"   Locations: {locations_str}")
                if len(result.locations) > 3:
                    print(f"   ... and {len(result.locations) - 3} more")
            else:
                print(f"   Locations: None found")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 Processing Complete!")
        print("=" * 60)
        print(f"\n📋 Next Steps:")
        print(f"   1. Review detailed results: {output_json}")
        print(f"   2. Analyze summary data: {output_csv}")
        print(f"   3. Open CSV in Excel/Pandas for further analysis")
        print(f"   4. Use extracted data for outbreak detection modeling")
        
        print(f"\n💡 Tips:")
        print(f"   - High confidence (>0.9) results are most reliable")
        print(f"   - Check documents with low confidence for manual review")
        print(f"   - Use country codes (ISO3) for geographic aggregation")
        print(f"   - Disease names are normalized (e.g., 'flu' → 'influenza')")
        
        return results, stats
        
    except Exception as e:
        print(f"\n❌ Error processing dataset: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def create_analysis_report(stats):
    """Create a detailed analysis report"""
    
    if not stats:
        return
    
    report_path = Path("results/analysis_report.txt")
    
    print(f"\n📝 Creating Analysis Report...")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("EpiWatch NLP Processing Report\n")
            f.write("Disease Outbreaks Dataset Analysis\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("DATASET OVERVIEW\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Documents: {stats['total_documents']:,}\n")
            f.write(f"Documents with Diseases: {stats['documents_with_diseases']:,} ({stats['coverage_percentage']['diseases']}%)\n")
            f.write(f"Documents with Locations: {stats['documents_with_locations']:,} ({stats['coverage_percentage']['locations']}%)\n")
            f.write(f"Documents with Both: {stats['documents_with_both']:,} ({stats['coverage_percentage']['both']}%)\n\n")
            
            f.write("EXTRACTION STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Unique Diseases Identified: {stats['unique_diseases']}\n")
            f.write(f"Unique Locations Identified: {stats['unique_locations']}\n")
            f.write(f"Unique Countries Identified: {stats['unique_countries']}\n\n")
            
            f.write("CONFIDENCE METRICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Average Confidence: {stats['confidence_stats']['average']}\n")
            f.write(f"Minimum Confidence: {stats['confidence_stats']['min']}\n")
            f.write(f"Maximum Confidence: {stats['confidence_stats']['max']}\n\n")
            
            f.write("TOP DISEASES (by frequency)\n")
            f.write("-" * 70 + "\n")
            for i, (disease, count) in enumerate(stats['top_diseases'][:20], 1):
                f.write(f"{i:3}. {disease:30} - {count:5} mentions\n")
            
            f.write("\nTOP COUNTRIES (by frequency)\n")
            f.write("-" * 70 + "\n")
            for i, (country, count) in enumerate(stats['top_countries'][:20], 1):
                f.write(f"{i:3}. {country:30} - {count:5} mentions\n")
            
            f.write("\nPERFORMANCE METRICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Average Processing Time: {stats['processing_stats']['avg_time_ms']:.2f}ms per document\n")
            f.write(f"Total Processing Time: {stats['processing_stats']['total_time_s']:.2f} seconds\n")
            f.write(f"Throughput: {stats['total_documents'] / stats['processing_stats']['total_time_s']:.1f} documents/second\n")
        
        print(f"   ✅ Report saved: {report_path}")
        
    except Exception as e:
        print(f"   ⚠️  Failed to create report: {e}")


def main():
    """Main execution function"""
    
    print("=" * 60)
    print("🔬 EpiWatch NLP - Disease Outbreaks Dataset Processor")
    print("=" * 60)
    
    # Step 1: Inspect the dataset
    print("\n📋 STEP 1: Dataset Inspection")
    columns = inspect_dataset()
    
    if not columns:
        print("\n❌ Failed to inspect dataset. Please check the file path.")
        return
    
    # Pause for user to review
    print("\n" + "=" * 60)
    input("Press Enter to continue with processing... ")
    
    # Step 2: Process the dataset
    print("\n📋 STEP 2: NLP Processing")
    results, stats = process_dataset()
    
    if not results:
        print("\n❌ Processing failed. Please check the error messages above.")
        return
    
    # Step 3: Create detailed report
    print("\n📋 STEP 3: Generate Analysis Report")
    create_analysis_report(stats)
    
    print("\n" + "=" * 60)
    print("✨ All Done! Check the 'results' folder for outputs.")
    print("=" * 60)


if __name__ == "__main__":
    main()