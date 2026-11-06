"""Tests use independent hand calculations and exhaustive tiny-data enumeration."""
from itertools import combinations
import math
import numpy as np
import pandas as pd
import pytest
from retail_rules.data import clean_lines, make_baskets, discovery
from retail_rules.evaluation import evaluate, summarize, select_configuration
from retail_rules.io import load_config
from retail_rules.mining import encode, mine, make_rules


@pytest.fixture
def cfg():
    c = load_config()
    c["evaluation_min_antecedent_count"] = 1
    return c


def test_both_algorithms_match_exhaustive_enumeration():
    baskets = pd.DataFrame({"items": [("A", "B", "C"), ("A", "B"), ("A", "C"), ("B",), ("D",)]})
    matrix = encode(baskets, .2)
    expected = {}
    for k in range(1, 4):
        for items in combinations("ABCD", k):
            count = sum(set(items).issubset(basket) for basket in baskets["items"])
            if count >= 1:
                expected[frozenset(items)] = count / 5
    for algorithm in ["apriori", "fpgrowth"]:
        found = mine(matrix, algorithm, .2, 3)
        assert dict(zip(found.itemsets, found.support)) == expected


def test_encoding_keeps_empty_after_pruning_orders():
    baskets = pd.DataFrame({"items": [("A",), ("A",), ("RARE",)]})
    matrix = encode(baskets, .5)
    assert matrix.shape == (3, 1)
    assert matrix.A.mean() == pytest.approx(2/3)


def test_rules_and_future_metrics_have_hand_computed_denominators(cfg):
    train = pd.DataFrame({"items": [("A", "B"), ("A", "B"), ("A",), ("C",)]})
    rules = make_rules(mine(encode(train, .25), "fpgrowth", .25, 3), 0, 0)
    ab = rules.loc[rules.rule_id.eq("A=>B")]
    assert ab.iloc[0].support_discovery == .5
    assert ab.iloc[0].confidence_discovery == pytest.approx(2/3)
    assert ab.iloc[0].lift_discovery == pytest.approx(4/3)
    future = pd.DataFrame({"items": [("A", "B"), ("A",), ("B",), ("C",)]})
    got = evaluate(ab, future, cfg, "2011-08").iloc[0]
    assert (got.orders, got.antecedent_count, got.consequent_count, got.joint_count) == (4, 2, 2, 1)
    assert got.support == .25 and got.confidence == .5 and got.lift == 1
    assert not got.retained
    assert got.confidence_low < .5 < got.confidence_high


def test_absent_and_low_count_rules_stay_in_retention_denominator(cfg):
    train = pd.DataFrame({"items": [("A", "B"), ("A", "B"), ("C",)]})
    rules = make_rules(mine(encode(train, .1), "fpgrowth", .1, 3), .5, 1)
    future = pd.DataFrame({"items": [("C",), ("C",)]})
    ev = evaluate(rules, future, cfg, "2011-08")
    assert len(ev) == len(rules) == 2
    assert ev.confidence.isna().all()
    assert ev.status.eq("no_antecedent").all()
    summary = summarize(ev).iloc[0]
    assert summary.discovered_rules == 2 and summary.retention_rate == 0
    assert math.isnan(summary.conditional_retention)
    cfg["evaluation_min_antecedent_count"] = 3
    low = evaluate(rules, train, cfg, "2011-08")
    assert low.status.eq("low_antecedent_count").all()


def test_singletons_missing_customers_and_order_item_deduplication_are_preserved(cfg):
    def row(invoice, stock, quantity=1, price=1, customer=np.nan):
        return dict(InvoiceNo=invoice, StockCode=stock, Quantity=quantity, UnitPrice=price, CustomerID=customer, Description=stock, InvoiceDate=pd.Timestamp("2011-01-01"), Country="United Kingdom")
    raw = pd.DataFrame([row("1", "A"), row("1", "A"), row("1", "A", 2), row("1", "B"), row("2", "B"), row("C3", "B"), row("4", "A", -1), row("5", "POST"), row("6", "A", price=0)])
    lines, audit = clean_lines(raw, ["POST"])
    baskets = make_baskets(lines)
    assert list(baskets["items"]) == [("A", "B"), ("B",)]
    assert not baskets.customer_known.any()
    assert audit.removed_rows.sum() + len(lines) == len(raw)


def test_discovery_end_is_exclusive(cfg):
    baskets = pd.DataFrame({"date": pd.to_datetime(["2010-11-30", "2010-12-01", "2011-05-31 23:59", "2011-06-01"], format="mixed")})
    assert list(discovery(baskets, cfg).index) == [1, 2]


def test_selection_uses_only_validation_scores_and_respects_rule_floor():
    scores = pd.DataFrame([{"configuration": "too_small", "rules": 1, "validation_retention": 1, "min_support": .01, "min_confidence": .7, "test_retention": 1}, {"configuration": "chosen", "rules": 30, "validation_retention": .8, "min_support": .01, "min_confidence": .7, "test_retention": 0}, {"configuration": "test_winner", "rules": 40, "validation_retention": .5, "min_support": .01, "min_confidence": .5, "test_retention": 1}])
    assert select_configuration(scores, 20).configuration == "chosen"


def test_zero_order_month_is_missing_not_a_measured_zero(cfg):
    train = pd.DataFrame({"items": [("A", "B"), ("C",)]})
    rules = make_rules(mine(encode(train, .1), "fpgrowth", .1, 3), 0, 0)
    ev = evaluate(rules, train.iloc[:0], cfg, "2011-08")
    assert ev.status.eq("no_orders").all() and ev.support.isna().all()


def test_same_day_time_spread_uses_earliest_but_cross_day_is_rejected():
    source = pd.DataFrame([dict(InvoiceNo="1", StockCode="10000", Description="item", Quantity=1, UnitPrice=1, CustomerID=None, Country="United Kingdom", InvoiceDate="2011-01-01 12:01"), dict(InvoiceNo="1", StockCode="20000", Description="item", Quantity=1, UnitPrice=1, CustomerID=None, Country="United Kingdom", InvoiceDate="2011-01-01 12:00")])
    lines, _ = clean_lines(source, [])
    assert make_baskets(lines).iloc[0].date == pd.Timestamp("2011-01-01 12:00")
    source.loc[1, "InvoiceDate"] = "2011-01-02 12:00"
    with pytest.raises(ValueError, match="spans dates or countries"):
        clean_lines(source, [])


def test_missing_consequent_keeps_zero_confidence_and_undefined_lift(cfg):
    train = pd.DataFrame({"items": [("A", "B"), ("C",)]})
    rules = make_rules(mine(encode(train, .1), "fpgrowth", .1, 3), 0, 0)
    ev = evaluate(rules.loc[rules.rule_id.eq("A=>B")], pd.DataFrame({"items": [("A",), ("A",)]}), cfg, "2011-08").iloc[0]
    assert ev.confidence == 0 and math.isnan(ev.lift)
    assert ev.status == "no_consequent" and not ev.retained
