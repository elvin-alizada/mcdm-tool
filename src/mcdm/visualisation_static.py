"""
Module: visualisation_static
============================

Static choropleth visualisation for MCDM results on a country's administrative map.
"""

import os
import textwrap
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np

def plot_country_results_static(country: str, scores_df: pd.DataFrame, bins=5, cmap="YlGn", save_path=None):
    """
    Generate a static choropleth map with MCDM scores and ranking table.

    Parameters
    ----------
    country : str
        ISO3 code matching GeoJSON file in data/shapefiles.
    scores_df : pd.DataFrame
        Must contain at least 'Region' and 'Score' columns. Optional 'Rank'.
    bins : int
        Number of color bins for choropleth.
    cmap : str
        Matplotlib colormap name.
    save_path : str, optional
        File path to save the figure. If None, figure is displayed.

    Returns
    -------
    None
    """
    # Shapefile path
    shapefile_path = os.path.join(
        os.path.dirname(__file__), "data", "shapefiles", f"{country}.geojson"
    )
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"{country} shapefile not found: {shapefile_path}")

    # Read shapefile
    gdf = gpd.read_file(shapefile_path)

    # Merge with scores
    merged = gdf.merge(scores_df, how="left", left_on="shapeName", right_on="Region")

    # Warnings
    missing_in_map = set(scores_df["Region"]) - set(merged["shapeName"])
    if missing_in_map:
        print("!!! The following regions could not be matched in the shapefile:", missing_in_map)

    empty_geom = merged[merged.geometry.is_empty]["shapeName"].tolist()
    if empty_geom:
        print("!!! The following regions contain empty or invalid geometries:", empty_geom)

    # Separate regions with and without valid scores
    valid_mask = merged["Score"].notna()

    # If Rank does not exist – compute it only for regions with valid scores
    if "Rank" not in merged.columns:
        merged["Rank"] = np.nan
        merged.loc[valid_mask, "Rank"] = (
            merged.loc[valid_mask, "Score"]
            .rank(ascending=False, method="min")
        )

    # Valid scores for scale calculation
    score_values = merged.loc[valid_mask, "Score"].values
    if len(score_values) == 0:
        raise ValueError("No valid 'Score' values found for any region.")

    if len(np.unique(score_values)) <= bins:
        bins = len(np.unique(score_values))
    color_bins = np.linspace(score_values.min(), score_values.max(), bins + 1)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Background map for regions without score values
    gdf.plot(
        ax=ax,
        color="#f0f0f0",  # light gray background
        edgecolor="gray",
        linewidth=0.5,
    )

    # Choropleth for regions with numeric scores
    merged.plot(
        column="Score",
        cmap=cmap,
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        scheme="user_defined",
        classification_kwds={"bins": color_bins},
        legend=True,
        legend_kwds={"title": "TOPSIS Score"},
    )

    # Annotating only regions that have a valid rank
    for _, row in merged.iterrows():
        if row.geometry.is_empty or pd.isna(row["Rank"]):
            continue
        x, y = row.geometry.centroid.coords[0]
        ax.text(
            x, y,
            str(int(row["Rank"])),
            fontsize=9,
            fontweight="bold",
            ha="center",
            va="center",
        )

    # Optional table for additional columns
    extra_cols = [c for c in scores_df.columns if c not in ["Region", "Score", "Rank"]]
    if extra_cols:
        table_data = merged.loc[valid_mask, ["Region", "Score"] + extra_cols].copy()
        for col in ["Region"] + extra_cols:
            table_data[col] = table_data[col].apply(lambda x: textwrap.fill(str(x), 15))

        table_ax = fig.add_axes([0.05, -0.25, 0.9, 0.2])
        table_ax.axis("off")
        table_ax.table(
            cellText=table_data.values,
            colLabels=table_data.columns,
            cellLoc="center",
            loc="center",
        )

    ax.axis("off")
    ax.set_title(f"{country} - MCDM TOPSIS Scores", fontdict={"fontsize": 16}, pad=20)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)
        print(f"Static map saved to {save_path}")
    else:
        plt.show()
