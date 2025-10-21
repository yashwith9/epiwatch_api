"""
EpiWatch - Anomaly Detection System
====================================

This module implements outbreak anomaly detection using:
1. Prophet for time series forecasting
2. Statistical thresholds for anomaly detection
3. Severity scoring based on deviation from forecast
4. Alert generation for unusual outbreak patterns

Usage:
    python -m models.anomaly_detector --disease "COVID-19" --window 30
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not installed. Install with: pip install prophet")


class OutbreakAnomalyDetector:
    """
    Detect anomalies in disease outbreak time series using Prophet forecasting
    """
    
    def __init__(
        self,
        sensitivity: str = 'medium',
        seasonality_mode: str = 'multiplicative'
    ):
        """
        Initialize anomaly detector
        
        Args:
            sensitivity: 'low', 'medium', or 'high' - controls anomaly threshold
            seasonality_mode: 'additive' or 'multiplicative'
        """
        self.sensitivity = sensitivity
        self.seasonality_mode = seasonality_mode
        
        # Set thresholds based on sensitivity
        self.thresholds = {
            'low': {'z_score': 3.0, 'percentile': 95},
            'medium': {'z_score': 2.5, 'percentile': 90},
            'high': {'z_score': 2.0, 'percentile': 85}
        }
        
        self.threshold_config = self.thresholds[sensitivity]
    
    def prepare_time_series(
        self, 
        df: pd.DataFrame,
        date_col: str = 'Year',
        value_col: str = 'outbreak_count',
        freq: str = 'Y'
    ) -> pd.DataFrame:
        """
        Prepare time series data for Prophet
        
        Args:
            df: Input dataframe
            date_col: Column containing dates
            value_col: Column containing values to forecast
            freq: Frequency ('Y' for yearly, 'M' for monthly, 'D' for daily)
        
        Returns:
            DataFrame with 'ds' and 'y' columns for Prophet
        """
        df_copy = df.copy()
        
        # Convert to datetime
        if freq == 'Y':
            df_copy['ds'] = pd.to_datetime(df_copy[date_col].astype(str) + '-01-01')
        elif freq == 'M':
            df_copy['ds'] = pd.to_datetime(df_copy[date_col])
        else:
            df_copy['ds'] = pd.to_datetime(df_copy[date_col])
        
        df_copy['y'] = df_copy[value_col]
        
        return df_copy[['ds', 'y']].sort_values('ds')
    
    def fit_forecast(
        self,
        df: pd.DataFrame,
        periods: int = 3,
        freq: str = 'Y'
    ) -> Tuple[Prophet, pd.DataFrame]:
        """
        Fit Prophet model and generate forecast
        
        Args:
            df: DataFrame with 'ds' and 'y' columns
            periods: Number of periods to forecast
            freq: Frequency for forecasting
        
        Returns:
            Fitted Prophet model and forecast DataFrame
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet is required. Install with: pip install prophet")
        
        # Initialize Prophet
        model = Prophet(
            seasonality_mode=self.seasonality_mode,
            yearly_seasonality=True if len(df) >= 2 else False,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )
        
        # Fit model
        model.fit(df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq=freq)
        
        # Generate forecast
        forecast = model.predict(future)
        
        return model, forecast
    
    def detect_anomalies(
        self,
        actual_df: pd.DataFrame,
        forecast_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Detect anomalies by comparing actual vs forecast
        
        Args:
            actual_df: DataFrame with actual values (ds, y)
            forecast_df: Prophet forecast DataFrame
        
        Returns:
            DataFrame with anomaly information
        """
        # Merge actual and forecast
        merged = actual_df.merge(
            forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            on='ds',
            how='left'
        )
        
        # Calculate residuals
        merged['residual'] = merged['y'] - merged['yhat']
        merged['residual_pct'] = (merged['residual'] / (merged['yhat'] + 1)) * 100
        
        # Calculate z-score of residuals
        residual_mean = merged['residual'].mean()
        residual_std = merged['residual'].std()
        merged['z_score'] = (merged['residual'] - residual_mean) / (residual_std + 1e-6)
        
        # Detect anomalies
        threshold = self.threshold_config['z_score']
        
        # Anomaly if:
        # 1. Above upper confidence interval
        # 2. Z-score exceeds threshold
        # 3. Significant increase
        merged['is_anomaly'] = (
            (merged['y'] > merged['yhat_upper']) |
            (merged['z_score'].abs() > threshold)
        )
        
        # Calculate severity (0-100)
        merged['severity'] = self._calculate_severity(merged)
        
        # Classify anomaly type
        merged['anomaly_type'] = merged.apply(self._classify_anomaly, axis=1)
        
        return merged
    
    def _calculate_severity(self, df: pd.DataFrame) -> pd.Series:
        """Calculate anomaly severity score (0-100)"""
        
        severity = pd.Series(0, index=df.index)
        
        # Factor 1: Z-score magnitude (0-40 points)
        z_normalized = np.clip(df['z_score'].abs() / 5.0, 0, 1)
        severity += z_normalized * 40
        
        # Factor 2: Percentage increase (0-30 points)
        pct_normalized = np.clip(df['residual_pct'] / 100.0, 0, 1)
        severity += pct_normalized * 30
        
        # Factor 3: Absolute outbreak count (0-30 points)
        if df['y'].max() > 0:
            count_normalized = df['y'] / df['y'].max()
            severity += count_normalized * 30
        
        # Only apply severity to anomalies
        severity = severity.where(df['is_anomaly'], 0)
        
        return np.clip(severity, 0, 100)
    
    def _classify_anomaly(self, row) -> str:
        """Classify type of anomaly"""
        
        if not row['is_anomaly']:
            return 'normal'
        
        if row['residual'] > 0:
            if row['severity'] >= 70:
                return 'severe_outbreak'
            elif row['severity'] >= 50:
                return 'moderate_outbreak'
            else:
                return 'mild_outbreak'
        else:
            return 'unexpected_decrease'
    
    def generate_alerts(
        self,
        anomaly_df: pd.DataFrame,
        disease: str,
        location: str = 'Global',
        min_severity: float = 50.0
    ) -> List[Dict]:
        """
        Generate alert messages for anomalies
        
        Args:
            anomaly_df: DataFrame with anomaly detection results
            disease: Disease name
            location: Location name
            min_severity: Minimum severity to generate alert
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Filter to anomalies above severity threshold
        significant = anomaly_df[
            (anomaly_df['is_anomaly']) &
            (anomaly_df['severity'] >= min_severity)
        ].copy()
        
        for _, row in significant.iterrows():
            alert = {
                'timestamp': datetime.now().isoformat(),
                'disease': disease,
                'location': location,
                'date': row['ds'].strftime('%Y-%m-%d'),
                'actual_count': int(row['y']),
                'expected_count': round(row['yhat'], 1),
                'deviation': round(row['residual'], 1),
                'deviation_pct': round(row['residual_pct'], 1),
                'severity': round(row['severity'], 1),
                'severity_level': self._get_severity_level(row['severity']),
                'anomaly_type': row['anomaly_type'],
                'z_score': round(row['z_score'], 2),
                'message': self._generate_alert_message(row, disease, location)
            }
            alerts.append(alert)
        
        return alerts
    
    def _get_severity_level(self, severity: float) -> str:
        """Convert severity score to level"""
        if severity >= 80:
            return 'critical'
        elif severity >= 60:
            return 'high'
        elif severity >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _generate_alert_message(
        self,
        row,
        disease: str,
        location: str
    ) -> str:
        """Generate human-readable alert message"""
        
        severity_level = self._get_severity_level(row['severity'])
        
        if row['anomaly_type'] == 'severe_outbreak':
            return (
                f"⚠️ SEVERE OUTBREAK DETECTED: {disease} cases in {location} "
                f"have reached {int(row['y'])}, which is {abs(row['residual_pct']):.0f}% "
                f"above expected levels. Immediate attention required."
            )
        elif row['anomaly_type'] == 'moderate_outbreak':
            return (
                f"⚠️ MODERATE OUTBREAK: {disease} in {location} shows {int(row['y'])} cases, "
                f"{abs(row['residual_pct']):.0f}% higher than forecast. Monitor closely."
            )
        elif row['anomaly_type'] == 'mild_outbreak':
            return (
                f"ℹ️ Elevated levels: {disease} in {location} at {int(row['y'])} cases, "
                f"{abs(row['residual_pct']):.0f}% above expected."
            )
        else:
            return (
                f"Unexpected decrease in {disease} cases in {location}: "
                f"{int(row['y'])} vs expected {row['yhat']:.0f}"
            )


def analyze_disease_outbreaks(
    disease: str,
    data_path: str = "results/disease_year_global_aggregates.csv",
    forecast_periods: int = 3,
    sensitivity: str = 'medium',
    output_dir: str = "results/anomaly_detection"
) -> Dict:
    """
    Complete anomaly detection pipeline for a specific disease
    
    Args:
        disease: Disease name to analyze
        data_path: Path to aggregated data
        forecast_periods: Number of years to forecast
        sensitivity: Anomaly detection sensitivity
        output_dir: Directory to save results
    
    Returns:
        Dictionary with analysis results
    """
    print(f"\n🔍 Analyzing {disease}")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv(data_path)
    disease_data = df[df['Disease'] == disease].copy()
    
    if len(disease_data) == 0:
        print(f"❌ No data found for {disease}")
        return None
    
    print(f"📊 Loaded {len(disease_data)} years of data ({disease_data['Year'].min()}-{disease_data['Year'].max()})")
    
    # Initialize detector
    detector = OutbreakAnomalyDetector(sensitivity=sensitivity)
    
    # Prepare time series
    ts_data = detector.prepare_time_series(disease_data)
    
    if len(ts_data) < 2:
        print(f"⚠️  Insufficient data for {disease} (need at least 2 data points)")
        return None
    
    # Fit and forecast
    print(f"🔮 Fitting Prophet model and forecasting {forecast_periods} periods...")
    model, forecast = detector.fit_forecast(ts_data, periods=forecast_periods)
    
    # Detect anomalies
    print(f"🎯 Detecting anomalies...")
    anomalies = detector.detect_anomalies(ts_data, forecast)
    
    # Count anomalies
    num_anomalies = anomalies['is_anomaly'].sum()
    print(f"⚠️  Found {num_anomalies} anomalies")
    
    if num_anomalies > 0:
        print(f"\n   Anomaly breakdown:")
        print(anomalies[anomalies['is_anomaly']][['ds', 'y', 'yhat', 'severity', 'anomaly_type']].to_string(index=False))
    
    # Generate alerts
    alerts = detector.generate_alerts(anomalies, disease=disease, min_severity=40)
    
    if alerts:
        print(f"\n🚨 Generated {len(alerts)} alerts:")
        for alert in alerts:
            print(f"\n   [{alert['severity_level'].upper()}] {alert['date']}")
            print(f"   {alert['message']}")
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save anomaly detection results
    safe_name = disease.replace(' ', '_').replace('/', '_')
    anomalies_file = output_path / f"{safe_name}_anomalies.csv"
    anomalies.to_csv(anomalies_file, index=False)
    print(f"\n💾 Saved anomalies: {anomalies_file}")
    
    # Save forecast
    forecast_file = output_path / f"{safe_name}_forecast.csv"
    forecast.to_csv(forecast_file, index=False)
    print(f"💾 Saved forecast: {forecast_file}")
    
    # Save alerts
    if alerts:
        import json
        alerts_file = output_path / f"{safe_name}_alerts.json"
        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        print(f"💾 Saved alerts: {alerts_file}")
    
    return {
        'disease': disease,
        'data_points': len(ts_data),
        'anomalies': num_anomalies,
        'alerts': len(alerts),
        'forecast': forecast,
        'anomaly_results': anomalies,
        'alert_list': alerts
    }


def batch_analyze_top_diseases(
    top_n: int = 10,
    data_path: str = "results/disease_year_global_aggregates.csv",
    sensitivity: str = 'medium'
):
    """
    Analyze top N diseases by outbreak count
    
    Args:
        top_n: Number of top diseases to analyze
        data_path: Path to aggregated data
        sensitivity: Anomaly detection sensitivity
    """
    print("=" * 70)
    print(f"🔬 EpiWatch - Batch Anomaly Detection (Top {top_n} Diseases)")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv(data_path)
    
    # Get top diseases
    top_diseases = df.groupby('Disease')['outbreak_count'].sum().nlargest(top_n).index
    
    print(f"\n📋 Analyzing top {top_n} diseases:")
    for i, disease in enumerate(top_diseases, 1):
        total = df[df['Disease'] == disease]['outbreak_count'].sum()
        print(f"   {i:2}. {disease:40} - {total:5.0f} total outbreaks")
    
    # Analyze each disease
    results = []
    for disease in top_diseases:
        result = analyze_disease_outbreaks(disease, data_path, sensitivity=sensitivity)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70)
    
    total_anomalies = sum(r['anomalies'] for r in results)
    total_alerts = sum(r['alerts'] for r in results)
    
    print(f"\n✅ Analyzed {len(results)} diseases")
    print(f"⚠️  Total anomalies detected: {total_anomalies}")
    print(f"🚨 Total alerts generated: {total_alerts}")
    
    print(f"\n📁 Results saved in: results/anomaly_detection/")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EpiWatch Anomaly Detection")
    parser.add_argument('--disease', type=str, help='Specific disease to analyze')
    parser.add_argument('--top', type=int, default=10, help='Number of top diseases to analyze')
    parser.add_argument('--sensitivity', type=str, default='medium', 
                       choices=['low', 'medium', 'high'],
                       help='Anomaly detection sensitivity')
    parser.add_argument('--forecast-periods', type=int, default=3,
                       help='Number of periods to forecast')
    
    args = parser.parse_args()
    
    if not PROPHET_AVAILABLE:
        print("\n❌ Prophet is not installed!")
        print("Install with: pip install prophet")
        print("\nNote: Prophet requires additional dependencies:")
        print("  - On Windows: May need Visual C++ Build Tools")
        print("  - On Linux/Mac: gcc and python development headers")
        exit(1)
    
    if args.disease:
        # Analyze specific disease
        analyze_disease_outbreaks(
            disease=args.disease,
            forecast_periods=args.forecast_periods,
            sensitivity=args.sensitivity
        )
    else:
        # Batch analyze top diseases
        batch_analyze_top_diseases(
            top_n=args.top,
            sensitivity=args.sensitivity
        )
