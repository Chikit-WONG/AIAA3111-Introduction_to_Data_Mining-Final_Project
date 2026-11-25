# Beyond Frequent Co-Purchases | Group 11

**3-minute presentation + 2-minute Q&A | 3 分钟讲解 + 2 分钟问答**

Deliver the English paragraphs. The 262 spoken words take about 2:38–2:52 at 100–110 words per minute, including 15 seconds for pointing and handoffs. The time windows below are rehearsal targets. Open the floor by 3:00.

现场讲英文，每段下面的中文供排练时对照。英文口播共 262 词，每分钟 100–110 词，加上 15 秒指图和交接，预计用时 2 分 38 秒至 2 分 52 秒。下面的分段时间供排练参考，最迟第 3 分钟转入问答。

## 0:00–0:55 · Speaker 1 · From receipts to a research question | 从小票说起

*Point down the left column from the A/B receipts to the order counts. 从左栏的 A/B 小票指向下方的订单拆分。*

**English**

If two products often appear on the same receipt today, will they still go together next month? Think of the pink polka-dot jumbo bag and the red spotted bag in our data. Among orders with the pink bag, how often did the red one also appear? To answer that question, we turned each invoice into a basket and counted each product once. Just over seventeen thousand orders went into the main study. Our data end on December ninth, so we used those last nine days for a separate check.

**中文**

如果两件商品今天经常出现在同一张小票上，下个月还会这样吗？以数据里的粉色波点大购物袋和红色斑点购物袋为例，买了粉色袋子的订单里，有多少也买了红色袋子？我们把每张发票整理成一个购物篮，同一商品只计一次。主研究用了 1.7 万多笔订单。数据在 12 月 9 日截止，该月前九天的订单单独用于补充检验。

## 0:55–1:55 · Speaker 2 · How we selected the rules | 如何选出规则

*Point to the validation box in the middle column. 指向中栏标有 78.2% 的验证结果框。*

**English**

We kept the orders in date order. In the first six months, Apriori and FP-Growth found the same frequent product sets. Different support and confidence thresholds gave us nine groups of rules. In June and July, we compared groups with at least twenty rules. The highest average monthly retention came from the group discovered at two percent support and fifty percent confidence. It contained seventy-one rules and passed seventy-eight point two percent of its monthly checks. We froze all seventy-one before looking at August.

**中文**

我们按时间顺序划分订单。先用前六个月的数据挖掘，Apriori 和 FP-Growth 找到了相同的频繁商品组合。不同的支持度和置信度门槛产生了九组规则。我们用六月和七月的数据，在至少含二十条规则的组中比较月均留存率。发现期支持度为 2%、置信度为 50% 的组最优，共 71 条规则，验证期月度检验的通过率为 78.2%。查看八月数据之前，我们就固定了这 71 条规则。

## 1:55–2:55 · Speaker 3 · What lasted in the test period | 哪些规则持续达标

*Point to the four bars at the bottom right. 指向右下角八月至十一月的四根柱子。*

**English**

From August through November, each rule faced the same checks every month. That gave us one observation per rule per month. Of two hundred and eighty-four checks, two hundred and twenty-five passed, or seventy-nine point two percent. Now count whole rules. Forty-six of the seventy-one passed in all four months, including the pink and red bag pairing. For this retailer, that makes the bags a plausible pair to recommend and monitor. To find out whether showing that recommendation actually increases sales, we would need a separate experiment. Thank you.

**中文**

从八月到十一月，每条规则每个月都按同一套标准检验。这样，一条规则在一个月里构成一次观察。总共 284 次检验，通过了 225 次，测试留存率是 79.2%。再按整条规则来看，71 条中有 46 条连续四个月都达标，开头提到的粉、红购物袋就是其中一条。对这家零售商来说，这是一组值得尝试推荐并持续监测的搭配。展示这条推荐能否真正提高销量，还需要另做实验。谢谢大家。

## 3:00–5:00 · Audience Q&A | 现场问答

Answer whichever question is asked. Aim for 20–30 seconds, and point to the figures when an exact count helps. 根据老师的问题选答，每题尽量控制在 20–30 秒，需要精确数字时指图说明。

**1. Why choose 71 rules when the 14-rule group reached 100%? | 14 条规则的组达到 100%，为什么选 71 条？**

**EN** We set a minimum of 20 rules per candidate group before selection. The 14-rule group fell below that minimum. Among the eligible groups, the 71-rule group had the highest June–July retention, so that was the group we froze.

**中** 选组前就规定每组至少有 20 条规则，14 条的组未达到门槛。在符合条件的组里，包含 71 条规则的这一组在六、七月的平均留存率最高，因此我们固定这组规则进入测试。

*Counts if asked | 追问时可用的数字*

June 55 of 71, July 56 of 71. Across both months, 111 of 142 checks passed (78.2%). 六月通过 55/71，七月通过 56/71，两个月共通过 111/142。

**2. How can both 79.2% and 46/71 be correct? | 为什么 79.2% 和 46/71 都成立？**

**EN** The first figure counts monthly checks. Each of the 71 rules gets four checks, giving 284 in total. A rule passing three months contributes three of the 225 passes. Only rules passing all four months count toward the 46.

**中** 前者按月度检验计数。每条规则有四次检验，71 条合计 284 次。一条规则如果通过三个月，就为 225 次通过贡献三次；只有四个月全部通过的规则才计入 46 条。

**3. What makes a rule pass in one month? | 一条规则在某个月怎样才算通过？**

**EN** At least 20 orders must contain the item or items on the left of the rule, and the item on the right must appear that month. The rule must also reach 0.5% support, 50% confidence and a lift of 1.2. All 71 rules stay in the monthly denominator.

**中** 当月至少 20 笔订单要包含规则左侧的商品或商品组合，右侧商品也必须出现。同时，支持度至少为 0.5%、置信度至少为 50%、提升度至少为 1.2。每个月的分母始终是 71。

**4. Where do the 17,901 orders go? | 17,901 笔订单分别用在哪里？**

**EN** The three main stages used just over seventeen thousand orders. The remaining 744 came from the first nine days of December 2011. We analysed those orders separately so that the main test compares full months.

**中** 三个主要阶段共用 1.7 万多笔订单。剩余 744 笔来自 2011 年 12 月的前九天。这个短窗口单独分析，主测试才能按完整月份比较。

*Point to the counts | 指图数字*

7,365 (discovery / 发现) + 2,696 (validation / 验证) + 7,096 (test / 测试) = 17,157. Add 744 supplementary orders for a total of 17,901. 再加补充分析的 744 笔，共 17,901 笔。

**5. What did comparing the two mining algorithms show? | 两种挖掘算法的比较说明了什么？**

**EN** At the same discovery thresholds they found identical itemsets. In our benchmark, low-memory Apriori used less peak memory at all three support settings and ran faster at 1% and 2%. Those costs describe the implementations and data we tested.

**中** 在相同的发现期门槛下，两者找到的频繁项集完全一致。在本次测试中，低内存模式的 Apriori 在三档支持度下的峰值内存都更低，并在 1% 和 2% 两档运行得更快。这些开销对应的是本次采用的实现和数据。
