"""
Tests for event_model module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.event_model import (
    create_association_matrix, 
    calculate_event_impact,
    validate_impact,
    get_strongest_impacts,
    IMPACT_FUNCTIONS
)


def test_create_association_matrix(sample_dataframe):
    """Test that association matrix is created correctly."""
    # Get events from sample data
    events = sample_dataframe[sample_dataframe['record_type'] == 'event'].copy()
    # Add an event_name column if it doesn't exist
    if 'event_name' not in events.columns:
        events['event_name'] = events['indicator_code'] + '_event'
    indicators = ['ACC_OWNERSHIP', 'ACC_MM_ACCOUNT']
    
    matrix = create_association_matrix(events, indicators)
    
    assert isinstance(matrix, pd.DataFrame)
    assert len(matrix) == len(events)
    assert set(matrix.columns) == set(indicators)


def test_calculate_event_impact_positive():
    """Test positive impact calculation."""
    impact = calculate_event_impact(
        event_magnitude=0.05,
        lag_months=12,
        current_month=24,  # 12 lag + 12 decay = full impact
        impact_type='linear'
    )
    
    # After 24 months, impact should be fully realized
    assert impact == 0.05


def test_calculate_event_impact_before_lag():
    """Test impact before lag period."""
    impact = calculate_event_impact(
        event_magnitude=0.05,
        lag_months=12,
        current_month=6,
        impact_type='linear'
    )
    
    # Before lag, impact should be 0
    assert impact == 0.0


def test_calculate_event_impact_ramp_up():
    """Test impact during ramp-up period."""
    impact = calculate_event_impact(
        event_magnitude=0.05,
        lag_months=12,
        current_month=18,  # 6 months into ramp-up (50% of 12-month decay)
        impact_type='linear'
    )
    
    # Partially realized (6 months into ramp-up = 50%)
    assert impact == 0.025


def test_calculate_event_impact_step():
    """Test step function impact."""
    impact = calculate_event_impact(
        event_magnitude=0.05,
        lag_months=12,
        current_month=18,
        impact_type='step'
    )
    
    # After lag, impact should be full
    assert impact == 0.05


def test_calculate_event_impact_before_lag_step():
    """Test step function before lag."""
    impact = calculate_event_impact(
        event_magnitude=0.05,
        lag_months=12,
        current_month=6,
        impact_type='step'
    )
    
    # Before lag, impact should be 0
    assert impact == 0.0


def test_validate_impact_valid():
    """Test validation of valid impact."""
    result = validate_impact(
        event_name='Telebirr Launch',
        indicator='ACC_MM_ACCOUNT',
        magnitude=0.05,
        lag_months=12,
        evidence='Mobile money grew from 4.7% to 9.45%'
    )
    
    assert result is True


def test_validate_impact_invalid_magnitude():
    """Test validation rejects invalid magnitude."""
    with pytest.raises(ValueError, match="Magnitude must be between -1 and 1"):
        validate_impact(
            event_name='Test',
            indicator='TEST',
            magnitude=1.5,
            lag_months=12,
            evidence='Test'
        )


def test_validate_impact_invalid_lag():
    """Test validation rejects invalid lag."""
    with pytest.raises(ValueError, match="Lag months must be non-negative"):
        validate_impact(
            event_name='Test',
            indicator='TEST',
            magnitude=0.05,
            lag_months=-1,
            evidence='Test'
        )


def test_get_strongest_impacts():
    """Test getting strongest impacts from matrix."""
    # Create a test matrix
    test_matrix = pd.DataFrame({
        'A': [0.10, 0.02, 0.01],
        'B': [0.05, 0.03, 0.08],
        'C': [0.01, 0.04, 0.02]
    }, index=['Event1', 'Event2', 'Event3'])
    
    strongest = get_strongest_impacts(test_matrix, top_n=3)
    
    assert len(strongest) == 3
    assert strongest.iloc[0]['value'] == 0.10


def test_impact_functions_constant():
    """Test IMPACT_FUNCTIONS constant exists."""
    assert 'linear' in IMPACT_FUNCTIONS
    assert 'step' in IMPACT_FUNCTIONS
    assert 'sigmoid' in IMPACT_FUNCTIONS