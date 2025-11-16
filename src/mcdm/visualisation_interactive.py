"""
Module: visualisation_interactive
===============================

This module provides functions for creating interactive choropleth maps
for Multi-Criteria Decision Making (MCDM) results using Folium.

Main Functionality:
- Visualize region-level MCDM scores on an interactive map.
- Display Rank, Score, and additional information in tooltip on hover.
- Highlight missing regions or empty geometries for debugging.

Usage:
------
from mcdm_tool.visualisation_interactive import plot_country_results_interactive

# scores_df should contain at least columns: Region, Score, Rank
plot_country_results_interactive("AZE", scores_df, save_path="interactive_map.html")

Notes:
------
- Ensure the relevant GeoJSON file exists in data/shapefiles/<country>.geojson
  before calling the function.
- Tooltip shows Rank, Score, and any additional columns in scores_df.
- Regions not found in GeoJSON are printed as warnings.
"""

import os
import geopandas as gpd
import folium
from branca.colormap import linear

def plot_country_results_interactive(country: str, scores_df, save_path=None):
    """
    Create an interactive Folium map of a country with MCDM scores.

    Parameters
    ----------
    country : str
        ISO3 code or country identifier matching the GeoJSON filename.
    scores_df : pd.DataFrame
        DataFrame containing at least columns: Region, Score, Rank.
        Additional columns will be displayed in the tooltip.
    save_path : str, optional
        File path to save the interactive map as HTML. If None, returns
        the Folium map object.

    Returns
    -------
    folium.Map
        Interactive map object (if save_path is None).

    Notes
    -----
    - GeoJSON file must exist at data/shapefiles/<country>.geojson
    - Regions in scores_df but not in the shapefile are printed as warnings.
    """
    shapefile_path = os.path.join(
        os.path.dirname(__file__), "data", "shapefiles", f"{country}.geojson"
    )
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"{country} shapefile tapılmadı. Zəhmət olmasa {shapefile_path} yaradın.")

    # Read GeoJSON
    gdf = gpd.read_file(shapefile_path)

    # Merge with scores_df
    merged = gdf.merge(scores_df, how="left", left_on="shapeName", right_on="Region")

    # Missing regions in shapefile
    missing_in_map = set(scores_df["Region"]) - set(merged["shapeName"])
    if missing_in_map:
        print("!!! The following regions could not be matched in the shapefile:", missing_in_map)

    # Regions with empty geometry
    empty_geom = merged[merged.geometry.is_empty]["shapeName"].tolist()
    if empty_geom:
        print("!!! The following regions contain empty or invalid geometries:", empty_geom)

    # Fill NaNs with 0
    merged['Score'] = merged['Score'].fillna(0)

    # Compute centroid for map center
    merged_proj = merged.to_crs(epsg=3857)
    centroids = merged_proj.geometry.centroid
    centroids_latlon = centroids.to_crs(epsg=4326)
    center = [centroids_latlon.y.mean(), centroids_latlon.x.mean()]

    # Color scale
    colormap = linear.YlGn_09.scale(merged['Score'].min(), merged['Score'].max())
    colormap.caption = f"{country} - Scores"

    # Folium map
    m = folium.Map(location=center, zoom_start=7)

    # Prepare tooltip fields and aliases
    tooltip_fields = ['shapeName', 'Score']
    aliases = ['Region:', 'Score:']
    extra_columns = [col for col in scores_df.columns if col not in ['Region', 'Score']]
    tooltip_fields.extend(extra_columns)
    aliases.extend([f"{col}:" for col in extra_columns])

    # Add regions to map
    folium.GeoJson(
        merged,
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['Score']) if feature['properties']['Score'] > 0 else 'lightgrey',
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=aliases,
            localize=True
        )
    ).add_to(m)

    # Add colormap
    colormap.add_to(m)

    if save_path:
        m.save(save_path)
        print(f"Interactive map saved to {save_path}")
    else:
        return m
