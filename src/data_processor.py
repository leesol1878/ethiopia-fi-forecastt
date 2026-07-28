"""
Data processing module for Ethiopia Financial Inclusion Forecasting.

This module handles data enrichment, cleaning, and transformation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentConfig:
    """Configuration for data enrichment."""
    confidence_levels: List[str] = None
    default_confidence: str = 'medium'
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = ['high', 'medium', 'low']


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataframe by handling missing values and standardizing formats.
    
    Args:
        df: Input dataframe.
        
    Returns:
        pd.DataFrame: Cleaned dataframe.
    """
    df_clean = df.copy()
    
    # Standardize date formats
    if 'observation_date' in df_clean.columns:
        df_clean['observation_date'] = pd.to_datetime(
            df_clean['observation_date'], errors='coerce'
        )
    
    # Fill missing values in key columns
    df_clean['pillar'] = df_clean['pillar'].fillna('UNKNOWN')
    df_clean['confidence'] = df_clean['confidence'].fillna('medium')
    
    logger.info(f"Cleaned {len(df_clean)} records")
    return df_clean


def create_observation_record(
    indicator_code: str,
    value: float,
    year: int,
    source_name: str,
    confidence: str = 'medium',
    **kwargs
) -> Dict[str, Union[str, float]]:
    """
    Create a new observation record for enrichment.
    
    Args:
        indicator_code: Code of the indicator.
        value: Numeric value.
        year: Year of observation.
        source_name: Source of the data.
        confidence: Confidence level ('high', 'medium', 'low').
        **kwargs: Additional fields.
        
    Returns:
        Dict: Observation record.
    """
    record = {
        'record_type': 'observation',
        'indicator_code': indicator_code,
        'value_numeric': value,
        'observation_date': f'{year}-12-31',
        'source_name': source_name,
        'confidence': confidence,
        'collected_by': 'Week 12 Enrichment',
    }
    record.update(kwargs)
    return record


def create_impact_link(
    parent_id: str,
    related_indicator: str,
    impact_direction: str,
    impact_magnitude: float,
    lag_months: int,
    evidence_basis: str,
    **kwargs
) -> Dict[str, Union[str, float]]:
    """
    Create a new impact link record.
    
    Args:
        parent_id: ID of the event.
        related_indicator: Indicator affected.
        impact_direction: 'positive' or 'negative'.
        impact_magnitude: Magnitude of impact (0-1).
        lag_months: Months before impact is observed.
        evidence_basis: Justification for the impact estimate.
        **kwargs: Additional fields.
        
    Returns:
        Dict: Impact link record.
    """
    record = {
        'record_type': 'impact_link',
        'parent_id': parent_id,
        'related_indicator': related_indicator,
        'impact_direction': impact_direction,
        'impact_magnitude': impact_magnitude,
        'lag_months': lag_months,
        'evidence_basis': evidence_basis,
        'confidence': 'medium',
        'collected_by': 'Week 12 Enrichment',
    }
    record.update(kwargs)
    return record