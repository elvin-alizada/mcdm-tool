"""
Module: mcdm_io
==================
This module provides tools to configure categories, sub-categories, and
pairwise comparison matrices for Multi-Criteria Decision Making (MCDM) projects.

Main functionality:
- Generate a default CSV template with sample data for regions, categories,
  sub-categories, and placeholder values.
- Allow users to edit CSV to include real data, add new categories or sub-categories.
- Generate Excel files with pairwise comparison matrices for AHP methodology.
- Read back the edited CSV and Excel files into Python structures:
    * `categories` dict for hierarchical access
    * `weights` dict for pairwise matrices
    * `data` DataFrame ready for MCDM calculations

Usage:
------
from mcdm_tool.mcdm_io import cat_config

categories, weights, data = cat_config()
"""

import os
import pandas as pd
import numpy as np

def cat_config(csv_path=None):
    """
    Configure categories and subcategories for MCDM analysis.

    This function guides the user through creating and editing a CSV file
    with regional criteria and sub-criteria. It also generates pairwise
    comparison matrices for AHP, allowing users to adjust weights.

    Parameters
    ----------
    csv_path : str, optional
        Full path to the CSV file for configuration. If None, a default file
        is created at "~/Documents/mcdm_config.csv".

    Returns
    -------
    categories : dict
        Nested dictionary mapping Region -> Category -> List of Sub-categories.
    weights : dict
        Dictionary containing pairwise comparison matrices for categories
        and sub-categories.
    data : pandas.DataFrame
        Simplified DataFrame with Region, Category, Sub-category, Value,
        and Cost/Benefit type, ready for MCDM analysis.

    Notes
    -----
    - Region names must match exactly with GeoJSON shapefiles for correct visualization.
    - Users can add new categories or sub-categories; the hierarchical structure
      adapts automatically.
    - Placeholder values in the default CSV are examples; users should enter
      actual regional data.
    """

    # --- 1. Creating default CSV template ---
    if csv_path is None:
        csv_path = os.path.expanduser("~/Documents/mcdm_config.csv")

    default_data = [
        # 1. Infrastructure and Accessibility
        ["A", "Infrastructure and Accessibility", "Highways", "km", 5, "Cost"],
        ["A", "Infrastructure and Accessibility", "Railway", "km", 10, "Cost"],
        ["A", "Infrastructure and Accessibility", "Seaport", "km", 1, "Cost"],
        ["A", "Infrastructure and Accessibility", "Airport", "km", 15, "Cost"],
        ["A", "Infrastructure and Accessibility", "Electricity", "MW power", 10, "Benefit"],
        ["A", "Infrastructure and Accessibility", "Gas Supply", "Max Volume (m³/year)", 500000, "Benefit"],
        ["A", "Infrastructure and Accessibility", "Optical internet", "Yes-1/No-0", 1, "Benefit"],
        # 2. Market Proximity and Trade
        ["A", "Market Proximity and Trade", "Distance to Border Crossing Points", "km", 15, "Cost"],
        ["A", "Market Proximity and Trade", "Distance to Main Export Markets", "hours", 2, "Cost"],
        # 3. Labor Market
        ["A", "Labor Market", "Average Salary", "USD/AZN", 600, "Benefit"],
        ["A", "Labor Market", "Workforce Density", "thousand people", 50, "Benefit"],
        ["A", "Labor Market", "Education Level (secondary+tertiary)", "%", 55, "Benefit"],
        ["A", "Labor Market", "Proximity to Vocational/Universities", "km", 15, "Cost"],
        # 4. Land and Property
        ["A", "Land and Property", "Industrial Land Area & Price", "ha / AZN/ha", 20, "Benefit"],
        ["A", "Land and Property", "Existing Industrial Parks", "binary + capacity", 1, "Benefit"],
        ["A", "Land and Property", "Earthquake/Flood/Land Risk Index", "index", 3, "Cost"],
        # 5. Economic & Institutional
        ["A", "Economic & Institutional", "Local Government Support", "score", 7, "Benefit"],
        ["A", "Economic & Institutional", "Tax/Custom Incentives", "policy score", 6, "Benefit"],
        ["A", "Economic & Institutional", "Business Establishment Time/Cost", "days / USD", 30, "Cost"],
        ["A", "Economic & Institutional", "Corruption/Perception Index", "index", 5, "Cost"],
        # 6 Socio-Economic Effects
        ["A", "Socio-Economic Effects", "Unemployment Level", "%", 7, "Cost"],
        ["A", "Socio-Economic Effects", "Population Density", "people/km²", 120, "Benefit"],
    ]

    # Convert to DataFrame
    df = pd.DataFrame(default_data,
                      columns=["Region", "Category", "Sub-category", "Unit", "Value", "Cost/Benefit"])
    df.to_csv(csv_path, index=False)
    print(f"\nDefault CSV file created: {csv_path}")

    # Open CSV for user to edit
    try:
        os.startfile(csv_path)
        print("CSV opened in Excel. Edit values and press Enter when done...")
    except Exception:
        print(f"Please open CSV manually: {csv_path}")

    input("Press ENTER after adjusting CSV...")

    # 2. Reading the CSV back
    try:
        df_final = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df_final = pd.read_csv(csv_path, encoding="cp1254")

    # 3. Create hierarchical categories structure
    categories = {}
    for _, row in df_final.iterrows():
        reg = row["Region"]
        cat = row["Category"]
        sub = row["Sub-category"]
        categories.setdefault(reg, {}).setdefault(cat, []).append(sub)

    # 4. Generate pairwise comparison matrices
    def create_pairwise_matrix(items):
        n = len(items)
        return pd.DataFrame(np.eye(n), index=items, columns=items)

    excel_path = os.path.expanduser("~/Documents/mcdm_weights.xlsx")
    with pd.ExcelWriter(excel_path) as writer:
        # General categories (only once)
        all_cats = sorted(set(df_final["Category"]))
        create_pairwise_matrix(all_cats).to_excel(writer, sheet_name="General")

        # Sub-categories
        for cat in all_cats:
            subcats = df_final[df_final["Category"] == cat]["Sub-category"].unique().tolist()
            if len(subcats) > 1:
                create_pairwise_matrix(subcats).to_excel(writer, sheet_name=cat[:25])

    print(f"\nPairwise matrices exported to Excel: {excel_path}")
    input("Press ENTER after adjusting the weights...")

    # 5. Reading user-modified weights
    weights = {}
    xls = pd.ExcelFile(excel_path)
    for sheet in xls.sheet_names:
        df_sheet = pd.read_excel(xls, sheet_name=sheet, index_col=0)
        weights[sheet] = df_sheet.to_dict()

    # 6. Prepare simplified data for MCDM
    data = df_final.drop(columns=["Unit"])  # Unit not used in calculations

    print("\nFinal data is ready.\n")
    return categories, weights, data
