---
summary: "Dev agent tools notes (EthoClaw)"
read_when:
  - Using the dev gateway templates
  - Updating the default dev agent identity
---

# TOOLS.md

**Animal Pose Estimation**:
Automatically invokes DeepLabCut's SuperAnimal method to perform annotation-free pose estimation. (corresponding to ethoclaw-animal-pose-estimation skill)

**Animal Grounding**:
Automatically locates the animal's center point using image processing-based methods. (corresponding to ethoclaw-animal-grounding skill)

**Chart & Report Generation**:
Generates velocity heatmaps and trajectory heatmaps from tracking data (corresponding to ethoclaw-trajectory_velocity_heatmap_generate skill);

Supports generation of violin plots, cluster maps, and radar plots for multi-group datasets (corresponding to ethoclaw-multiparameter-violin-stats-generate skill, ethoclaw-multiparameter-clustermap-generate skill, ethoclaw-multiparameter-radar-generate skill);

Supports format conversion from CSV/Excel to the recommended standard format (corresponding to ethoclaw-normalize-tabular skill);

Automatically typesets and generates publication-ready figures for academic papers (corresponding to ethoclaw-paper-figure-layout skill);

Generates full analysis reports including experimental background, sample information, analytical content, and conclusions (corresponding to ethoclaw-analysis-report skill).

**Tutorial Assistance**:
Provides beginners with detailed explanations of parameter calculation methods, chart data sources, clustering algorithms and corresponding parameters, to facilitate the writing of the methods section in academic papers. (No corresponding skill module)

**Local Knowledge Base**:
Reads, summarizes, and outputs content from local PDF papers and reports. (corresponding to ethoclaw-pdf-research skill)

**Web Search**:
Retrieves the latest papers via web or academic search, and supports scheduled daily push of relevant papers from arXiv and PubMed. (corresponding to ethoclaw-daily-paper skill)
