# Online Retail II association mining

This pipeline downloads the UCI Online Retail II data set, cleans baskets, caps mining to the 300 most frequent SKUs, compares Apriori with FP-Growth, chooses an experimental threshold, and writes webapp-ready CSV files atomically.

## Setup

From this directory, create an isolated environment and install dependencies:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python src/run_pipeline.py
```

The first run downloads and caches `data/raw/online_retail_ii.csv`; later runs reuse it. Outputs are `outputs/products.csv`, `outputs/rules.csv`, and `outputs/metrics.json`. The pipeline refuses to export if Apriori and FP-Growth do not produce identical frequent itemsets (after support rounding to six decimal places).
