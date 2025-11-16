# normalisation.py
import pandas as pd
import numpy as np

def min_max_normalize(data: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize values for MCDM (Cost/Benefit aware).

    Parameters
    ----------
    data : pd.DataFrame
        Must contain columns: ["Region", "Category", "Sub-category", "Value", "Cost/Benefit"]

    Returns
    -------
    pd.DataFrame
        Normalized values in "Value" column, range [0,1]
    """
    norm_data = data.copy()
    norm_data["Value"] = (
        norm_data["Value"]
        .astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="raise")
    )

    for cat in norm_data["Category"].unique():
        for sub in norm_data[norm_data["Category"] == cat]["Sub-category"].unique():
            mask = (norm_data["Category"] == cat) & (norm_data["Sub-category"] == sub)
            values = norm_data.loc[mask, "Value"]
            ctype = norm_data.loc[mask, "Cost/Benefit"].iloc[0]

            if values.max() == values.min():
                # bütün dəyərlər eyni → 1.0
                norm_data.loc[mask, "Value"] = 1.0
            elif ctype.lower() == "cost":
                # Cost: az daha yaxşı → ters çevirmək
                norm_data.loc[mask, "Value"] = (values.max() - values) / (values.max() - values.min())
            else:
                # Benefit: artmaq daha yaxşı
                norm_data.loc[mask, "Value"] = (values - values.min()) / (values.max() - values.min())

    return norm_data
