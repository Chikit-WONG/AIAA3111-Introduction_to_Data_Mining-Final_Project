"""Independently recompute selected results by direct basket membership scans."""
import hashlib
import json
import numpy as np
import pandas as pd
from .data import discovery
from .experiment import load_baskets
from .io import ROOT, load_config, save_json, sha256


def verify_results(cfg):
    tables = ROOT / "results/tables"
    rules = pd.read_csv(tables / "selected_rules.csv", dtype={"rule_id": str, "antecedent": str, "consequent": str})
    evaluations = pd.read_csv(tables / "test_rule_months.csv")
    summary = load_config("results/summary.json")
    protocol = load_config("results/protocol.json")
    selection = load_config("results/selection.json")
    audit = pd.read_csv(tables / "cleaning_audit.csv")
    baskets = load_baskets()
    uk = baskets.loc[baskets.country.eq(cfg["country"])]
    train = discovery(uk, cfg)
    checks = []

    def check(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(int(audit.removed_rows.sum()) + int(audit.remaining_rows.iloc[-1]) == int(audit.remaining_rows.iloc[0]), "Cleaning exclusions reconcile exactly to raw rows")
    check(protocol["raw_sha256"] == sha256(ROOT / "data/raw/Online Retail.xlsx"), "Source checksum matches locked protocol")
    check(protocol["configuration_sha256"] == hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest(), "Configuration matches locked protocol")
    check(selection["rule_ids_sha256"] == hashlib.sha256("\n".join(rules.rule_id).encode()).hexdigest(), "Selected rule set matches frozen selection hash")
    check(rules.rule_id.is_unique, "Rule IDs are unique")
    check(len(evaluations) == len(rules) * len(cfg["test_months"]), "All selected rules appear in every test month")
    check(not evaluations.duplicated(["rule_id", "month"]).any(), "No duplicate rule-month evaluations")
    check(int(evaluations.retained.sum()) == summary["test_retained_rule_months"], "Summary retained count reconciles to rule-level evidence")
    benchmark = pd.read_csv(tables / "benchmark.csv")
    check(benchmark.groupby("min_support").signature.nunique().eq(1).all(), "Apriori and FP-Growth match at every benchmark support")
    sample = rules.sample(min(40, len(rules)), random_state=cfg["seed"])
    month_sets = {month: [set(x) for x in uk.loc[uk.month.eq(month), "items"]] for month in cfg["test_months"]}
    train_sets = [set(x) for x in train["items"]]
    tested = 0
    for rule in sample.itertuples():
        a, b = set(rule.antecedent.split("|")), {rule.consequent}
        discovery_count = sum((a | b).issubset(x) for x in train_sets)
        check(np.isclose(discovery_count / len(train_sets), rule.support_discovery), f"Discovery support independently matches {rule.rule_id}")
        for month, sets in month_sets.items():
            na = sum(a.issubset(x) for x in sets)
            nb = sum(b.issubset(x) for x in sets)
            nab = sum((a | b).issubset(x) for x in sets)
            row = evaluations.loc[evaluations.rule_id.eq(rule.rule_id) & evaluations.month.eq(month)].iloc[0]
            assert (row.orders, row.antecedent_count, row.consequent_count, row.joint_count) == (len(sets), na, nb, nab)
            expected = [nab / len(sets), nab / na if na else np.nan, nab * len(sets) / (na * nb) if na and nb else np.nan]
            assert np.allclose([row.support, row.confidence, row.lift], expected, equal_nan=True)
            expected_retained = na >= cfg["evaluation_min_antecedent_count"] and nb > 0 and expected[0] + 1e-12 >= cfg["evaluation_min_support"] and expected[1] + 1e-12 >= cfg["evaluation_min_confidence"] and expected[2] + 1e-12 >= cfg["evaluation_min_lift"]
            assert bool(row.retained) == bool(expected_retained)
            tested += 1
    save_json({"status": "passed", "scope": "Core integrity checks plus a deterministic independent sample, not a full audit of every rule", "integrity_checks": checks[:9], "independently_checked_discovery_rules": len(sample), "independently_checked_test_rule_months": tested, "sampling_seed": cfg["seed"]}, ROOT / "results/verification.json")
    print(f"Verified core integrity, {len(sample)} discovery rules and {tested} test rule-months independently.")
