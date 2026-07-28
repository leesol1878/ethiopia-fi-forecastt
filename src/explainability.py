"""
Model explainability module using SHAP.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not installed. Install with: pip install shap")


def create_shap_explainer(model, X_train, feature_names: Optional[List[str]] = None):
    """
    Create a SHAP explainer for a model.
    
    Args:
        model: Trained model (scikit-learn compatible).
        X_train: Training data.
        feature_names: List of feature names.
        
    Returns:
        shap.Explainer: SHAP explainer object.
    """
    if not SHAP_AVAILABLE:
        raise ImportError("SHAP is not installed. Run: pip install shap")
    
    if feature_names is None:
        if hasattr(X_train, 'columns'):
            feature_names = X_train.columns.tolist()
        else:
            feature_names = [f'feature_{i}' for i in range(X_train.shape[1])]
    
    explainer = shap.Explainer(model, X_train, feature_names=feature_names)
    logger.info(f"Created SHAP explainer with {len(feature_names)} features")
    return explainer


def plot_global_importance(shap_values, X_test, feature_names: Optional[List[str]] = None, 
                          max_display: int = 10, save_path: Optional[str] = None):
    """
    Create a global feature importance plot.
    
    Args:
        shap_values: SHAP values from explainer.
        X_test: Test data.
        feature_names: List of feature names.
        max_display: Maximum number of features to display.
        save_path: Path to save the figure.
        
    Returns:
        matplotlib.figure.Figure: The figure object.
    """
    if not SHAP_AVAILABLE:
        raise ImportError("SHAP is not installed.")
    
    plt.figure(figsize=(10, 6))
    
    # Create summary plot
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, 
                      max_display=max_display, show=False)
    
    plt.title('Global Feature Importance (SHAP)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved global importance plot to: {save_path}")
    
    plt.show()
    return plt.gcf()


def plot_individual_prediction(shap_values, X_test, index: int, 
                               feature_names: Optional[List[str]] = None,
                               save_path: Optional[str] = None):
    """
    Create an individual prediction explanation.
    
    Args:
        shap_values: SHAP values from explainer.
        X_test: Test data.
        index: Index of the prediction to explain.
        feature_names: List of feature names.
        save_path: Path to save the figure.
        
    Returns:
        matplotlib.figure.Figure: The figure object.
    """
    if not SHAP_AVAILABLE:
        raise ImportError("SHAP is not installed.")
    
    # Extract single prediction
    single_shap = shap_values[index] if isinstance(shap_values, list) else shap_values[index]
    single_X = X_test.iloc[index] if hasattr(X_test, 'iloc') else X_test[index]
    
    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(single_shap, max_display=10, show=False)
    
    plt.title(f'Individual Prediction Explanation (Index: {index})', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"Saved individual prediction plot to: {save_path}")
    
    plt.show()
    return plt.gcf()


def get_feature_importance_df(shap_values, feature_names: List[str]) -> pd.DataFrame:
    """
    Get feature importance as a DataFrame.
    
    Args:
        shap_values: SHAP values from explainer.
        feature_names: List of feature names.
        
    Returns:
        pd.DataFrame: Feature importance with columns: feature, importance.
    """
    if not SHAP_AVAILABLE:
        raise ImportError("SHAP is not installed.")
    
    # Calculate mean absolute SHAP values
    if isinstance(shap_values, list):
        shap_matrix = np.array([sv.values for sv in shap_values])
    else:
        shap_matrix = shap_values.values if hasattr(shap_values, 'values') else shap_values
    
    mean_abs_shap = np.abs(shap_matrix).mean(axis=0)
    
    importance_df = pd.DataFrame({
        'feature': feature_names[:len(mean_abs_shap)],
        'importance': mean_abs_shap
    }).sort_values('importance', ascending=False)
    
    return importance_df


def detect_concerning_patterns(shap_values, X_test, feature_names: List[str]) -> Dict:
    """
    Detect concerning patterns in SHAP values.
    
    Args:
        shap_values: SHAP values from explainer.
        X_test: Test data.
        feature_names: List of feature names.
        
    Returns:
        Dict: Dictionary with concerning patterns.
    """
    patterns = {
        'high_variance_features': [],
        'extreme_outliers': [],
        'potential_bias_indicators': []
    }
    
    if not SHAP_AVAILABLE:
        return patterns
    
    # Get shap matrix
    if isinstance(shap_values, list):
        shap_matrix = np.array([sv.values for sv in shap_values])
    else:
        shap_matrix = shap_values.values if hasattr(shap_values, 'values') else shap_values
    
    # Check for high variance features
    variances = shap_matrix.var(axis=0)
    threshold = np.percentile(variances, 90)
    for i, var in enumerate(variances):
        if var > threshold:
            patterns['high_variance_features'].append({
                'feature': feature_names[i] if i < len(feature_names) else f'feature_{i}',
                'variance': var
            })
    
    # Check for extreme outliers
    for i in range(shap_matrix.shape[1]):
        values = shap_matrix[:, i]
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        outliers = values[(values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr)]
        if len(outliers) > len(values) * 0.05:  # More than 5% outliers
            patterns['extreme_outliers'].append({
                'feature': feature_names[i] if i < len(feature_names) else f'feature_{i}',
                'outlier_count': len(outliers)
            })
    
    return patterns