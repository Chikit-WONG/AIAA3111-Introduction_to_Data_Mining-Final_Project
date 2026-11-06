"""Vector method overview and descriptive diagnostics for the paper revision.

These read frozen results. No discovery, selection or primary evaluation changes.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
import numpy as np
import pandas as pd

from .io import ROOT, load_config, save_json

NAVY = "#15324F"
BLUE = "#317CB0"
TEAL = "#198B83"
ORANGE = "#D97832"
GRAY = "#DCE3E9"


def save(fig, name):
    folder = ROOT / "results/figures"
    for ext in ["pdf", "svg", "png"]:
        fig.savefig(folder / f"{name}.{ext}", dpi=240, facecolor="white")
    plt.close(fig)


def build_paper_figures(cfg):
    tables = ROOT / "results/tables"
    summary = load_config("results/summary.json")
    profile = load_config("results/data_profile.json")
    protocol = load_config("results/protocol.json")
    monthly = pd.read_csv(tables / "monthly_retention.csv")
    rules = pd.read_csv(tables / "selected_rules.csv", dtype={"antecedent": str, "consequent": str})
    ev = pd.read_csv(tables / "test_rule_months.csv")
    unions = [tuple(sorted(set(a.split("|")) | {b})) for a, b in zip(rules.antecedent, rules.consequent)]
    # Post-hoc policy diagnostic: keep the discovered cohort and every other gate fixed.
    gate = (ev.antecedent_count >= cfg["evaluation_min_antecedent_count"]) & (ev.consequent_count > 0)
    gate &= (ev.support + 1e-12 >= cfg["evaluation_min_support"]) & (ev.lift + 1e-12 >= cfg["evaluation_min_lift"])
    sensitivity = []
    for confidence in [.45, .50, .55]:
        retained = gate & (ev.confidence + 1e-12 >= confidence)
        if confidence == cfg["evaluation_min_confidence"]:
            assert retained.equals(ev.retained), "The diagnostic must recover the frozen primary result"
        sensitivity.append({"evaluation_min_confidence": confidence, "retained_rule_months": int(retained.sum()), "all_rule_months": len(ev), "retention": float(retained.mean())})
    save_json({
        "status": "post_hoc_descriptive_diagnostics",
        "selection_changed": False,
        "definition": "Fixed selected rules and test data; confidence-gate sensitivity keeps support, lift and evidence gates unchanged. No new selection or significance test.",
        "selected_rules": len(rules),
        "unique_union_itemsets": len(set(unions)),
        "unique_products": len(set().union(*(set(x) for x in unions))),
        "distinct_consequents": int(rules.consequent.nunique()),
        "largest_consequent_group": {"product": str(rules.consequent.value_counts().index[0]), "rules": int(rules.consequent.value_counts().iloc[0])},
        "confidence_between_45_and_55_percent_rule_months": int(ev.confidence.between(.45, .55).sum()),
        "evaluation_confidence_sensitivity": sensitivity,
    }, ROOT / "results/report_diagnostics.json")

    # A readable four-stage diagram; the dashed handoff marks the test boundary.
    fig = plt.figure(figsize=(9.4, 3.05))
    ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 9.4), ylim=(0, 3.05))
    ax.axis("off")
    n_valid = int(monthly.loc[monthly.split.eq("validation"), "orders"].sum())
    n_test = int(monthly.loc[monthly.split.eq("test"), "orders"].sum())
    stages = [
        (.06, 1.72, "1  AUDIT", "Fixed cleaning", [f'{profile["raw_rows"]:,} raw lines', f'{profile["uk_baskets"]:,} UK baskets', "Invoice = one set", "Missing IDs retained"], "#EFF3F6", NAVY),
        (2.06, 2.12, "2  DISCOVER", "Dec 2010-May 2011", [f'{protocol["discovery_orders"]:,} orders', "Apriori / FP-Growth", "9 support/conf. settings", "At most 3 products"], "#EAF1F8", BLUE),
        (4.46, 2.12, "3  SELECT", "Jun-Jul 2011", [f'{n_valid:,} orders', "Maximize val. retention", "At least 20 rules", f'Freeze {len(rules)} rule IDs'], "#EAF5F2", TEAL),
        (6.88, 2.46, "4  EVALUATE", "Aug-Nov 2011", [f'{n_test:,} orders', f'Same {len(rules)} rules, 4 months', f'{summary["test_retained_rule_months"]}/{summary["test_rule_months"]} rule-months retained', "No test-driven reselection"], "#FCF1E8", ORANGE),
    ]
    for x, w, title, date, lines, face, edge in stages:
        ax.add_patch(FancyBboxPatch((x, .99), w, 1.72, boxstyle="round,pad=0.008,rounding_size=0.07", fc=face, ec=edge, lw=1.1))
        ax.text(x+w/2, 2.49, title, ha="center", va="center", fontsize=12.4, color=edge, weight="bold")
        ax.text(x+w/2, 2.23, date, ha="center", va="center", fontsize=11.4, color=NAVY)
        for j, line in enumerate(lines):
            ax.text(x+w/2, 1.94-j*.235, line, ha="center", va="center", fontsize=11.2, color=NAVY)
    for left, right in [(1.79, 2.05), (4.19, 4.45), (6.59, 6.87)]:
        ax.add_patch(FancyArrowPatch((left, 1.75), (right, 1.75), arrowstyle="-|>", mutation_scale=12, lw=1.4, color=NAVY))
    ax.plot([6.72, 6.72], [.91, 2.77], color=ORANGE, lw=1.2, ls=(0, (3, 3)))
    ax.text(6.72, 2.91, "Locked handoff", fontsize=10.7, color=ORANGE, ha="center", va="center")
    ax.add_patch(FancyBboxPatch((.06, .12), 9.28, .60, boxstyle="round,pad=0.008,rounding_size=0.06", fc="#F5F7F9", ec="#CAD4DC", lw=.8))
    ax.text(4.7, .51, "COMMON MONTHLY GATE: support >= 0.5% | confidence >= 50% | lift >= 1.2", ha="center", va="center", fontsize=11.7, color=NAVY, weight="bold")
    ax.text(4.7, .28, "Require >= 20 antecedent orders and an observed consequent; every frozen rule stays in the denominator.", ha="center", va="center", fontsize=11.1, color=NAVY)
    save(fig, "08_method_overview")

    grid = pd.read_csv(tables / "threshold_sensitivity.csv").merge(pd.read_csv(tables / "threshold_evaluability.csv"), on=["configuration", "rules", "test_retention"], validate="one_to_one")
    fig = plt.figure(figsize=(9.6, 3.45))
    left = fig.add_axes([.075, .27, .37, .57])
    right = fig.add_axes([.645, .27, .31, .57])
    values = grid.pivot(index="min_confidence", columns="min_support", values="test_retention").sort_index()
    im = left.imshow(values.to_numpy()*100, vmin=0, vmax=100, cmap="Blues", aspect="auto")
    left.set_xticks(range(3), [f"{x*100:g}%" for x in values.columns], fontsize=11.5)
    left.set_yticks(range(3), [f"{x*100:g}%" for x in values.index], fontsize=11.5)
    left.set_xlabel("Discovery support", fontsize=12)
    left.set_ylabel("Discovery confidence", fontsize=12)
    for i, confidence in enumerate(values.index):
        for j, support in enumerate(values.columns):
            row = grid.loc[grid.min_confidence.eq(confidence) & grid.min_support.eq(support)].iloc[0]
            star = " *" if row.selected else ""
            left.text(j, i, f"{row.rules:,}\n{100*row.test_retention:.1f}%{star}", ha="center", va="center", fontsize=12, color="white" if row.test_retention > .6 else NAVY)
    cb = fig.colorbar(im, cax=fig.add_axes([.462, .27, .013, .57]))
    cb.ax.tick_params(labelsize=9)
    left.set_title("(a) Cohort size and test retention", fontsize=12, pad=14)
    subset = grid.loc[grid.min_confidence.eq(.5)].sort_values("min_support")
    components = [subset.test_retention.to_numpy(), (subset.test_evaluation_coverage-subset.test_retention).to_numpy(), (1-subset.test_evaluation_coverage).to_numpy()]
    assert np.allclose(np.sum(components, axis=0), 1)
    offset = np.zeros(3)
    for part, color in zip(components, [BLUE, ORANGE, GRAY]):
        right.barh(range(3), part*100, left=offset, color=color, height=.55)
        for y, (v, start) in enumerate(zip(part*100, offset)):
            if v >= 12:
                right.text(start+v/2, y, f"{v:.1f}", ha="center", va="center", fontsize=11.5, color="white" if color == BLUE else NAVY)
        offset += part*100
    right.set_yticks(range(3), [f'{x.min_support*100:g}%\n({x.rules:,} rules)' for x in subset.itertuples()], fontsize=10.5)
    right.invert_yaxis()
    right.set_xlim(0, 100)
    right.set_xticks([0, 50, 100], ["0", "50", "100%"], fontsize=11)
    right.set_xlabel("Share of all test rule-months", fontsize=12)
    right.set_title("(b) Coverage at 50% confidence", fontsize=12, pad=14)
    fig.legend(handles=[Patch(color=BLUE, label="Retained"), Patch(color=ORANGE, label="Evaluable, fails"), Patch(color=GRAY, label="Not evaluable")], frameon=False, fontsize=10.5, loc="lower center", bbox_to_anchor=(.74, .01), ncol=3, handlelength=1, columnspacing=1)
    save(fig, "09_threshold_observability")
