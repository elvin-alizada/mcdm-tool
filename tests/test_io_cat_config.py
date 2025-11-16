import os
import pytest
from mcdm.mcdm_io import cat_config


def test_cat_config(tmp_path):
    # --- 1️⃣ Müvəqqəti CSV path-i ---
    csv_path = tmp_path / "mcdm_config.csv"

    # --- 2️⃣ Funksiyanı çağır ---
    categories, weights = cat_config(csv_path=str(csv_path))

    # --- 3️⃣ Check basic structure ---
    assert isinstance(categories, dict)
    assert isinstance(weights, dict)

    # Region A və ümumi kateqoriya yoxla
    assert "A" in categories
    assert len(categories["A"]) > 0

    # Hər region üçün alt-kateqoriyalar
    for cat, subcats in categories["A"].items():
        assert isinstance(subcats, list)
        assert len(subcats) > 0

    # Weights check
    for sheet, rows in weights.items():
        for row, cols in rows.items():
            # Hər satırın toplamı təxminən 1 olmalıdır (normalize)
            total = sum(cols.values())
            assert abs(total - 1.0) < 1e-6
