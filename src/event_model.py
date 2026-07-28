# Event impact modeling module 
"""
Event impact modeling module for Ethiopia Financial Inclusion Forecasting.

This module handles the creation and validation of event-indicator association matrices.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Impact function types
IMPACT_FUNCTIONS = ['linear', 'step', 'sigmoid']


@dataclass
class EventConfig:
    """Configuration for event impact modeling."""
    default_lag_months: int = 12
    default_impact_type: str = 'linear'
    decay_months: int = 12


def create_association_matrix(
    events: pd.DataFrame,
    indicators: List[str],
    config: Optional[EventConfig] = None
) -> pd.DataFrame:
    """
    Create an event-indicator association matrix.
    
    Args:
        events: DataFrame containing events.
        indicators: List of indicator codes.
        config: EventConfig object.
        
    Returns:
        pd.DataFrame: Association matrix with events as rows and indicators as columns.
    """
    if config is None:
        config = EventConfig()
    
    # Ensure we have an event_name column
    if 'event_name' not in events.columns:
        if 'indicator' in events.columns:
            events = events.copy()
            events['event_name'] = events['indicator']
        else:
            raise ValueError("Events DataFrame must have 'event_name' or 'indicator' column")
    
    # Initialize matrix with float dtype (important for decimal values)
    matrix = pd.DataFrame(0.0, index=events['event_name'], columns=indicators)
    
    # Fill with default values (to be overridden with actual data)
    for idx, event in events.iterrows():
        for indicator in indicators:
            matrix.loc[event['event_name'], indicator] = 0.01
    
    logger.info(f"Created association matrix: {len(matrix)} events × {len(matrix.columns)} indicators")
    return matrix

def calculate_event_impact(
    event_magnitude: float,
    lag_months: int,
    current_month: int,
    impact_type: str = 'linear',
    decay_months: Optional[int] = None
) -> float:
    """
    Calculate event impact at a given time.
    
    Args:
        event_magnitude: Maximum impact magnitude.
        lag_months: Months before impact starts.
        current_month: Current month since event.
        impact_type: Type of impact function ('linear', 'step', 'sigmoid').
        decay_months: Months for full effect (linear only).
        
    Returns:
        float: Impact at current_month.
    """
    if current_month < lag_months:
        return 0.0
    
    if impact_type == 'step':
        return event_magnitude
    
    elif impact_type == 'linear':
        if decay_months is None:
            decay_months = 12
        progress = min(1.0, (current_month - lag_months) / decay_months)
        return event_magnitude * progress
    
    elif impact_type == 'sigmoid':
        # S-curve adoption
        steepness = 4  # Controls curve steepness
        x = (current_month - lag_months) / steepness
        return event_magnitude / (1 + np.exp(-x))
    
    else:
        logger.warning(f"Unknown impact_type: {impact_type}, using linear")
        return event_magnitude


def validate_impact(
    event_name: str,
    indicator: str,
    magnitude: float,
    lag_months: int,
    evidence: str
) -> bool:
    """
    Validate an impact estimate.
    
    Args:
        event_name: Name of the event.
        indicator: Indicator affected.
        magnitude: Impact magnitude (-1 to 1).
        lag_months: Months before impact.
        evidence: Justification for the impact.
        
    Returns:
        bool: True if valid.
        
    Raises:
        ValueError: If validation fails.
    """
    if not (-1 <= magnitude <= 1):
        raise ValueError(f"Magnitude must be between -1 and 1, got {magnitude}")
    
    if lag_months < 0:
        raise ValueError(f"Lag months must be non-negative, got {lag_months}")
    
    if not evidence or len(evidence.strip()) < 5:
        raise ValueError(f"Evidence must be provided and at least 5 characters")
    
    logger.info(f"Validated impact: {event_name} → {indicator}: {magnitude:.2f} with lag {lag_months}m")
    return True


def get_strongest_impacts(
    matrix: pd.DataFrame,
    top_n: int = 5,
    direction: Optional[str] = None
) -> pd.DataFrame:
    """
    Get the strongest impacts from an association matrix.
    
    Args:
        matrix: Association matrix.
        top_n: Number of top impacts to return.
        direction: Filter by direction ('positive', 'negative', None for all).
        
    Returns:
        pd.DataFrame: Top impacts with event, indicator, and value.
    """
    # Melt the matrix to get long format
    impacts = matrix.reset_index().melt(
        id_vars=['index'],
        var_name='indicator',
        value_name='value'
    ).rename(columns={'index': 'event'})
    
    # Filter by direction
    if direction == 'positive':
        impacts = impacts[impacts['value'] > 0]
    elif direction == 'negative':
        impacts = impacts[impacts['value'] < 0]
    
    # Sort by absolute value
    impacts['abs_value'] = impacts['value'].abs()
    impacts = impacts.sort_values('abs_value', ascending=False)
    
    return impacts.head(top_n)