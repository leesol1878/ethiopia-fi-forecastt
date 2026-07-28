# Data loading module 
"""
Data loading module for Ethiopia Financial Inclusion Forecasting.

This module handles loading and validating the enriched dataset.
"""

from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataConfig:
    """
    Configuration for data loading.
    
    Attributes:
        raw_data_path: Path to raw data directory
        processed_data_path: Path to processed data directory
        enriched_file: Name of the enriched dataset file
    """
    raw_data_path: str = 'data/raw/'
    processed_data_path: str = 'data/processed/'
    enriched_file: str = 'ethiopia_fi_enriched.csv'
    
    def get_enriched_path(self) -> Path:
        """Get the full path to the enriched dataset."""
        return Path(self.processed_data_path) / self.enriched_file


def load_enriched_data(config: Optional[DataConfig] = None) -> pd.DataFrame:
    """
    Load the enriched financial inclusion dataset.
    
    Args:
        config: DataConfig object with file paths. If None, uses defaults.
        
    Returns:
        pd.DataFrame: Enriched dataset with all records.
        
    Raises:
        FileNotFoundError: If the dataset file doesn't exist.
    """
    if config is None:
        config = DataConfig()
    
    file_path = config.get_enriched_path()
    
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {file_path}")
    
    logger.info(f"Loading dataset from: {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    return df


def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that the dataframe has the expected structure.
    
    Args:
        df: DataFrame to validate.
        
    Returns:
        bool: True if valid, raises ValueError if invalid.
        
    Raises:
        ValueError: If required columns are missing.
    """
    required_columns = [
        'record_type', 'pillar', 'indicator_code', 
        'value_numeric', 'observation_date'
    ]
    
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    logger.info("Dataframe validation passed")
    return True


def filter_by_type(df: pd.DataFrame, record_type: str) -> pd.DataFrame:
    """
    Filter dataframe by record type.
    
    Args:
        df: Input dataframe.
        record_type: Type to filter ('observation', 'event', 'target', 'impact_link').
        
    Returns:
        pd.DataFrame: Filtered dataframe.
    """
    return df[df['record_type'] == record_type].copy()


def get_indicator_data(
    df: pd.DataFrame, 
    indicator_code: str
) -> pd.DataFrame:
    """
    Get data for a specific indicator.
    
    Args:
        df: Input dataframe.
        indicator_code: Code of the indicator to extract.
        
    Returns:
        pd.DataFrame: Filtered and sorted indicator data.
    """
    data = df[(df['record_type'] == 'observation') & 
              (df['indicator_code'] == indicator_code)].copy()
    
    if len(data) == 0:
        logger.warning(f"No data found for indicator: {indicator_code}")
        return data
    
    data['date'] = pd.to_datetime(data['observation_date'])
    return data.sort_values('date')


# Constants
RECORD_TYPES = ['observation', 'event', 'target', 'impact_link']
INDICATORS = {
    'ACC_OWNERSHIP': 'Account Ownership Rate',
    'ACC_MM_ACCOUNT': 'Mobile Money Account Penetration',
    'ACC_FAYDA': 'Fayda Digital ID Enrollment',
    'USG_P2P_COUNT': 'P2P Transaction Count',
    'USG_TELEBIRR_USERS': 'Telebirr Users',
    'USG_MPESA_USERS': 'M-Pesa Users',
}