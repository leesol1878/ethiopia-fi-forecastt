"""
Test fixtures for Ethiopia Financial Inclusion project.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_dataframe():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        'record_type': ['observation', 'observation', 'event'],
        'pillar': ['ACCESS', 'ACCESS', 'UNKNOWN'],
        'indicator_code': ['ACC_OWNERSHIP', 'ACC_MM_ACCOUNT', 'EVENT_001'],
        'value_numeric': [22.0, 4.7, np.nan],
        'observation_date': ['2014-12-31', '2021-05-17', '2021-05-17'],
        'confidence': ['high', 'high', 'high']
    })


@pytest.fixture
def sample_config():
    """Create a sample DataConfig for testing."""
    from src.data_loader import DataConfig
    return DataConfig(
        raw_data_path='data/raw/',
        processed_data_path='data/processed/',
        enriched_file='test_data.csv'
    )