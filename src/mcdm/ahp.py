"""
Module: ahp
===========

This module provides functions to calculate normalized weights for Multi-Criteria
Decision Making (MCDM) using the Analytic Hierarchy Process (AHP) methodology.

Main Functionality:
- Compute normalized weights from pairwise comparison matrices provided in dictionary form.
- Implements Saaty's geometric mean method for deriving priority vectors.
- Outputs normalized weights suitable for use in AHP or other MCDM methods like TOPSIS.

Usage:
------
from mcdm_tool.ahp import ahp_weights

# weights_dict is obtained from mcdm_io.cat_config output
normalized_weights = ahp_weights(weights_dict)
"""

# mcdm/ahp.py
import numpy as np
import pandas as pd


def ahp_weights(weights_dict: dict) -> dict:
    """
    Calculate normalized AHP weights for each category/sub-category
    using Saaty's geometric mean method.

    Parameters
    ----------
    weights_dict : dict
        Dictionary of pairwise comparison matrices (from Excel or cat_config).

    Returns
    -------
    final_weights : dict
        Dictionary with normalized weights.
        Format:
        { "Category1": {"Sub1": 0.4, "Sub2": 0.6}, ... }

    Notes
    -----
    - Uses geometric mean method:
        w_i = (Π_j a_ij)^(1/n), then normalize sum(w_i) = 1
    - Checks for reciprocal consistency and square matrix.
    """
    final_weights = {}

    for sheet_name, matrix in weights_dict.items():
        # Convert to DataFrame if dict
        df = pd.DataFrame(matrix)

        # Check if square
        if df.shape[0] != df.shape[1]:
            raise ValueError(f"AHP matrix '{sheet_name}' is not square: {df.shape}")

        # Ensure indices match columns
        if not all(df.index == df.columns):
            df.index = df.columns

        arr = df.values.astype(float)

        # Optional: check reciprocity
        if not np.allclose(arr, 1 / arr.T, atol=1e-2):
            print(f"⚠️ Warning: Matrix '{sheet_name}' may not be fully reciprocal.")

        # Geometric mean method
        geom_means = np.prod(arr, axis=1) ** (1 / arr.shape[0])
        norm_weights = geom_means / np.sum(geom_means)

        # Store as dict
        final_weights[sheet_name] = dict(zip(df.index, norm_weights))

    return final_weights

