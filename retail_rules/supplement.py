"""Explicitly post-hoc diagnostics; never change the locked primary selection."""
from datetime import datetime, timezone
import pandas as pd
from .experiment import load_baskets, _monthly
from .evaluation import summarize, select_configuration
from .io import ROOT, save_csv, save_json
from .data import discovery
from .mining import encode, mine, make_rules


def run_supplements(cfg):
    tables = ROOT / "results/tables"
    baskets = load_baskets()
    uk = baskets.loc[baskets.country.eq(cfg["country"])]
    rules = pd.read_csv(tables / "selected_rules.csv", dtype={"antecedent": str, "consequent": str})
    primary = pd.read_csv(tables / "test_rule_months.csv")
    # 100-product threshold is a diagnostic chosen after the raw basket-size
    # audit. This changes the evaluation population, not the frozen rule cohort.
    small = uk.loc[uk.n_items.le(100)]
    ev = _monthly(rules, small, cfg["test_months"], cfg, "UK at most 100 products")
    save_csv(ev, tables / "small_basket_rule_months.csv")
    save_csv(summarize(ev), tables / "basket_size_sensitivity.csv")
    grid = pd.read_csv(tables / "threshold_sensitivity.csv")
    train = discovery(uk, cfg)
    matrix = encode(train, min(cfg["support_grid"]))
    coverage = []
    for support in cfg["support_grid"]:
        sets = mine(matrix, "fpgrowth", support, cfg["max_itemset_length"])
        for confidence in cfg["confidence_grid"]:
            cohort = make_rules(sets, confidence, cfg["discovery_min_lift"])
            evidence = _monthly(cohort, uk, cfg["test_months"], cfg)
            evaluable = evidence.status.eq("evaluable")
            coverage.append({"configuration": f"s{support:g}_c{confidence:g}", "rules": len(cohort), "test_evaluation_coverage": float(evaluable.mean()) if len(evidence) else 0.0, "test_conditional_retention": float(evidence.loc[evaluable, "retained"].mean()) if evaluable.any() else 0.0, "test_retention": float(evidence.retained.mean()) if len(evidence) else 0.0})
    save_csv(pd.DataFrame(coverage), tables / "threshold_evaluability.csv")
    floors = []
    for floor in [10, 20, 50, 100]:
        chosen = select_configuration(grid, floor)
        floors.append({"minimum_rules": floor, "configuration": chosen.configuration, "rules": chosen.rules, "validation_retention": chosen.validation_retention, "test_retention": chosen.test_retention})
    save_csv(pd.DataFrame(floors), tables / "rule_floor_sensitivity.csv")
    part = uk.loc[uk.month.isin(cfg["test_months"])].copy()
    part["customer_id_status"] = part.customer_known.map({True: "recorded", False: "missing"})
    segments = part.groupby(["month", "customer_id_status"]).agg(orders=("InvoiceNo", "size"), median_products=("n_items", "median"), mean_products=("n_items", "mean"), over_100_products=("n_items", lambda s: int(s.gt(100).sum())))
    save_csv(segments.reset_index(), tables / "customer_id_basket_profile.csv")
    failure = primary.copy()
    def reason(row):
        if row.status != "evaluable":
            return row.status
        if row.support + 1e-12 < cfg["evaluation_min_support"]:
            return "below_support"
        if row.confidence + 1e-12 < cfg["evaluation_min_confidence"]:
            return "below_confidence"
        if row.lift + 1e-12 < cfg["evaluation_min_lift"]:
            return "below_lift"
        return "retained"
    failure["first_failed_requirement"] = [reason(r) for r in failure.itertuples()]
    save_csv(failure.groupby(["month", "first_failed_requirement"]).size().rename("rule_months").reset_index(), tables / "retention_failure_breakdown.csv")
    save_json({"created_utc": datetime.now(timezone.utc).isoformat(), "status": "post_hoc_descriptive_diagnostics", "primary_selection_changed": False, "diagnostics": ["Exclude evaluation invoices with more than 100 unique products, keeping the selected rules fixed", "Recompute validation-only selection with minimum rule floors of 10, 20, 50 and 100", "Profile basket size by presence of CustomerID", "Partition failures in order: evaluability, support, confidence, lift"]}, ROOT / "results/supplemental_protocol.json")
    print("Supplementary diagnostics saved; primary selection unchanged.")
