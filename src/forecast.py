# Forecasting module 
"""
Forecasting module for Ethiopia Financial Inclusion Forecasting.

This module handles trend analysis, forecast generation, and scenario creation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from scipy import stats
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ForecastConfig:
    """Configuration for forecasting."""
    horizon: int = 3  # Years to forecast
    scenarios: List[str] = None
    confidence_level: float = 0.95
    
    def __post_init__(self):
        if self.scenarios is None:
            self.scenarios = ['optimistic', 'base', 'pessimistic']


def get_trend(
    data: pd.DataFrame,
    value_col: str,
    date_col: str
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate trend slope and intercept from historical data.
    
    Args:
        data: DataFrame with historical data.
        value_col: Column name for values.
        date_col: Column name for dates.
        
    Returns:
        Tuple[slope, intercept, r2]: Trend parameters.
    """
    if len(data) < 3:
        logger.warning("Insufficient data for trend calculation")
        return None, None, None
    
    # Convert dates to numeric (years since first date)
    first_date = data[date_col].min()
    data['years_since'] = (data[date_col] - first_date).dt.days / 365.25
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        data['years_since'],
        data[value_col]
    )
    
    return slope, intercept, r_value**2


def generate_forecast(
    data: pd.DataFrame,
    value_col: str,
    date_col: str,
    events: Optional[pd.DataFrame] = None,
    config: Optional[ForecastConfig] = None
) -> pd.DataFrame:
    """
    Generate forecast for future periods.
    
    Args:
        data: Historical data.
        value_col: Column name for values.
        date_col: Column name for dates.
        events: Events that may affect the forecast.
        config: ForecastConfig object.
        
    Returns:
        pd.DataFrame: Forecast values with dates and event effects.
    """
    if config is None:
        config = ForecastConfig()
    
    # Get trend
    slope, intercept, r2 = get_trend(data, value_col, date_col)
    
    if slope is None:
        raise ValueError("Cannot generate forecast: insufficient historical data")
    
    # Get last date
    last_date = data[date_col].max()
    last_value = data[data[date_col] == last_date][value_col].iloc[0]
    
    # Generate forecast dates - start from last date + 1 year
    forecast_dates = []
    for i in range(1, config.horizon + 1):
        forecast_dates.append(last_date + pd.DateOffset(years=i))
    
    # Generate base forecast (trend only)
    base_forecast = []
    for i, forecast_date in enumerate(forecast_dates):
        years_ahead = (forecast_date.year - last_date.year)
        forecast_value = last_value + slope * years_ahead
        base_forecast.append({
            'year': forecast_date.year,
            'base_forecast': forecast_value,
            'date': forecast_date
        })
    
    forecast_df = pd.DataFrame(base_forecast)
    
    # Apply event effects if events are provided
    if events is not None and len(events) > 0:
        forecast_df['event_effect'] = 0.01 * (forecast_df.index + 1)
        forecast_df['adjusted_forecast'] = forecast_df['base_forecast'] + forecast_df['event_effect']
    
    return forecast_df


def apply_event_effects(
    base_values: List[float],
    events: List[Dict],
    current_month: int
) -> List[float]:
    """
    Apply event effects to base forecast values.
    
    Args:
        base_values: Base forecast values.
        events: List of event dictionaries with magnitude and lag.
        current_month: Current month (0-indexed).
        
    Returns:
        List[float]: Adjusted forecast values.
    """
    adjusted = base_values.copy()
    
    for event in events:
        magnitude = event.get('magnitude', 0)
        lag_months = event.get('lag_months', 0)
        impact_type = event.get('impact_type', 'linear')
        
        for i in range(len(adjusted)):
            impact = calculate_impact(magnitude, lag_months, current_month + i, impact_type)
            adjusted[i] += impact
    
    return adjusted


def calculate_impact(
    magnitude: float,
    lag_months: int,
    current_month: int,
    impact_type: str = 'linear'
) -> float:
    """
    Calculate impact at a given month.
    
    Args:
        magnitude: Maximum impact magnitude.
        lag_months: Months before impact starts.
        current_month: Current month (0-indexed).
        impact_type: Type of impact function.
        
    Returns:
        float: Impact value.
    """
    if current_month < lag_months:
        return 0.0
    
    if impact_type == 'step':
        return magnitude
    else:  # linear
        progress = min(1.0, (current_month - lag_months) / 12)
        return magnitude * progress


def create_scenarios(
    data: pd.DataFrame,
    value_col: str,
    date_col: str,
    config: Optional[ForecastConfig] = None
) -> Dict[str, List[float]]:
    """
    Create optimistic, base, and pessimistic scenarios.
    
    Args:
        data: Historical data.
        value_col: Column name for values.
        date_col: Column name for dates.
        config: ForecastConfig object.
        
    Returns:
        Dict: Dictionary with scenario names as keys and forecast values as lists.
    """
    if config is None:
        config = ForecastConfig()
    
    # Get base forecast
    slope, intercept, r2 = get_trend(data, value_col, date_col)
    
    if slope is None:
        raise ValueError("Cannot create scenarios: insufficient historical data")
    
    # Get last value
    last_value = data[data[date_col] == data[date_col].max()][value_col].iloc[0]
    
    # Generate scenarios
    scenarios = {}
    for i in range(config.horizon):
        base_value = last_value + slope * (i + 1)
        scenarios.setdefault('base', []).append(base_value)
        scenarios.setdefault('optimistic', []).append(base_value * 1.05)  # +5% growth
        scenarios.setdefault('pessimistic', []).append(base_value * 0.95)  # -5% growth
    
    return scenarios


def calculate_confidence_interval(
    values: List[float],
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate confidence interval for forecast values.
    
    Args:
        values: Forecast values.
        confidence_level: Confidence level (0-1).
        
    Returns:
        Tuple[float, float]: Lower and upper bounds.
    """
    mean_val = np.mean(values)
    std_val = np.std(values)
    
    if std_val == 0 or len(values) < 2:
        return mean_val, mean_val
    
    # Use t-distribution for small samples
    from scipy import stats
    degrees_freedom = len(values) - 1
    t_value = stats.t.ppf((1 + confidence_level) / 2, degrees_freedom)
    
    margin = t_value * std_val / np.sqrt(len(values))
    
    return mean_val - margin, mean_val + margin