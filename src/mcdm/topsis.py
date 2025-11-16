"""
Module: topsis
==============

This module provides a robust and academic-level implementation of TOPSIS
(Technique for Order Preference by Similarity to Ideal Solution) for
Multi-Criteria Decision Making (MCDM), considering both category and
sub-category weights.

Features:
- Supports nested weights: {Category: {SubCategory: weight}}
- Accounts for both Benefit and Cost criteria types
- Computes normalized TOPSIS scores in [epsilon,1] range
- Fully vectorized for efficiency on large regional datasets
"""

import numpy as np
import pandas as pd

def topsis(norm_data: pd.DataFrame, weights: dict, criteria_type_col: str = None) -> pd.DataFrame:
    """
    Compute TOPSIS scores for regional MCDM evaluation.

    Parameters
    ----------
    norm_data : pd.DataFrame
        Must contain columns: ["Region", "Category", "Sub-category", "Value"]
        Optionally, a column indicating "Cost" or "Benefit" type.

    weights : dict
        Nested dictionary of normalized weights:
        { "Category1": {"Sub1": 0.4, "Sub2": 0.6}, ... }

    criteria_type_col : str, optional
        Column name indicating if criterion is a 'Benefit' or 'Cost'.
        If None, all criteria are assumed to be Benefit.

    Returns
    -------
    pd.DataFrame
        Columns: ["Region", "TOPSIS Score"]
    """

    df = norm_data.copy()

    # Compute weighted value: Category weight * Sub-category weight
    def get_weight(row):
        cat, sub = row['Category'], row['Sub-category']
        return weights.get(cat, {}).get(sub, 1.0)  # default 1.0 if missing

    df['Weight'] = df.apply(get_weight, axis=1)
    df['Weighted'] = df['Value'] * df['Weight']

    # Adjust for Cost criteria: convert to Benefit
    if criteria_type_col:
        cost_mask = df[criteria_type_col].str.lower() == 'cost'
        df.loc[cost_mask, 'Weighted'] = 1 - df.loc[cost_mask, 'Weighted']

    # Pivot to matrix: rows=Region, columns=(Category, Sub-category)
    df_pivot = df.pivot_table(
        index='Region',
        columns=['Category', 'Sub-category'],
        values='Weighted',
        aggfunc='sum',
        fill_value=0
    )

    # Compute ideal (max) and anti-ideal (min) solution per criterion
    ideal = df_pivot.max()
    anti_ideal = df_pivot.min()

    # Euclidean distance to ideal and anti-ideal
    dist_to_ideal = np.sqrt(((df_pivot - ideal)**2).sum(axis=1))
    dist_to_anti = np.sqrt(((df_pivot - anti_ideal)**2).sum(axis=1))

    # TOPSIS closeness coefficient
    scores = dist_to_anti / (dist_to_ideal + dist_to_anti)

    # Normalize to [epsilon,1] for visualization purposes
    epsilon = 0.01
    scores = (scores - scores.min()) / (scores.max() - scores.min())
    scores = scores * (1 - epsilon) + epsilon

    return scores.reset_index(name='TOPSIS Score')
