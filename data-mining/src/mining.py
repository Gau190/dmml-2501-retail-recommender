"""TOP-N encoding plus Apriori / FP-Growth comparison (pipeline step b3)."""
from __future__ import annotations

from time import perf_counter

import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

TOP_N_ITEMS = 300


def prepare_mining_transactions(transactions: pd.DataFrame, top_n: int = TOP_N_ITEMS) -> tuple[list[list[str]], dict[str, float | int]]:
    counts: dict[str, int] = {}
    for basket in transactions["items"]:
        for sku in basket:
            counts[sku] = counts.get(sku, 0) + 1
    top_skus = {sku for sku, _ in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:top_n]}
    mining_transactions = [sorted(set(basket) & top_skus) for basket in transactions["items"]]
    mining_transactions = [basket for basket in mining_transactions if len(basket) >= 2]
    total = len(transactions)
    metadata = {
        "n_transactions_total_clean": total, "n_transactions_used_for_mining": len(mining_transactions),
        "n_unique_skus_total": len(counts), "n_skus_used_for_mining": len(top_skus), "top_n_items_cap": top_n,
        "coverage_pct_after_cap": round((len(mining_transactions) / total * 100) if total else 0.0, 6),
        "mining_skus": sorted(top_skus),
    }
    return mining_transactions, metadata


def encode_transactions(transactions: list[list[str]]) -> pd.DataFrame:
    encoder = TransactionEncoder()
    encoded = encoder.fit(transactions).transform(transactions)
    return pd.DataFrame(encoded, columns=encoder.columns_)


def _benchmark(method, encoded: pd.DataFrame, min_support: float) -> tuple[pd.DataFrame, float]:
    results: list[tuple[pd.DataFrame, float]] = []
    for _ in range(3):
        start = perf_counter()
        itemsets = method(encoded, min_support=min_support, use_colnames=True)
        results.append((itemsets, perf_counter() - start))
    return results[0][0], min(runtime for _, runtime in results)


def _signature(itemsets: pd.DataFrame) -> set[tuple[frozenset[str], float]]:
    return {(frozenset(items), round(float(support), 6)) for support, items in itemsets[["support", "itemsets"]].itertuples(index=False, name=None)}


def mine_and_compare(encoded: pd.DataFrame, min_support: float) -> dict:
    apriori_sets, apriori_runtime = _benchmark(apriori, encoded, min_support)
    fpgrowth_sets, fpgrowth_runtime = _benchmark(fpgrowth, encoded, min_support)
    equal = _signature(apriori_sets) == _signature(fpgrowth_sets)
    return {"apriori_itemsets": apriori_sets, "fpgrowth_itemsets": fpgrowth_sets, "itemsets_equal": equal,
            "apriori_runtime_sec": apriori_runtime, "fpgrowth_runtime_sec": fpgrowth_runtime}
