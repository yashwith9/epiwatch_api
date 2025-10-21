"""
Process Structured Disease Outbreaks Dataset

This script processes your disease_outbreaks_minimal.csv which already
contains structured outbreak data. We'll aggregate and prepare it for
time series analysis and anomaly detection.

Dataset Structure:
- id_outbreak: Unique outbreak identifier
- Year: Year of outbreak
- Disease: Disease name
- Country: Country name
- iso3: ISO3 country code
- unsd_region: UN region classification
- who_region: WHO region classification
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json


def load_and_explore_dataset():
    """Load and explore the outbreak dataset"""
    
    dataset_path = r"C:\Users\Bruger\Downloads\disease_outbreaks_minimal.csv"
    
    print("📥 Loading Disease Outbreaks Dataset")
    print("=" * 70)
    
    try:
        df = pd.read_csv(dataset_path)
        
        print(f"✅ Loaded {len(df):,} outbreak records")
        print(f"\n📊 Dataset Overview:")
        print(f"   Time period: {df['Year'].min()} - {df['Year'].max()}")
        print(f"   Unique diseases: {df['Disease'].nunique()}")
        print(f"   Countries affected: {df['Country'].nunique()}")
        print(f"   Regions: {df['unsd_region'].nunique()} (UNSD), {df['who_region'].nunique()} (WHO)")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Dataset not found: {dataset_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


def analyze_disease_patterns(df):
    """Analyze disease outbreak patterns"""
    
    print("\n🦠 Disease Analysis")
    print("=" * 70)
    
    # Top diseases by outbreak count
    disease_counts = df['Disease'].value_counts()
    print(f"\n📈 Top 20 Diseases by Outbreak Frequency:")
    for i, (disease, count) in enumerate(disease_counts.head(20).items(), 1):
        print(f"   {i:2}. {disease:30} - {count:4} outbreaks")
    
    # Disease trends over time
    print(f"\n📅 Disease Trends by Year:")
    disease_year = df.groupby(['Year', 'Disease']).size().reset_index(name='count')
    
    # Top diseases per year
    for year in sorted(df['Year'].unique())[-5:]:  # Last 5 years
        year_data = disease_year[disease_year['Year'] == year].nlargest(5, 'count')
        print(f"\n   {year}:")
        for _, row in year_data.iterrows():
            print(f"      {row['Disease']:25} - {row['count']:3} outbreaks")
    
    return disease_counts


def analyze_geographic_patterns(df):
    """Analyze geographic outbreak patterns"""
    
    print("\n🌍 Geographic Analysis")
    print("=" * 70)
    
    # Top countries by outbreak count
    country_counts = df['Country'].value_counts()
    print(f"\n📍 Top 20 Countries by Outbreak Frequency:")
    for i, (country, count) in enumerate(country_counts.head(20).items(), 1):
        print(f"   {i:2}. {country:30} - {count:4} outbreaks")
    
    # Regional distribution
    print(f"\n🗺️  Outbreak Distribution by UN Region:")
    region_counts = df['unsd_region'].value_counts()
    for region, count in region_counts.items():
        pct = (count / len(df)) * 100
        print(f"   {region:20} - {count:4} outbreaks ({pct:5.1f}%)")
    
    # WHO regions
    print(f"\n🏥 Outbreak Distribution by WHO Region:")
    who_counts = df['who_region'].value_counts()
    for region, count in who_counts.items():
        pct = (count / len(df)) * 100
        print(f"   {region:40} - {count:4} outbreaks ({pct:5.1f}%)")
    
    return country_counts


def create_time_series_aggregates(df):
    """Create aggregated time series data for forecasting"""
    
    print("\n📊 Creating Time Series Aggregates")
    print("=" * 70)
    
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # 1. Disease-Country-Year aggregates
    print("\n1️⃣  Disease × Country × Year aggregates")
    disease_country_year = df.groupby(['Disease', 'Country', 'iso3', 'Year']).size().reset_index(name='outbreak_count')
    disease_country_year = disease_country_year.sort_values(['Disease', 'Country', 'Year'])
    
    output_file = results_dir / "disease_country_year_aggregates.csv"
    disease_country_year.to_csv(output_file, index=False)
    print(f"   ✅ Saved: {output_file}")
    print(f"   Records: {len(disease_country_year):,}")
    
    # 2. Disease-Year aggregates (global)
    print("\n2️⃣  Disease × Year aggregates (global)")
    disease_year = df.groupby(['Disease', 'Year']).size().reset_index(name='outbreak_count')
    disease_year = disease_year.sort_values(['Disease', 'Year'])
    
    output_file = results_dir / "disease_year_global_aggregates.csv"
    disease_year.to_csv(output_file, index=False)
    print(f"   ✅ Saved: {output_file}")
    print(f"   Records: {len(disease_year):,}")
    
    # 3. Country-Year aggregates (all diseases)
    print("\n3️⃣  Country × Year aggregates (all diseases)")
    country_year = df.groupby(['Country', 'iso3', 'Year']).agg({
        'id_outbreak': 'count',
        'Disease': lambda x: x.nunique()
    }).reset_index()
    country_year.columns = ['Country', 'iso3', 'Year', 'total_outbreaks', 'unique_diseases']
    country_year = country_year.sort_values(['Country', 'Year'])
    
    output_file = results_dir / "country_year_aggregates.csv"
    country_year.to_csv(output_file, index=False)
    print(f"   ✅ Saved: {output_file}")
    print(f"   Records: {len(country_year):,}")
    
    # 4. Region-Year aggregates
    print("\n4️⃣  Region × Year aggregates")
    region_year = df.groupby(['unsd_region', 'Year']).agg({
        'id_outbreak': 'count',
        'Disease': lambda x: x.nunique(),
        'Country': lambda x: x.nunique()
    }).reset_index()
    region_year.columns = ['region', 'Year', 'total_outbreaks', 'unique_diseases', 'countries_affected']
    region_year = region_year.sort_values(['region', 'Year'])
    
    output_file = results_dir / "region_year_aggregates.csv"
    region_year.to_csv(output_file, index=False)
    print(f"   ✅ Saved: {output_file}")
    print(f"   Records: {len(region_year):,}")
    
    return {
        'disease_country_year': disease_country_year,
        'disease_year': disease_year,
        'country_year': country_year,
        'region_year': region_year
    }


def identify_high_risk_combinations(df):
    """Identify high-risk disease-country combinations"""
    
    print("\n⚠️  High-Risk Analysis")
    print("=" * 70)
    
    # Disease-country combinations with most outbreaks
    disease_country = df.groupby(['Disease', 'Country', 'iso3']).agg({
        'id_outbreak': 'count',
        'Year': ['min', 'max', 'count']
    }).reset_index()
    
    disease_country.columns = ['Disease', 'Country', 'iso3', 'total_outbreaks', 
                               'first_year', 'last_year', 'years_affected']
    
    disease_country = disease_country.sort_values('total_outbreaks', ascending=False)
    
    print(f"\n🔴 Top 20 High-Risk Disease-Country Combinations:")
    for i, row in disease_country.head(20).iterrows():
        print(f"   {row['Disease']:20} × {row['Country']:20} - {row['total_outbreaks']:3} outbreaks "
              f"({row['first_year']}-{row['last_year']})")
    
    # Save to file
    output_file = Path("results/high_risk_combinations.csv")
    disease_country.to_csv(output_file, index=False)
    print(f"\n   ✅ Full list saved: {output_file}")
    
    return disease_country


def create_forecasting_ready_dataset(aggregates):
    """Prepare data specifically for time series forecasting"""
    
    print("\n🔮 Preparing Forecasting-Ready Datasets")
    print("=" * 70)
    
    results_dir = Path("results/forecasting")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # For each major disease, create complete time series
    disease_year = aggregates['disease_year']
    
    # Get top diseases (those with most outbreaks)
    top_diseases = disease_year.groupby('Disease')['outbreak_count'].sum().nlargest(20).index
    
    print(f"\n📈 Creating forecasting datasets for top 20 diseases:")
    
    for disease in top_diseases:
        disease_data = disease_year[disease_year['Disease'] == disease].copy()
        
        # Fill missing years with 0 outbreaks
        all_years = range(disease_data['Year'].min(), disease_data['Year'].max() + 1)
        complete_data = pd.DataFrame({'Year': list(all_years)})
        complete_data = complete_data.merge(disease_data[['Year', 'outbreak_count']], 
                                           on='Year', how='left')
        complete_data['outbreak_count'] = complete_data['outbreak_count'].fillna(0)
        complete_data['Disease'] = disease
        
        # Save individual disease file
        safe_disease_name = disease.replace(' ', '_').replace('/', '_')
        output_file = results_dir / f"{safe_disease_name}_timeseries.csv"
        complete_data.to_csv(output_file, index=False)
        
        print(f"   ✅ {disease:25} - {len(complete_data)} years ({complete_data['Year'].min()}-{complete_data['Year'].max()})")
    
    print(f"\n   📁 Forecasting datasets saved in: {results_dir}")


def create_summary_report(df, disease_counts, country_counts, aggregates):
    """Create comprehensive summary report"""
    
    print("\n📝 Creating Summary Report")
    print("=" * 70)
    
    report_path = Path("results/outbreak_analysis_report.txt")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DISEASE OUTBREAKS ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("DATASET OVERVIEW\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Outbreak Records: {len(df):,}\n")
        f.write(f"Time Period: {df['Year'].min()} - {df['Year'].max()}\n")
        f.write(f"Unique Diseases: {df['Disease'].nunique()}\n")
        f.write(f"Countries Affected: {df['Country'].nunique()}\n")
        f.write(f"UN Regions: {df['unsd_region'].nunique()}\n")
        f.write(f"WHO Regions: {df['who_region'].nunique()}\n\n")
        
        f.write("TOP 30 DISEASES BY OUTBREAK FREQUENCY\n")
        f.write("-" * 80 + "\n")
        for i, (disease, count) in enumerate(disease_counts.head(30).items(), 1):
            pct = (count / len(df)) * 100
            f.write(f"{i:3}. {disease:35} - {count:5} outbreaks ({pct:5.1f}%)\n")
        
        f.write("\nTOP 30 COUNTRIES BY OUTBREAK FREQUENCY\n")
        f.write("-" * 80 + "\n")
        for i, (country, count) in enumerate(country_counts.head(30).items(), 1):
            pct = (count / len(df)) * 100
            f.write(f"{i:3}. {country:35} - {count:5} outbreaks ({pct:5.1f}%)\n")
        
        f.write("\nREGIONAL DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        region_counts = df['unsd_region'].value_counts()
        for region, count in region_counts.items():
            pct = (count / len(df)) * 100
            f.write(f"{region:25} - {count:5} outbreaks ({pct:5.1f}%)\n")
        
        f.write("\nANNUAL OUTBREAK TRENDS\n")
        f.write("-" * 80 + "\n")
        year_counts = df['Year'].value_counts().sort_index()
        for year, count in year_counts.items():
            f.write(f"{year}: {count:5} outbreaks\n")
        
        f.write("\nGENERATED AGGREGATES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Disease × Country × Year: {len(aggregates['disease_country_year']):,} records\n")
        f.write(f"Disease × Year (global): {len(aggregates['disease_year']):,} records\n")
        f.write(f"Country × Year: {len(aggregates['country_year']):,} records\n")
        f.write(f"Region × Year: {len(aggregates['region_year']):,} records\n")
    
    print(f"   ✅ Report saved: {report_path}")


def main():
    """Main execution"""
    
    print("=" * 70)
    print("🔬 EpiWatch - Structured Outbreak Dataset Processor")
    print("=" * 70)
    
    # Load dataset
    df = load_and_explore_dataset()
    if df is None:
        return
    
    # Analyze patterns
    disease_counts = analyze_disease_patterns(df)
    country_counts = analyze_geographic_patterns(df)
    
    # Create aggregates
    aggregates = create_time_series_aggregates(df)
    
    # Identify high-risk combinations
    high_risk = identify_high_risk_combinations(df)
    
    # Prepare forecasting data
    create_forecasting_ready_dataset(aggregates)
    
    # Create summary report
    create_summary_report(df, disease_counts, country_counts, aggregates)
    
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print("=" * 70)
    print(f"\n📁 Output Files (in 'results/' folder):")
    print(f"   • disease_country_year_aggregates.csv - Disease × Country × Year")
    print(f"   • disease_year_global_aggregates.csv - Disease × Year (global)")
    print(f"   • country_year_aggregates.csv - Country × Year summary")
    print(f"   • region_year_aggregates.csv - Regional trends")
    print(f"   • high_risk_combinations.csv - High-risk disease-country pairs")
    print(f"   • outbreak_analysis_report.txt - Comprehensive report")
    print(f"   • forecasting/ - Time series data for Prophet modeling")
    
    print(f"\n🔮 Next Steps:")
    print(f"   1. Review aggregated data in 'results/' folder")
    print(f"   2. Use forecasting datasets for Prophet time series modeling")
    print(f"   3. Implement anomaly detection on time series data")
    print(f"   4. Build alert system for unusual outbreak patterns")
    
    print(f"\n💡 Ready for:")
    print(f"   ✅ Time series forecasting (Prophet, SARIMA)")
    print(f"   ✅ Anomaly detection")
    print(f"   ✅ Dashboard visualization")
    print(f"   ✅ API integration")


if __name__ == "__main__":
    main()