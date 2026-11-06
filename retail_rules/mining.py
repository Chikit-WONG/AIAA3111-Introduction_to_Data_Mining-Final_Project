"""Shared encoding and deterministic, single-consequent association rules."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import math
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth


def encode(baskets: pd.DataFrame, min_support: float) -> pd.DataFrame:
    """Prune only infrequent singletons, using discovery observations alone.

    All original baskets, including those emptied by pruning, remain in the
    matrix so that the support denominator cannot silently change.
    """
    counts = Counter(item for items in baskets["items"] for item in set(items))
    n = len(baskets)
    minimum_count = math.ceil(min_support * n - 1e-12)
    columns = sorted(item for item, count in counts.items() if count >= minimum_count)
    positions = {item: i for i, item in enumerate(columns)}
    matrix = np.zeros((n, len(columns)), dtype=bool)
    for row, items in enumerate(baskets["items"]):
        matrix[row, [positions[x] for x in items if x in positions]] = True
    return pd.DataFrame(matrix, columns=columns)


def mine(matrix: pd.DataFrame, algorithm: str, support: float, max_length: int, low_memory: bool = True) -> pd.DataFrame:
    if len(matrix) == 0 or matrix.shape[1] == 0:
        return pd.DataFrame(columns=["support", "itemsets"])
    if algorithm == "apriori":
        return apriori(matrix, min_support=support, use_colnames=True, max_len=max_length, low_memory=low_memory)
    if algorithm == "fpgrowth":
        return fpgrowth(matrix, min_support=support, use_colnames=True, max_len=max_length)
    raise ValueError(f"Unknown algorithm: {algorithm}")


def signature(itemsets: pd.DataFrame, n: int) -> str:
    canonical = sorted((tuple(sorted(row.itemsets)), round(row.support * n)) for row in itemsets.itertuples())
    return hashlib.sha256(json.dumps(canonical, separators=(",", ":")).encode()).hexdigest()


def make_rules(itemsets: pd.DataFrame, min_confidence: float, min_lift: float) -> pd.DataFrame:
    columns = ["rule_id", "antecedent", "consequent", "support_discovery", "confidence_discovery", "lift_discovery", "antecedent_support_discovery", "consequent_support_discovery", "length"]
    supports = {frozenset(r.itemsets): r.support for r in itemsets.itertuples()}
    rows = []
    for union, supp in supports.items():
        if len(union) < 2:
            continue
        for b in sorted(union):
            a = union - {b}
            sa, sb = supports[a], supports[frozenset([b])]
            confidence = supp / sa
            lift = confidence / sb
            if confidence + 1e-12 < min_confidence or lift + 1e-12 < min_lift:
                continue
            astr = "|".join(sorted(a))
            rows.append({"rule_id": f"{astr}=>{b}", "antecedent": astr, "consequent": b, "support_discovery": supp, "confidence_discovery": confidence, "lift_discovery": lift, "antecedent_support_discovery": sa, "consequent_support_discovery": sb, "length": len(union)})
    return pd.DataFrame(rows, columns=columns).sort_values("rule_id").reset_index(drop=True)
