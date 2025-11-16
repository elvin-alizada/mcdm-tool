# examples/quick_start_full.py
from mcdm.mcdm_io import cat_config
from mcdm.normalisation import min_max_normalize
from mcdm.ahp import ahp_weights
from mcdm.topsis import topsis
from mcdm.visualisation_static import plot_country_results_static
from mcdm.visualisation_interactive import plot_country_results_interactive
from mcdm.sensitivity import sensitivity_analysis
import os
import webbrowser

# 1-Data collection
categories, weights_dict, data = cat_config()

# 2-Normalisation
norm_data = min_max_normalize(data)

# 3-AHP weights
final_weights = ahp_weights(weights_dict)

# 4-TOPSIS rsult
scores_df = topsis(norm_data, final_weights)
scores_df = scores_df.rename(columns={"TOPSIS Score": "Score"})

# 5-Static visualisation
plot_country_results_static("AZE", scores_df, save_path="static_map.png")

# 6-Interactive visualisation
#map_path = os.path.abspath("interactive_map.html")
#plot_country_results_interactive("AZE", scores_df, save_path=map_path)
#webbrowser.open(f"file://{map_path}")

# 7-Perform sensitivity analysis

# Default ±10% change
base_scores, sensitivity_results = sensitivity_analysis(norm_data, final_weights, delta=0.1)

# Optional: convert one of the sensitivity results to DataFrame for inspection
# Example: first category_sub variation
first_key = list(sensitivity_results.keys())[0]
sensitivity_example_df = sensitivity_results[first_key]

print(f"Base TOPSIS scores:\n{base_scores.head()}")
print(f"Sensitivity example ({first_key}):\n{sensitivity_example_df.head()}")
