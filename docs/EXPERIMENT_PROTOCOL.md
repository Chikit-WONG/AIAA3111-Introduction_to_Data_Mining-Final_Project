# Experiment definitions and limitations

The unit of observation is an invoice containing a set of distinct product codes. Quantity and price are validity filters; quantity does not weight item presence. The primary result concerns positive-sales baskets, not net sales after matched refunds. All nonempty cleaned baskets, including singletons, are kept. Empty rows created by singleton-feature pruning still contribute to the support denominator.

## Cleaning

`cleaning_audit.csv` reports **sequential** exclusions: raw 541,909; 5,268 exact duplicate rows; 9,251 cancellation rows; 1,336 other nonpositive quantity rows; 1,176 nonpositive price rows; 2,341 non-product rows; 522,537 remaining. Missing essential basket fields remove zero additional rows after deduplication. These categories must not be interpreted as independent raw-data prevalence estimates.

The explicit non-product code list is in the configuration. Valid nonnumeric product codes are not rejected by a numeric-only regular expression. `retained_unusual_codes.csv` records retained exceptional formats for inspection. There are 42 same-day invoices whose lines span one minute; earliest time is used. Cross-day or cross-country invoice conflicts raise an error. Date values are used as recorded; the source does not provide timezone metadata.

CustomerID is missing in 135,080 raw rows. It is unnecessary for basket identity, so dropping it would change the population. The known-ID and large-basket checks measure sensitivity to that choice; they do not establish a causal effect of identifier missingness. Descriptions are only labels, selected from discovery-period UK records.

## Time and selection

Discovery is `[2010-12-01, 2011-06-01)`. Validation months are June and July 2011. Held-out test months are August through November 2011. No random split is used. December 2011 contains only days 1-9 and is excluded from the main comparison. The protocol, raw checksum and configuration digest are saved before evaluation, and the winning rule IDs and parameters are persisted before test-rule metrics are computed.

The 3 x 3 discovery grid uses supports 0.005/0.01/0.02 and confidences 0.3/0.5/0.7; lift is at least 1.2. The maximum itemset size is three, and consequents contain one product. The objective is maximum mean validation retention, requiring at least 20 discovery rules. Ties prefer more rules, then higher support, then higher confidence. The rule floor is an explicit coverage policy, not a statistical minimum. Test-grid results do not alter the selected configuration.

## Metrics and denominators

For month t with N orders and antecedent A/consequent B, support = n(A union B)/N; confidence = n(A union B)/n(A); lift = n(A union B)N/[n(A)n(B)]. An absent antecedent yields undefined confidence, not zero. Absent antecedent/consequent marginals yield undefined lift. The monthly operational requirements are support >= 0.005, confidence >= 0.5, lift >= 1.2, and n(A) >= 20. An evaluable rule additionally has n(B) > 0.

Retention = retained rules / all frozen rules. Coverage = evaluable rules / all frozen rules. Conditional retention = retained / evaluable. Unobservable and underpowered rules remain in the main denominator. Persistence counts months retained. Monthly rates have equal weight; with a constant cohort this is also retained rule-months / all rule-months. The four monthly rates are not independent samples, and rule-month counts are not a statistical effective sample size.

Wilson intervals in illustrative case plots are nominal 95% binomial intervals for confidence only. They ignore repeat-customer dependence and multiple comparisons, and do not establish statistically significant drift. The main work makes descriptive claims.

## Computational comparison

Both algorithms receive the same 7,365 x 1,409 Boolean matrix and limits. Apriori low-memory mode is explicit; results are about these library implementations, not universal algorithm complexity rankings. Each setting runs three times in a fresh subprocess. Algorithm order alternates; numerical-library threads are capped at one. Time excludes startup, imports, matrix loading, encoding, rules and output. Peak working-set memory includes interpreter, dependencies and matrix; it is not full-pipeline memory. Exact canonical itemset/count signatures must match.

## Supplemental analysis

All-country evaluation uses the same UK-discovered rules and includes UK orders, so it is not an independent replication. The known-CustomerID subset also overlaps the primary population. Rolling three-month discovery uses only months before each held-out month and retains the thresholds already selected on June-July; its rule cohorts vary, so their retained fractions are not a paired comparison on identical rules.

Post-hoc diagnostics are labeled explicitly: evaluation restricted to baskets of at most 100 products, rule-count floor sensitivity, basket sizes by CustomerID availability, grid evaluability and sequential failure attribution. They do not change the primary protocol or selection. Removing large test baskets while holding rules fixed is a population-sensitivity check, not a separately trained small-basket model.

## Validation scope

Tests use hand-computed examples and exhaustive enumeration on tiny baskets, including denominator preservation, zero samples and exclusive time boundaries. Numerical verification independently scans baskets for 40 discovery rules and 160 rule-months, sampled with seed 3111. It also checks complete cohort membership, hash integrity, cleaning reconciliation and benchmark equivalence. The deterministic sampled check is not a full independent audit of every rule or narrative sentence.

The dataset covers one retailer for approximately a year. There are no verified promotion, stock-availability or intervention records. Seasonal, supply and promotional explanations remain hypotheses. The results do not demonstrate causality, long-term permanence or increased sales.
