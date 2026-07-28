# Tests for data processor 

"""
Tests for data_processor module.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_processor import (
    EnrichmentConfig, clean_dataframe, create_observation_record,
    create_impact_link
)


def test_enrichment_config_defaults():
    """Test EnrichmentConfig default values."""
    config = EnrichmentConfig()
    assert config.confidence_levels == ['high', 'medium', 'low']
    assert config.default_confidence == 'medium'


def test_clean_dataframe(sample_dataframe):
    """Test clean_dataframe handles missing values correctly."""
    df_clean = clean_dataframe(sample_dataframe)
    
    # Check missing values filled
    assert df_clean['pillar'].isna().sum() == 0
    assert df_clean['confidence'].isna().sum() == 0
    
    # Check date conversion
    assert pd.api.types.is_datetime64_any_dtype(df_clean['observation_date'])


def test_create_observation_record():
    """Test creation of observation record."""
    record = create_observation_record(
        indicator_code='TEST_IND',
        value=75.5,
        year=2025,
        source_name='Test Source',
        confidence='high'
    )
    
    assert record['record_type'] == 'observation'
    assert record['indicator_code'] == 'TEST_IND'
    assert record['value_numeric'] == 75.5
    assert record['observation_date'] == '2025-12-31'
    assert record['confidence'] == 'high'


def test_create_observation_record_defaults():
    """Test observation record with default values."""
    record = create_observation_record(
        indicator_code='TEST_IND',
        value=50.0,
        year=2024,
        source_name='Test Source'
    )
    
    assert record['confidence'] == 'medium'


def test_create_impact_link():
    """Test creation of impact link."""
    record = create_impact_link(
        parent_id='EVT_TEST',
        related_indicator='ACC_MM_ACCOUNT',
        impact_direction='positive',
        impact_magnitude=0.05,
        lag_months=12,
        evidence_basis='Test evidence'
    )
    
    assert record['record_type'] == 'impact_link'
    assert record['parent_id'] == 'EVT_TEST'
    assert record['impact_direction'] == 'positive'
    assert record['impact_magnitude'] == 0.05
    assert record['lag_months'] == 12


def test_create_impact_link_negative():
    """Test creation of negative impact link."""
    record = create_impact_link(
        parent_id='EVT_TEST',
        related_indicator='USG_ATM_COUNT',
        impact_direction='negative',
        impact_magnitude=-0.05,
        lag_months=6,
        evidence_basis='Test evidence'
    )
    
    assert record['impact_direction'] == 'negative'
    assert record['impact_magnitude'] == -0.05