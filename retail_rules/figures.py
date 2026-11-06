"""Publication figures from saved result tables; no re-mining or manual values."""
from __future__ import annotations
import textwrap
import os
from pathlib import Path
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "tmp/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from .io import ROOT, load_config

NAVY = "#15324F"
BLUE = "#317CB0"
TEAL = "#198B83"
ORANGE = "#D97832"
GRAY = "#7C8996"


def build_figures(cfg):
    tables = ROOT / "results/tables"
    out = ROOT / "results/figures"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#8293A1", "axes.labelcolor": NAVY, "text.color": NAVY, "xtick.color": NAVY, "ytick.color": NAVY, "figure.facecolor": "white", "savefig.facecolor": "white", "svg.fonttype": "none", "pdf.fonttype": 42})

    def finish(fig, name, source, bottom=.18):
        source = "\n".join(textwrap.fill(line, width=int(fig.get_figwidth()*15)) for line in source.splitlines())
        bottom = max(bottom, (len(source.splitlines())*9 + 50)/(fig.get_figheight()*72))
        fig.subplots_adjust(bottom=bottom, top=.89, left=.1, right=.97)
        fig.text(.1, .025, source, fontsize=8, color="#536779", va="bottom")
        fig.savefig(out / f"{name}.png", dpi=220)
        fig.savefig(out / f"{name}.svg")
        fig.savefig(out / f"{name}.pdf")
        plt.close(fig)

    monthly = pd.read_csv(tables / "monthly_uk.csv")
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    colors = [NAVY if m < min(cfg["validation_months"]) else TEAL if m in cfg["validation_months"] else ORANGE if m in cfg["test_months"] else GRAY for m in monthly.month]
    ax.bar(np.arange(len(monthly)), monthly.orders, color=colors, width=.72)
    ax.set_xticks(np.arange(len(monthly)), [m[2:] for m in monthly.month], rotation=45, ha="right")
    ax.set(ylabel="Eligible UK orders", xlabel="Month (YY-MM)", title="Chronological split and monthly order counts")
    for x, row in monthly.iterrows():
        ax.text(x, row.orders + 30, f"{row.orders:,}", ha="center", fontsize=8)
    ax.set_ylim(0, monthly.orders.max() * 1.18)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=NAVY, label="Discovery"), Patch(color=TEAL, label="Validation"), Patch(color=ORANGE, label="Test"), Patch(color=GRAY, label="Partial month")], ncol=4, fontsize=8, loc="upper left", frameon=False)
    finish(fig, "01_monthly_orders", "Source: UCI Online Retail; cleaned UK invoices. December 2011 covers only days 1-9.", bottom=.24)

    benchmark = pd.read_csv(tables / "benchmark.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.5))
    x = np.arange(len(cfg["support_grid"]))
    for j, (metric, ylabel) in enumerate([("seconds", "Mining wall time (seconds)"), ("peak_process_rss_mib", "Peak process memory (MiB)")]):
        for i, (algorithm, color, label) in enumerate([("apriori", BLUE, "Apriori (low memory)"), ("fpgrowth", ORANGE, "FP-Growth")]):
            data = benchmark.loc[benchmark.algorithm.eq(algorithm)].groupby("min_support")[metric]
            med = data.median().reindex(cfg["support_grid"])
            lo = data.min().reindex(cfg["support_grid"])
            hi = data.max().reindex(cfg["support_grid"])
            axes[j].bar(x + (i-.5)*.35, med, .33, label=label, color=color, yerr=np.vstack([med-lo, hi-med]), capsize=3)
        axes[j].set_xticks(x, [f"{s*100:g}%" for s in cfg["support_grid"]])
        axes[j].set(xlabel="Minimum support", ylabel=ylabel)
        axes[j].grid(axis="y", alpha=.2)
        axes[j].set_axisbelow(True)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Same itemsets, implementation-dependent resource costs", y=.98)
    fig.subplots_adjust(wspace=.35)
    finish(fig, "02_benchmark", "Source: 7,365 UK discovery orders; 3 fresh processes per setting. Bars: median; whiskers: min-max.\nMining time excludes loading/encoding; memory includes the Python process and input matrix.")

    retention = pd.read_csv(tables / "monthly_retention.csv")
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = np.arange(len(retention))
    ax.axvspan(-.5, 1.5, color=TEAL, alpha=.08)
    for metric, color, label, style in [("retention_rate", BLUE, "Retained / all frozen rules", "-"), ("evaluation_coverage", GRAY, "Evaluable / all frozen rules", "--")]:
        ax.plot(x, retention[metric]*100, style, color=color, marker="o", label=label)
    for i, value in enumerate(retention.retention_rate*100):
        ax.annotate(f"{value:.1f}%", (i, value), xytext=(0, -16), textcoords="offset points", ha="center", fontsize=9)
    ax.axvline(1.5, color=GRAY, ls=":")
    ax.set_xticks(x, retention.month.str.slice(2))
    ax.set(xlabel="Month (YY-MM); shaded months used for selection", ylabel="Share of frozen rules (%)", ylim=(0, 105), title="Fixed-rule temporal retention")
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=.2)
    finish(fig, "03_temporal_retention", "Source: selected UK rules. Common thresholds: support >= 0.5%, confidence >= 50%, lift >= 1.2, antecedent count >= 20.")

    grid = pd.read_csv(tables / "threshold_sensitivity.csv")
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    values = grid.pivot(index="min_confidence", columns="min_support", values="test_retention").sort_index()
    im = ax.imshow(values.to_numpy()*100, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(values.columns)), [f"{s*100:g}%" for s in values.columns])
    ax.set_yticks(range(len(values.index)), [f"{c*100:g}%" for c in values.index])
    for i, conf in enumerate(values.index):
        for j, sup in enumerate(values.columns):
            row = grid.loc[grid.min_confidence.eq(conf) & grid.min_support.eq(sup)].iloc[0]
            label = f"{row.test_retention*100:.1f}%\n{row.rules:,} rules" + ("\nselected" if row.selected else "")
            ax.text(j, i, label, ha="center", va="center", fontsize=10, color="white" if row.test_retention > .6 else NAVY)
    fig.colorbar(im, ax=ax, label="Mean test retention (%)", shrink=.85)
    ax.set(xlabel="Discovery minimum support", ylabel="Discovery minimum confidence", title="Rule quantity and stability across discovery thresholds")
    finish(fig, "04_threshold_sensitivity", "Source: August-November 2011 UK tests. All cells use the SAME evaluation thresholds.\nThe selected cell was chosen on June-July validation only; test-grid comparisons are descriptive.", bottom=.23)

    distribution = pd.read_csv(tables / "stability_distribution.csv")
    fig, ax = plt.subplots(figsize=(7.3, 3.3))
    ax.bar(distribution.months_retained, distribution.rules, color=[GRAY, BLUE, BLUE, BLUE, TEAL], width=.65)
    for row in distribution.itertuples():
        ax.text(row.months_retained, row.rules, str(row.rules), ha="center", va="bottom")
    ax.set(xlabel="Number of test months meeting all retention requirements", ylabel="Frozen rules", title="Persistence across four held-out months")
    ax.set_xticks(range(5))
    ax.set_ylim(0, max(distribution.rules)*1.18)
    finish(fig, "05_persistence", "Source: fixed UK rule cohort; August-November 2011. Unobservable and underpowered months are not counted as retained.")

    cases = pd.read_csv(tables / "case_studies.csv", dtype={"antecedent": str, "consequent": str})
    evidence = pd.read_csv(tables / "test_rule_months.csv")
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.3), sharex=True, sharey=True)
    for ax, row in zip(axes.flat, cases.itertuples()):
        ev = evidence.loc[evidence.rule_id.eq(row.rule_id)].sort_values("month")
        xs = np.arange(len(ev))
        color = TEAL if row.case == "most_persistent" else ORANGE
        ax.plot(xs, ev.confidence*100, "o-", color=color)
        ax.fill_between(xs, ev.confidence_low*100, ev.confidence_high*100, alpha=.16, color=color)
        ax.axhline(50, ls=":", color=GRAY, lw=1)
        title = f"{row.antecedent} -> {row.consequent}\n{row.months_retained}/4 months retained"
        ax.set_title(title, fontsize=9)
        ax.set_xticks(xs, ev.month.str.slice(5))
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=.15)
    for ax in axes[:, 0]:
        ax.set_ylabel("Confidence (%)")
    for ax in axes[-1, :]:
        ax.set_xlabel("Test month in 2011")
    fig.suptitle("Post-hoc examples of persistent and fragile rules", y=.98)
    fig.subplots_adjust(hspace=.46, wspace=.18)
    finish(fig, "06_case_studies", "Source: UK fixed rules, August-November 2011. Cases chosen after evaluation; not representative estimates.\nShading: nominal 95% Wilson intervals; customer dependence is unmodeled. Retention also requires support, lift and count thresholds.", bottom=.18)

    countries = pd.read_csv(tables / "country_sensitivity.csv")
    customers = pd.read_csv(tables / "customer_sensitivity.csv")
    rolling = pd.read_csv(tables / "rolling_retention.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.6))
    fixed = countries.loc[countries.scope.eq("UK")].sort_values("month")
    for data, label, color, style in [(fixed, "UK primary", BLUE, "-"), (countries.loc[countries.scope.eq("All countries")].sort_values("month"), "All countries", TEAL, "--"), (customers.sort_values("month"), "UK with customer ID", ORANGE, ":")]:
        axes[0].plot(range(4), data.retention_rate*100, marker="o", color=color, ls=style, label=label)
    for data, label, color in [(fixed, "Fixed cohort", BLUE), (rolling.sort_values("month"), "Rolling cohort", ORANGE)]:
        axes[1].plot(range(4), data.retention_rate*100, marker="o", color=color, label=label)
    for ax in axes:
        ax.set_xticks(range(4), [m[5:] for m in cfg["test_months"]])
        ax.set(xlabel="Test month in 2011", ylabel="Rule retention (%)", ylim=(0, 105))
        ax.legend(frameon=False, fontsize=8, loc="lower left")
    axes[0].set_title("Same frozen rules, different populations", fontsize=10)
    axes[1].set_title("Fixed versus refreshed rule cohorts", fontsize=10)
    fig.subplots_adjust(wspace=.3)
    finish(fig, "07_robustness", "Source: held-out months. Country/customer populations overlap. Rolling cohorts have different rules and denominators;\nthis is a descriptive policy comparison, not a paired accuracy test.", bottom=.23)
    from .paper_figures import build_paper_figures
    build_paper_figures(cfg)
    print(f"Wrote 9 PNG/SVG/PDF figures to {out}")
