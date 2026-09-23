"""Atomic RFC4180 exports for the web application (pipeline step b5)."""
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _atomic_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    os.replace(temporary, path)


def _atomic_json(path: Path, payload: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)


def export_outputs(clean: pd.DataFrame, rules: pd.DataFrame, metadata: dict, mining: dict, min_support: float, min_confidence: float, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    product_stats = clean.groupby("StockCode", sort=True).agg(
        unit_price=("UnitPrice", "median"),
        description=("Description", lambda values: values.value_counts().index[0]),
    ).reset_index()
    # Keep the complete cleaned catalog; rules will naturally use only the TOP-N mining subset.
    products = product_stats.copy()
    products = products.sort_values("StockCode")
    _atomic_csv(output_dir / "products.csv", ["sku", "description", "unit_price", "category"], [
        [row.StockCode, row.description, f"{float(row.unit_price):.2f}", "General"] for row in products.itertuples(index=False)
    ])
    valid_skus = set(products["StockCode"])
    export_rules = rules.copy()
    if export_rules.empty:
        export_rules = pd.DataFrame(columns=["antecedents", "consequents", "support", "confidence", "lift"])
    export_rules = export_rules[(export_rules["antecedents"].map(len) == 1) & (export_rules["consequents"].map(len) == 1)].copy()
    export_rules["antecedent_sku"] = export_rules["antecedents"].map(lambda items: next(iter(items)))
    export_rules["consequent_sku"] = export_rules["consequents"].map(lambda items: next(iter(items)))
    export_rules = export_rules[(export_rules["antecedent_sku"] != export_rules["consequent_sku"]) & export_rules["antecedent_sku"].isin(valid_skus) & export_rules["consequent_sku"].isin(valid_skus)]
    export_rules = export_rules.drop_duplicates(["antecedent_sku", "consequent_sku"]).sort_values(["confidence", "lift"], ascending=False)
    _atomic_csv(output_dir / "rules.csv", ["antecedent_sku", "consequent_sku", "support", "confidence", "lift"], [
        [row.antecedent_sku, row.consequent_sku, f"{float(row.support):.6f}", f"{float(row.confidence):.6f}", f"{float(row.lift):.6f}"]
        for row in export_rules.itertuples(index=False)
    ])
    descriptions = dict(zip(products["StockCode"], products["description"]))
    preview = [{"antecedent_sku": row.antecedent_sku, "consequent_sku": row.consequent_sku,
                "antecedent_desc": descriptions[row.antecedent_sku], "consequent_desc": descriptions[row.consequent_sku],
                "support": round(float(row.support), 6), "confidence": round(float(row.confidence), 6), "lift": round(float(row.lift), 6)}
               for row in export_rules.head(10).itertuples(index=False)]
    metrics = {"schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
               **{key: metadata[key] for key in ("n_transactions_total_clean", "n_transactions_used_for_mining", "n_unique_skus_total", "n_skus_used_for_mining", "top_n_items_cap", "coverage_pct_after_cap")},
               "min_support": min_support, "min_confidence": min_confidence,
               "apriori": {"n_itemsets": len(mining["apriori_itemsets"]), "runtime_sec": round(mining["apriori_runtime_sec"], 6)},
               "fpgrowth": {"n_itemsets": len(mining["fpgrowth_itemsets"]), "runtime_sec": round(mining["fpgrowth_runtime_sec"], 6)},
               "itemsets_equal": bool(mining["itemsets_equal"]), "n_rules_total": len(rules),
               "n_rules_1to1_exported": len(export_rules), "top_rules_preview": preview}
    _atomic_json(output_dir / "metrics.json", metrics)
    return metrics
