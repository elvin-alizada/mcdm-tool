"""
Module: sensitivity
==================

This module provides functions to perform **sensitivity analysis** for
Multi-Criteria Decision Making (MCDM) results using TOPSIS.

Main Functionality:
- Evaluate how changes in AHP weights affect TOPSIS scores.
- Perform ±delta variations for each category or sub-category.
- Return a structured dictionary with results for comparison.

Usage:
------
from mcdm_tool.sensitivity import sensitivity_analysis

# norm_data: DataFrame with columns ["Region", "Category", "Sub-category", "Value"]
# weights: nested dict from ahp_weights()
base_scores, results = sensitivity_analysis(norm_data, weights, delta=0.1)
"""

import copy
import pandas as pd
from mcdm.topsis import topsis

def sensitivity_analysis(norm_data: pd.DataFrame, weights: dict, delta: float = 0.1):
    """
    Perform sensitivity analysis by varying AHP weights ±delta.

    Parameters
    ----------
    norm_data : pd.DataFrame
        Normalized data with columns ["Region", "Category", "Sub-category", "Value"].
    weights : dict
        Nested dictionary of normalized weights:
        { "Category1": {"Sub1": 0.4, "Sub2": 0.6}, ... }
    delta : float, optional
        Relative change to apply to each weight (default 0.1 = ±10%).

    Returns
    -------
    base_scores : pd.DataFrame
        TOPSIS scores with original weights.
    results : dict
        Dictionary of TOPSIS scores for each weight perturbation.
        Format: {"Category_Sub_plus": DataFrame, "Category_Sub_minus": DataFrame, ...}
    """
    # Compute base TOPSIS scores
    base_scores = topsis(norm_data, weights)

    results = {}

    # Iterate over categories and sub-categories
    for category, sub_dict in weights.items():
        for sub_category, orig_weight in sub_dict.items():
            # Increase weight by delta
            weights_plus = copy.deepcopy(weights)
            weights_plus[category][sub_category] = orig_weight * (1 + delta)
            # Normalize weights within the category to sum=1
            total = sum(weights_plus[category].values())
            for key in weights_plus[category]:
                weights_plus[category][key] /= total
            scores_plus = topsis(norm_data, weights_plus)
            results[f"{category}_{sub_category}_plus"] = scores_plus

            # Decrease weight by delta
            weights_minus = copy.deepcopy(weights)
            weights_minus[category][sub_category] = orig_weight * (1 - delta)
            # Normalize weights within the category to sum=1
            total = sum(weights_minus[category].values())
            for key in weights_minus[category]:
                weights_minus[category][key] /= total
            scores_minus = topsis(norm_data, weights_minus)
            results[f"{category}_{sub_category}_minus"] = scores_minus

    return base_scores, results
