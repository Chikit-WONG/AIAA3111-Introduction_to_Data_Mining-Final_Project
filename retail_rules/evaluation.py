"""Evaluate frozen rules without re-mining or dropping unsuccessful rules."""
from __future__ import annotations
from collections import defaultdict
import math
import numpy as np
import pandas as pd


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054):
    """Nominal 95% binomial interval; repeated-customer dependence is not modeled."""
    if trials == 0:
        return (np.nan, np.nan)
    p = successes / trials
    d = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / d
    radius = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / d
    return max(0, center - radius), min(1, center + radius)


def evaluate(rules: pd.DataFrame, baskets: pd.DataFrame, cfg: dict, month: str, scope: str = "UK") -> pd.DataFrame:
    n = len(baskets)
    index = defaultdict(set)
    for order, items in enumerate(baskets["items"]):
        for item in items:
            index[item].add(order)
    cache = {}

    def count(items):
        key = tuple(sorted(items))
        if key not in cache:
            sets = [index[x] for x in key]
            cache[key] = len(set.intersection(*sets)) if sets else n
        return cache[key]

    rows = []
    for rule in rules.itertuples(index=False):
        a = tuple(rule.antecedent.split("|"))
        b = (rule.consequent,)
        na, nb, nab = count(a), count(b), count(a + b)
        support = nab / n if n else np.nan
        confidence = nab / na if na else np.nan
        lift = nab * n / (na * nb) if na and nb else np.nan
        if not n:
            status = "no_orders"
        elif not na:
            status = "no_antecedent"
        elif na < cfg["evaluation_min_antecedent_count"]:
            status = "low_antecedent_count"
        elif not nb:
            status = "no_consequent"
        else:
            status = "evaluable"
        retained = bool(status == "evaluable" and support + 1e-12 >= cfg["evaluation_min_support"] and confidence + 1e-12 >= cfg["evaluation_min_confidence"] and lift + 1e-12 >= cfg["evaluation_min_lift"])
        lo, hi = wilson_interval(nab, na)
        rows.append({"rule_id": rule.rule_id, "month": month, "scope": scope, "orders": n, "antecedent_count": na, "consequent_count": nb, "joint_count": nab, "support": support, "confidence": confidence, "lift": lift, "confidence_low": lo, "confidence_high": hi, "confidence_change_pp": (confidence - rule.confidence_discovery) * 100, "status": status, "retained": retained})
    columns = ["rule_id", "month", "scope", "orders", "antecedent_count", "consequent_count", "joint_count", "support", "confidence", "lift", "confidence_low", "confidence_high", "confidence_change_pp", "status", "retained"]
    return pd.DataFrame(rows, columns=columns)


def summarize(evaluations: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scope, month), group in evaluations.groupby(["scope", "month"], sort=True):
        eligible = group["status"].eq("evaluable")
        retained = int(group["retained"].sum())
        rows.append({"scope": scope, "month": month, "orders": int(group["orders"].iloc[0]), "discovered_rules": len(group), "evaluable_rules": int(eligible.sum()), "retained_rules": retained, "retention_rate": retained / len(group), "evaluation_coverage": float(eligible.mean()), "conditional_retention": retained / int(eligible.sum()) if eligible.any() else np.nan, "median_confidence": group.loc[eligible, "confidence"].median(), "median_lift": group.loc[eligible, "lift"].median(), "median_confidence_change_pp": group.loc[eligible, "confidence_change_pp"].median(), "insufficient_antecedent_rules": int(group["status"].isin(["no_antecedent", "low_antecedent_count"]).sum()), "no_consequent_rules": int(group["status"].eq("no_consequent").sum())})
    return pd.DataFrame(rows)


def select_configuration(scores: pd.DataFrame, minimum_rules: int) -> pd.Series:
    """Only validation scores are accepted; deterministic tie-breaks are explicit."""
    if "validation_retention" not in scores:
        raise ValueError("Expected validation scores")
    candidates = scores.loc[scores["rules"] >= minimum_rules]
    if candidates.empty:
        raise ValueError("No configuration meets minimum rule count; revise protocol before opening test results")
    return candidates.sort_values(["validation_retention", "rules", "min_support", "min_confidence"], ascending=[False, False, False, False], kind="stable").iloc[0]
