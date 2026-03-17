# Clustering Reference

Read this file when users ask about clustering, dendrograms, heatmaps, dimensionality reduction grouping, or behavior type classification.

## Core Questions for Clustering Explanation

When explaining clustering results, must answer:

1. What objects are being clustered.
2. What features represent each object.
3. Whether features were scaled or standardized.
4. How similarity or distance is defined.
5. Which clustering algorithm was used.
6. How the number of clusters was determined.
7. How clustering results are visualized.
8. Whether results are sensitive to parameter choices.

## Common Input Structures

### Sample x Feature Matrix

Most common input is a matrix:

- Rows: individuals, sessions, trials, groups, or time windows.
- Columns: behavior frequencies, durations, proportions, network indicators, kinematic features, etc.

When explaining, must clarify:

- What each row represents.
- What each column represents.
- Whether features have consistent dimensions.

## Common Methods

### Hierarchical Clustering

- Suitable for: wanting to show hierarchical similarity relationships between samples, or output dendrograms.
- Key parameters: distance metric, linkage method.
- Common metrics: Euclidean, Manhattan, correlation distance.
- Common linkages: complete, average, single, Ward.
- Output: dendrogram, can accompany heatmap to show feature patterns.

Explanation focus:

- Dendrogram branch height represents dissimilarity at merge.
- Different linkages affect cluster shape and boundaries.
- If Ward linkage is used, typically paired with Euclidean distance.

### K-means

- Suitable for: pre-setting number of clusters, focusing on centroid-type grouping.
- Key parameters: k, initialization method, random seed.
- Prerequisites: features should be continuous and scaled.
- Output: cluster label for each sample and cluster centroids.

Explanation focus:

- Must explain how k is chosen.
- Results may be affected by initialization and seed.
- Not suitable for strongly non-spherical clusters or large outlier scenarios.

### Density-based Clustering

- e.g., DBSCAN.
- Suitable for: existing noise points, irregular cluster shapes.
- Key parameters: eps, min_samples.
- Output: cluster labels and noise points.

Explanation focus:

- Must explain why density clustering was chosen over k-means.
- Sensitive to parameters, especially eps.

## Feature Preprocessing

Prioritize checking in clustering explanations:

- Whether each feature was z-score standardized.
- Whether log transform or other transformations were done.
- Whether highly collinear variables were excluded.
- Whether missing values were imputed.
- Whether repeated observations within individuals were averaged or median-ed.

If feature dimension differences are obvious and not scaled, must explicitly point out this will cause large-value variables to dominate distance calculation.

## How to Determine Number of Clusters

Common basis:

- Elbow method
- Silhouette score
- Gap statistic
- AIC / BIC (more common in model-based clustering)
- Prior biological reasons or known number of categories

When explaining, do not present these methods as "automatically giving the true value". More accurate statement: they are guidelines to help choose a relatively reasonable number of groupings.

## Common Figure Explanations

### Dendrogram

Must explain:

- What objects leaf nodes represent.
- What branch heights represent.
- At what height the tree is cut to get how many clusters.

### Heatmap with Clustering

Must explain:

- Whether colors represent raw values, standardized values, or z-scores.
- Whether both row and column clustering are done.
- The heatmap itself shows patterns, not statistical significance proof.

### PCA / t-SNE / UMAP Colored by Cluster

Must explain:

- Dimensionality reduction is for visualization, not equal to clustering itself.
- Clusters may be computed in original high-dimensional space, or directly in low-dimensional space; the meanings are different.

## Common Pitfalls

- Not explaining features and objects, causing clusters to have no biological meaning.
- Mistaking visualized groupings for formal clustering algorithms.
- Not reporting scaling method, distance metric, and linkage/k.
- Using clustering results to directly draw biological conclusions without robustness checks.
- Seeing separation on figures and saying "significantly different".

## Recommended Output Sentence Patterns

### Provenance Card Minimum Template

- Clustering objects:
- Input features:
- Preprocessing:
- Distance or similarity:
- Clustering method:
- Parameter selection basis:
- Visualization method:
- Sensitivity explanation:

### Methods Writing Tips

In English:

"Samples were clustered based on standardized behavioral feature vectors using ... distance and ... clustering method."
