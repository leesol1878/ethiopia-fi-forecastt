"""
Tests for data_loader module.
"""

import pytest
import pandas as pd
import os
from pathlib import Path
from src.data_loader import (
    DataConfig, load_enriched_data, validate_dataframe,
    filter_by_type, get_indicator_data, RECORD_TYPES
)


def test_data_config_defaults():
    """Test DataConfig default values."""
    config = DataConfig()
    assert config.raw_data_path == 'data/raw/'
    assert config.processed_data_path == 'data/processed/'
    assert config.enriched_file == 'ethiopia_fi_enriched.csv'


def test_data_config_custom():
    """Test DataConfig with custom values."""
    config = DataConfig(
        raw_data_path='custom/raw/',
        processed_data_path='custom/processed/',
        enriched_file='custom_data.csv'
    )
    assert config.raw_data_path == 'custom/raw/'
    assert config.processed_data_path == 'custom/processed/'
    assert config.enriched_file == 'custom_data.csv'


def test_get_enriched_path():
    """Test get_enriched_path returns correct Path."""
    config = DataConfig(
        processed_data_path='data/processed/',
        enriched_file='test.csv'
    )
    path = config.get_enriched_path()
    assert path == Path('data/processed/test.csv')


def test_validate_dataframe_valid(sample_dataframe):
    """Test validate_dataframe passes with valid data."""
    result = validate_dataframe(sample_dataframe)
    assert result is True


def test_validate_dataframe_invalid():
    """Test validate_dataframe raises error with invalid data."""
    df = pd.DataFrame({'wrong_column': [1, 2, 3]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dataframe(df)


def test_filter_by_type(sample_dataframe):
    """Test filter_by_type returns correct records."""
    observations = filter_by_type(sample_dataframe, 'observation')
    assert len(observations) == 2
    assert all(observations['record_type'] == 'observation')


def test_filter_by_type_empty(sample_dataframe):
    """Test filter_by_type returns empty when type not found."""
    result = filter_by_type(sample_dataframe, 'nonexistent')
    assert len(result) == 0


def test_get_indicator_data(sample_dataframe):
    """Test get_indicator_data returns correct indicator data."""
    acc_data = get_indicator_data(sample_dataframe, 'ACC_OWNERSHIP')
    assert len(acc_data) == 1
    assert acc_data.iloc[0]['value_numeric'] == 22.0


def test_get_indicator_data_not_found(sample_dataframe):
    """Test get_indicator_data returns empty for missing indicator."""
    result = get_indicator_data(sample_dataframe, 'MISSING')
    assert len(result) == 0


def test_record_types_constant():
    """Test RECORD_TYPES constant contains expected values."""
    expected = ['observation', 'event', 'target', 'impact_link']
    assert set(RECORD_TYPES) == set(expected)