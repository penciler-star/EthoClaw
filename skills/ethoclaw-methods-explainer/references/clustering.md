# Clustering Reference

在用户询问聚类、树状图、热图、降维后分组、行为类型划分时读取本文件。

## 聚类解释的核心问题

解释聚类结果时，必须回答：

1. 被聚类的对象是什么。
2. 每个对象由哪些特征表示。
3. 特征是否做了缩放或标准化。
4. 相似性或距离如何定义。
5. 使用了哪种聚类算法。
6. 聚类数如何确定。
7. 聚类结果如何可视化。
8. 结果对参数选择是否敏感。

## 常见输入结构

### 样本 x 特征矩阵

最常见的输入是一个矩阵：

- 行：个体、session、trial、群体或时间窗。
- 列：行为频次、持续时间、比例、网络指标、运动学特征等。

解释时必须说清：

- 每行代表谁。
- 每列代表什么。
- 特征是否量纲一致。

## 常见方法

### Hierarchical Clustering

- 适合：希望展示样本之间的层级相似关系，或输出树状图（dendrogram）。
- 关键参数：distance metric、linkage method。
- 常见 metric：Euclidean、Manhattan、correlation distance。
- 常见 linkage：complete、average、single、Ward。
- 输出：树状图，可配合热图展示特征模式。

解释重点：

- 树状图分支高度表示合并时的不相似程度。
- 不同 linkage 会影响簇形状和边界。
- 如果用了 Ward linkage，通常默认搭配 Euclidean distance 更常见。

### K-means

- 适合：预先设定 cluster 数量，关注质心（centroid）型分组。
- 关键参数：k、初始化方式、随机种子。
- 前提：特征最好连续且已缩放。
- 输出：每个样本的 cluster label 和各 cluster centroid。

解释重点：

- k 必须说明如何选择。
- 结果可能受初始化和 seed 影响。
- 不适合强非球形簇或大量离群值场景。

### Density-based Clustering

- 例如 DBSCAN。
- 适合：存在噪声点、簇形状不规则。
- 关键参数：eps、min_samples。
- 输出：簇标签和噪声点。

解释重点：

- 需要说明为什么选择密度聚类而不是 k-means。
- 对参数敏感，尤其是 eps。

## 特征预处理

聚类解释里优先检查：

- 是否对每个特征做 z-score 标准化。
- 是否做 log transform 或其他变换。
- 是否剔除高度共线的变量。
- 是否对缺失值做插补。
- 是否先对个体内重复观测求均值或中位数。

如果特征量纲差异明显而未缩放，要明确指出这会让大数值变量主导距离计算。

## 如何决定 cluster 数量

常见依据：

- Elbow method
- Silhouette score
- Gap statistic
- AIC / BIC（更常见于模型型聚类）
- 先验生物学理由或已知类别数

解释时不要把这些方法说成“自动给出真值”。更准确的说法是：它们是帮助选择相对合理分组数的准则。

## 常见图形解释

### Dendrogram

必须说明：

- 叶节点代表什么对象。
- 分支高度表示什么。
- 在哪一高度切树得到几个 cluster。

### Heatmap with clustering

必须说明：

- 颜色代表原始值、标准化值还是 z-score。
- 行聚类和列聚类是否都做了。
- 热图本身是展示模式，不是统计显著性证明。

### PCA / t-SNE / UMAP 后再着色 cluster

必须说明：

- 降维用于可视化，不等于聚类本身。
- cluster 可能是在原始高维空间算的，也可能直接在低维空间算的，两者含义不同。

## 常见坑

- 不说明特征和对象，导致 cluster 没有生物学含义。
- 把可视化分组错当成正式聚类算法。
- 不报告缩放方法、距离度量和 linkage / k。
- 用聚类结果直接得出生物学结论，却不做稳健性检查。
- 看到图上分开就说“显著不同”。

## 建议输出句式

### 来源卡最小模板

- 聚类对象：
- 输入特征：
- 预处理：
- 距离或相似度：
- 聚类方法：
- 参数选择依据：
- 可视化方式：
- 敏感性说明：

### Methods 写法提示

中文：

“基于每个个体在各行为指标上的标准化特征向量，采用……距离与……聚类方法对样本进行分组。”

英文：

"Samples were clustered based on standardized behavioral feature vectors using ... distance and ... clustering."
