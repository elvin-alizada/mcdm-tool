# examples/quick_start_minimal.py
from mcdm.mcdm_io import cat_config
from mcdm.normalisation import min_max_normalize
from mcdm.ahp import ahp_weights
from mcdm.topsis import topsis
import pandas as pd

# 1-Load configuration (categories, weight matrices, input data)
categories, weights_dict, data = cat_config()

# 2-Normalize data
norm_data = min_max_normalize(data)

# 3-Compute final weights using AHP
final_weights = ahp_weights(weights_dict)

# 4-Apply TOPSIS and visualise results
scores_df = topsis(norm_data, final_weights)
scores_df = scores_df.rename(columns={"TOPSIS Score": "Score"})

import matplotlib.pyplot as plt

# Assume scores_df has columns: ["Region", "Score"] (or after renaming from "TOPSIS Score")
results = scores_df.sort_values("Score", ascending=False).reset_index(drop=True)
results["Score"] = results["Score"].round(3)
n_rows = len(results)
fig_height = 0.4 * n_rows + 1
fig, ax = plt.subplots(figsize=(8, fig_height))
ax.axis("off")
table = ax.table(
    cellText=results.values,
    colLabels=results.columns,
    cellLoc="center",
    loc="center",
)

for (row, col), cell in table.get_celld().items():
    if row == 0:  # header row
        cell.set_text_props(weight="bold")

# Control font size and scaling
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.2)

fig.tight_layout()
fig.savefig("topsis_results.png", dpi=300, bbox_inches="tight")
print("Saved TOPSIS ranking table to topsis_results.png")

# 5-Print sorted results
print("\nTOPSIS Scores (ranked):")
print(scores_df.sort_values("Score", ascending=False).reset_index(drop=True))
