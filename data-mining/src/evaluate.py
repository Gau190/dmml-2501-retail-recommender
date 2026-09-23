"""Experimental threshold selection for association rules (pipeline step b4)."""
from __future__ import annotations

from mlxtend.frequent_patterns import association_rules, fpgrowth
import pandas as pd

SUPPORT_LEVELS = (0.01, 0.02, 0.05)
CONFIDENCE_LEVELS = (0.20, 0.35, 0.50)
TARGET_MIN_RULES = 50
TARGET_MAX_RULES = 300


def rules_from_itemsets(itemsets: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
    if itemsets.empty:
        return pd.DataFrame()
    return association_rules(itemsets, metric="confidence", min_threshold=min_confidence)


def choose_threshold(encoded: pd.DataFrame) -> tuple[float, float, pd.DataFrame, str]:
    candidates: list[tuple[int, float, float, pd.DataFrame]] = []
    print("[b4] Rule-count experiment (all rule sizes):")
    print("  min_support  min_confidence  n_rules")
    for support in SUPPORT_LEVELS:
        itemsets = fpgrowth(encoded, min_support=support, use_colnames=True)
        for confidence in CONFIDENCE_LEVELS:
            rules = rules_from_itemsets(itemsets, confidence)
            count = len(rules)
            print(f"  {support:>11.2f}  {confidence:>14.2f}  {count:>7,}")
            # Prefer the strongest thresholds that retain a report-friendly volume.
            candidates.append((count, support, confidence, rules))
    suitable = [candidate for candidate in candidates if TARGET_MIN_RULES <= candidate[0] <= TARGET_MAX_RULES]
    if suitable:
        count, support, confidence, rules = sorted(suitable, key=lambda item: (-item[1], -item[2], item[0]))[0]
        reason = f"selected {count} rules, within the target range {TARGET_MIN_RULES}-{TARGET_MAX_RULES}, with the strongest tested support/confidence"
    else:
        count, support, confidence, rules = min(candidates, key=lambda item: abs(item[0] - (TARGET_MIN_RULES + TARGET_MAX_RULES) / 2))
        reason = f"no experiment produced {TARGET_MIN_RULES}-{TARGET_MAX_RULES} rules; selected closest tested result ({count} rules)"
    print(f"[b4] Final threshold: min_support={support:.2f}, min_confidence={confidence:.2f}; {reason}.")
    return support, confidence, rules, reason
