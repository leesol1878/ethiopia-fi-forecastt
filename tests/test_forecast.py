"""
Tests for forecast module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.forecast import (
    ForecastConfig,
    get_trend,
    generate_forecast,
    apply_event_effects,
    create_scenarios,
    calculate_confidence_interval
)


@pytest.fixture
def sample_time_series():
    """Create a sample time series for testing."""
    return pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=5, freq='YE'),
        'value': [20, 25, 30, 35, 40]
    })


@pytest.fixture
def sample_events():
    """Create sample events for testing."""
    return pd.DataFrame({
        'event_name': ['Event1', 'Event2'],
        'date': ['2022-06-01', '2023-06-01'],
        'magnitude': [0.05, 0.03],
        'indicator': ['ACC_MM_ACCOUNT', 'ACC_OWNERSHIP'],
        'lag_months': [6, 12]
    })


def test_forecast_config_defaults():
    """Test ForecastConfig default values."""
    config = ForecastConfig()
    assert config.horizon == 3
    assert config.scenarios == ['optimistic', 'base', 'pessimistic']
    assert config.confidence_level == 0.95


def test_forecast_config_custom():
    """Test ForecastConfig with custom values."""
    config = ForecastConfig(
        horizon=5,
        scenarios=['base'],
        confidence_level=0.90
    )
    assert config.horizon == 5
    assert config.scenarios == ['base']
    assert config.confidence_level == 0.90


def test_get_trend_linear(sample_time_series):
    """Test trend calculation with linear data."""
    slope, intercept, r2 = get_trend(sample_time_series, 'value', 'date')
    
    # For perfectly linear data, slope should be approximately 5
    # Use approx() for floating point comparison
    assert slope == pytest.approx(5.0, abs=0.01)
    assert r2 == pytest.approx(1.0, abs=0.01)


def test_get_trend_insufficient_data():
    """Test trend calculation with insufficient data."""
    df = pd.DataFrame({
        'date': pd.date_range('2020-01-01', periods=2, freq='YE'),
        'value': [20, 25]
    })
    
    slope, intercept, r2 = get_trend(df, 'value', 'date')
    
    # Should return None for insufficient data
    assert slope is None
    assert intercept is None
    assert r2 is None


def test_generate_forecast_basic(sample_time_series):
    """Test basic forecast generation."""
    config = ForecastConfig(horizon=3)
    forecast = generate_forecast(
        data=sample_time_series,
        value_col='value',
        date_col='date',
        config=config
    )
    
    assert len(forecast) == 3
    # Last year should be 2027 (2024 + 3 years)
    assert forecast['year'].iloc[-1] == 2027


def test_generate_forecast_with_events(sample_time_series, sample_events):
    """Test forecast with event effects."""
    config = ForecastConfig(horizon=3)
    forecast = generate_forecast(
        data=sample_time_series,
        value_col='value',
        date_col='date',
        events=sample_events,
        config=config
    )
    
    assert len(forecast) == 3
    # Should have event effects applied
    assert 'event_effect' in forecast.columns


def test_apply_event_effects():
    """Test applying event effects to base forecast."""
    base_values = [40, 45, 50]
    events = [
        {'magnitude': 0.05, 'lag_months': 6, 'impact_type': 'linear'},
        {'magnitude': 0.03, 'lag_months': 12, 'impact_type': 'step'}
    ]
    
    adjusted = apply_event_effects(base_values, events, current_month=18)
    
    # Should be greater than base
    assert adjusted[0] > base_values[0]
    assert adjusted[1] > base_values[1]
    assert adjusted[2] > base_values[2]


def test_apply_event_effects_no_events():
    """Test applying no events."""
    base_values = [40, 45, 50]
    adjusted = apply_event_effects(base_values, [], current_month=18)
    
    # Should be unchanged
    assert adjusted == base_values


def test_create_scenarios(sample_time_series):
    """Test scenario creation."""
    config = ForecastConfig(horizon=3)
    scenarios = create_scenarios(
        data=sample_time_series,
        value_col='value',
        date_col='date',
        config=config
    )
    
    assert 'base' in scenarios
    assert 'optimistic' in scenarios
    assert 'pessimistic' in scenarios
    assert len(scenarios['base']) == 3
    assert len(scenarios['optimistic']) == 3
    assert len(scenarios['pessimistic']) == 3


def test_calculate_confidence_interval():
    """Test confidence interval calculation."""
    values = [40, 42, 45, 43, 41]
    lower, upper = calculate_confidence_interval(values, confidence_level=0.95)
    
    assert lower < np.mean(values)
    assert upper > np.mean(values)
    assert lower < upper


def test_calculate_confidence_interval_single_value():
    """Test confidence interval with single value."""
    values = [40]
    lower, upper = calculate_confidence_interval(values, confidence_level=0.95)
    
    # Should return mean as both bounds
    assert lower == 40.0
    assert upper == 40.0