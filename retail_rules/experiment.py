"""Reproducible experiment orchestration, selection and resource accounting."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import numpy as np
import pandas as pd
import psutil
from .data import discovery
from .evaluation import evaluate, summarize, select_configuration
from .io import ROOT, save_json, save_csv, sha256
from .mining import encode, mine, make_rules


def load_baskets():
    p = ROOT / "data/processed/baskets.pkl"
    if not p.exists():
        raise FileNotFoundError("Run python run.py prepare first")
    # Only load the cache created locally from the verified UCI input.
    return pd.read_pickle(p)


def environment():
    info = {"python": sys.version, "platform": platform.platform(), "logical_processors": os.cpu_count(), "physical_cores": psutil.cpu_count(logical=False), "memory_gib": psutil.virtual_memory().total / 2**30, "versions": {name: importlib.metadata.version(name) for name in ["numpy", "pandas", "mlxtend", "scipy", "matplotlib", "psutil", "openpyxl"]}}
    if sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            info["cpu"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    else:
        info["cpu"] = platform.processor()
    return info


def benchmark(matrix: pd.DataFrame, cfg: dict, pilot: bool = False):
    work = ROOT / "results/work" / ("pilot" if pilot else "benchmark")
    work.mkdir(parents=True, exist_ok=True)
    np.save(work / "matrix.npy", matrix.to_numpy(dtype=bool))
    save_json(list(matrix.columns), work / "columns.json")
    records, fp_sets = [], {}
    supports = [0.01] if pilot else cfg["support_grid"]
    repeats = 1 if pilot else cfg["benchmark_repeats"]
    env = os.environ.copy()
    for key in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        env[key] = "1"
    for support in supports:
        for repeat in range(repeats):
            algorithms = ["apriori", "fpgrowth"] if repeat % 2 == 0 else ["fpgrowth", "apriori"]
            for algorithm in algorithms:
                tag = f"{algorithm}_{support:g}_{repeat}"
                output = work / (tag + ".pkl")
                cmd = [sys.executable, "-m", "retail_rules.benchmark_worker", "--matrix", str(work / "matrix.npy"), "--columns", str(work / "columns.json"), "--output", str(output), "--algorithm", algorithm, "--support", str(support), "--max-length", str(cfg["max_itemset_length"])]
                if cfg["apriori_low_memory"]:
                    cmd.append("--low-memory")
                print(f"Benchmark {algorithm}: support={support}, repetition={repeat+1}/{repeats}", flush=True)
                start = time.perf_counter()
                proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                observed_peak = 0
                failure = None
                task = psutil.Process(proc.pid)
                while proc.poll() is None:
                    try:
                        observed_peak = max(observed_peak, task.memory_info().rss)
                    except psutil.NoSuchProcess:
                        break
                    if observed_peak > cfg["benchmark_memory_limit_gib"] * 2**30:
                        failure = "memory_limit"
                    if time.perf_counter() - start > cfg["benchmark_timeout_seconds"]:
                        failure = "timeout"
                    if failure:
                        proc.kill()
                        break
                    time.sleep(.05)
                stdout, stderr = proc.communicate()
                if failure or proc.returncode:
                    raise RuntimeError(f"Benchmark failed ({tag}, {failure}): {stderr[-3000:]}")
                measured = json.loads(stdout.strip().splitlines()[-1])
                measured["peak_process_rss_mib"] = max(observed_peak / 2**20, measured.pop("os_peak_rss_mib"))
                measured.update(algorithm=algorithm, min_support=support, repeat=repeat+1, orders=len(matrix), encoded_products=matrix.shape[1], max_length=cfg["max_itemset_length"], apriori_low_memory=cfg["apriori_low_memory"] if algorithm == "apriori" else False)
                records.append(measured)
                print(f"  {measured['seconds']:.3f} s, {measured['peak_process_rss_mib']:.1f} MiB, {measured['itemsets']} itemsets", flush=True)
                if algorithm == "fpgrowth" and repeat == 0:
                    fp_sets[support] = pd.read_pickle(output)
    frame = pd.DataFrame(records)
    if not frame.groupby("min_support")["signature"].nunique().eq(1).all():
        raise AssertionError("Algorithms/repetitions disagree on exact itemsets and support counts")
    save_csv(frame, ROOT / "results/tables" / ("pilot_benchmark.csv" if pilot else "benchmark.csv"))
    return fp_sets, frame


def pilot(cfg: dict):
    baskets = load_baskets()
    train = discovery(baskets.loc[baskets["country"].eq(cfg["country"])], cfg).sort_values(["date", "InvoiceNo"]).head(2000)
    matrix = encode(train, .01)
    sets, measured = benchmark(matrix, cfg, pilot=True)
    save_json({"orders": len(train), "frequent_products": matrix.shape[1], "rules_at_confidence_0_5": len(make_rules(sets[.01], .5, cfg["discovery_min_lift"])), "max_peak_rss_mib": measured["peak_process_rss_mib"].max(), "note": "First 2000 discovery invoices; feasibility check only, not reported performance comparison"}, ROOT / "results/pilot.json")


def _monthly(rules, baskets, months, cfg, scope="UK"):
    return pd.concat([evaluate(rules, baskets.loc[baskets["month"].eq(month)], cfg, month, scope) for month in months], ignore_index=True)


def run_experiments(cfg: dict):
    started = time.perf_counter()
    all_baskets = load_baskets()
    uk = all_baskets.loc[all_baskets["country"].eq(cfg["country"])].copy()
    train = discovery(uk, cfg)
    if set(cfg["validation_months"]) & set(cfg["test_months"]):
        raise ValueError("Validation and test periods overlap")
    if train["month"].max() >= min(cfg["validation_months"]) or max(cfg["validation_months"]) >= min(cfg["test_months"]):
        raise ValueError("Periods must be strictly chronological")
    config_digest = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    protocol = {"locked_utc": datetime.now(timezone.utc).isoformat(), "configuration_sha256": config_digest, "raw_sha256": sha256(ROOT / "data/raw/Online Retail.xlsx"), "configuration": cfg, "discovery_orders": len(train), "selection_has_seen_test_metrics": False}
    save_json(protocol, ROOT / "results/protocol.json")
    save_json(environment(), ROOT / "results/environment.json")
    splits = [{"split": "discovery", "month": m, "orders": len(g)} for m, g in train.groupby("month")]
    splits += [{"split": split, "month": m, "orders": int(uk["month"].eq(m).sum())} for split, months in [("validation", cfg["validation_months"]), ("test", cfg["test_months"]), ("partial_supplement", [cfg["partial_month"]])] for m in months]
    save_csv(pd.DataFrame(splits), ROOT / "results/tables/splits.csv")
    matrix = encode(train, min(cfg["support_grid"]))
    save_json({"orders": len(matrix), "frequent_singletons": matrix.shape[1], "matrix_mib": matrix.to_numpy().nbytes / 2**20, "all_discovery_baskets_preserved": len(matrix) == len(train)}, ROOT / "results/encoding.json")
    itemsets, measured = benchmark(matrix, cfg)
    candidates, scores, validation_parts = {}, [], []
    for support in cfg["support_grid"]:
        for confidence in cfg["confidence_grid"]:
            key = f"s{support:g}_c{confidence:g}"
            rules = make_rules(itemsets[support], confidence, cfg["discovery_min_lift"])
            candidates[key] = rules
            evaluation = _monthly(rules, uk, cfg["validation_months"], cfg)
            score = float(evaluation["retained"].mean()) if len(evaluation) else 0.0
            scores.append({"configuration": key, "min_support": support, "min_confidence": confidence, "rules": len(rules), "validation_retention": score})
            if len(evaluation):
                part = summarize(evaluation)
                part["configuration"] = key
                validation_parts.append(part)
    scores = pd.DataFrame(scores)
    selected = select_configuration(scores, cfg["selection_min_rules"])
    key = selected["configuration"]
    rules = candidates[key]
    # Persist the decision before any test rule metrics are evaluated.
    selection = selected.to_dict()
    selection.update(selected_utc=datetime.now(timezone.utc).isoformat(), configuration_sha256=config_digest, rule_ids_sha256=hashlib.sha256("\n".join(rules["rule_id"]).encode()).hexdigest(), evaluation_thresholds={k: v for k, v in cfg.items() if k.startswith("evaluation_")}, objective=cfg["selection_objective"])
    save_json(selection, ROOT / "results/selection.json")
    save_csv(scores, ROOT / "results/tables/validation_selection.csv")
    save_csv(pd.concat(validation_parts, ignore_index=True), ROOT / "results/tables/validation_grid_monthly.csv")
    save_csv(rules, ROOT / "results/tables/selected_rules.csv")
    print(f"Selection locked before test evaluation: {key}, {len(rules)} rules", flush=True)
    test = _monthly(rules, uk, cfg["test_months"], cfg)
    validation = _monthly(rules, uk, cfg["validation_months"], cfg)
    partial = _monthly(rules, uk, [cfg["partial_month"]], cfg)
    save_csv(test, ROOT / "results/tables/test_rule_months.csv")
    save_csv(validation, ROOT / "results/tables/selected_validation_rule_months.csv")
    save_csv(partial, ROOT / "results/tables/partial_month_rule_metrics.csv")
    monthly = summarize(pd.concat([validation, test], ignore_index=True))
    monthly["split"] = monthly["month"].map(lambda m: "validation" if m in cfg["validation_months"] else "test")
    save_csv(monthly, ROOT / "results/tables/monthly_retention.csv")
    grid_test = []
    for row in scores.itertuples():
        ev = _monthly(candidates[row.configuration], uk, cfg["test_months"], cfg)
        grid_test.append({**row._asdict(), "test_retention": float(ev["retained"].mean()) if len(ev) else np.nan, "selected": row.configuration == key})
    save_csv(pd.DataFrame(grid_test), ROOT / "results/tables/threshold_sensitivity.csv")
    # Hold the UK-discovered rules fixed; this is an overlapping-population sensitivity check.
    all_eval = _monthly(rules, all_baskets, cfg["test_months"], cfg, "All countries")
    country_summary = summarize(pd.concat([test, all_eval], ignore_index=True))
    save_csv(country_summary, ROOT / "results/tables/country_sensitivity.csv")
    # Unknown customer IDs remain in the primary population. Check their influence separately.
    known_eval = _monthly(rules, uk.loc[uk["customer_known"]], cfg["test_months"], cfg, "UK known customers")
    save_csv(summarize(known_eval), ROOT / "results/tables/customer_sensitivity.csv")
    rolling_rows = []
    rolling_evaluations = []
    for month in cfg["test_months"]:
        end = pd.Timestamp(month + "-01")
        start = end - pd.DateOffset(months=cfg["rolling_discovery_months"])
        roll_train = uk.loc[uk["date"].ge(start) & uk["date"].lt(end)]
        encoded = encode(roll_train, float(selected["min_support"]))
        mined = mine(encoded, "fpgrowth", float(selected["min_support"]), cfg["max_itemset_length"])
        roll_rules = make_rules(mined, float(selected["min_confidence"]), cfg["discovery_min_lift"])
        ev = evaluate(roll_rules, uk.loc[uk["month"].eq(month)], cfg, month, "Rolling three months")
        if len(ev):
            record = summarize(ev).iloc[0].to_dict()
            record.update(discovery_start=str(start.date()), discovery_end_exclusive=str(end.date()), discovery_orders=len(roll_train), shared_with_fixed_rules=len(set(roll_rules["rule_id"]) & set(rules["rule_id"])))
            rolling_rows.append(record)
            rolling_evaluations.append(ev)
        print(f"Rolling validation {month}: {len(roll_rules)} rules", flush=True)
    save_csv(pd.DataFrame(rolling_rows), ROOT / "results/tables/rolling_retention.csv")
    if rolling_evaluations:
        save_csv(pd.concat(rolling_evaluations, ignore_index=True), ROOT / "results/tables/rolling_rule_months.csv")
    stability = test.groupby("rule_id").agg(months_retained=("retained", "sum"), evaluable_months=("status", lambda s: int(s.eq("evaluable").sum())), mean_test_confidence=("confidence", "mean"), min_test_confidence=("confidence", "min"), confidence_std=("confidence", "std"), mean_test_lift=("lift", "mean"), min_antecedent_count=("antecedent_count", "min"))
    stability = rules.merge(stability.reset_index(), on="rule_id", validate="one_to_one")
    save_csv(stability, ROOT / "results/tables/rule_stability.csv")
    labels = pd.read_csv(ROOT / "results/tables/product_labels.csv", dtype=str).set_index("StockCode")["description"].to_dict()
    stable = stability.sort_values(["months_retained", "min_antecedent_count", "rule_id"], ascending=[False, False, True]).head(3).copy()
    unstable = stability.loc[~stability["rule_id"].isin(stable["rule_id"])].sort_values(["months_retained", "confidence_discovery", "rule_id"], ascending=[True, False, True]).head(3).copy()
    examples = pd.concat([stable.assign(case="most_persistent"), unstable.assign(case="least_persistent")], ignore_index=True)
    examples["antecedent_name"] = examples["antecedent"].map(lambda s: " + ".join(labels.get(i, i) for i in s.split("|")))
    examples["consequent_name"] = examples["consequent"].map(lambda s: labels.get(s, s))
    save_csv(examples, ROOT / "results/tables/case_studies.csv")
    hist = stability["months_retained"].value_counts().reindex(range(len(cfg["test_months"])+1), fill_value=0).rename_axis("months_retained").reset_index(name="rules")
    save_csv(hist, ROOT / "results/tables/stability_distribution.csv")
    summary = {"selected_configuration": key, "selected_rules": len(rules), "test_rule_months": len(test), "test_retained_rule_months": int(test["retained"].sum()), "mean_monthly_test_retention": float(test["retained"].mean()), "rules_retained_all_test_months": int(stability["months_retained"].eq(len(cfg["test_months"])).sum()), "rules_retained_no_test_month": int(stability["months_retained"].eq(0).sum()), "test_evaluation_coverage": float(test["status"].eq("evaluable").mean()), "benchmark_max_peak_rss_mib": float(measured["peak_process_rss_mib"].max()), "experiment_wall_seconds": time.perf_counter() - started, "completed_utc": datetime.now(timezone.utc).isoformat()}
    save_json(summary, ROOT / "results/summary.json")
    print(json.dumps(summary, indent=2), flush=True)
