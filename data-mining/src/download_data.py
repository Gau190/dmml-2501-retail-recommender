"""Download and cache the UCI Online Retail II data set (id=502)."""
from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "online_retail_ii.csv"
UCI_XLSX_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip() for column in frame.columns]
    required = {"Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "UnitPrice"}
    if "Price" in frame.columns and "UnitPrice" not in frame.columns:
        frame = frame.rename(columns={"Price": "UnitPrice"})
    missing = {"Invoice", "StockCode", "Description", "Quantity", "UnitPrice"} - set(frame.columns)
    if missing:
        raise ValueError(f"UCI data is missing required columns: {sorted(missing)}")
    return frame


def _read_excel_bytes(payload: bytes) -> pd.DataFrame:
    if payload[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            excel_names = [name for name in archive.namelist() if name.lower().endswith((".xlsx", ".xls"))]
            if not excel_names:
                raise ValueError("Official UCI archive contains no Excel workbook")
            payload = archive.read(excel_names[0])
    sheets = pd.read_excel(io.BytesIO(payload), sheet_name=None, engine="openpyxl")
    return _normalise_columns(pd.concat(sheets.values(), ignore_index=True))


def _download_with_ucimlrepo() -> pd.DataFrame:
    from ucimlrepo import fetch_ucirepo

    dataset = fetch_ucirepo(id=502)
    original = getattr(dataset.data, "original", None)
    if original is None or original.empty:
        original = pd.concat([dataset.data.features, dataset.data.targets], axis=1)
    return _normalise_columns(original)


def _download_official_archive() -> pd.DataFrame:
    with urllib.request.urlopen(UCI_XLSX_URL, timeout=120) as response:
        return _read_excel_bytes(response.read())


def ensure_raw_data(force: bool = False) -> Path:
    """Return the cached CSV, downloading it only when it does not exist."""
    if RAW_PATH.exists() and RAW_PATH.stat().st_size > 0 and not force:
        print(f"[b1] Reusing cached raw data: {RAW_PATH} ({RAW_PATH.stat().st_size:,} bytes)")
        return RAW_PATH
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    for label, loader in (("ucimlrepo", _download_with_ucimlrepo), ("official UCI archive", _download_official_archive)):
        try:
            print(f"[b1] Downloading Online Retail II through {label}...")
            frame = loader()
            frame.to_csv(RAW_PATH, index=False, encoding="utf-8")
            print(f"[b1] Cached {len(frame):,} rows to {RAW_PATH}")
            return RAW_PATH
        except Exception as exc:  # the fallback is intentional for network/package failures
            errors.append(f"{label}: {type(exc).__name__}: {exc}")
            print(f"[b1] {label} failed; trying fallback if available: {exc}", file=sys.stderr)
    raise RuntimeError("Could not download Online Retail II; no synthetic data was created.\n" + "\n".join(errors))


if __name__ == "__main__":
    ensure_raw_data()
