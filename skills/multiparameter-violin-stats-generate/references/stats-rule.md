# 组间差异检验规则（约定）

本 skill 的统计检验选择遵循以下规则：

- **两组（2 groups）**：
  - 参数检验：**t 检验（t-test）**（默认：Welch t-test，方差不齐更稳健）
  - 非参数检验：**Mann–Whitney U 检验**
  - 直接比较两组间差异

- **三组及以上（>=3 groups）**：
  - 参数检验：**单因素方差分析（One-way ANOVA）**
  - 非参数检验：**Kruskal–Wallis 检验**
  - 先做整体检验是否存在组间差异；若整体显著（p <= alpha），再做**两两比较**

- **两两比较（pairwise）**：
  - 若整体为参数法：默认使用 **Welch t-test** 做 pairwise
  - 若整体为非参数法：默认使用 **Mann–Whitney U** 做 pairwise
  - 多重比较校正：默认 **Holm–Bonferroni**（输出 p_holm）
