"""Cleaning and basket construction for Online Retail II (pipeline step b2)."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

NON_PRODUCT_CODES = {
    "POST", "D", "DOT", "M", "MANUAL", "BANK CHARGES", "PADS", "AMAZONFEE", "C2",
    "CRUK", "S", "ADJUST", "ADJUST2", "TEST001", "TEST002", "SAMPLES", "GIFT",
}
GIFT_CARD_PATTERN = re.compile(r"^gift_?0*\d+", re.IGNORECASE)


def clean_and_group(raw_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    frame = pd.read_csv(raw_path, low_memory=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    if "Price" in frame.columns and "UnitPrice" not in frame.columns:
        frame = frame.rename(columns={"Price": "UnitPrice"})
    # String dtype preserves values such as stock code 000123 and makes cancellation checks reliable.
    frame["Invoice"] = frame["Invoice"].astype("string").str.strip()
    frame["StockCode"] = frame["StockCode"].astype("string").str.strip().str.upper()
    frame["Description"] = frame["Description"].astype("string").str.strip()
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="coerce")
    frame["UnitPrice"] = pd.to_numeric(frame["UnitPrice"], errors="coerce")
    initial_rows = len(frame)
    cancellation = frame["Invoice"].str.startswith("C", na=False)
    invalid = (
        frame["Invoice"].isna() | frame["Invoice"].eq("") | frame["StockCode"].isna() |
        frame["StockCode"].eq("") | frame["Description"].isna() | frame["Description"].eq("") |
        frame["Quantity"].le(0) | frame["UnitPrice"].le(0)
    )
    non_product = frame["StockCode"].isin(NON_PRODUCT_CODES) | frame["StockCode"].str.match(GIFT_CARD_PATTERN, na=False)
    clean = frame.loc[~cancellation & ~invalid & ~non_product].copy()
    transactions = (
        clean.groupby("Invoice", sort=False)["StockCode"]
        .agg(lambda values: sorted(set(values.dropna())))
        .reset_index(name="items")
    )
    stats = {
        "rows_initial": initial_rows, "rows_cancellations_removed": int(cancellation.sum()),
        "rows_invalid_removed": int((~cancellation & invalid).sum()),
        "rows_non_product_removed": int((~cancellation & ~invalid & non_product).sum()),
        "rows_clean": len(clean), "n_transactions_total_clean": len(transactions),
        "n_unique_skus_total": int(clean["StockCode"].nunique()),
    }
    print("[b2] Cleaning rows:", stats)
    print(f"[b2] Built {len(transactions):,} unique invoice baskets from {len(clean):,} valid rows")
    return clean, transactions, stats
