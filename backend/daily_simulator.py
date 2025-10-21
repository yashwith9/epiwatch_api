"""
Daily Data Simulator - Convert yearly outbreak data to realistic daily patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict


class DailyDataSimulator:
    """
    Simulates realistic daily outbreak data from yearly aggregates
    Uses statistical distributions and seasonal patterns
    """
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility"""
        np.random.seed(seed)
    
    def generate_daily_breakdown(
        self,
        yearly_count: int,
        year: int,
        disease: str,
        days_back: int = 7
    ) -> List[Dict]:
        """
        Generate daily data points from yearly total
        
        Args:
            yearly_count: Total outbreaks for the year
            year: Year of data
            disease: Disease name (for pattern selection)
            days_back: Number of days to generate
        
        Returns:
            List of daily data points
        """
        # Calculate average daily rate
        daily_average = yearly_count / 365
        
        # Generate realistic variation using disease-specific patterns
        pattern_type = self._get_disease_pattern(disease)
        
        daily_data = []
        base_date = datetime.now()
        
        for i in range(days_back):
            date = base_date - timedelta(days=days_back - i - 1)
            
            # Apply pattern-based variation
            if pattern_type == 'seasonal':
                # Seasonal diseases peak at certain times
                seasonal_factor = self._seasonal_factor(date, disease)
                daily_count = daily_average * seasonal_factor
            elif pattern_type == 'sporadic':
                # Sporadic outbreaks with occasional spikes
                if np.random.random() < 0.2:  # 20% chance of spike
                    daily_count = daily_average * np.random.uniform(2, 5)
                else:
                    daily_count = daily_average * np.random.uniform(0.5, 1.5)
            else:  # steady
                # Relatively steady with small variation
                daily_count = daily_average * np.random.uniform(0.8, 1.2)
            
            # Add some noise
            daily_count = max(0, daily_count + np.random.normal(0, daily_average * 0.1))
            
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': int(round(daily_count)),
                'day_of_week': date.strftime('%A'),
                'is_weekend': date.weekday() >= 5
            })
        
        return daily_data
    
    def _get_disease_pattern(self, disease: str) -> str:
        """Determine disease outbreak pattern type"""
        disease_lower = disease.lower()
        
        # Seasonal diseases
        if any(d in disease_lower for d in ['influenza', 'flu', 'dengue', 'measles']):
            return 'seasonal'
        
        # Sporadic outbreak diseases
        elif any(d in disease_lower for d in ['ebola', 'cholera', 'yellow fever', 'mers']):
            return 'sporadic'
        
        # Steady/endemic diseases
        else:
            return 'steady'
    
    def _seasonal_factor(self, date: datetime, disease: str) -> float:
        """Calculate seasonal factor for a given date"""
        disease_lower = disease.lower()
        month = date.month
        
        # Influenza peaks in winter (Nov-Mar in Northern Hemisphere)
        if 'influenza' in disease_lower or 'flu' in disease_lower:
            if month in [11, 12, 1, 2, 3]:
                return 1.5  # 50% higher in winter
            elif month in [6, 7, 8]:
                return 0.5  # 50% lower in summer
            else:
                return 1.0
        
        # Dengue peaks in rainy season (varies by region, using Jun-Oct)
        elif 'dengue' in disease_lower:
            if month in [6, 7, 8, 9, 10]:
                return 1.6
            else:
                return 0.7
        
        # Measles slightly higher in spring
        elif 'measles' in disease_lower:
            if month in [3, 4, 5]:
                return 1.3
            else:
                return 0.9
        
        # Default: no strong seasonality
        return 1.0
    
    def generate_weekly_trend(
        self,
        disease_data: pd.DataFrame,
        weeks_back: int = 4
    ) -> List[Dict]:
        """
        Generate weekly aggregated data
        
        Args:
            disease_data: DataFrame with yearly data
            weeks_back: Number of weeks to generate
        
        Returns:
            List of weekly data points
        """
        if len(disease_data) == 0:
            return []
        
        latest_year = disease_data['Year'].max()
        latest_count = disease_data[disease_data['Year'] == latest_year]['outbreak_count'].values[0]
        disease = disease_data['Disease'].values[0]
        
        # Generate daily data first
        daily_data = self.generate_daily_breakdown(
            yearly_count=int(latest_count),
            year=latest_year,
            disease=disease,
            days_back=weeks_back * 7
        )
        
        # Group into weeks
        weekly_data = []
        for week in range(weeks_back):
            week_start = week * 7
            week_end = week_start + 7
            week_days = daily_data[week_start:week_end]
            
            weekly_total = sum(d['count'] for d in week_days)
            start_date = week_days[0]['date'] if week_days else ''
            end_date = week_days[-1]['date'] if week_days else ''
            
            weekly_data.append({
                'week': weeks_back - week,
                'start_date': start_date,
                'end_date': end_date,
                'total_count': weekly_total,
                'daily_average': weekly_total / 7 if weekly_total > 0 else 0
            })
        
        return list(reversed(weekly_data))
    
    def calculate_realistic_change(
        self,
        current_count: int,
        previous_count: int,
        time_period: str = 'week'
    ) -> Dict:
        """
        Calculate realistic percentage change with context
        
        Args:
            current_count: Current period count
            previous_count: Previous period count
            time_period: 'week', 'month', or 'year'
        
        Returns:
            Dictionary with change metrics
        """
        if previous_count == 0:
            if current_count > 0:
                change_pct = 100.0
                trend = 'up'
            else:
                change_pct = 0.0
                trend = 'stable'
        else:
            change_pct = ((current_count - previous_count) / previous_count) * 100
            if abs(change_pct) < 5:
                trend = 'stable'
            elif change_pct > 0:
                trend = 'up'
            else:
                trend = 'down'
        
        # Determine severity
        if abs(change_pct) >= 50:
            severity = 'significant'
        elif abs(change_pct) >= 20:
            severity = 'moderate'
        else:
            severity = 'minor'
        
        return {
            'change_pct': round(change_pct, 1),
            'change_absolute': current_count - previous_count,
            'trend': trend,
            'severity': severity,
            'time_period': time_period,
            'description': self._generate_change_description(
                change_pct, current_count, previous_count, time_period
            )
        }
    
    def _generate_change_description(
        self,
        change_pct: float,
        current: int,
        previous: int,
        period: str
    ) -> str:
        """Generate human-readable description of change"""
        abs_change = abs(current - previous)
        direction = 'increase' if change_pct > 0 else 'decrease'
        
        if abs(change_pct) < 5:
            return f"Stable at {current} cases (no significant change)"
        elif abs(change_pct) < 20:
            return f"Slight {direction} of {abs_change} cases ({abs(change_pct):.1f}%) this {period}"
        elif abs(change_pct) < 50:
            return f"Moderate {direction} of {abs_change} cases ({abs(change_pct):.1f}%) this {period}"
        else:
            return f"Significant {direction} of {abs_change} cases ({abs(change_pct):.1f}%) this {period} - requires attention"


# Example usage and testing
if __name__ == "__main__":
    simulator = DailyDataSimulator()
    
    # Test with COVID-19 data
    test_data = pd.DataFrame({
        'Disease': ['COVID-19', 'COVID-19'],
        'Year': [2024, 2025],
        'outbreak_count': [142, 107]
    })
    
    print("=" * 70)
    print("Daily Data Simulator - Test Output")
    print("=" * 70)
    
    # Generate 7-day data
    daily_covid = simulator.generate_daily_breakdown(
        yearly_count=107,
        year=2025,
        disease='COVID-19',
        days_back=7
    )
    
    print("\n7-Day COVID-19 Breakdown:")
    print("-" * 70)
    for day in daily_covid:
        print(f"{day['date']} ({day['day_of_week']}): {day['count']} cases")
    
    # Calculate change
    change = simulator.calculate_realistic_change(107, 142, 'year')
    print(f"\nYear-over-year change:")
    print(f"  {change['description']}")
    print(f"  Trend: {change['trend']}, Severity: {change['severity']}")
    
    # Generate weekly trend
    weekly = simulator.generate_weekly_trend(test_data, weeks_back=4)
    print(f"\n4-Week Trend:")
    print("-" * 70)
    for week in weekly:
        print(f"Week {week['week']}: {week['total_count']} cases "
              f"({week['start_date']} to {week['end_date']})")
