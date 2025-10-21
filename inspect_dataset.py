"""
Quick Dataset Inspector

Checks the structure of your disease_outbreaks_minimal.csv
to determine the best columns to use for NLP processing.
"""

import pandas as pd
from pathlib import Path

dataset_path = r"C:\Users\Bruger\Downloads\disease_outbreaks_minimal.csv"

print("🔍 Quick Dataset Inspector")
print("=" * 60)

try:
    # Check if file exists
    if not Path(dataset_path).exists():
        print(f"❌ File not found: {dataset_path}")
        print("\nPlease verify:")
        print("  1. The file is in the Downloads folder")
        print("  2. The filename is correct: disease_outbreaks_minimal.csv")
        exit(1)
    
    # Load dataset
    print(f"📂 Loading: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"\n✅ Dataset loaded successfully!")
    print(f"\n📊 Quick Statistics:")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns)}")
    
    print(f"\n📋 Columns in Your Dataset:")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_pct = (len(df) - non_null) / len(df) * 100
        
        print(f"   {i}. '{col}'")
        print(f"      Type: {dtype}")
        print(f"      Non-null: {non_null:,} ({100-null_pct:.1f}%)")
        
        # Show sample values for text columns
        if dtype == 'object':
            sample_vals = df[col].dropna().head(2).tolist()
            for j, val in enumerate(sample_vals):
                val_str = str(val)[:80] + "..." if len(str(val)) > 80 else str(val)
                print(f"      Sample {j+1}: {val_str}")
    
    print(f"\n🔍 First 3 Rows Preview:")
    print("=" * 60)
    print(df.head(3).to_string())
    
    # Suggest columns
    print(f"\n💡 Suggested Configuration:")
    
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    # Find best text column
    best_text_col = None
    if text_cols:
        # Prefer columns with 'text', 'content', 'description' in name
        for keyword in ['text', 'content', 'description', 'article', 'body']:
            matching = [col for col in text_cols if keyword.lower() in col.lower()]
            if matching:
                best_text_col = matching[0]
                break
        
        if not best_text_col:
            # Use column with longest average text
            avg_lengths = {col: df[col].astype(str).str.len().mean() for col in text_cols}
            best_text_col = max(avg_lengths, key=avg_lengths.get)
    
    # Find ID column
    best_id_col = None
    for keyword in ['id', 'index', 'key']:
        matching = [col for col in df.columns if keyword.lower() in col.lower()]
        if matching:
            best_id_col = matching[0]
            break
    
    if best_text_col:
        print(f"   Text column: '{best_text_col}'")
    else:
        print(f"   Text column: No obvious text column found")
    
    if best_id_col:
        print(f"   ID column: '{best_id_col}'")
    else:
        print(f"   ID column: Will auto-generate IDs")
    
    print(f"\n✅ Dataset is ready for processing!")
    print(f"\n🚀 Next Step:")
    print(f"   Run: python process_your_dataset.py")
    
except FileNotFoundError:
    print(f"❌ File not found: {dataset_path}")
    print("\nTroubleshooting:")
    print("  1. Check if file is in Downloads folder")
    print("  2. Verify filename spelling")
    print("  3. Make sure you have read permissions")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)