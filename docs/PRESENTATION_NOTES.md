# Group 11 explanation and defense preparation

These notes explain the executed project. They do not assign or invent individual contributions. Read the report and inspect the evidence before using them in a presentation.

## 用中文理解整个项目

研究的问题是：早期经常一起购买的商品，到了后面的月份是否还保持这种关系？一行原始数据是一件商品的交易明细；一笔订单里的不同商品组合才是一个购物篮。我们把 541,909 行明细清洗成 19,773 个购物篮，主实验使用其中的英国订单。

2010 年 12 月到 2011 年 5 月用来发现规则，6-7 月选择参数，8-11 月用来检验。后面的月份检验的是同一批固定规则，不是每个月只挑当月表现最好的规则。最终选中 71 条规则，四个月共 284 个“规则 × 月份”记录，其中 225 个达到全部标准，所以平均保留率是 79.2%。46 条规则四个月都达标。

保留标准是：支持度至少 0.5%，置信度至少 50%，提升度至少 1.2，而且当月至少有 20 笔订单包含规则前件。支持度的分母是全部有效订单；置信度的分母是包含前件的订单；提升度还考虑后件本身的流行程度。箭头表示同一订单中的条件关联，不代表购买先后或因果。

“没被保留”不一定表示关系发生了变化，也可能是当月相关订单太少。因此需要同时报告可评估比例。主实验的可评估比例为 99.3%，而低支持度规则很多，但经常没有足够的月度样本。只看高 confidence 而忽略出现次数，会产生误导。

一个重要限制是大购物篮：客户编号缺失的订单平均商品数较多。只保留有客户编号的订单，平均保留率降到 64.8%；去掉商品数超过 100 的订单，保留率为 62.3%。因此我们不能把结果直接推广为所有消费者的购买习惯，更不能宣称促销造成了变化。

## A short English poster walkthrough

Our project asks whether retail associations discovered in historical orders remain reliable in later months. We use UCI Online Retail and treat each invoice as a set of distinct products. After cleaning, the dataset contains 19,773 baskets, with UK orders forming our primary population.

We discover rules using December through May, select parameters using June and July, and freeze the selected rules before evaluating August through November. Apriori and FP-Growth receive the same input and search limits. They return identical frequent itemsets; both are practical on our local CPU under these settings.

Our main measure is retention: the proportion of all frozen rules meeting common monthly support, confidence, lift and sample-count requirements. We also report how many rules are evaluable, so a lack of evidence is not confused with a weakening association.

The selected setting produces 71 rules. Mean test retention is 79.2%, and 46 rules satisfy the requirements in all four months. A jumbo-bag association is a persistent example. A wicker-heart association retains a high lift but falls below our confidence target, showing that these metrics answer different questions.

The result has important qualifications. A narrower set of 14 rules achieves complete observed retention but is below our predeclared 20-rule coverage floor. In addition, restricting orders to those with customer IDs lowers retention to 64.8%. Large baskets and population composition clearly matter. We therefore conclude that temporal evaluation helps identify a useful subset, while the preferred rule set depends on coverage and evidence requirements. We do not claim causation, permanent stability or increased revenue.

## Questions and evidence-backed answers

**What is the project's contribution?**
The contribution is a reproducible chronological evaluation and analysis of quantity, evaluability and persistence, plus a fair implementation benchmark. It is not a new association-mining algorithm.

**Why not randomly split the data?**
The question is performance in later months. A random split mixes periods and does not test that temporal transfer. All products and rules for the main cohort are learned from discovery data only.

**Why is the selected configuration not the one with 100% retention?**
That configuration produces only 14 rules and fails the predeclared minimum of 20. We explicitly show a floor sensitivity analysis: 10 allows 14 rules with 100% observed retention; 20 or 50 yields 71 rules; 100 yields 816 rules with 56.7% retention. The choice depends on desired coverage and is not statistically canonical.

**Why are CustomerID-missing records retained?**
InvoiceNo, StockCode and InvoiceDate are sufficient for basket analysis. Dropping missing IDs changes the population. The sensitivity check quantifies the consequence rather than assuming the missing rows are invalid. A missing ID is not evidence about the customer's identity or retail/wholesale status.

**How is an absent antecedent handled?**
Confidence is undefined, not zero. The rule remains in the frozen cohort and is not retained; it is separately labeled as unobservable. Conditional retention is calculated only among evaluable rules.

**Why is there no accuracy or F1 score?**
This is descriptive association-rule evaluation, not a supervised classifier with defined positive/negative labels. The outcomes are support, confidence, lift, observability and retention.

**Does higher discovery confidence always help?**
No. At 1% support, the 70% confidence cohort has only 42.2% test evaluability. Among those evaluable rule-months retention is 98.6%, but overall retention is 41.6%. An association can be strong when observable and still be too rare for monthly use.

**Why did FP-Growth not dominate Apriori in speed?**
The comparison concerns MLxtend implementations, a maximum length of three, this dataset, and Apriori low-memory mode. At the lowest tested support, timing ranges overlap. We cannot infer a universal algorithm ranking from three local repetitions.

**How did you check correctness?**
We compare algorithm signatures of complete bounded itemsets and integer counts. Tiny tests use exhaustive enumeration and hand calculations. An independent check scans baskets directly for 40 discovery rules and 160 held-out rule-months. The latter is a sample, not a full independent audit.

**Do the confidence bands establish statistically significant changes?**
No. They are nominal Wilson intervals for illustrative conditional proportions and do not adjust for repeated customers, dependent rules or selection. The conclusions are descriptive. A formal follow-up would need an appropriate resampling design and multiple-comparison control.

**Does rolling discovery perform better?**
Not uniformly. Its monthly retention ranges from 66.7% to 86.1%, and it generates a different set of rules each time. Comparing these fractions is descriptive because cohort sizes and members differ. It is not a paired accuracy test.

**What explains the lower November retention?**
The thresholds fail mainly through confidence, and population sensitivity indicates order composition matters. We do not have verified stock or promotion records, so those causes cannot be established.

**Were Apriori and FP-Growth written from scratch?**
No. We use and cite MLxtend. The project code implements data auditing, basket construction, deterministic rule construction, temporal evaluation, benchmarking, diagnostics and reproducibility around the library algorithms. Codex's extensive role is disclosed separately and must be understood and revised by the team.

## Where to inspect a question

- Cleaning and missingness: `results/data_profile.json`, `results/tables/cleaning_audit.csv`.
- Chosen parameters: `results/selection.json`, `results/tables/validation_selection.csv`.
- A particular rule/month: `results/tables/test_rule_months.csv`.
- Algorithm comparison: `results/tables/benchmark.csv`.
- Thresholds and coverage: `results/tables/threshold_sensitivity.csv`, `threshold_evaluability.csv`.
- Population limitations: `customer_sensitivity.csv`, `basket_size_sensitivity.csv`, `customer_id_basket_profile.csv`.
- Actual human review and contributions: complete `TEAM_REVIEW.md` and record real work; do not infer them from these generated notes.
