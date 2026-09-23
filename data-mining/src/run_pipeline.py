"""Run the Online Retail II association-mining pipeline end to end."""
from __future__ import annotations

from pathlib import Path

from download_data import ensure_raw_data
from evaluate import choose_threshold, rules_from_itemsets
from export_for_webapp import export_outputs
from mining import encode_transactions, mine_and_compare, prepare_mining_transactions
from preprocessing import clean_and_group

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    print("=== Online Retail II association-rule pipeline ===")
    raw_path = ensure_raw_data()
    clean, transactions, _ = clean_and_group(raw_path)
    mining_transactions, metadata = prepare_mining_transactions(transactions)
    if not mining_transactions:
        raise RuntimeError("No baskets with at least two TOP_N_ITEMS remain for mining.")
    print("[b3] TOP_N_ITEMS={top_n_items_cap}; mining {n_transactions_used_for_mining:,}/{n_transactions_total_clean:,} baskets ({coverage_pct_after_cap:.2f}% coverage).".format(**metadata))
    encoded = encode_transactions(mining_transactions)
    print(f"[b3] Encoded one-hot matrix: {encoded.shape[0]:,} transactions x {encoded.shape[1]:,} SKUs")
    support, confidence, _, reason = choose_threshold(encoded)
    print(f"[b3] Benchmarking Apriori and FP-Growth at final min_support={support:.2f} (three runs each)...")
    mining = mine_and_compare(encoded, support)
    if not mining["itemsets_equal"]:
        raise RuntimeError("Apriori and FP-Growth itemsets differ after 6-decimal support rounding; refusing export.")
    # The export source is specifically the benchmarked FP-Growth itemsets.
    final_rules = rules_from_itemsets(mining["fpgrowth_itemsets"], confidence)
    print("[b3] Itemsets match. Apriori={:,} ({:.4f}s), FP-Growth={:,} ({:.4f}s).".format(
        len(mining["apriori_itemsets"]), mining["apriori_runtime_sec"], len(mining["fpgrowth_itemsets"]), mining["fpgrowth_runtime_sec"]))
    metrics = export_outputs(clean, final_rules, metadata, mining, support, confidence, ROOT / "outputs")
    print("[b5] Atomic exports written: outputs/products.csv, outputs/rules.csv, outputs/metrics.json")
    print("=== Summary ===")
    print("transactions clean={n_transactions_total_clean:,}; used={n_transactions_used_for_mining:,}; rules total={n_rules_total:,}; exported 1->1={n_rules_1to1_exported:,}; itemsets_equal={itemsets_equal}".format(**metrics))
    print(f"threshold rationale: {reason}")


if __name__ == "__main__":
    main()
